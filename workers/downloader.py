from fsm.validator import can_transition
from fsm.states import STATES, TRANSITIONS
import time
while True:
    time.sleep(10)

# FSM check
# use can_transition(old_state,new_state) before state change
