from gi.repository import Gtk, GObject
from datetime import datetime

UUID_COLUMN   = 0
TITLE_COLUMN  = 1
STATUS_COLUMN = 2
DUE_COLUMN    = 3


def stringify_date(d):
  return str(d)

class TaskList:
  def __init__(self, **kwargs):
    self.taskwarrior = kwargs["taskwarrior"]
    self.model = Gtk.ListStore(str, str, str, str)
    self.refresh()

  def refresh(self, **kwargs):
    """Refresh the model contents. 
       Arguments are passed directly to taskwarrior.tasks.filter
    """
    if kwargs:
      self.tasks = self.taskwarrior.tasks.filter(**kwargs)
    else:
      self.tasks = self.taskwarrior.tasks.all()

    self.model.clear()
    for task in self.tasks:
      print(task)
      self.model.append([
        task['uuid'],
        str(task),
        task['status'],
        stringify_date(task['due'])
      ])
