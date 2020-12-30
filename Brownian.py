# -*- coding: utf-8 -*-
"""
Created on Wed Dec 30 01:24:40 2020

@author: johan
"""

## Trajectory plot of Brownian motion by Johanna

import os
import csv
import matplotlib.pyplot as plt

# Changes working directory
os.chdir('/Users/Johanna/OneDrive - Danmarks Tekniske Universitet/DTU/3. Semester/Fagprojekt/Data 27112020/Brownian motion_after60min')

# Empty lists for the trajectory number and the coordinates
trajec = []
x = []
y = []

# Reads the csv file
with open('Trajectories2.csv', 'r') as rf:
    reader = csv.reader(rf, delimiter=',')
    # Appends the trajectory number and the coordinates to the empty lists
    for row in reader:
        trajec.append(row[1])
        x.append(row[3])
        y.append(row[4])

# Deletes the first element in the lists, which is the title of the category
del trajec[0]
del x[0]
del y[0]

# Converts strings to float in list
new_trajec = [float(i) for i in trajec]

# Empty list for the indices of different trajectories
indices = []

# Loop to find where one trajectory ends and another begins
# The appended value is the last index before a new trajectory begins
for j in range(0, len(new_trajec)-1):
    if new_trajec[j]-new_trajec[j+1] != 0:
        indices.append(j)

# The number 0 is added to the list of indices
indices.insert(0, 0)

# Converts strings to float in lists
new_x = [float(i) for i in x]
new_y = [float(i) for i in y]

# Makes sure that each trajectory gets a different color
def get_cmap(n, name='hsv'):
    '''Returns a function that maps each index in 0, 1, ..., n-1 to a distinct 
    RGB color; the keyword argument name must be a standard mpl colormap name.'''
    return plt.cm.get_cmap(name, n)

# Makes sure that each trajectory gets a different color
N = len(indices)-1
cmap = get_cmap(N)

# Loop that plots each trajectory based on the indices 
for k in range(0, len(indices)-1):
    x2 = new_x[indices[k]+1:indices[k+1]+1]
    x3 = [x * 0.132 for x in x2]
    y2 = new_y[indices[k]+1:indices[k+1]+1]
    y3 = [y * 0.132 for y in y2]
    #print(x2)
    #print(y2)
    if len(x2) >= 10 and len(y2) >= 10:
        plt.plot(x3, y3, '--', c=cmap(k))
        plt.title("Particle Trajectory due to Brownian Motion")
        plt.xlabel('x [\u03BCm]')
        plt.ylabel('y [\u03BCm]')
        plt.show()

