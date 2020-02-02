from gi.repository import Gtk, Gio, GLib

from tasklib import TaskWarrior 
from handytask.tasklist import TaskList
import handytask.tasklist as tasklist

class HandyTaskAppWindow(Gtk.ApplicationWindow):

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)


    # This will be in the windows group and have the "win" prefix
    max_action = Gio.SimpleAction.new_stateful("maximize", None,
                                       GLib.Variant.new_boolean(False))
    max_action.connect("change-state", self.on_maximize_toggle)
    self.add_action(max_action)

    # Keep it in sync with the actual state
    self.connect("notify::is-maximized",
                        lambda obj, pspec: max_action.set_state(
                                           GLib.Variant.new_boolean(obj.props.is_maximized)))

    self.scroller = Gtk.ScrolledWindow()
    self.add(self.scroller)
    self.scroller.show()

    self.tasks = TaskList(taskwarrior = TaskWarrior())
    self.task_view = Gtk.TreeView()
    self.task_view.set_model(self.tasks.model)
    self.scroller.add(self.task_view)
    self.task_view.show()

    self.task_view.append_column(
      Gtk.TreeViewColumn("Task", Gtk.CellRendererText(), text = tasklist.TITLE_COLUMN)
    )
    self.task_view.append_column(
      Gtk.TreeViewColumn("Due", Gtk.CellRendererText(), text = tasklist.DUE_COLUMN)
    )

  def on_maximize_toggle(self, action, value):
      action.set_state(value)
      if value.get_boolean():
          self.maximize()
      else:
          self.unmaximize()
