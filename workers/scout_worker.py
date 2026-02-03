from fsm.validator import can_transition
import sys; sys.path.append("/srv/memory/fsm")
import os,time,uuid,json
from fsm.api import safe_set

SRC="/srv/memory/scout/manual_sources.txt"

def main():
    if not os.path.exists(SRC): return
    lines=[x.strip() for x in open(SRC) if x.strip()]
    for l in lines[:20]:
        item=str(uuid.uuid4())[:12]
        safe_set(item,None,"scouted",{"source":l})
        print("SCOUTED",item,l)

if __name__=="__main__":
    main()

# FSM guard must wrap set_state calls
