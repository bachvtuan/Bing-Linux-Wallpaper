Bing-Linux-Wallpaper
====================

This tool downloads newest wallpapers from Bing to computer and set as wallpaper on your Linux computer.

I tested on my Ubuntu1 4.04 which is using Unity as an enviroment

# Features

- GUI interface .
- Choose random wallpapers from the folder store all wallpapers are downloaded from Bing
- Notify important event on the app.
- Select timer to change your wallpaper.
- Select mode to select wallpapers, There are 2 modes, 1 is select the wallpaper is uploaded recent 8 days or all wallpapers.
- You can use your pictures by copy them to ~/Pictures/BingWallpapers and select mode is "All".
- Remember your config to use for next time open the app.
- Refresh wallpapers if needed.

# Install 

```
sudo bash install.sh
```

# Usage
And from terminal you can call app by command

```
bing_wallpaper
```

Or you can run by alt + F2 and type 
```
bing_wallpaper

```
then press enter

The app will appear on taskbar, You can do some options via it's context menu.

# Run app when startup
Please follow this [link](http://www.howtogeek.com/189995/how-to-manage-startup-applications-in-ubuntu-14.04/)
In the command text box, you type the value

```
bing_wallpaper
```


# Remove

```
sudo rm /usr/local/bin/bing_wallpaper
```