import json,time,os,subprocess
INP="/srv/memory/radio/stations.json"

def alive(url):
 try:
  r=subprocess.run(["ffprobe","-v","error","-rw_timeout","8000000","-i",url,"-show_entries","format=format_name","-of","default=nw=1"],stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=12,text=True)
  return r.returncode==0
 except Exception:
  return False

def load():
 try:
  return json.load(open(INP,"r",encoding="utf-8"))
 except Exception:
  return {"stations":[]}

def save(j):
 tmp=INP+".tmp"
 open(tmp,"w",encoding="utf-8").write(json.dumps(j,ensure_ascii=False))
 os.replace(tmp,INP)

def main():
 j=load(); st=j.get("stations",[])
 now=int(time.time()); ok=0
 for s in st:
  url=s.get("stream_url","")
  a=alive(url) if url else False
  s["alive"]=bool(a); s["checked_ts"]=now
  if a: ok+=1
 save(j)
 print("OK radio alive:",ok,"/",len(st))

if __name__=="__main__":
 main()
