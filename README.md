
############# REQUIRED LIBRARIES #############
This script uses the following libraries. Make sure that you have them all installed for the code to run.

numpy
math
matplotlib
os
gc
sys
scipy - DOWNLOAD REQUIRED
opencv / cv2 - DOWNLOAD REQUIRED
skimage / scikit-image - DOWNLOAD REQUIRED
ffmpeg - DOWNLOAD REQUIRED (Use "conda install -c mrinaljain17 ffmpeg" in anaconda prompt in windows)
statistics - MAY REQUIRE DOWNLOAD

If using anaconda, use the anaconda prompt to download libraries. In windows, simple use the search function. For mac, use anaconda navigator to open anaconda prompt. Some libraries take a while to download.

############# USING THE CODE #############
This code is meant to analyse the length of streaks of nanoparticles in a microchannel. To obtain proper results, ensure that:
	1. Your video is as high a resolution as possible
	2. All streaks are oriented along one axis (video can be rotated by the code)
	3. You have at least 8 GB ram, as data is stored there temporarily

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


Additional tips for each step can be found below, and an example of the above method can be found at the bottom of the code. Do be aware that while some functions start counting frames from 1, python (and normal programming languages) generally count from 0.

############# LOADING DATA IN GREYSCALE #############
When loading your data, ensure that the file you're working on is in the same folder as the script, as the working directory is changed to its current directory. This can be changed manually in the beginning of the code. Also, remember the file extension when loading your video.

Set allFrames to True (or anything the isn't False for that matter) if you don't want to bother with not loading all frames. The frames can in this case just be set to 1 and 2.

############# PROCESSING YOUR IMAGE #############
When processing your image you can either decide to remove the background using removeaverage, and then blurr to improve result, or the other way around. Or you can entirely forego the blurring or background removal. The best tip here is that the image processing is very dependant upon your video file, and there really isn't an universal answer to 'How should i do this?'.

When using gaussianfilter, a sigma of 0.5 is a weak blurr, a sigma of approx. 1.0 is a decent amount of blurring and everything above 2.0-3.0 is a very aggresive blurring. Usually a sigma of 1.0 or 1.5 is fine. Sometimes less of your video resolution is high. Just remember that the blurring is to compensate for a limited video resolution.

Use slideShow to see if your processing works for your given video. If slideShow doesn't work, then you likely need to change backline to 'Automatic' under Tools->Preferences->IPython Console->Graphics.

############# FINDING THE ONE #############
When trying to find a template, use the slideShow function with your cmap of choice ('gray' is a classic) and begin looking through your frames. When you've found something that looks promising, remember to use the zoom function to ensure it is properly well defined.

Now, you've got to figure out which x you start at and end at. The same with y. Also, remember to subtract one from your chosen frame, as python counts from 0. After you've identified these sizes, you can simply extract the image from your 3D-array. See the example at the bottom of the script, if need be.

For reference, the method used in template matching is TM_CCOEFF_NORMED.

############# TEMPLATE MATCHING #############
The template streak should ideally not be less than 1/4 of the width of the frame, from the center axis.
This is due to the streakLength function expecting the streak to:
	1. Be centered (this is *very* important)
	2. Fill a decent part of the image (Do be aware that the template matching function ignores everything too close to the edge of the image - about 8 pixels)

An example of such a template is included.

Aditionally, when using templateMatch, a good threshold for matching lies in or around the 0.7-0.8 range. This of course depends upon the quality of your template, and I've personally had to use 0.65 before, to get a good amount of data.

############# CALCULATING THE MEAN AND STANDARD DEVIATION #############
To calculate the mean, use stat.mean() and to calculate the std dev use stat.pstdev() in the first output from the streakLength function. In other words streakLength()[0].

