"""
Emma Dialogs module
"""
import gtk

from About import About
from ChangeLog import ChangeLog
from ExecuteQueryFromDisk import ExecuteQueryFromDisk


def alert(message):
    """
    :param message: str
    """
    dialog = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_INFO, gtk.BUTTONS_CLOSE, message)
    dialog.set_border_width(5)
    dialog.set_title("Information")
    dialog.label.set_property("use-markup", True)
    dialog.run()
    dialog.destroy()


def show_message(title, message, window=None):
    """
    :param title: str
    :param message: str
    :param window: gtk.Window
    """
    dialog = gtk.MessageDialog(window, gtk.DIALOG_MODAL, gtk.MESSAGE_INFO, gtk.BUTTONS_OK, message)
    dialog.set_border_width(5)
    dialog.label.set_property("use-markup", True)
    dialog.set_title(title)
    dialog.run()
    dialog.hide()


def confirm(title, message, window=None):
    """
    :param title: str
    :param message: str
    :param window: gtk.Window
    :return:
    """
    dialog = gtk.MessageDialog(
        window, gtk.DIALOG_MODAL, gtk.MESSAGE_QUESTION, gtk.BUTTONS_YES_NO, message)
    dialog.set_border_width(5)
    dialog.label.set_property("use-markup", True)
    dialog.set_title(title)
    answer = dialog.run()
    dialog.hide()
    return answer == gtk.RESPONSE_YES


def input_dialog(title, message, default="", window=None):
    """
    :param title: str
    :param message: str
    :param default: str
    :param window: gtk.Window
    :return:
    """
    dialog = gtk.Dialog(title, window, gtk.DIALOG_MODAL,
                        (gtk.STOCK_OK, gtk.RESPONSE_ACCEPT,
                         gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT))

    label = gtk.Label(message)
    label.set_property("use-markup", True)
    dialog.set_border_width(5)
    dialog.vbox.pack_start(label, True, True, 5)
    entry = gtk.Entry()
    entry.connect("activate", lambda *a: dialog.response(gtk.RESPONSE_ACCEPT))
    dialog.vbox.pack_start(entry, False, True, 5)
    label.show()
    entry.show()
    entry.set_text(default)
    answer = dialog.run()
    dialog.hide()
    if answer != gtk.RESPONSE_ACCEPT:
        return None
    return entry.get_text()
