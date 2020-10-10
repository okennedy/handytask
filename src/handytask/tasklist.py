from gi.repository import Gtk, GObject
from datetime import datetime, timedelta
from tzlocal import get_localzone
from tasklib import Task

UUID_COLUMN             = 0
TITLE_COLUMN            = 1
ELLIPSIZED_TITLE_COLUMN = 2
STATUS_COLUMN           = 3
DUE_COLUMN              = 4
COMPLETED_COLUMN        = 5
PENDING_COLUMN          = 6
ACTIVE_COLUMN           = 7
TAGS_COLUMN             = 8
URGENCY_COLUMN          = 9
TASK_COLUMN             = 10

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
    task['uuid'],                                                       # 0
    str(task),                                                          # 1
    ellipsize(str(task)),                                               # 2
    task['status'],                                                     # 3
    stringify_date(task['due']),                                        # 4
    is_task_completed(task),                                            # 5
    task.pending,                                                       # 6
    task.active,                                                        # 7
    task["tags"],                                                       # 8
    str(int(float(task["urgency"])*100)/100.0) if task.pending else "", # 9
    task                                                                # 10
  ]

class TaskList:
  def __init__(self, **kwargs):
    self.taskwarrior = kwargs["taskwarrior"]
    self.model = Gtk.ListStore(
      str, 
      str, 
      str, 
      str, 
      str, 
      bool, 
      bool, 
      bool, 
      GObject.TYPE_PYOBJECT, 
      str,
      GObject.TYPE_PYOBJECT, 
    )
    self.refresh( )


  def refresh(self, 
      limit = default_limit(), 
      include_recurring = False, 
      sync = False,
      **kwargs
    ):
    """Refresh the model contents. 
       Arguments are passed directly to taskwarrior.tasks.filter
    """
    if sync:
      self.sync()

    if kwargs:
      self.tasks = self.taskwarrior.tasks.filter(**kwargs)
    else:
      self.tasks = self.taskwarrior.tasks.all()

    if not include_recurring: 
      self.tasks = [
        task
        for task in self.tasks
        if task["status"] != "recurring"
      ]

    if limit is not None:# and False:
      self.tasks = [
        task
        for task in self.tasks
        if ((task["end"] == None) or (task["end"] > limit))
      ]

    self.tasks.sort(key = lambda task: -task["urgency"] if task["urgency"] is not None and task["status"] == "pending" else 0)

    self.model.clear()
    for task in self.tasks:
      # print("{} -- {} ({}; {})".format("✓" if task.pending else "x", task, task["end"] or task["urgency"], ",".join(task["tags"])))
      # print(task["annotations"])
      self.model.append(task_tuple(task))

  def __getitem__(self, idx):
    return self.tasks[idx]

  def commit(self, idx):
    task = self[idx]
    task.save()
    updated = task_tuple(task)
    self.model[idx] = updated
    return updated

  def add(self, task):
    self.tasks.append(task)
    task.save()
    created = task_tuple(task)
    self.model.append(created)
    assert(len(self.model) == len(self.tasks))
    return created

  def toggle_done(self, idx):
    task = self[idx]
    if is_task_completed(task):
      print("Un-completing task"+task["uuid"])
      task["status"] = "pending"
    else:
      print("Completing task "+task["uuid"])
      task.done()
    self.commit(idx)

  def index_of_task(self, task_row):
    uuid = task_row[UUID_COLUMN]
    for idx, row in enumerate(self.model):
      if row[UUID_COLUMN] == uuid:
        return idx
    return None

  def update( self,
              idx, 
              description = None,
              completed = None,
              due = None
            ):
    if idx is None:
      task = Task(self.taskwarrior)
    else:
      task = self[idx]
    if description is not None:
      task["description"] = description
    if completed is not None:
      if is_task_completed(task):
        if not completed:
          task["status"] = "pending"
      else:
        if completed:
          task.done()
    if due is not None:
      task["due"] = due
    if idx is None:
      return self.add(task)
    else:
      return self.commit(idx)

  def sync(self):
    self.taskwarrior.sync()