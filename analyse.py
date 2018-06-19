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
    kilometres  = [0] # first in list of kilometre start times
    current_km  = 0

    # move time zero to the start_index: values before start become negative
    for index in range(len(timestamp)):
        timestamp[index] -= starttime

        # use actual distance prior to start and modulus 1km thereafter
        if distance[index] < startdist:
            distance[index] /= 1000
        else:
            km, m = divmod(distance[index]-startdist, 1000)
            if km > current_km:
                kilometres.append(timestamp[index])
                current_km = km
            distance[index] = m/1000

    def get_km(seconds):
        count = -1
        if seconds > kilometres[-1]:
            return len(kilometres)-1

        for i in kilometres: # list of kilometre start times
            if i <= seconds:
                count += 1
            else:
                return count

    # SIMPLE START
    # simple matplotlib figure with two subplots speed and distance versus time
    fig, (spd_axes, dst_axes) = plt.subplots(2, sharex=True)

    spd_axes.plot(timestamp, speed, color='r')
    dst_axes.plot(timestamp, distance, color='b')
    spd_axes.grid()
    dst_axes.grid()
    spd_axes.set_title('Data source: {}'.format(filename))
    spd_axes.set_ylabel('Speed\n(km/h)')
    dst_axes.set_ylabel('Distance\n(km)')
    dst_axes.set_xlabel('Time (seconds)')
    # SIMPLE END

    # ANNOTATION START - comment out between START and END for simple plot
    # create object for speed xy scatter because this can be queried and annotated
    spd_scat = spd_axes.scatter(timestamp, speed, color='r', marker='.')
    dst_scat = dst_axes.scatter(timestamp, distance, color='b', marker='.')

    spd_anno = spd_axes.annotate("", # set the annotation text based on value
                   xy=(0,0), xytext=(20,20),
                   textcoords="offset points",
                   bbox=dict(boxstyle="round", fc="w"),
                   arrowprops=dict(arrowstyle="->"))
    dst_anno = dst_axes.annotate("", # set the annotation text based on value
                   xy=(0,0), xytext=(20,20),
                   textcoords="offset points",
                   bbox=dict(boxstyle="round", fc="w"),
                   arrowprops=dict(arrowstyle="->"))

    spd_anno.set_visible(False)
    dst_anno.set_visible(False)

    def hover(event):
        spd_vis = spd_anno.get_visible()
        dst_vis = dst_anno.get_visible()

        if event.inaxes == spd_axes:
            cont, ind = spd_scat.contains(event) # mouse event on scatter obj?
            spd_anno.set_visible(cont)
            if cont:
                pos = spd_scat.get_offsets()[ind["ind"][0]]
                spd_anno.xy = pos
                minutes, seconds = divmod(int(pos[0]), 60)
                spd_anno.set_text("Time {:02d}:{:02d}  {:.1f}km/h".format(minutes, seconds, pos[1]))
                fig.canvas.draw_idle()
            else:
                if spd_vis:
                    fig.canvas.draw_idle()

        if event.inaxes == dst_axes:
            cont, ind = dst_scat.contains(event) # mouse event on scatter obj?
            dst_anno.set_visible(cont)
            if cont:
                pos = dst_scat.get_offsets()[ind["ind"][0]]
                dst_anno.xy = pos
                minutes, seconds = divmod(int(pos[0]), 60)
                dst_anno.set_text("Time {:02d}:{:02d}  {:.2f}km".format(minutes, seconds, get_km(pos[0]) + pos[1]))
                fig.canvas.draw_idle()
            else:
                if dst_vis:
                    fig.canvas.draw_idle()

    fig.canvas.mpl_connect("motion_notify_event", hover)
    # ANNOTATION END

    # SIMPLE START
    plt.tight_layout()
    plt.show()
    # SIMPLE END
