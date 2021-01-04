#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# BEWARE ALL YE WHO ENTER
# This program stores all data in ram, meaning that if you're analysing a lot of data, you need a lot of ram

# Resets all variables
from IPython import get_ipython
get_ipython().magic('reset -sf')

# Import libraries
import numpy as np
import scipy.ndimage
import matplotlib.pyplot as plt
import cv2
import skimage.color
import skimage.filters
import skimage.viewer
import skimage.io
import skvideo.io
import os
import gc
import math as m
import statistics as stat
import sys
from itertools import compress


#Change working directory
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)
print("This is the cwd: ",os.getcwd())

def loadDataAsGrey(fileName,allFrames,firstFrame,lastFrame):
    # Function by Johannes Koblitz Aaen
    
    # This function loads a RGB video file and converts it to a greyscale image without weighting
    # fileName is the name of the video file in the same folder as the script
    # If allFrames!=False then the funciton uses all frames from the file
    # firstFrame defines the first frame in the desired interval, while lastFrame defines the last
    
    # Load data
    videodata = skvideo.io.vread("{}".format(fileName))
    
    # Define colour weights. [1,1,1] for 1:1 conversion.
    rgb_weights = [1, 1, 1]
    
    # Find image dimensions, and define initial array (this could be optimized to one line. See later funcitons.)
    vShape=videodata.shape
    greyarray = np.zeros((vShape[1],vShape[2]))
    
    # Define frames to be converted
    if lastFrame<=firstFrame:
        raise Exception("lastFrame must be higher than firstFrame. Your firstFrame was {} and lastFrame was {}.".format(firstFrame,lastFrame))
    if firstFrame<=0 or lastFrame<=0:
        raise Exception("Your defined frames must be higher than 0. Your firstFrame was {} and lastFrame was {}.".format(firstFrame,lastFrame))
    if firstFrame>vShape[0] or lastFrame>vShape[0]:
        raise Exception("Your defined frames must not be higher than {}. Your firstFrame was {} and lastFrame was {}.".format((vShape[0]),firstFrame,lastFrame))
    if allFrames==False:
        imrange=range(firstFrame-1,lastFrame)
    else:
        imrange=range(vShape[0])
    
    for i in imrange:     
        # Load one frame, then convert with weights
        oneimage=videodata[i,:,:]
        greyscale_image = np.dot(oneimage[...,:3],rgb_weights)/(9)
        
        # Add greyscale frame to array
        greyarray=np.dstack((greyarray,greyscale_image))    
    
    # Remove the first frame, then clear unused memory
    greyarray=np.delete(greyarray,0,axis=2)
    gc.collect()
    return greyarray

def removeaverage(array):
    # Function by Johanna Neumann Sørensen & Johannes Koblitz Aaen
    
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


def gaussianfilter(array, sigma):
    # Gaussian blurs the image according to input sigma value
    blurred = scipy.ndimage.gaussian_filter(array, sigma)
    
    return blurred


def threshold(array):
    # Function by Johanna Neumann Sørensen
    # Puts adaptive threshold on the image 
    
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

def slideShow(Movie_stack,mapput):
    # Original code by Murat Nulati Yesibolati and Anders Brostrøm
    
    # Modified by Johannes Koblitz Aaen
    # note: mapput should be changed to an optional argument
    
    # This function takes in a 3D array (must be numpy), and plots it as a 'slideshow', where it's possible to update the shown frame
    # The input called Movie_stack is the required 3D array, mapput is a string corresponding to a cmap
    # Beware that the slideshow may freeze
    
    # Remember to change backline to 'Automatic' under Tools->Preferences->IPython Console->Graphics
    
    # The Slider_val used later is defined as a global variable, to prevent freezing
    global Slider_val

    # Axes and stuff is defined, together with the slider and the shown image
    fig1, ax = plt.subplots()
    plt.subplots_adjust(bottom=0.20)
    try:
        test = ax.imshow(Movie_stack[:,:,0],cmap=mapput)
    except:
        test = ax.imshow(Movie_stack[:,:,0],cmap="Blues")
    ax_slider = plt.axes([0.1, 0.1, 0.80, 0.04], facecolor="red")
    
    # Defines slider value
    Slider_val = Slider(ax_slider, 'Frame', 1, Movie_stack.shape[2], valinit=10, valstep=1)
    
    def update(val):
        # Updates the shown frame, accordingly
        frame_val = int(Slider_val.val)-1
        test.set_data(Movie_stack[:,:,frame_val])
        plt.draw()
        
        # Uncomment print statement to print current frame if desired
        # WARNING: THIS WILL SPAM THE CONSOLE
        #print(frame_val)
    
    #If the slider value changes, call function above
    Slider_val.on_changed(update)


