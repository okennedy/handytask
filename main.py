import sys
sys.path += ["src"]

from handytask import HandyTaskApplication


# from gi.repository import GLib, Gio, Gtk


if __name__ == "__main__":
    app = HandyTaskApplication()
    app.run(sys.argv)