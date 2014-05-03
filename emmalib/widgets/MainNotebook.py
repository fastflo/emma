import gc
import gtk
import widgets
from emmalib.QueryTab import QueryTab


class MainNotebook(gtk.Notebook):

    def __init__(self, emma):
        super(MainNotebook, self).__init__()
        self.emma = emma
        self.connect('switch_page', self.main_notebook_on_change_page)

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
        q.get_tab_close_button().connect('clicked', self.close_query_tab, q)
        self.set_current_page(new_page_index)
        self.emma.current_query.textview.grab_focus()

    def close_query_tab(self, button, tab_class):
        if len(self.emma.queries) == 1:
            return
        for q in self.emma.queries:
            if q == tab_class:
                i = self.emma.queries.index(q)
                del self.emma.queries[i]
                q.destroy()
                del q

                page_num = self.page_num(tab_class.get_ui())
                self.remove_page(page_num)
                gc.collect()
                return

    #
    #   Process List
    #

    def add_process_list_tab(self, host):
        process_list = widgets.TabProcessList(self.emma, host)
        new_page_num = self.append_page(process_list.get_ui(), process_list.get_label_ui())
        process_list.get_tab_close_button().connect('clicked', self.close_process_list_tab, process_list)
        self.set_current_page(new_page_num)

    def close_process_list_tab(self, button, tab_class):
        page_num = self.page_num(tab_class.get_ui())
        self.remove_page(page_num)

    def add_tables_list_tab(self):
        tables_list = widgets.TabTablesList(self.emma)
        new_page_num = self.append_page(tables_list.get_ui(), tables_list.get_label_ui())
        tables_list.get_tab_close_button().connect('clicked', self.close_tables_list_tab, tables_list)
        self.set_current_page(new_page_num)

    def close_tables_list_tab(self, button, tab_class):
        page_num = self.page_num(tab_class.get_ui())
        self.remove_page(page_num)
        del tab_class

