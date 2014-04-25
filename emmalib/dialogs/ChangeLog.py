import os
import gtk


class ChangeLog(gtk.Window):
    def __init__(self, emma_path, *args, **kwargs):
        super(ChangeLog, self).__init__(*args, **kwargs)

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

    def on_changelog_delete(self, window, event):
        window.hide()
        return True



