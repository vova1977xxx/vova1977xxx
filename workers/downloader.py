import os, time, json
from fsm.api import safe_set
FSM_DIR='/srv/memory/fsm/items'
def run():
    while True:
        for f in os.listdir(FSM_DIR):
            p=os.path.join(FSM_DIR,f)
            try:
                d=json.load(open(p))
                if d.get('state')=='scouted':
                    safe_set(f,'scouted','downloaded',{})
            except: pass
        time.sleep(5)

if __name__=='__main__': run()
