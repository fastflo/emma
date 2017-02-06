"""
Emma's global event manager
"""


class EventsManager:
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
        if event_name in self.__handlers__:
            for event in self.__handlers__[event_name]:
                if len(args) > 0:
                    event(args)
                else:
                    event()
