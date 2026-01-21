import json,time,hashlib,redis,sqlite3
R=redis.Redis(host="127.0.0.1",port=6379,decode_responses=True)
Q="q:tasks"
DB="/srv/gemivas-platform/db/gemivas.sqlite"
MAX_QUEUE=20
COOLDOWN_SEC=21600
SLEEP_SEC=300

def h(s): return hashlib.sha256(s.encode()).hexdigest()[:16]
def load_urls():
  con=sqlite3.connect(DB);cur=con.cursor()
  rows=cur.execute("select id,url from sources where kind='video' and enabled=1 order by id").fetchall()
  con.close();return rows
def push(url,sid):
  key="src:seen:"+h(url)
  if R.get(key) or R.llen(Q)>=MAX_QUEUE: return False
  tid=f"brain-{int(time.time()*1000)}"
  R.lpush(Q,json.dumps({"id":tid,"type":"download","payload":{"url":url,"source_id":sid},"try":0,"ts":int(time.time())}))
  R.setex(key,COOLDOWN_SEC,"1");return True
def main():
  while True:
    try:
      for sid,url in load_urls():
        url=(url or "").strip()
        if not url.startswith("http"): continue
        ok=push(url,sid);print("push",url,ok,flush=True)
    except Exception as e:
      print("err",str(e),flush=True)
    time.sleep(SLEEP_SEC)
if __name__=="__main__": main()
