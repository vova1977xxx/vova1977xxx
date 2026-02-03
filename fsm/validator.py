from .states import TRANSITIONS
def can_transition(a,b): return b in TRANSITIONS.get(a,[])
