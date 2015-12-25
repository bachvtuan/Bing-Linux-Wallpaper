import json, helper, os, sys
import urllib2
#import requests
import subprocess
import time
import urllib
import ntpath

home_site = "http://bing.com"
weekly_wallpapers_url = home_site + "/HPImageArchive.aspx?format=js&idx=0&n=8&mkt=en-US"


def get_desktop_environment():

  enviroment_desktops = ['gnome','unity','mate','cinnamon','xfce']
  result = subprocess.check_output( 'pgrep -l "%s"' %  ( "|".join(enviroment_desktops)), shell=True)
  #print result
  enviroment_name = 'gnome'
  count_appear = 0

  for enviroment_desktop in enviroment_desktops:
    count_occur = result.count( enviroment_desktop )
    if count_occur > count_appear:
      count_appear = count_occur
      enviroment_name = enviroment_desktop

  return enviroment_name

def set_wallpaper( wallpaper_file_path ):
  #http://stackoverflow.com/questions/1977694/change-desktop-background

  desktop_environment = get_desktop_environment()
  print "desktop_environment is " + desktop_environment

  if desktop_environment in ["gnome", "unity", "cinnamon"]:
    os.system("gsettings set org.gnome.desktop.background picture-uri file://%s" % ( wallpaper_file_path ))
  elif desktop_environment == 'mate':
    os.system("gsettings set org.mate.background picture-filename '%s'" % ( wallpaper_file_path ))
  elif desktop_environment == 'xfce':
    os.system('xfconf-query -c xfce4-desktop -p /backdrop/screen0/monitor0/image-show -s true')
    os.system('xfconf-query -c xfce4-desktop -p /backdrop/screen0/monitor0/image-path -s %s' % (wallpaper_file_path ))

def is_valid( file_name, date_ranges ):
  return  len( date_ranges ) == 0 or file_name[:8] in date_ranges


def random_wallpaper( curr_wallpaper, wallpapers_folder, date_ranges):
  from os import listdir
  from os.path import isfile, join
  from random import randrange

  
  wallpaper_files = [ f for f in listdir(wallpapers_folder) if isfile(join(wallpapers_folder,f)) and is_valid(f, date_ranges) ]

  count_wallpapers = len(wallpaper_files)
  
  if count_wallpapers > 0:
    choose_wallper =wallpaper_files[ randrange( count_wallpapers ) ] 
    

    if choose_wallper == curr_wallpaper and count_wallpapers > 1:
      #Rescursive again because it's using the same wallpaper
      print "duplicated, let do again"
      return random_wallpaper( curr_wallpaper, wallpapers_folder, date_ranges)
    else:
      set_wallpaper( os.path.join( wallpapers_folder, choose_wallper ) )
      helper.notify("Your wallpaper is set from " + choose_wallper)

      return choose_wallper

  else:
    return None


def create_queue_obj( action_name, action_message ):
  return {
    'action': action_name,
    'message': action_message
  }

def get_weekly_wallpapers(wallpapers_folder, q, is_force = False):

  q.put( create_queue_obj('child_pid',os.getpid() ) )

  if not os.path.exists(wallpapers_folder):
    os.makedirs(wallpapers_folder)  

  helper.notify("Getting weekly wallpapers")

  try:

    #r = requests.get( weekly_wallpapers_url )
    r = urllib2.urlopen( weekly_wallpapers_url )
  
    helper.notify("Downloading all newest wallpapers to your computer")

    weekly_wallpapers =  json.load(r)['images']

    print "There are %s wallpapers on the feed" % (len(weekly_wallpapers))

    for wallpaper in weekly_wallpapers:
      
      download_url =  wallpaper['url']

      if home_site not in download_url:
        download_url = home_site + download_url
      
      file_name = wallpaper['startdate'] + "_" + ntpath.basename( wallpaper['url'])

      #temp_path = os.path.join('/tmp', file_name )

      wallpaper_path = os.path.join(wallpapers_folder, file_name )

      #Wallpaper doesn't existing
      if os.path.isfile(wallpaper_path) is False or is_force is True:
        helper.notify("Downloading " + wallpaper['copyright'] )

        #Download to tmp folder first to prevent happend corrupt file while download a wallpaper
        #urllib.urlretrieve ( download_url, temp_path  )
        #ok. move to wallpaper path when done
        #os.rename( temp_path, wallpaper_path )

        urllib.urlretrieve ( download_url, wallpaper_path  )


    helper.notify("All weekly wallpapers are downloaded successfully")

    q.put( create_queue_obj('weekly_complete', len( weekly_wallpapers ) ) )

  except Exception, e:
    print "error"
    print e
    helper.notify("Happended error while downloading weekly wallpapers")
    time.sleep(1)

    q.put( create_queue_obj('weekly_fail', None ) )


  else:
    pass
  finally:
    pass
