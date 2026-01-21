import json,time,hashlib,redis

R=redis.Redis(host="127.0.0.1",port=6379,decode_responses=True)
Q="q:tasks"
CFG="/srv/gemivas-platform/configs/video_sources.json"
MAX_QUEUE=20
COOLDOWN_SEC=6*3600
SLEEP_SEC=300

def h(s:str)->str:
    return hashlib.sha256(s.encode()).hexdigest()[:16]

def push(url:str)->bool:
    key="src:seen:"+h(url)
    if R.get(key):
        return False
    if R.llen(Q)>=MAX_QUEUE:
        return False
    tid=f"brain-{int(time.time()*1000)}"
    R.lpush(Q,json.dumps({"id":tid,"type":"download","payload":{"url":url},"try":0,"ts":int(time.time())}))
    R.setex(key,COOLDOWN_SEC,"1")
    return True

def main():
    while True:
        try:
            data=json.load(open(CFG,"r"))
            srcs=data.get("video_sources",[])
            for s in srcs:
                url=(s.get("url") or "").strip()
                if not url.startswith("http"):
                    continue
                ok=push(url)
                print("push",url,ok,flush=True)
        except Exception as e:
            print("err",str(e),flush=True)
        time.sleep(SLEEP_SEC)

if __name__=="__main__":
    main()
