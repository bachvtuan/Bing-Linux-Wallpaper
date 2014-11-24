import requests, json, helper, os
import time
from datetime import date, timedelta, datetime
import urllib
import ntpath

home_site = "http://bing.com"
daily_wallpapers_url = home_site + "/HPImageArchive.aspx?format=js&idx=0&n=8&mkt=en-US"

def set_wallpaper( wallpaper_file_path ):
  os.system("gsettings set org.gnome.desktop.background picture-uri file://%s" % ( wallpaper_file_path ))

def is_valid( file_name, date_ranges ):

  if len( date_ranges ) == 0:
    return True

  return  file_name[:8] in date_ranges
      
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

def random_wallpaper( curr_wallpaper, wallpapers_folder, date_ranges):
  from os import listdir
  from os.path import isfile, join
  from random import randrange

  
  wallpaper_files = [ f for f in listdir(wallpapers_folder) if isfile(join(wallpapers_folder,f)) and is_valid(f, date_ranges) ]

  print wallpaper_files
  count_wallpapers = len(wallpaper_files)
  
  if count_wallpapers > 0:
    choose_wallper =wallpaper_files[ randrange( count_wallpapers ) ] 
    print choose_wallper

    if choose_wallper == curr_wallpaper and count_wallpapers > 1:
      #Rescursive again because it's using the same wallpaper
      print "duplicated, let do again"
      return random_wallpaper( curr_wallpaper, wallpapers_folder, date_ranges)
    else:
      set_wallpaper( os.path.join( wallpapers_folder, choose_wallper ) )
      helper.notify("Wallpaper is set from " + choose_wallper)

      return choose_wallper

  else:
    return None


def create_queue_obj( action_name, action_message ):
  return {
    'action': action_name,
    'message': action_message
  }

def get_daily_wallpapers(wallpapers_folder, q, is_force = False):

  q.put( create_queue_obj('child_pid',os.getpid() ) )

  print wallpapers_folder
  if not os.path.exists(wallpapers_folder):
    os.makedirs(wallpapers_folder)  

  helper.notify("Getting daily wallpapers")
  r = requests.get( daily_wallpapers_url )
  
  
  helper.notify("Downloading all daily wallpapers to your computer")

  daily_wallpapers =  r.json()['images']

  print len(daily_wallpapers)

  for wallpaper in daily_wallpapers:
    
    download_url = home_site + wallpaper['url']
    

    wallpaper_path = os.path.join(wallpapers_folder, wallpaper['startdate'] + "_" + ntpath.basename( wallpaper['url'] ))

    #Wallpaper doesn't existing
    if os.path.isfile(wallpaper_path) is False or is_force is True:
      helper.notify("Downloading " + wallpaper['copyright'] )
      urllib.urlretrieve ( download_url, wallpaper_path  )

  helper.notify("All daily wallpapers are downloaded successfully")

  q.put( create_queue_obj('daily_complete', len( daily_wallpapers ) ) )

  
  
