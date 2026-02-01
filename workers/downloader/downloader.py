import json,pathlib
SRC_DB="/srv/memory/brain/source_scores.json"
def source_disabled(src):
    try:
        db=json.load(open(SRC_DB))
        return db.get(src)=="DISABLED"
    except:
        return False

import collections
import os,json,time,hashlib,subprocess,pathlib
FSM_DIR="/srv/memory/fsm/items"
VIDEO_DIR="/srv/web/feed/videos"
FP_DB="/srv/memory/fsm/fingerprints/seen.txt"
def sha1(s): return hashlib.sha1(s.encode()).hexdigest()[:16]
def seen(fp):
    if not os.path.exists(FP_DB): return False
    return fp in open(FP_DB).read().splitlines()
def remember(fp): open(FP_DB,"a").write(fp+"\n")
def load_items():
    for f in pathlib.Path(FSM_DIR).glob("*.json"):
        try: yield f,json.load(open(f))
        except: continue
def save_item(p,d):
    t=str(p)+".tmp"; json.dump(d,open(t,"w")); os.replace(t,p)
def download(src,out):
    cmd=["yt-dlp","-f","mp4","-o",out,src]
    return subprocess.run(cmd,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode==0
def main():
    src_count=collections.Counter()
    os.makedirs(VIDEO_DIR,exist_ok=True)
    for path,item in load_items():
        src=item.get("src","")
        if source_disabled(src):
            item["state"]="dropped"; item["error"]="source disabled"; save_item(path,item); continue
        src_count[src]+=1
        if item.get("state")!="scouted": continue
        if src_count[src]>3:
            item["state"]="dropped"; item["error"]="source spam"; save_item(path,item); continue
        src=item.get("src")
        if source_disabled(src):
            item["state"]="dropped"; item["error"]="source disabled"; save_item(path,item); continue
        if not src:
            item["state"]="dropped"; item["error"]="no src"; save_item(path,item); continue
        fp=sha1(src)
        if seen(fp):
            item["state"]="dropped"; item["error"]="duplicate"; save_item(path,item); continue
        out=os.path.join(VIDEO_DIR,fp+".mp4")
        ok=download(src,out)
        if ok and os.path.exists(out):
            remember(fp)
            item["state"]="downloaded"
            item["download_path"]=out
            item["downloaded_at"]=int(time.time())
        else:
            item["fail_count"]=item.get("fail_count",0)+1
            if item["fail_count"]>=3: item["state"]="dropped"
            item["last_error"]="download fail"
        save_item(path,item)
if __name__=="__main__": main()

