#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from IPython import get_ipython
get_ipython().magic('reset -sf')

import numpy as np
import scipy.ndimage
import matplotlib.pyplot as plt
#import scipy
import cv2
#from PIL import image
import skvideo.io
import os
import gc
import math as m

#Change working directory
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)
print("This is the cwd: ",os.getcwd())

def loadDataAsGrey(fileName,allFrames,firstFrame,lastFrame):
    #Function by Johannes (<-- blame this guy if stuff breaks)
    
    #This function loads a RGB video file and converts it to a greyscale image without weighting
    #fileName is the name of the video file in the same folder as the script
    #If allFrames!=0 then the funciton uses all frames the file
    #firstFrame defines the first frame in the desired interval, while lastFrame defines the last
    
    #Load data
    videodata = skvideo.io.vread("{}".format(fileName))
    
    #Define colour weights. [1,1,1] for 1:1 conversion.
    rgb_weights = [1, 1, 1]
    
    #Find image dimensions, and define initial array
    vShape=videodata.shape
    greyarray = np.zeros((vShape[1],vShape[2]))
    
    #Define frames to be converted
    if lastFrame<=firstFrame:
        raise Exception("lastFrame must be higher than firstFrame. Your firstFrame was {} and lastFrame was {}.".format(firstFrame,lastFrame))
    if firstFrame<=0 or lastFrame<=0:
        raise Exception("Your defined frames must be higher than 0. Your firstFrame was {} and lastFrame was {}.".format(firstFrame,lastFrame))
    if firstFrame>vShape[0] or lastFrame>vShape[0]:
        raise Exception("Your defined frames must not be higher than {}. Your firstFrame was {} and lastFrame was {}.".format((vShape[0]),firstFrame,lastFrame))
    if allFrames==0:
        imrange=range(firstFrame-1,lastFrame)
    else:
        imrange=range(vShape[0])
    
    for i in imrange:     
        #Load one frame, then convert with weights
        oneimage=videodata[i,:,:]
        greyscale_image = np.dot(oneimage[...,:3],rgb_weights)/(255*9)
        
        #Visualise if needed
        #plt.imshow(videodata[i,:,:])
        #plt.imshow(greyscale_image,cmap='gray')
        
        #Add greyscale frame to array
        greyarray=np.dstack((greyarray,greyscale_image))    
    
    greyarray=np.delete(greyarray,0,axis=2)
    gc.collect()
    #print("Final shape: ",greyarray.shape)
    return greyarray


def removeaverage(array):
    # Removes the average background of the image
    
    #Calculates average 2D array of 3D array
    average=np.mean(array,axis=2)

    # Removes the average of all the layers and stacks the new layers on top of each other
    result = []
    for i in range(array.shape[2]):
        new = array[:,:,i]-average
        result.append(new)
    result = np.array(np.dstack(result))
    
    # Removes values under 0
    result[result<0]=0

    return result


# Gaussian blurs the image
def gaussianfilter(array, sigma):
    
    blurred = scipy.ndimage.gaussian_filter(array, sigma)
    
    return blurred

import skimage.color
import skimage.filters
import skimage.io
import skimage.viewer

#Puts threshhold on the image 
def threshhold(array):
    # Function by Johanna Neumann Sørensen
    
    #Finds the adaptive threshhold
    t=skimage.filters.threshold_otsu(array)
    
    #Binary threshhold
    mask = array > t
    
    #Applies the threshhold
    sel = np.zeros_like(array)
    sel[mask] = array[mask]
    
    return sel

# import required for slideShow function
from matplotlib.widgets import Slider

def slideShow(Movie_stack):
    # Original code by Murat Nulati Yesibolati and Anders Brostrøm
    
    # Modified by Johannes Koblitz Aaen
    
    # This function takes in a 3D array, and plots it as a 'slideshow', where it's possible to update the shown frame
    # The input called Movie_stack is the required 3D array
    # Beware that the slideshow may freeze
    
    # The Slider_val used later is defined as a global variable, to prevent freezing
    global Slider_val
    
    #Axes and stuff is defined, together with the slider and the shown image
    fig1, ax = plt.subplots()
    plt.subplots_adjust(bottom=0.20)
    test = ax.imshow(Movie_stack[:,:,0],cmap="gray")
    ax_slider = plt.axes([0.1, 0.1, 0.80, 0.04], facecolor="red")
    
    #Defines slider value
    Slider_val = Slider(ax_slider, 'Frame', 1, Movie_stack.shape[2], valinit=10, valstep=1)
    
    def update(val):
        #Updates the shown frame, accordingly
        frame_val = int(Slider_val.val)-1
        test.set_data(Movie_stack[:,:,frame_val])
        plt.draw()
        
        #Uncomment print statement to print current frame if desired
        #print(frame_val)
    
    #If the slider value changes, call function above
    Slider_val.on_changed(update)

greyedVid=loadDataAsGrey("0DC- AC 50 Hz 0.7V WE3 CERE24.avi",0,101,200)
noAvg=removeaverage(greyedVid)
gaussBlurr=gaussianfilter(noAvg,3)

#print(removeaverage(loadDataAsGrey("0DC- AC 50 Hz 0.7V WE3 CERE24.avi",0,1,20)).shape)

