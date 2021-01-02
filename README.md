
############# REQUIRED LIBRARIES #############
This script uses the following libraries. Make sure that you have them all installed for the code to run.

numpy
math
matplotlib
os
gc
scipy - DOWNLOAD REQUIRED
opencv / cv2 - DOWNLOAD REQUIRED
skimage / scikit-image - DOWNLOAD REQUIRED
statistics - MAY REQUIRE DOWNLOAD

############# USING THE CODE #############
This code is meant to analyse the length of streaks of nanoparticles in a microchannel. To obtain proper results, ensure that:
	1. Your video is as high a resolution as possible
	2. All streaks are oriented along one axis (video can be rotated by the code)

The functions are:
	loadDataAsGrey(fileName, allFrames, firstFrame, lastFrame)
	removeaverage(array)
	gaussianfilter(array, sigma)
	threshold(array)
	slideShow(Movie_stck, mapput)
	rotate(video,x1,y1,x2,y2,orientation)
	templateMatch(imageStack,template,threshold)
	streakLength(streakImages,pixelSize)
	viewStreaks(list1,columns)
	acceptedStreaks(list1,boolean,columns)

Documentation of each function, their required inputs and their outputs can be found at the beginning of each function within the script. For a deeper understanding comments have been added within each function, but do be aware that each function have not been made deal with wrong user input. If you recieve an error, check your inputs.

There are a few ways to proceed with the image processing, but the general process goes something like this:
Step 1: Load the code using loadDataAsGrey
Step 2: Ensure the streaks are oriented vertically (long direction must be vertical) using rotate, then use removeaverage and gaussianfilter in whatever order gives this be result. This depends upon the video, and is therefore on a case-by-case basis.
Step 3: Using slideShow on your frame stack, find an approriate template, then define it by frame and x/y. Remember to check your template with plt.imshow() before proceeding.
Step 4: Using your template, find all matches using templateMatch. Then find all streak lengths by using streakLength. Remember to give a pixel size.
Step 5: Use the list of streak lengths to calculate the standard deviation and mean length of streak lengths.


Additional tips for each function can be found below, and an example of the above method can be found at the bottom of the code. Do be aware that while some functions start counting frames from 1, python (and normal programming languages) generally counts from 0.

############# TEMPLATE MATCHING #############
The template should ideally not go beyond 1/6 of the width of the frame, from the center axis.
If the streak fills more than 2/6 of the image, a worse result may be obtained.
This is due to the streakLength function expecting the streak to:
	1. Be centered (this is *very* important)
	2. Only fill part of the image (specifically +-1/6 of the image width, from center)

An example of such a template is included.


