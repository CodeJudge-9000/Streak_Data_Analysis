# -*- coding: utf-8 -*-

from IPython import get_ipython
get_ipython().magic('reset -sf')

import numpy as np
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
        plt.imshow(greyscale_image,cmap='gray')
        
        #Add greyscale frame to array
        greyarray=np.dstack((greyarray,greyscale_image))    
    
    greyarray=np.delete(greyarray,0,axis=2)
    gc.collect()
    #print("Final shape: ",greyarray.shape)
    return greyarray

print(loadDataAsGrey("0DC_-_AC_50_Hz_0.7V_WE3_CERE24.avi",0,1,20).shape)


