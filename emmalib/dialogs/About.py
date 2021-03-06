"""
Emma's about dialog
"""
import gtk
from emmalib import version


class About(gtk.AboutDialog):
    """
    Emma's about dialog
    """
    def __init__(self):
        super(About, self).__init__()
        self.set_authors((
            "Florian Schmidt <schmidt_florian at gmx.de>",
            "Nickolay Karnaukhov <mr.electronick@gmail.com>"
        ))
        self.set_program_name('Emma')
        self.set_version(version)
        self.set_copyright("(c) Florian 'fastflo' Schmidt 2006\n"
                           "(c) Nickolay 'mr.electronick' Karnaukhov 2014")
        self.set_comments("Extendable Database Managing Assistant\n\nsuccessor of yamysqlfront")
        self.set_website('http://emma-assistant.org')
