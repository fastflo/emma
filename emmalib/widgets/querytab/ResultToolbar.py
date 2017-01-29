"""
Result tool bar
"""
import gtk
from resulttoolbar.AddRecord import AddRecord
from resulttoolbar.RememberOrder import RememberOrder
from resulttoolbar.ApplyRecord import ApplyRecord
from resulttoolbar.DeleteRecord import DeleteRecord
from resulttoolbar.LocalSearch import LocalSearch
from resulttoolbar.RemoveOrder import RemoveOrder
from resulttoolbar.SaveResultCsv import SaveResultCsv
from resulttoolbar.SaveResultSql import SaveResultSql
from resulttoolbar.SetRequltFont import SetResultFont


class ResultToolbar(gtk.Toolbar):
    """
    Result tool bar
    """
    def __init__(self, query, emma):
        """
        @param query: QueryTab
        @param emma: Emma
        """
        super(ResultToolbar, self).__init__()

        self.set_orientation(gtk.ORIENTATION_VERTICAL)
        self.set_style(gtk.TOOLBAR_ICONS)

        # self.emma = emma
        # self.query = query

        self.add_record = AddRecord(query, emma)
        self.delete_record = DeleteRecord(query, emma)
        self.apply_record = ApplyRecord(query, emma)
        self.local_search = LocalSearch(query, emma)

        self.remember_order = RememberOrder(query, emma)
        self.remove_order = RemoveOrder(query, emma)

        self.save_result_csv = SaveResultCsv(query, emma)
        self.save_result_sql = SaveResultSql(query, emma)

        self.set_result_font = SetResultFont(query, emma)

        self.insert(self.remove_order, 0)
        self.insert(self.remember_order, 0)

        self.insert(self.set_result_font, 0)

        self.insert(self.local_search, 0)

        self.insert(self.save_result_csv, 0)
        self.insert(self.save_result_sql, 0)

        self.insert(self.apply_record, 0)
        self.insert(self.delete_record, 0)
        self.insert(self.add_record, 0)

