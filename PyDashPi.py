#!/usr/bin/env python2.7
########################
####### PyDashPi #######
########################
##### By Eric King #####
##########################################################################
####                                                                  ####
#### For use on a raspberry pi, the program will interrupt            ####
#### when a gpio pin changes state, such as when a button is pressed  ####
#### for example, and save roughly the last 10 minutes of video.      ####
####                                                                  ####
##########################################################################

### Imports
import numpy as np
from datetime import datetime, date, time
import time
import os
from collections import deque
from gpiozero import Button, RGBLED
from picamera import PiCamera, Color
import shutil
    

def recbuttonpress():
    global save
    save = True
    led.blink(on_color=(0,0,1),off_color=(1,0,0),n=3)
def stopbuttonpress():
    global shutdown
    print "Closing..."
    shutdown = True
    

if __name__ == '__main__':
    ### Video
    ## Video properties
    vid_width = 1280
    vid_height = 720
    vid_length = 300 #In seconds
    ## Initializing the PiCamera
    camera = PiCamera()
    camera.resolution = (vid_width, vid_height)
    camera.framerate = 30
    
    time.sleep(0.1)
    
    user = os.getenv('USER')
    
    video_dir = '/media/DashCamRecordings/'  # Local temporary storage
    video_store = '/media/pi/DASHCAMSTOR/'   # Long term storage on the USB thumb drive.
    
    if user is not None:
        video_dir = '/home/'+user+'/Videos/'
        video_store = video_dir
 
    if not os.path.exists(video_dir):
        os.makedirs(video_dir)
        
    save = False
    shutdown = False
    
    
    ### Styling
    ## Font
    camera.annotate_background = Color('black')
    camera.annotate_text_size = 16
    camera.vflip = True
    start = time.time()
    #camera.start_preview()
    filename = video_dir+'dashcam_'+datetime.now().strftime('%Y-%m-%d_%H.%M.%S')+'.h264'
    videos = deque([filename])
    camera.start_recording(filename,format='h264',resize=(vid_width,vid_height))
    rec_button = Button(4)
    stop_button = Button(25)
    rec_button.when_pressed = recbuttonpress
    stop_button.when_pressed = stopbuttonpress
    led = RGBLED(27,8,17)

    while not camera.closed:
        led.color = (1,0,1)
        if not shutdown:
            end = time.time() 
            seconds = end - start
            camera.annotate_text = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
           
            if  save == True:
                save = False
                print "Saving video"
                filename = video_dir+'dashcam_'+datetime.now().strftime('%Y-%m-%d_%H.%M.%S')+'.h264'
                camera.split_recording(filename)
                dst = video_store+datetime.now().strftime('%Y')+'/'+datetime.now().strftime('%b')+'/'+datetime.now().strftime('%d')+'/'
                if not os.path.exists(dst):
                    os.makedirs(dst)
                for i in range(len(videos)):
                    src = videos.popleft()
                    shutil.copy2(src,dst)
                    os.remove(src)
                videos.clear()
                videos.append(filename)
                start = time.time()
                
            
            if seconds >= vid_length:
                filename = video_dir+'dashcam_'+datetime.now().strftime('%Y-%m-%d_%H.%M.%S')+'.h264'
                if len(videos) >= 2:
                    os.remove(videos.popleft())
                videos.append(filename)
                camera.split_recording(filename)
                start = time.time()
                
        else:
            camera.close()
            break
    for i in range(len(videos)):
        os.remove(videos.popleft())
