from .validator import can_transition
from fsm import set_state
def safe_set(item,old,new,meta=None):
    if old and not can_transition(old,new): return False
    set_state(item,new,meta or {})
    return True
