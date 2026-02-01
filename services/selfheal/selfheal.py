import os, time, pathlib, json

VIDEO_DIR="/srv/web/feed/videos"
FSM_DIR="/srv/memory/fsm/items"
TTL=7*24*3600
MAX_GB=200

def disk_used_gb():
    st=os.statvfs(VIDEO_DIR)
    used=(st.f_blocks-st.f_bfree)*st.f_frsize
    return used/1024/1024/1024
def cleanup_old():
    now=time.time()
    for f in pathlib.Path(VIDEO_DIR).glob("*.mp4"):
        if now-f.stat().st_mtime > TTL:
            try: os.remove(f)
            except: pass

def drop_missing():
    for f in pathlib.Path(FSM_DIR).glob("*.json"):
        try:
            item=json.load(open(f))
            p=item.get("download_path")
            if p and not os.path.exists(p):
                item["state"]="dropped"
                json.dump(item,open(f,"w"))
        except: pass
def main():
    cleanup_old()
    drop_missing()

if __name__=="__main__": main()
