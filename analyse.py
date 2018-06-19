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

    # move time zero to the start_index: values before start become negative
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

    fig, (spd_axes, dst_axes) = plt.subplots(2, sharex=True)

    spd_scat = spd_axes.plot(timestamp, speed, color='r')
    dst_scat = dst_axes.plot(timestamp, distance, color='b')

    spd_scat = spd_axes.scatter(timestamp, speed, color='r')
    dst_scat = dst_axes.scatter(timestamp, distance, color='b')

    spd_axes.grid()
    dst_axes.grid()

    spd_axes.set_ylabel(spd_label)
    dst_axes.set_ylabel(dst_label)

    spd_axes.set_title(xtitle)
    dst_axes.set_xlabel(xlabel)

    spd_anno = spd_axes.annotate("",
                   xy=(0,0), xytext=(20,20),
                   textcoords="offset points",
                   bbox=dict(boxstyle="round", fc="w"),
                   arrowprops=dict(arrowstyle="->"))

    spd_anno.set_visible(False)

    def spd_update_anno(ind):
        pos = spd_scat.get_offsets()[ind["ind"][0]]
        spd_anno.xy = pos
        minutes, seconds = divmod(pos[0], 60)
        spd_anno.set_text("Time {:02d}:{:02d}  {:.1f}km/h".format(int(minutes), int(seconds), pos[1]))

    def hover(event):
        spd_vis = spd_anno.get_visible()

        if event.inaxes == spd_axes:
            cont, ind = spd_scat.contains(event)
            spd_anno.set_visible(cont)
            if cont:
                spd_update_anno(ind)
                fig.canvas.draw_idle()
            else:
                if spd_vis:
                    fig.canvas.draw_idle()

    fig.canvas.mpl_connect("motion_notify_event", hover)

    plt.tight_layout()
    plt.show()
