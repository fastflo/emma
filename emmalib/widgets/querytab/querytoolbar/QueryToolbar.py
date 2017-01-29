import gtk
from CloseQuery import CloseQuery
from RenameQuery import RenameQuery
from NewQuery import NewQuery
# from SetFont import SetFont
# from LoadQuery import LoadQuery
# from SaveQuery import SaveQuery
# from ReExBox import ReExBox
from ExecuteQuery import ExecuteQuery


class QueryToolbar(gtk.Toolbar):
    """
    @param query: QueryTab
    @param emma: Emma
    """
    def __init__(self, query, emma):
        super(QueryToolbar, self).__init__()
        # self.emma = emma
        # self.query = query

        self.insert(CloseQuery(query, emma), 0)

        self.insert(gtk.SeparatorToolItem(), 0)

        self.insert(RenameQuery(query, emma), 0)

        self.insert(NewQuery(query, emma), 0)

        self.insert(gtk.SeparatorToolItem(), 0)

        # btn_set_font = SetFont(query, emma)
        # self.insert(btn_set_font, 0)
        #
        # self.insert(gtk.SeparatorToolItem(), 0)

        # btn_load_query = LoadQuery(query, emma)
        # self.insert(btn_load_query, 0)
        #
        # btn_save_query = SaveQuery(query, emma)
        # self.insert(btn_save_query, 0)

        # self.reex = ReExBox(query, emma)
        # self.insert(self.reex, 0)

        self.insert(ExecuteQuery(query, emma), 0)