#plt.imshow(np.asarray(removeaverage(loadDataAsGrey("0DC- AC 50 Hz 0.7V WE3 CERE24.avi",0,1,20))[:,:,0]),cmap='gray')
#plt.imshow(np.asarray(loadDataAsGrey("0DC- AC 50 Hz 0.7V WE3 CERE24.avi",0,1,20))[:,:,0])
#print(loadDataAsGrey("0DC- AC 50 Hz 0.7V WE3 CERE24.avi",0,1,20)[0,:,:]-removeaverage(loadDataAsGrey("0DC- AC 50 Hz 0.7V WE3 CERE24.avi",0,1,20))[0,:,:])

#print(loadDataAsGrey("0DC- AC 50 Hz 0.7V WE3 CERE24.avi",0,1,20)[0,:,:])
#print(removeaverage(loadDataAsGrey("0DC- AC 50 Hz 0.7V WE3 CERE24.avi",0,1,20))[0,:,:])

import math as m

def rotate(video,x1,y1,x2,y2,orientation):
    # Function by Johanna Neumann Sørensen
    # This function can rotate an video so that a tilted line in the video becomes vertical or horizontal
    # The input requires two sets of coordinates that the tilted line passes through
    
    # Slope of the tilted line
    a = (y1-y2)/(x2-x1)
    # Rotation angles depending on the desired orientation
    angleh = -m.degrees(m.atan(a))
    anglev = angleh - 90
    
    # While-loop to aske user for the correct orientation input
    while True:
        try:
            orientation = str(input("Please choose either a vertical or horizontal orientation:"))
        except ValueError:
            print("Sorry, I didn't understand that.")
            continue
        if orientation != 'horizontal' and orientation != 'vertical':
            print("Sorry, orientation must either be horizontal or vertical.")
        else:
            break
    
    # Rotates the video
    if orientation == 'horizontal':
        rotatedvideo = scipy.ndimage.rotate(video,angleh)
        return rotatedvideo
    if orientation == 'vertical':
        rotatedvideo = scipy.ndimage.rotate(video,anglev)
        return rotatedvideo
    
def templateMatch(imageStack,template,threshold,frame):
    
    # An empty list, in which the streak images are stored
    streakImages = []
    
    # Frame is converted to a scale starting from 0, instead of 1
    frame = frame-1
    
    # workingCoords is apparently y, then x. Watch out for this.
    workingCoords=cv2.matchTemplate(imageStack[:,:,frame].astype(np.float32),template.astype(np.float32),cv2.TM_CCOEFF_NORMED)
    workingCoords=np.where(workingCoords >= threshold)
    
    # For some reason there's a displacement of the coordinates by ~10-20, which *could* be because of the template
    # Below is a temporary™ fix, which also fixes the coordinates
    templateW = int(round(template.shape[0]/2))
    templateH = int(round(template.shape[1]/2))
    workingCoords=np.array((workingCoords[1]+templateH,workingCoords[0]+templateW))
    #workingCoords=np.array((workingCoords[1]+12,workingCoords[0]+16))
    
    # Create binary image of identified points
    binaryPoints = np.zeros_like(imageStack[:,:,frame])
    binaryPoints[workingCoords[1],workingCoords[0]]=255
    #plt.imshow(a)
    
    # Use the binary contours to find center coordinates
    contours = cv2.findContours(binaryPoints.astype(np.uint8), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_TC89_L1)[0]
    xCent = np.array([])
    yCent = np.array([])
    for c in contours:
        x,y,w,h = cv2.boundingRect(c)
        
        # If the height-to-width ratio if high enough, add the center value
        if h/w >= 1.2:
            centX = x + w/2
            centY = y + h/2
            xCent = np.append(xCent,centX)
            yCent = np.append(yCent,centY)
    
    # Crop images, and add to list streakImages
    xMov = int(round((template.shape[1]+8)/2))
    yMov = int(round((template.shape[0]+8)/2))
    
    for i in range(len(xCent)):
        xCenter = int(round(xCent[i]))
        yCenter = int(round(yCent[i]))
        if imageStack[yCenter-yMov:yCenter+yMov,xCenter-xMov:xCenter+xMov,frame].shape[0] > 0:
            streakImages.append(imageStack[yCenter-yMov:yCenter+yMov,xCenter-xMov:xCenter+xMov,frame])

    
    # Shows the macthes' coordinates with red dots, and center with blue dots
    # plt.figure()
    # plt.imshow(imageStack[:,:,frame-1],cmap='Blues')
    # plt.scatter(x=workingCoords[0], y=workingCoords[1], c='r', s=0.2)
    # plt.scatter(x=xCent, y=yCent, c='b', s=0.4)
    # plt.show()
    
    return streakImages

greyedVid=loadDataAsGrey("0DC- AC 50 Hz 0.7V WE3 CERE24.avi",0,101,200)
greyedVid=rotate(greyedVid,0,86,341,78,"h")
noAvg=removeaverage(greyedVid)
gaussBlurr=gaussianfilter(noAvg,1.5)

gaussBlurr2=gaussianfilter(greyedVid,1.5)
noAvg2=removeaverage(gaussBlurr2)


exp = 3
templateA=noAvg2[201-exp:243+exp,245-exp:262+exp,91]
templateG=gaussBlurr2[201-exp:243+exp,245-exp:262+exp,91]

gaussBlurr2=gaussianfilter(greyedVid[104:319,143:323,:],1.5)
noAvg2=removeaverage(gaussBlurr2)



