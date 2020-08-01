from gi.repository import Gtk, Gio, GLib, Handy

from tasklib import TaskWarrior 
from handytask.tasklist import TaskList
import handytask.tasklist as tasklist
from datetime import datetime

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
      Gtk.TreeViewColumn("🤯", Gtk.CellRendererText(), text = tasklist.URGENCY_COLUMN)
    )

    # We want to be at least 600 pixels wide (-1 = no height minimum)
    self.set_size_request(600, -1)
    # If we have more space, please give it to us!
    self.set_hexpand(True)

    # Connect the selection callback if not none
    if select is not None:
      self.selection = self.body.get_selection()
      self.selection.connect("changed", select)

  def unselect(self):
    self.selection.unselect_all()



class TaskDetailView(Gtk.Box):
  def __init__(self, on_save, on_cancel, *args, **kwargs):
    super().__init__(
      orientation = Gtk.Orientation.VERTICAL, 
      spacing = 10,
      *args, **kwargs
    )

    self.task = None

    # We want to be at least 300 pixels wide (-1 = no height minimum)
    self.set_size_request(300, -1)

    label = Gtk.Label("Task")
    label.set_hexpand(True)
    label.set_justify(Gtk.Justification.LEFT)
    label.show()
    self.pack_start(label, False, False, 0)
    self.task_title = Gtk.Entry()
    self.pack_start(self.task_title, False, False, 0)
    self.task_title.show()

    box = Gtk.Box()
    box.show()
    self.completed_check = Gtk.CheckButton()
    self.completed_check.show()
    box.pack_start(self.completed_check, False, False, 10)
    label = Gtk.Label("Completed")
    label.show()
    box.pack_start(label, False, False, 0)
    self.completed_date = Gtk.Label("")
    self.completed_date.show()
    box.pack_start(self.completed_date, True, True, 0)
    self.completed_date.show()
    self.pack_start(box, False, False, 0)

    label = Gtk.Label("Due Date")
    label.show()
    self.pack_start(label, False, False, 0)
    self.due_date = Gtk.Calendar()
    self.due_date.show()
    self.pack_start(self.due_date, False, False, 0)

    label = Gtk.Label("Annotations (TBD)")
    self.pack_start(label, True, True, 0)
    label.show()

    box = Gtk.Box()
    box.show()
    button = Gtk.Button.new_with_mnemonic("_Cancel")
    if on_cancel is not None:
      button.connect("clicked", on_cancel)
    box.pack_start(button, True, True, 0)
    button.show()
    button = Gtk.Button.new_with_mnemonic("_Save")
    self.save_button = button
    if on_save is not None:
      button.connect("clicked", on_save)
    box.pack_start(button, True, True, 0)
    button.show()
    self.pack_start(box, False, False, 0)
    self.clear_task()

  def clear_task(self):
    self.task = None
    self.task_title.set_text("")
    self.completed_check.set_active(False)
    today = datetime.now()
    self.due_date.select_month(today.month-1, today.year)
    self.due_date.select_day(today.day)
    self.save_button.set_label("Create")

  def set_task(self, task):
    self.task = task
    self.task_title.set_text(task[tasklist.TITLE_COLUMN])
    self.completed_check.set_active(task[tasklist.COMPLETED_COLUMN])
    if task[tasklist.COMPLETED_COLUMN]:
      self.completed_date.set_text("DUE?")
    else:
      self.completed_date.set_text("")
    task = task[tasklist.TASK_COLUMN]
    due = task["due"]
    self.due_date.select_month(due.month-1, due.year)
    self.due_date.select_day(due.day)
    self.save_button.set_label("Save")

  def reset_task(self):
    if self.task is not None:
      self.set_task(self.task)

  def selected_due_date(self):
    selected = self.due_date.get_date()
    return datetime(
      year = selected.year,
      month = selected.month+1,
      day = selected.day,
    )

  def save_task(self, task_list):
    if self.task is None:
      idx = None
    else:
      idx = task_list.index_of_task(self.task)
    task_list.update(
      idx,
      description = self.task_title.get_text(),
      completed = self.completed_check.get_active(),
      due = self.selected_due_date()
    )


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

    # Allocate a universal taskwarrior instance
    self.tasks = TaskList(taskwarrior = TaskWarrior())

    # Responsive Box -> Stack transition
    # If there's enough width, we show the sidebar as a box (adjacent fields)
    # If not (see set_size_request in each of the children), Handy.Leaflet
    #   instead displays as a stack (one view at a time)
    self.multi_view = Handy.Leaflet(orientation = Gtk.Orientation.HORIZONTAL)
    self.add(self.multi_view)
    self.multi_view.show()

    # Allocate the task list view itself
    self.initial_selection = True
    self.task_view = TaskListView(
      tasks = self.tasks, 
      toggle = self.on_done_toggled,
      select = self.on_select_task
    )
    self.multi_view.add(self.task_view)
    self.task_view.show()

    # Allocate the task detail sidebar
    self.detail_view = TaskDetailView(
      on_save = self.on_detail_save_clicked,
      on_cancel = self.on_detail_cancel_clicked
    )
    self.multi_view.add(self.detail_view)
    # self.detail_view.hide()
    self.detail_view.show()

    self.task_view.unselect()
    # self.multi_view.set_visible_child(self.detail_view)

  def show_default_view(self):
    self.task_view.unselect()
    self.detail_view.clear_task()
    self.multi_view.set_visible_child(self.task_view)

  def show_task_view(self, task):
    self.detail_view.set_task(task)
    self.multi_view.set_visible_child(self.detail_view)

  def on_select_task(self, selection):
    if self.initial_selection:
      self.task_view.unselect()
      self.initial_selection = False
    model, treeiter = selection.get_selected()
    if treeiter is None:
      self.show_default_view()
    else:
      task = model[treeiter]
      self.show_task_view(task)

  def on_done_toggled(self, action, value):
    self.tasks.toggle_done(int(value))

  def on_maximize_toggle(self, action, value):
      action.set_state(value)
      if value.get_boolean():
          self.maximize()
      else:
          self.unmaximize()

  def on_detail_cancel_clicked(self, button):
    self.show_default_view()

  def on_detail_save_clicked(self, button):
    self.detail_view.save_task(self.tasks)
    self.show_default_view()
