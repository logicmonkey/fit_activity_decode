#!/usr/bin/env python

import sys
import csv
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

def extract(filename):
    timestamp = []
    distance = []
    speed = []

    with open(filename) as csvfile:
        alldata = csv.reader(csvfile, delimiter=',')
        oneskipped = False
        for row in alldata: # discard line containing column title text
            if oneskipped:
                timestamp.append(int(float(row[0])))
                distance.append(float(row[1]))
                speed.append(float(row[2])*3.6) # convert m/s to km/h here
            oneskipped = True

    return timestamp, distance, speed

def maxdiff(dataset):
    # look for the point of the maximum positive difference
    max_delta = 0.0
    max_delta_index = -1 # default to error code
    for index in range(1, len(dataset)):
        delta = dataset[index] - dataset[index-1]
        if delta > max_delta and delta > 0.0:
            max_delta = delta
            max_delta_index = index - 1

    return max_delta_index

if __name__ == '__main__' :

    filename = sys.argv[1]

    timestamp, distance, speed = extract(filename)
    # assume race start has the maximum acceleration
    start_index = maxdiff(speed)

    starttime   = timestamp[start_index]
    startdist   = distance[start_index]

    # move time zero to the start_index: time values before start become negative
    for index in range(len(timestamp)):
        timestamp[index] -= starttime

        # use actual distance prior to start and modulus 1km thereafter
        if distance[index] < startdist:
            distance[index] /= 1000
        else:
            km, m = divmod(distance[index]-startdist, 1000)
            distance[index] = m/1000

    xlabel    = 'Time (seconds)'
    xtitle    = 'Data source: {}'.format(filename)
    spd_label = 'Speed\n(km/h)'
    dst_label = 'Distance\n(km)'

    # fig, (spd_axes, dst_axes) = plt.subplots(2, sharex=True)
    gs = GridSpec(2,1) # rows, columns
    spd_axes = plt.subplot(gs[0,0])
    dst_axes = plt.subplot(gs[1,0])

    spd_dots, = spd_axes.plot(timestamp, speed, 'r')
    spd_axes.grid(b=True)
    spd_axes.set_ylabel(spd_label)

    dst_line, = dst_axes.plot(timestamp, distance, 'b')
    dst_axes.grid(b=True)
    dst_axes.set_ylabel(dst_label)

    spd_axes.set_title(xtitle)
    dst_axes.set_xlabel(xlabel)

    plt.tight_layout()
    plt.show()
