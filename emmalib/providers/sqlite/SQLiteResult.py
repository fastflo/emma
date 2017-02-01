class SQLiteResult(object):
    """

    @param result:
    @param d:
    """

    def __init__(self, result, d):
        self.result = result
        if d:
            self.description = tuple(d)
        else:
            self.description = ()

    def fetch_row(self, arg):
        """
        @param arg:
        @return:
        """
        return self.result

    def describe(self):
        """
        @return: ()
        """
        return self.description

    def num_rows(self):
        """
        @return: int
        """
        return len(self.result)