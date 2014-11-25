import os
import pynotify
import time
from datetime import date, timedelta, datetime
import socket, sys

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

def get_lock(process_name):
  global lock_socket
  lock_socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
  try:
    lock_socket.bind('\0' + process_name)
  except socket.error:
    print 'Another bing wallpaper is already run'
    sys.exit()

def get_range_dates(mode):
  #https://docs.python.org/2/library/time.html#time.strftime

  if mode == "All":
    return []

  curr_date = datetime.now()
  
  ranges = []

  #Will get recent 8 days
  for i in range(0, 8):
    ranges.append( curr_date.strftime("%Y%m%d") ) 
    curr_date = curr_date - timedelta(1)
    
  return ranges