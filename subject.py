

#
# Subject class 
#
# Written by Kenny Gilfilen
# September 19, 2012
#
# Rev 0.2
#
# Taken from the active state (http://code.activestate.com/recipes/131499-observer-pattern/) web site.
#
# An implementation of the Subscriber/Observer pattern:
#
# this class makes derived classes Subjects. This gives them the capability of notifying interested objects
# (observers) of important situations. So in the IM message world, this will be derived by a device 
# (the subject), which will maintain a list of message flow objects (observers) waiting for responses. The 
# subject will invoke the object pointers it has, which pointers point to observers with update methods. 
# Those update methods will check the message to see if it's a response to a request they sent.
#
#  SO...
# 1. a derived class, such as the client, is a Subject
# 2. the subject adds observers, which must have an update method defined, which does something because it was
# notified (checks the response to see if it is a response to its request). 
#

class Subject(object):
    def __init__(self):
        self._observers = []

    def addObserver(self, observer):
        if not observer in self._observers:
            self._observers.append(observer)

    def delObserver(self, observer):
        try:
            self._observers.remove(observer)
        except ValueError:
            pass

    def notifyObserver(self, modifier=None,cargo=None):
        for observer in self._observers:
            if modifier == observer:
                observer.update(cargo)
