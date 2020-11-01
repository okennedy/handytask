from gi.repository import Gtk, Handy

from tasklib import TaskWarrior
from datetime import datetime
from .task import TaskList
from .list import TaskListView
from .detail import TaskDetailView


class HandyTaskAppWindow(Gtk.ApplicationWindow):

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

    self.set_icon_from_file("images/taskwarrior.png")
    self.set_wmclass("HandyTask", "HandyTask")

    # This will be in the windows group and have the "win" prefix
    # max_action = Gio.SimpleAction.new_stateful("maximize", None,
    #                                    GLib.Variant.new_boolean(False))
    # max_action.connect("change-state", self.on_maximize_toggle)
    # self.add_action(max_action)

    self.header = Handy.HeaderBar()
    self.header.set_title("HandyTask")
    self.back_button = Gtk.Button.new_from_icon_name("go-previous", Gtk.IconSize.BUTTON)
    # self.back_button.set_label("<")
    # self.back_button.set_image(
    #   Gtk.Image.new_from_icon_name("go-previous", Gtk.IconSize.BUTTON)
    # )
    self.back_button.connect("clicked", self.on_detail_cancel_clicked)
    self.header.pack_start(self.back_button)
    # self.back_button.show()

    # self.refresh_button = Gtk.ToolButton()
    # self.refresh_button.set_icon_name("view-refresh")
    self.refresh_button = Gtk.Button.new_from_icon_name("view-refresh", Gtk.IconSize.BUTTON)
    self.refresh_button.show()
    self.refresh_button.connect("clicked", self.on_refresh_clicked)
    self.header.pack_end(self.refresh_button)

    self.new_button = Gtk.Button.new_from_icon_name("appointment-new", Gtk.IconSize.BUTTON)
    self.new_button.connect("clicked", self.on_new_clicked)
    self.new_button.show()
    self.header.pack_end(self.new_button)

    self.set_titlebar(self.header)
    self.header.show()
    self.set_show_menubar(False)


    # Keep it in sync with the actual state
    # self.connect("notify::is-maximized",
    #                     lambda obj, pspec: max_action.set_state(
    #                                        GLib.Variant.new_boolean(obj.props.is_maximized)))

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
      on_select = self.on_select_task
    )
    self.multi_view.add(self.task_view)
    self.task_view.show()

    # Allocate the task detail sidebar
    self.detail_view = TaskDetailView(
      on_save = self.on_detail_save_clicked,
      on_cancel = self.on_detail_cancel_clicked,
      on_update_date = self.on_update_date
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
    self.back_button.hide()

  def show_task_view(self, task):
    # print("Showing task: {}".format(task))
    if task is None:
      self.detail_view.clear_task()
    else:
      self.detail_view.set_task(task)
    self.multi_view.set_visible_child(self.detail_view)
    self.back_button.show()

  def on_new_clicked(self, button):
    self.task_view.unselect()
    self.show_task_view(None)

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

  def on_update_date(self, due_date_calendar):
    date = due_date_calendar.get_date()
    print(date)
    date = datetime(
      year = date.year,
      month = date.month+1,
      day = date.day,
      hour = 17
    )
    task = self.detail_view.get_task()
    if task is not None:
      if(task['due'] != date):
        task['due'] = date
        task.save()
        self.refresh()
        print(date)
      else:
        print("SAME")

  def refresh(self):
    self.tasks.refresh()
    # self.task_view.refresh(self.tasks)

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
    self.tasks.sync()

  def on_refresh_clicked(self, button):
    self.tasks.refresh(sync = True)
