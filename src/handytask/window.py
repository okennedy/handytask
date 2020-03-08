from gi.repository import Gtk, Gio, GLib, Handy


from tasklib import TaskWarrior 
from handytask.tasklist import TaskList
import handytask.tasklist as tasklist

class TaskListView(Gtk.ScrolledWindow):

  def __init__(self, tasks, toggle, select, *args, **kwargs):
    super().__init__(*args, **kwargs)

    self.body = Gtk.TreeView()
    self.body.set_model(tasks.model)
    self.add(self.body)
    self.body.show()

    done_toggle_renderer = Gtk.CellRendererToggle()
    done_toggle_renderer.connect("toggled", toggle)
    self.body.append_column(
      Gtk.TreeViewColumn("✓", done_toggle_renderer, active = tasklist.COMPLETED_COLUMN)
    )

    self.body.append_column(
      Gtk.TreeViewColumn("Task", Gtk.CellRendererText(), text = tasklist.ELLIPSIZED_TITLE_COLUMN)
    )

    self.body.append_column(
      Gtk.TreeViewColumn("Due", Gtk.CellRendererText(), text = tasklist.DUE_COLUMN)
    )

    self.body.append_column(
      Gtk.TreeViewColumn("Urg.", Gtk.CellRendererText(), text = tasklist.URGENCY_COLUMN)
    )

class TaskDetailView(Gtk.Box):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, { "orientation" : Gtk.Orientation.VERTICAL, **kwargs })

    # self.set_property("maximum-width", 100)

    label = Gtk.Label("Detail")
    self.pack_start(label, True, True, 0)
    label.show()

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

    self.tasks = TaskList(taskwarrior = TaskWarrior())

    self.multi_view = Handy.Leaflet(orientation = Gtk.Orientation.HORIZONTAL)
    self.add(self.multi_view)
    self.multi_view.show()

    self.task_view = TaskListView(
      tasks = self.tasks, 
      toggle = self.on_done_toggled,
      select = self.on_select_task
    )
    self.multi_view.add(self.task_view)
    self.task_view.show()

    self.detail_view = TaskDetailView()
    self.multi_view.add(self.detail_view)
    self.detail_view.show()

  def on_select_task(select, action, value):
    print("Select task: {}".format(value))


  def on_done_toggled(self, action, value):
    self.tasks.toggle_done(int(value))

  def on_maximize_toggle(self, action, value):
      action.set_state(value)
      if value.get_boolean():
          self.maximize()
      else:
          self.unmaximize()
