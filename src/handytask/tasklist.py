from gi.repository import Gtk, GObject
from datetime import datetime, timedelta
from tzlocal import get_localzone

UUID_COLUMN             = 0
TITLE_COLUMN            = 1
ELLIPSIZED_TITLE_COLUMN = 2
STATUS_COLUMN           = 3
DUE_COLUMN              = 4
COMPLETED_COLUMN        = 5
PENDING_COLUMN          = 6
ACTIVE_COLUMN           = 7

def stringify_date(d, now = datetime.now()):
  if d == None:
    return ""
  return d.strftime("%a, %b %d, %Y")
  # if(d.year == now.year):

def ellipsize(s, cutoff = 50):
  if len(s) > cutoff-3:
    return s[0:cutoff-3]+"..."
  else:
    return s

def default_limit():
  return datetime.now(get_localzone()) - timedelta(days = 7)

def is_task_completed(task):
  return not (task.pending or task.waiting)

def task_tuple(task):
  return [
    task['uuid'],                 # 0
    str(task),                    # 1
    ellipsize(str(task)),         # 2
    task['status'],               # 3
    stringify_date(task['due']),  # 4
    is_task_completed(task),      # 5
    task.pending,                 # 6
    task.active,                  # 7
  ]

class TaskList:
  def __init__(self, **kwargs):
    self.taskwarrior = kwargs["taskwarrior"]
    self.model = Gtk.ListStore(str, str, str, str, str, bool, bool, bool)
    self.refresh( )


  def refresh(self, limit = default_limit(), **kwargs):
    """Refresh the model contents. 
       Arguments are passed directly to taskwarrior.tasks.filter
    """
    if kwargs:
      self.tasks = self.taskwarrior.tasks.filter(**kwargs)
    else:
      self.tasks = self.taskwarrior.tasks.all()

    if limit is not None:# and False:
      self.tasks = [
        task
        for task in self.tasks
        if (task["end"] == None) or (task["end"] > limit)
      ]

    self.model.clear()
    for task in self.tasks:
      print("{} -- {} ({})".format("✓" if task.pending else "x", task, task["end"]))
      self.model.append(task_tuple(task))

  def __getitem__(self, idx):
    return self.tasks[idx]

  def commit(self, idx):
    task = self[idx]
    task.save()
    self.model[idx] = task_tuple(task)

  def toggle_done(self, idx):
    task = self[idx]
    if is_task_completed(task):
      print("Un-completing task"+task["uuid"])
      task["status"] = "pending"
    else:
      print("Completing task "+task["uuid"])
      task.done()
    self.commit(idx)
