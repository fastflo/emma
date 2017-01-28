import gtk
from CloseQuery import CloseQuery
from RenameQuery import RenameQuery
from NewQuery import NewQuery
from SetFont import SetFont
from LoadQuery import LoadQuery
from SaveQuery import SaveQuery
from ReExBox import ReExBox
from ExecuteQuery import ExecuteQuery


class QueryToolbar(gtk.Toolbar):

    def __init__(self, query, emma):
        """
        @param query: QueryTab
        @param emma: Emma
        """
        super(QueryToolbar, self).__init__()
        # self.emma = emma
        # self.query = query

        query_toolbar = self
        btn_close_query = CloseQuery(query, emma)
        query_toolbar.insert(btn_close_query, 0)

        query_toolbar.insert(gtk.SeparatorToolItem(), 0)

        btn_rename_query = RenameQuery(query, emma)
        query_toolbar.insert(btn_rename_query, 0)

        btn_new_query = NewQuery(query, emma)
        query_toolbar.insert(btn_new_query, 0)

        query_toolbar.insert(gtk.SeparatorToolItem(), 0)

        btn_set_font = SetFont(query, emma)
        query_toolbar.insert(btn_set_font, 0)

        query_toolbar.insert(gtk.SeparatorToolItem(), 0)

        btn_load_query = LoadQuery(query, emma)
        query_toolbar.insert(btn_load_query, 0)

        btn_save_query = SaveQuery(query, emma)
        query_toolbar.insert(btn_save_query, 0)

        self.reex = ReExBox(query, emma)
        query_toolbar.insert(self.reex, 0)

        btn_ex_query = ExecuteQuery(query, emma)
        query_toolbar.insert(btn_ex_query, 0)
