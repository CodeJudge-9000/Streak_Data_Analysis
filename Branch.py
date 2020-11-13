#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov  6 16:27:28 2020

@author: Johanna
"""


# -*- coding: utf-8 -*-

from IPython import get_ipython
get_ipython().magic('reset -sf')

import numpy as np
import scipy.ndimage
import matplotlib.pyplot as plt
#import scipy
#import cv2
#from PIL import image
import skvideo.io
import os
import gc

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

import cv2 as cv
y=removeaverage(loadDataAsGrey("0DC- AC 50 Hz 0.7V WE3 CERE24.avi",0,1,80))

x = gaussianfilter(y,5)

#print(np.asarray(cv.threshold(y,0,1,cv.THRESH_BINARY)))

#print(cv.threshold(y,0,1,cv.THRESH_BINARY)[1])

#plt.imshow(np.asarray(gaussianfilter(y,3))[:,:,0],cmap='gray')

#print(np.asarray(cv.threshold(y,0,1,cv.THRESH_BINARY)))

#print(x.shape)



#plt.imshow(np.asarray(cv.threshold(y,0,1.5,cv.THRESH_BINARY)[1])[:,:,0],cmap='gray')



#With threshhold and gaussianfilter
#plt.imshow(np.asarray(cv.threshold(gaussianfilter(y,3),127, 255,cv.THRESH_BINARY)[1])[:,:,0],cmap='gray')

#Without gaussionfilter
#plt.imshow(np.asarray(cv.threshold(y,0, 1,cv.THRESH_BINARY)[1])[:,:,0])

import skimage.color
import skimage.filters
import skimage.io
import skimage.viewer

#Puts threshhold on the image 
def threshhold(array):
    
    #Finds the adaptive threshhold
    t=skimage.filters.threshold_otsu(x)
    
    #Binary threshhold
    mask = x > t
    
    #Applies the threshhold
    sel = np.zeros_like(x)
    sel[mask] = x[mask]
    
    return sel

#plt.imshow(np.asarray(sel)[:,:,0],cmap='gray')


#skvideo.io.vwrite("Video1.mp4",y)
#skvideo.io.vwrite("Video2.mp4",gaussianfilter(y,3))


#plt.imshow(np.asarray(loadDataAsGrey("0DC- AC 50 Hz 0.7V WE3 CERE24.avi",0,1,20))[:,:,0])

#print(loadDataAsGrey("0DC- AC 50 Hz 0.7V WE3 CERE24.avi",0,1,20)[0,:,:])
#print(removeaverage(loadDataAsGrey("0DC- AC 50 Hz 0.7V WE3 CERE24.avi",0,1,20))[0,:,:])
