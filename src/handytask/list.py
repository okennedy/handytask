from gi.repository import Gtk

from . import task as tasklist


class TaskListView(Gtk.ScrolledWindow):

  def __init__(self, tasks, toggle, on_select, *args, **kwargs):
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

    task_column = Gtk.TreeViewColumn("Task", Gtk.CellRendererText(), text = tasklist.ELLIPSIZED_TITLE_COLUMN)
    task_column.set_fixed_width(150)
    # task_column.set_max_width(300)
    task_column.set_expand(True)
    self.body.append_column(task_column)

    self.body.append_column(
      Gtk.TreeViewColumn("Due", Gtk.CellRendererText(), text = tasklist.DUE_COLUMN)
    )

    self.body.append_column(
      Gtk.TreeViewColumn("🤯", Gtk.CellRendererText(), text = tasklist.URGENCY_COLUMN)
    )

    # We want to be at least 600 pixels wide (-1 = no height minimum)
    self.set_size_request(200, -1)
    # If we have more space, please give it to us!
    self.set_hexpand(True)

    # Connect the selection callback if not none
    if on_select is not None:
      self.selection = self.body.get_selection()
      self.selection.connect("changed", on_select)

  def unselect(self):
    self.selection.unselect_all()

  def refresh(self, tasks):
    self.body.set_model(tasks.model)