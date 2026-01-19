import os,json,time,shutil,glob,uuid
from datetime import datetime
MEM="/srv/memory/feed"
IDX=os.path.join(MEM,"index.json")
VIDEOS="/srv/web/feed/videos"
UPLOAD="/srv/uploads/feed"
LOOPS="/srv/web/video_8k/loops"

def load():
 os.makedirs(MEM,exist_ok=True)
 if os.path.exists(IDX):
  try: return json.load(open(IDX,"r",encoding="utf-8"))
  except: pass
 return {"items":[]}

def save(j):
 os.makedirs(MEM,exist_ok=True)
 tmp=IDX+".tmp"
 open(tmp,"w",encoding="utf-8").write(json.dumps(j,ensure_ascii=False))
 os.replace(tmp,IDX)

def list_mp4(path):
 return sorted(glob.glob(os.path.join(path,"*.mp4")))

def ensure_dst():
 d=datetime.utcnow(); p=os.path.join(VIDEOS,str(d.year),f"{d.month:02d}")
 os.makedirs(p,exist_ok=True); return p

def publish(src):
 dst_dir=ensure_dst()
 vid=str(uuid.uuid4())[:12]
 dst=os.path.join(dst_dir,vid+".mp4")
 shutil.copy2(src,dst)
 url="/feed/videos/"+os.path.relpath(dst,VIDEOS).replace(os.sep,"/")
 return vid,url

def main():
 j=load(); items=j.get("items",[])
 have=set([str(x.get("src","")) for x in items])
 cand=list_mp4(UPLOAD)
 if not cand: cand=list_mp4(LOOPS)
 added=0
 for src in cand[:50]:
  if src in have: continue
  vid,url=publish(src)
  items.insert(0,{"id":vid,"title":"GEMIVAS Video","url":url,"src":src,"ts":int(time.time())})
  added+=1
  if added>=10: break
 j["items"]=items[:500]
 save(j)
 print("OK published:",added,"total:",len(items))

if __name__=="__main__":
 main()
