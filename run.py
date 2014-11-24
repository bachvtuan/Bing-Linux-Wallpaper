#! /usr/bin/python

import appindicator
import gtk, helper, service, os, signal

from multiprocessing import Process, Queue,freeze_support
import gobject

import threading 
import time

#https://wiki.gnome.org/Projects/PyGObject/Threading

# do after 1 second
watch_milliseconds = 1000
current_wallpaper = None
all_modes = ['Recent 8 days','All']
curr_mode = all_modes[0]

date_ranges =  service.get_range_dates(curr_mode)

# 1 minute is default
timer_milliseconds = 60 * 1000
count_milliseconds = 0
is_dowloading_wallpapers = False
wallpapers_folder = "~/Pictures/BingWallpapers"

def random_wallpaper(data= None):
  global wallpapers_folder, current_wallpaper;
  current_wallpaper = service.random_wallpaper(current_wallpaper, wallpapers_folder, date_ranges)

def set_timer( minutes ):

  global timer_milliseconds
  
  temp_milliseconds = minutes * 60 * 1000

  if temp_milliseconds != timer_milliseconds:
    timer_milliseconds = timer_milliseconds
    helper.notify("The next wallpaper will be changed after %s" % ( helper.string_label( minutes, 'minute' )  ) )
    refresh_menu()

def refresh_menu():
  if 'tray_app' in globals():
    tray_app.set_menu( make_menu() )

def set_mode(mode):
  global curr_mode, date_ranges

  if mode != curr_mode:
    curr_mode = mode
    helper.notify("%s wallpapers are choosen to select random to set as your wallpaper" %( curr_mode ) )
    date_ranges =  service.get_range_dates(curr_mode)
    refresh_menu()

def refresh_daily_wallpaper(data =None):
  start_child( True )
  return None

def kill_child():
  global t;
  t.join()

def make_menu(event_button = None, event_time = None, data=None):
  global timer_milliseconds, curr_mode, is_dowloading_wallpapers, all_modes
  menu = gtk.Menu()
  
  random_item = gtk.MenuItem("Random")
  menu.append(random_item)
  random_item.connect_object("activate", random_wallpaper, "random")
  random_item.show()

  separator = gtk.SeparatorMenuItem()
  menu.append(separator)
  separator.show()

  select_timer_item = gtk.MenuItem("Select timer")
  menu.append(select_timer_item)

  sub_menu = gtk.Menu()

  select_timer_item.set_submenu( sub_menu)
  select_timer_item.show()

  for timer in [1,2,5,10,30,60]:
    
    menu_string =  helper.string_label( timer, 'minute' )

    if timer * 60 * 1000 == timer_milliseconds:
      menu_string += " [selected]"

    menu_item = gtk.MenuItem( menu_string )
    sub_menu.append(menu_item)

    menu_item.connect_object("activate", set_timer, timer)
    menu_item.show()


  select_wallpaper_item = gtk.MenuItem("Select wallpapers")
  menu.append(select_wallpaper_item)

  sub_menu = gtk.Menu()

  select_wallpaper_item.set_submenu( sub_menu)
  select_wallpaper_item.show()

  for mode in all_modes:
    menu_string =  mode  if mode != curr_mode else mode + " [ selected ]" 

    menu_item = gtk.MenuItem( menu_string )
    sub_menu.append(menu_item)

    menu_item.connect_object("activate", set_mode, mode)
    menu_item.show()

  #End select wallpaper model

  if is_dowloading_wallpapers is False:
    refresh_item = gtk.MenuItem("Refresh")
    menu.append(refresh_item)
    refresh_item.connect_object("activate", refresh_daily_wallpaper, "refresh")
    refresh_item.show()


  close_item = gtk.MenuItem("Quit")
  menu.append(close_item)
  
  close_item.connect_object("activate", gtk.main_quit,[])
  close_item.show()
  #End quit item

  return menu

def start_child(is_force=False):
  global t,q, is_dowloading_wallpapers;

  if is_dowloading_wallpapers is False:
    is_dowloading_wallpapers = True
    t = threading.Thread(target=service.get_daily_wallpapers, args=(wallpapers_folder,q, is_force))
    t.daemon = True
    t.start()

    refresh_menu()

  else:
    print "ignore because there is the child process is working"


def watch():
  global q, child_pid, is_dowloading_wallpapers, timer_milliseconds, count_milliseconds;

  count_milliseconds += watch_milliseconds


  if count_milliseconds >= timer_milliseconds:
    #Set random wallpaper
    print "Set random wallpaper"
    count_milliseconds = 0
    random_wallpaper()


  if q.empty():
    return True
  

  message = q.get()

  action = message['action']

  if  action == 'child_pid':
    child_pid = message['message']
    print "Child pid is " + str(child_pid)
  elif action == "daily_complete":
    print "Tool downloaded all dailly wallpapers"
    is_dowloading_wallpapers = False
    refresh_menu()
    kill_child( )
  
  return True

if __name__ == '__main__':

  freeze_support()
  

  q = Queue()
  start_child()

  gobject.timeout_add(watch_milliseconds, watch)
  
  gobject.threads_init()

  tray_app = appindicator.Indicator('bing_indicator', helper.icon_path('Bing_Icon.png') , appindicator.CATEGORY_APPLICATION_STATUS)
  tray_app.set_status( appindicator.STATUS_ACTIVE )
  tray_app.set_menu( make_menu() )

  gtk.gdk.threads_init()
  gtk.gdk.threads_enter()
  gtk.main()

  gtk.gdk.threads_leave()