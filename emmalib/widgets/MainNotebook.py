import gc
import gtk
from TabProcessList import TabProcessList
from TabTablesList import TabTablesList
from emmalib.QueryTab import QueryTab


class MainNotebook(gtk.Notebook):

    def __init__(self, emma):
        """
        @param emma: Emma
        """
        super(MainNotebook, self).__init__()
        self.emma = emma
        self.tabs = []
        self.connect('switch_page', self.main_notebook_on_change_page)
        self.set_scrollable(True)

    #
    #   Set emma.current_query properly
    #   to keep backward compatibiluty for now
    #

    def main_notebook_on_change_page(self, np, pointer, page):
        page_ui = self.get_nth_page(page)
        for q in self.emma.queries:
            if q.ui == page_ui:
                self.emma.current_query = q
                q.on_query_db_eventbox_button_press_event(None, None)
                return

    #
    #   QueryTab
    #

    def add_query_tab(self):
        q = QueryTab(self.emma)
        self.emma.query_count += 1
        self.emma.current_query = q
        self.emma.queries.append(q)
        new_page_index = self.append_page(q.get_ui(), q.get_label_ui())
        self.set_tab_reorderable(q.get_ui(), True)
        q.get_tab_close_button().connect('clicked', self.close_query_tab, q)
        self.set_current_page(new_page_index)
        self.emma.current_query.textview.grab_focus()
        self.tabs.append(q)

    def close_query_tab(self, button, tab_class):
        if not tab_class:
            return False
        if len(self.emma.queries) == 1:
            return False
        for q in self.emma.queries:
            if q == tab_class:
                i = self.emma.queries.index(q)
                del self.emma.queries[i]
                i = self.tabs.index(q)
                del self.tabs[i]
                q.destroy()
                del q

                page_num = self.page_num(tab_class.get_ui())
                self.remove_page(page_num)
                gc.collect()
                return True
        return False

    def add_process_list_tab(self, host):
        self.add_generic_tab(TabProcessList(self.emma, host))

    def add_tables_list_tab(self):
        self.add_generic_tab(TabTablesList(self.emma))

    def add_generic_tab(self, tab_class):
        new_page_num = self.append_page(tab_class.get_ui(), tab_class.get_label_ui())
        self.set_tab_reorderable(tab_class.get_ui(), True)
        tab_class.get_tab_close_button().connect('clicked', self.close_generic_tab, tab_class)
        self.set_current_page(new_page_num)
        self.tabs.append(tab_class)

    def close_generic_tab(self, button, tab_class):
        if not tab_class:
            return
        page_num = self.page_num(tab_class.get_ui())
        self.remove_page(page_num)
        i = self.tabs.index(tab_class)
        del self.tabs[i]
        gc.collect()

    def close_current_tab(self):
        page_num = self.get_current_page()
        if page_num < 0:
            return
        current_tab = self.get_nth_page(page_num)
        for tab in self.tabs:
            if tab.get_ui() == current_tab:
                if type(tab) is QueryTab:
                    self.close_query_tab(None, tab)
                else:
                    self.close_generic_tab(None, tab)