def rotate(video,x1,y1,x2,y2,orientation):
    # Function by Johanna Neumann Sørensen
    
    # This function can rotate an video so that a tilted line in the video becomes vertical or horizontal
    # The input requires two sets of coordinates that the tilted line passes through
    
    # Slope of the tilted line
    a = (y1-y2)/(x2-x1)
    
    # Rotation angles depending on the desired orientation
    angleh = -m.degrees(m.atan(a))
    anglev = angleh - 90
    
    # Rotates the video
    if orientation == 'h':
        rotatedvideo = scipy.ndimage.rotate(video,angleh)
    if orientation == 'v':
        rotatedvideo = scipy.ndimage.rotate(video,anglev)
    
    return rotatedvideo
    
def templateMatch(imageStack,template,threshold):
    # Function by Johannes Koblitz Aaen
    
    # For best results, ensure the streak is in the middle of the template
    # The lowest threshold value which should be used is ~0.4-0.5
    
    # An empty list, in which the streak images are stored
    streakImages = []
    
    for frame in range(imageStack.shape[2]):
        
        # workingCoords is apparently y, then x. Watch out for this.
        workingCoords=cv2.matchTemplate(imageStack[:,:,frame].astype(np.float32),template.astype(np.float32),cv2.TM_CCOEFF_NORMED)
        workingCoords=np.where(workingCoords >= threshold)
        
        # Due to the method used, all coordinates have an offset which depends upon the dimensions of the used template
        # Below is a fix, which solves the coordinate issue
        templateW = int(round(template.shape[0]/2))
        templateH = int(round(template.shape[1]/2))
        workingCoords=np.array((workingCoords[1]+templateH,workingCoords[0]+templateW))
        
        # Create binary image of identified points
        binaryPoints = np.zeros_like(imageStack[:,:,frame])
        binaryPoints[workingCoords[1],workingCoords[0]]=255
        
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
        # First determine the variables used to cut out the image (from the center)
        xMov = int(round((template.shape[1]+8)/2))
        yMov = int(round((template.shape[0]+8)/2))
        for i in range(len(xCent)):
            # Extract and convert the center coordinates to nearest integer
            xCenter = int(round(xCent[i]))
            yCenter = int(round(yCent[i]))
            
            # Add cutout to output if conditions are true
            if imageStack[yCenter-yMov:yCenter+yMov,xCenter-xMov:xCenter+xMov,frame].shape[0] == 2*yMov:
                if imageStack[yCenter-yMov:yCenter+yMov,xCenter-xMov:xCenter+xMov,frame].shape[1] == 2*xMov:
                    if imageStack[yCenter-yMov:yCenter+yMov,xCenter-xMov:xCenter+xMov,frame].shape[0] > 0:
                        streakImages.append(imageStack[yCenter-yMov:yCenter+yMov,xCenter-xMov:xCenter+xMov,frame])
        
        # Shows the macthes' coordinates with red dots, and center with blue dots
        # May not be a great idea to uncomment without removing the loop, and defining 'frame', but great for visualisation
        # plt.figure()
        # plt.imshow(imageStack[:,:,frame-1],cmap='Blues')
        # plt.scatter(x=workingCoords[0], y=workingCoords[1], c='r', s=0.2)
        # plt.scatter(x=xCent, y=yCent, c='b', s=0.4)
        # plt.show()
    
    return streakImages


def streakLength(streakImages,pixelSize):
    # Function by Johannes Koblitz Aaen
    
    # Takes a list of images in the same size, and determines the streak length
    # Output is a tuple where first element is an array of lengths, and second is a list of bools used for sorting purposes
    # False means an image has been removed, True means it has not
    
    # Additionally, the profiles of the streaks are also given as a third element in a list of np arrays
    # This is purely for visualisation, but can also be used for other purposes
    
    # Remember: Specifically for the 50X lens, each pixel had a size of 132 nm.
    
    # Make a check whether there are any matches at all
    if len(streakImages)==0:
        sys.exit("Something went wrong. streakLength received an empty list. Please check your template for templateMatch using plt.imshow().")
    
    # Find approximate middle of image
    imWidth = streakImages[0].shape[1]
    midPoint = int(round(imWidth/2))
    
    # Define value used for width of cutout, three empty lists and an array
    if int(round(imWidth/6))!=0:
        cutVal = int(round(imWidth/6))
    else:
        cutVal = 1
    meanStrips = []
    streakLen = np.array([])
    removedImgs = []
    cutOuts = []
    
    # Create a list of cutouts to be used in analysis
    for elem in streakImages:
        cutOut = elem[:,midPoint-cutVal:midPoint+cutVal]
        cutOuts.append(cutOut)
    
    # Take a cutout of each image from middle of image to a set value, then find the mean on second axis
    for elem in cutOuts:
        
        # Mean of cutout along second axis is found, and added to a list
        meanAxis = np.mean(elem,axis=1)
        
        # Normalize for ease of analysis, and add to list
        # meanStrips isn't used in the code, but can be output if a visualisation is needed
        meanAxis = meanAxis/np.max(meanAxis)
        meanStrips.append(meanAxis)
        
        # Find the peaks of the strip, and add to list
        peakvar = scipy.signal.find_peaks(meanAxis,height=np.max(meanAxis)*0.5,prominence=np.max(meanAxis)*0.1)
        
        # Now for some sorting
        # If there's less than one peak, do not add it, and go to next value
        if len(peakvar[0])<2:
            removedImgs.append(False)
            streakLen = np.append(streakLen,0)
            continue
        else:
            removedImgs.append(True)
        
        # If the loop is still running, calculate the streak length from outer peaks
        lenvar = np.max(peakvar[0])-np.min(peakvar[0])
        streakLen = np.append(streakLen,lenvar)
        
    
    # Due to the image analysis method there are going to be outliers
    # These outliers are known false positives, and can therefore be removed
    # This is done using the std Dev
    
    # Create array without zero values
    noZeros = list(compress(streakLen,removedImgs))
    
    # Calculate mean and std of streaklengths
    lenMean = stat.mean(noZeros)
    stdDev = stat.pstdev(noZeros)
    
    # Sort based on mean and stdDev
    for i in range(len(streakLen)):
        if (abs(streakLen[i]-lenMean)>2*stdDev):
            removedImgs[i] = False
    
    #streakSort = streakLen
    streakSort = list(compress(streakLen,removedImgs))
    
    # Convert list by multiplying each element with the pixelsize
    # I really should had used numpy for this
    # Hindsight is 20/20
    for i in range(len(streakSort)):
        streakSort[i] = streakSort[i]*pixelSize
        
    # Clear unused memory
    gc.collect()
    
    return streakSort,removedImgs,meanStrips

