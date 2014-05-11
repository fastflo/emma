import gtk


class Spinner:
    def __init__(self):
        window = gtk.Window()
        window.set_default_size(200, 200)
        vbox = gtk.VBox(False, 5)
        hbox = gtk.HBox(True, 5)

        self.spinner = gtk.Spinner()
        button_start = gtk.Button("Start")
        button_stop = gtk.Button("Stop")

        window.connect("destroy", lambda w: gtk.main_quit())
        button_start.connect("clicked", self.start_animation)
        button_stop.connect("clicked", self.stop_animation)

        window.add(vbox)
        vbox.pack_start(self.spinner, True, True, 0)
        vbox.pack_end(hbox, False, False, 0)
        hbox.pack_start(button_start)
        hbox.pack_start(button_stop)

        window.show_all()

    def start_animation(self, widget):
        self.spinner.start()

    def stop_animation(self, widget):
        self.spinner.stop()

Spinner()
gtk.main()