import socket
import sys
import time

def get_lock(process_name):
  global lock_socket
  lock_socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
  try:
    lock_socket.bind('\0' + process_name)
  except socket.error:
    print 'Another bing wallpaper is already run'
    sys.exit()

get_lock('running_test')
while True:
    time.sleep(3)