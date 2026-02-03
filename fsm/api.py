from .validator import can_transition
def safe_set(old,new): return can_transition(old,new)
