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

        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.add(sw)
        tv = gtk.TextView()
        sw.add(tv)

        fp = file(os.path.join(emma_path, "../changelog"))
        changelog = fp.read()
        fp.close()

        tv.get_buffer().set_text(changelog.decode("latin1", "replace"))

        self.connect('delete-event', self.on_changelog_delete)

        tv.show()
        sw.show()

    @staticmethod
    def on_changelog_delete(window, _):
        """
        :param window: gtk.Window
        :param _:
        :return: bool
        """
        window.hide()
        return True



