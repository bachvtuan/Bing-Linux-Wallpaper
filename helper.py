import os
import pynotify
import time

g_notice = None

def icon_path(file_name):
  if os.name != "nt":
    return os.path.dirname(__file__) + '/icons/' + file_name
  else:
    return 'icons/' + file_name


def notify(message, title = "Bing Wallpaper"):
  global g_notice

  if g_notice is None:
    pynotify.init("Test")
    g_notice = pynotify.Notification(title, message)
  else:
    g_notice.update( title, message)

  g_notice.show()

def string_label( number, string, suffix= 's' ):
  if number > 1:
    return "%s %s%s" %( number, string, suffix )
  else:
    return "%s %s" %( number, string)