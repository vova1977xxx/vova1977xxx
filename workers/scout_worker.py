import sys; sys.path.append("/srv/memory/fsm")
import os,time,uuid,json
from fsm import set_state

SRC="/srv/memory/scout/manual_sources.txt"

def main():
    if not os.path.exists(SRC): return
    lines=[x.strip() for x in open(SRC) if x.strip()]
    for l in lines[:20]:
        item=str(uuid.uuid4())[:12]
        set_state(item,"scouted",{"source":l})
        print("SCOUTED",item,l)

if __name__=="__main__":
    main()
