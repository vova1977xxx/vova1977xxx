import os,json,subprocess,hashlib
CFG="/srv/gemivas-platform/configs/video_sources.json"
OUTDIR="/srv/uploads/feed"

def sha1(s):
 return hashlib.sha1(s.encode("utf-8")).hexdigest()[:12]

def load():
 try:
  return json.load(open(CFG,"r",encoding="utf-8"))
 except Exception:
  return {"video_sources":[]}

def dl(url):
 os.makedirs(OUTDIR,exist_ok=True)
 fn=sha1(url)+".mp4"
 dst=os.path.join(OUTDIR,fn)
 if os.path.exists(dst) and os.path.getsize(dst)>1024*50:
  return "skip",dst
 tmp=dst+".tmp"
 r=subprocess.run(["curl","-L","--fail","--max-time","180","-o",tmp,url],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
 if r.returncode!=0:
  try: os.unlink(tmp)
  except: pass
  return "fail",r.stderr.strip()[:120]
 os.replace(tmp,dst)
 return "ok",dst

def main():
 j=load(); src=j.get("video_sources",[])
 ok=0
 for s in src[:20]:
  url=s.get("url","")
  if not url: continue
  st,res=dl(url)
  if st=="ok": ok+=1
 print("OK downloaded:",ok,"/",len(src))

if __name__=="__main__":
 main()
