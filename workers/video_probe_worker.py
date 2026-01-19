import os,glob,json,subprocess
DIR="/srv/uploads/feed"

def probe(path):
 r=subprocess.run(["ffprobe","-v","error","-select_streams","v:0","-show_entries","stream=width,height,duration","-of","json",path],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
 if r.returncode!=0: return None
 j=json.loads(r.stdout or "{}")
 s=(j.get("streams") or [{}])[0]
 w=int(float(s.get("width") or 0))
 h=int(float(s.get("height") or 0))
 d=float(s.get("duration") or 0)
 # audio check
 ra=subprocess.run(["ffprobe","-v","error","-select_streams","a:0","-show_entries","stream=codec_name","-of","default=nw=1",path],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
 has_audio=(ra.returncode==0 and ("codec_name" in (ra.stdout or "")))
 return {"w":w,"h":h,"d":d,"audio":has_audio}

def ok(meta):
 if not meta: return False
 if not meta["audio"]: return False
 if meta["h"]<480: return False
 if meta["d"]<20 or meta["d"]>300: return False
 return True

def main():
 files=sorted(glob.glob(os.path.join(DIR,"*.mp4")))
 kept=0; deleted=0
 for f in files:
  m=probe(f)
  if ok(m):
   kept+=1
   continue
  try:
   os.unlink(f)
   deleted+=1
  except Exception:
   pass
 print("OK probe kept:",kept,"deleted:",deleted)

if __name__=="__main__":
 main()
