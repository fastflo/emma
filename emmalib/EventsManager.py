"""
Emma's global event manager
"""


class EventsManager(object):
    """
    Emma's global event manager
    """

    def __init__(self):
        self.__handlers__ = {}

    def on(self, event_name, event_callback):
        """
        :param event_name: str
        :param event_callback: function
        """
        if event_name not in self.__handlers__:
            self.__handlers__[event_name] = []
        self.__handlers__[event_name].append(event_callback)

    def trigger(self, event_name, *args):
        """
        :param event_name: str
        :param args: []
        """
        # print '---'
        # print 'EventManager.trigger : ', event_name
        # print '---'
        if event_name in self.__handlers__:
            # print 'Count of handlers: ', len(self.__handlers__[event_name])
            for event in self.__handlers__[event_name]:
                if len(args) > 0:
                    event(*args)
                else:
                    event()
