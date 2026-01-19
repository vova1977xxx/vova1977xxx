import os,json,glob
MEM="/srv/memory/feed/index.json"
ROOT="/srv/web/feed/videos"
MAX_KEEP=80

def load():
 try: return json.load(open(MEM,"r",encoding="utf-8"))
 except: return {"items":[]}

def save(j):
 tmp=MEM+".tmp"
 open(tmp,"w",encoding="utf-8").write(json.dumps(j,ensure_ascii=False))
 os.replace(tmp,MEM)

def main():
 j=load(); items=j.get("items",[])
 # remove broken
 ok=[]
 for it in items:
  url=it.get("url","")
  if url.startswith("/feed/videos/"):
   p=os.path.join(ROOT,url.replace("/feed/videos/",""))
   if os.path.exists(p): ok.append(it)
  else:
   ok.append(it)
 items=ok
 # delete old files
 files=sorted(glob.glob(ROOT+"/**/*.mp4",recursive=True),key=lambda x: os.path.getmtime(x))
 if len(files)>MAX_KEEP:
  for f in files[:len(files)-MAX_KEEP]:
   try: os.unlink(f)
   except: pass
 # trim index
 j["items"]=items[:MAX_KEEP]
 save(j)
 print("OK cleanup items:",len(j["items"]),"files:",len(files))

if __name__=="__main__":
 main()
