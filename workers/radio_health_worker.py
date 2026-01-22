import time,subprocess,sqlite3

DB="/srv/gemivas_platform/data/gemivas.db"

def alive(url:str)->bool:
 try:
  r=subprocess.run(["ffprobe","-v","error","-rw_timeout","8000000","-i",url,"-show_entries","format=format_name","-of","default=nw=1"],
                   stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=12,text=True)
  return r.returncode==0
 except Exception:
  return False

def main():
 conn=sqlite3.connect(DB)
 conn.execute("PRAGMA journal_mode=WAL;")
 now=int(time.time())
 rows=conn.execute("SELECT id,stream_url,fail_count,is_enabled FROM radio_stations WHERE is_enabled=1 ORDER BY id").fetchall()

 ok=0; total=len(rows)
 for (rid,url,fail_count,is_enabled) in rows:
  a=alive(url) if url else False
  if a:
   ok+=1
   conn.execute("UPDATE radio_stations SET fail_count=0,last_ok_ts=?,last_checked_ts=? WHERE id=?",(now,now,rid))
  else:
   fc=int(fail_count)+1
   conn.execute("UPDATE radio_stations SET fail_count=?,last_fail_ts=?,last_checked_ts=? WHERE id=?",(fc,now,now,rid))
   if fc>=3:
    conn.execute("UPDATE radio_stations SET is_enabled=0 WHERE id=?",(rid,))

 conn.commit()
 conn.close()
 print("OK radio alive:",ok,"/",total)

if __name__=="__main__":
 main()
