from gi.repository import Gtk
from datetime import datetime

from . import task as tasklist


class TaskDetailView(Gtk.Box):
  def __init__(self, on_save, on_cancel, on_update_date, *args, **kwargs):
    super().__init__(
      orientation = Gtk.Orientation.VERTICAL, 
      spacing = 10,
      *args, **kwargs
    )

    self.task = None
    self.silence_updates = True

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
    self.on_update_date = on_update_date
    self.due_date.connect("day-selected", self.handle_update_date)
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
    self.silence_updates = False

  def clear_task(self):
    self.task = None
    self.task_title.set_text("")
    self.completed_check.set_active(False)
    today = datetime.now()
    self.due_date.select_month(today.month-1, today.year)
    self.due_date.select_day(today.day)
    self.save_button.set_label("Create")


  def set_task(self, task):
    self.silence_updates = True
    self.task = task
    self.task_title.set_text(task[tasklist.TITLE_COLUMN])
    self.completed_check.set_active(task[tasklist.COMPLETED_COLUMN])
    if task[tasklist.COMPLETED_COLUMN]:
      self.completed_date.set_text("DUE?")
    else:
      self.completed_date.set_text("")
    task = task[tasklist.TASK_COLUMN]
    due = task["due"]
    if due is not None:
      self.due_date.select_month(due.month-1, due.year)
      self.due_date.select_day(due.day)
    else:
      today = datetime.now()
      self.due_date.select_month(today.month-1, today.year)
      self.due_date.select_day(today.day)
    self.silence_updates = False
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

  def get_task(self):
    if self.task is None: 
      return None
    return self.task[tasklist.TASK_COLUMN]

  def handle_update_date(self, calendar):
    if not self.silence_updates:
      if self.on_update_date is not None:
        self.on_update_date(calendar)
