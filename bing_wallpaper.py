#! /usr/bin/python

import appindicator
import gtk, helper, service, os, signal

from multiprocessing import Process, Queue,freeze_support
import gobject

import threading 
import time
from os.path import expanduser



#https://wiki.gnome.org/Projects/PyGObject/Threading

# do after 1 second


current_wallpaper = None
all_modes = ['Recent 8 days','All']

# 2 minutes is default

count_milliseconds = 0
is_dowloading_wallpapers = False
watch_milliseconds = 1000

#Init default config
config = {
  'curr_mode': all_modes[0],
  'wallpapers_folder': os.path.join( expanduser('~'), 'Pictures/BingWallpapers' ),
  'timer_milliseconds': 2 * 60 * 1000
}

date_ranges =  helper.get_range_dates(config['curr_mode'])


def random_wallpaper(data= None):
  global config, current_wallpaper;
  current_wallpaper = service.random_wallpaper(current_wallpaper, config['wallpapers_folder'], date_ranges)

def set_timer( minutes ):

  global config,count_milliseconds
  
  temp_milliseconds = minutes * 60 * 1000

  if temp_milliseconds != config['timer_milliseconds']:
    config['timer_milliseconds'] = temp_milliseconds
    helper.notify("The next wallpaper will be changed after %s" % ( helper.string_label( minutes, 'minute' )  ) )
    count_milliseconds = 0
    refresh_menu()
    helper.save_config( config )


def refresh_menu():
  if 'tray_app' in globals():
    tray_app.set_menu( make_menu() )

def set_mode(mode):
  global config, date_ranges

  if mode != config['curr_mode']:
    config['curr_mode'] = mode
    helper.notify("%s wallpapers are choosen to select random to set as your wallpaper" %( config['curr_mode'] ) )
    date_ranges =  helper.get_range_dates(config['curr_mode'])
    refresh_menu()
    helper.save_config( config )

def refresh_weekly_wallpaper(data =None):
  start_child( True )

def kill_child():
  global t;
  t.join()

def seperate_menu_item():
  separator = gtk.SeparatorMenuItem()
  separator.show()
  return separator

def create_image_menu( label, image_path ):
  img = gtk.Image()
  img.set_from_file( helper.icon_path( image_path ) )
  
  menu_item = gtk.ImageMenuItem( label )
  menu_item.set_image(img)
  menu_item.set_always_show_image(True)

  return menu_item
  
  

def make_menu(event_button = None, event_time = None, data=None):
  global config, is_dowloading_wallpapers, all_modes
  menu = gtk.Menu()

  random_item = create_image_menu( "Random", 'Bing_Icon.png' )
  menu.append(random_item)
  random_item.connect_object("activate", random_wallpaper, "random")
  random_item.show()

  menu.append( seperate_menu_item() )

  select_timer_item = create_image_menu( "Select timer", 'clock.png' )
  menu.append(select_timer_item)

  sub_menu = gtk.Menu()

  select_timer_item.set_submenu( sub_menu)
  select_timer_item.show()

  for timer in [1,2,5,10,30,60]:
    
    menu_string =  helper.string_label( timer, 'minute' )

    if timer * 60 * 1000 == config['timer_milliseconds']:
      menu_item = create_image_menu( menu_string, 'circle_active.png' )
    else:
      menu_item = create_image_menu( menu_string, 'circle_deactive.png' )
    
    sub_menu.append(menu_item)

    menu_item.connect_object("activate", set_timer, timer)
    menu_item.show()


  select_wallpaper_item = create_image_menu( "Select wallpapers", 'folder.png' )
  menu.append(select_wallpaper_item)

  sub_menu = gtk.Menu()

  select_wallpaper_item.set_submenu( sub_menu)
  select_wallpaper_item.show()

  for mode in all_modes:

    if mode != config['curr_mode']:
      menu_item = create_image_menu( mode, 'circle_deactive.png' )
    else:
      menu_item = create_image_menu( mode, 'circle_active.png' )

    sub_menu.append(menu_item)

    menu_item.connect_object("activate", set_mode, mode)
    menu_item.show()

  #End select wallpaper model

  menu.append( seperate_menu_item() )

  if is_dowloading_wallpapers is False:

    refresh_item = create_image_menu( "Refresh", 'refresh.png' )
    
    menu.append(refresh_item)

    refresh_item.connect_object("activate", refresh_weekly_wallpaper, "refresh")
    refresh_item.show()

    menu.append( seperate_menu_item() )
  

  close_item = create_image_menu( "Quit", 'shutdown.png' )
  menu.append(close_item)
  
  close_item.connect_object("activate", gtk.main_quit,[])
  close_item.show()
  #End quit item

  return menu

def start_child(is_force=False):
  global t,q, is_dowloading_wallpapers;

  if is_dowloading_wallpapers is False:
    is_dowloading_wallpapers = True
    t = threading.Thread(target=service.get_weekly_wallpapers, args=(config['wallpapers_folder'],q, is_force))
    t.daemon = True
    t.start()

    refresh_menu()

  else:
    print "ignore because there is the child process is working"


def watch():
  global q, child_pid, is_dowloading_wallpapers, config, count_milliseconds;

  count_milliseconds += watch_milliseconds

  if count_milliseconds >= config['timer_milliseconds']:
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
  elif action == "weekly_complete":
    print "Tool downloaded all dailly wallpapers"
    is_dowloading_wallpapers = False
    refresh_menu()
    kill_child( )

  elif action == "weekly_fail":
    print "Happended error white download weekly wallpapers"
    is_dowloading_wallpapers = False
    refresh_menu()
    kill_child( )
  
  return True

if __name__ == '__main__':

  #Register to socket to prevent run many instance at one time
  helper.get_lock('bing_wallpaper')

  freeze_support()

  temp_config = helper.get_config()

  if temp_config is not None:
    print "Found previous config"
    
    if 'curr_mode' in temp_config and temp_config['curr_mode'] in all_modes:
      config['curr_mode'] = temp_config['curr_mode']

    if 'timer_milliseconds' in temp_config :
      config['timer_milliseconds'] = temp_config['timer_milliseconds']

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