def viewStreaks(list1,columns):
    # Function by Johanna Neumann Sørensen
    # This function takes a list of arrays (images) and displays them as one image
    # The input requires a list of arrays and a number of wanted columns
    
    # Empty figure with size
    fig=plt.figure(figsize=(8, 8))
    # Number of columns and rows in the final figure
    columns = 4
    rows = m.ceil(len(list1)/columns)
    
    # Loop that adds each image to the final figure and displays it
    for k in range(1,len(list1)+1):
        fig.add_subplot(rows, columns, k)
        plt.imshow(list1[k-1])
        plt.show()

        
        
def acceptedStreaks(list1,boolean,columns):
    # Function by Johanna Neumann Sørensen
    # This function takes a list of arrays (images), sorts them and displays them in one figure
    # The input requires a list of arrays, a boolean list containing True and False and a number of wanted columns
    
    # Empty figure with specfied size
    fig=plt.figure(figsize=(8, 8))
    streaks = []
    
    # Loop that filters out the declined streaks
    for i in range(1,len(list1)+1):
        if boolean[i-1] == True:
            streaks.append(list1[i-1])
           
    # Calculating number of rows needed
    rows = m.ceil(len(streaks)/4)
    
    # Loop that adds each image to the final figure and displays it
    for k in range(1,len(streaks)+1):
        fig.add_subplot(rows, columns, k)
        plt.imshow(streaks[k-1])
        plt.suptitle('Accepted Streaks')
        plt.show()
            

def declinedStreaks(list1,boolean,columns):
    # Function by Johanna Neumann Sørensen
    # This function takes a list of arrays (images), sorts them and displays them in one figure
    # The input requires a list of arrays, a boolean list containing True and False and a number of wanted columns
    
    # Empty figure with specfied size
    fig=plt.figure(figsize=(8, 8))
    streaks = []
    
    # Loop that filters out the accepted streaks
    for i in range(1,len(list1)+1):
        if boolean[i-1] == False:
            streaks.append(list1[i-1])
    
    # Calculating number of rows needed
    rows = m.ceil(len(streaks)/4)
    
    # Loop that adds each image to the final figure and displays it
    for k in range(1,len(streaks)+1):
        fig.add_subplot(rows, columns, k)
        plt.imshow(streaks[k-1])
        plt.suptitle('Declined Streaks')
        plt.show()


# Actual Image Processing
# Just type in whatever you need underneath

# Example of data processing, using the example file:
# Load data
greyedVid = loadDataAsGrey("60 Hz 15 fps 0.8 V_Exp1.avi",False,60,410)

# Rotate and image process
greyedVid = rotate(greyedVid, 45, 22, 455, 14, 'h')
noAvg=removeaverage(greyedVid)
gaussBlurr=gaussianfilter(noAvg,1.0)

# Find a suitable template by using slideShow. Remember that frames in slideShow count from 1, while python generally counts from 0
#slideShow(gaussBlurr, 'gray')
tempG = gaussBlurr[38:64,174:189,209]

# Use template to get matches
Frames = templateMatch(gaussBlurr, tempG, 0.75)

# Use matches to find length of streaks
streakLengths=streakLength(Frames,132)

# Beregning af gennemsnitslig længde og standardafvigelse
lenmean=stat.mean(streakLengths[0])
lenStd=stat.pstdev(streakLengths[0])

# Print statements for automatisering
print('\nHow many matches: ',len(Frames))
print("N: ",sum(streakLengths[1]))
print('lengthMean: ',lenmean)
print('lengthStd: {} \n'.format(lenStd))
