"""
Emma's Changelog dialog
"""
import os
import gtk
from emmalib.Constants import emma_path


class ChangeLog(gtk.Window):
    """
    Emma's Changelog dialog
    """
    def __init__(self):
        super(ChangeLog, self).__init__()

        self.set_position(gtk.WIN_POS_CENTER)
        self.resize(640, 480)

        scrolled_window = gtk.ScrolledWindow()
        scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.add(scrolled_window)
        text_view = gtk.TextView()
        scrolled_window.add(text_view)

        changelog_file = file(os.path.join(emma_path, "../changelog"))
        changelog = changelog_file.read()
        changelog_file.close()

        text_view.get_buffer().set_text(changelog.decode("latin1", "replace"))

        self.connect('delete-event', self.on_changelog_delete)

        text_view.show()
        scrolled_window.show()

    @staticmethod
    def on_changelog_delete(window, _):
        """
        :param window: gtk.Window
        :param _:
        :return: bool
        """
        window.hide()
        return True
