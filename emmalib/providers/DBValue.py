import gobject


class DBValue(gobject.GObject):

    def __init__(self, value):
        super(DBValue, self).__init__()
        self.value = value

    def __cmp__(self, other):
        print self.value, '?', other.value
        return self.value > other.value

    def __eq__(self, other):
        # Defines behavior for the equality operator, ==.
        return self.value == other.value

    def __ne__(self, other):
        # Defines behavior for the inequality operator, !=.
        return self.value != other.value

    def __lt__(self, other):
        # Defines behavior for the less-than operator, <.
        return self.value < other.value

    def __gt__(self, other):
        # Defines behavior for the greater-than operator, >.
        return self.value > other.value

    def __le__(self, other):
        # Defines behavior for the less-than-or-equal-to operator, <=.
        return self.value <= other.value

    def __ge__(self, other):
        # Defines behavior for the greater-than-or-equal-to operator, >=.
        return self.value <= other.value