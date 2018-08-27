import time
from string import upper


#
# StateMachine class
#
# Written by Kenny Gilfilen
# September 28, 2012
#
# Rev 0.2
#
# Taken from "Charming Python: Using state machines", an article by David Mertz on the IBM Developer Works web site.
#
# this class makes derived classes state machines. This gives them the capability of stepping through processes
# in an orderly manner and not stopping till they are done.
#
# State handler methods are defined in the derived classes, and take cargo (data passed from previous state),
# and return the name of the next state and the cargo.
#
#  SO...
# 1. the derived classes are initialized with nothing pertaining to this base class,
# 2. they add states using the "add_state" method, which are pointers to real methods already created. 
#    The final state has the third (optional) parameter set to 1, or True. 
# 3. the initial state is added by name to the "set_start" method. 


class StateMachine(object):
    def __init__(self):
        self.handlers = {}
        self.startState = None
        self.endStates = []
        self.sleep=1

    def add_state(self, name, handler, end_state=0):
        name = upper(name)
        self.handlers[name] = handler
        if end_state:
            self.endStates.append(name)

    def set_start(self, name):
        self.startState = upper(name)

    def set_sleep(self, sleep):
        self.sleep = sleep

    def clear_state(self):
        self.handlers = {}
        self.startState = None
        self.endStates = []

    def runStates(self, cargo):
        try:
            handler = self.handlers[self.startState]
        except:
            raise  "InitializationError", "must call .set_start() before .run()"

        if not self.endStates:
            raise  "InitializationError", "at least one state must be an end_state"

        while 1:
            (newState, cargo) = handler(cargo)
            if upper(newState) in self.endStates:
                break 
            else:
                handler = self.handlers[upper(newState)]     
