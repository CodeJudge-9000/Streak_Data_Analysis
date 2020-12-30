
############# TEMPLATE MATCHING #############
The template should ideally not go beyond 1/6 of the width of the frame, from the center axis.
If the streak fills more than 2/6 of the image, a worse result may be obtained.
This is due to the streakLength function expecting the streak to:
	1. Be centered
	2. Only fill part of the image

An example of such a template is included.
