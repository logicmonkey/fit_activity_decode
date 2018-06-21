#!/usr/bin/env python

import sys
import csv
import matplotlib.pyplot as plt
from fitparse import FitFile
from datetime import timedelta

def extract(filename, mode):
    timestamp = []
    distance = []
    speed = []

    if csvmode:
        with open(filename) as csvfile:
            alldata = csv.reader(csvfile, delimiter=',')
            oneskipped = False
            for row in alldata: # discard line containing column title text
                if oneskipped:
                    timestamp.append(int(float(row[0])))
                    distance.append(float(row[1]))
                    speed.append(float(row[2])*3.6) # convert m/s to km/h here
                oneskipped = True
    else:
        fitfile = FitFile(filename)

        for record in fitfile.get_messages('record'):
            for field in record:
                if field.name == 'timestamp':
                    timestamp.append(field.value)
                elif field.name == 'distance':
                    distance.append(field.value)
                elif field.name == 'speed':
                    speed.append(field.value*3.6) # convert m/s to km/h here

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

    racemode = False
    csvmode = False

    if len(sys.argv) == 4:
        filename = sys.argv[3]

        if (sys.argv[1] == '--race') or (sys.argv[1] == '-r') or (sys.argv[2] == '--race') or (sys.argv[2] == '-r'):
            racemode = True

        if (sys.argv[1] == '--csv') or (sys.argv[1] == '-c') or (sys.argv[2] == '--csv') or (sys.argv[2] == '-c'):
            csvmode = True

        if not racemode or not csvmode:
            print("Unrecognised option. Use none, --race or -r, --csv or -c\n")
            print("Usage: analyse.py [-r|--race] [-c|--csv] <filename>\n")

    elif len(sys.argv) == 3:
        filename = sys.argv[2]

        if (sys.argv[1] == '--race') or (sys.argv[1] == '-r'):
            racemode = True

        elif (sys.argv[1] == '--csv') or (sys.argv[1] == '-c'):
            csvmode = True

        else:
            print("Unrecognised option. Use none, --race or -r, --csv or -c\n")
            print("Usage: analyse.py [-r|--race] [-c|--csv] <filename>\n")

    elif len(sys.argv) == 2:
        filename = sys.argv[1]

    elif len(sys.argv) == 1:
        print("Usage: analyse.py [-r|--race] [-c|--csv] <filename>\n")
        exit()

    timestamp, distance, speed = extract(filename, csvmode)

    if racemode:
        # assume race start has the maximum acceleration
        start_index = maxdiff(speed)
    else:
        start_index = 0

    starttime  = timestamp[start_index]
    startdist  = distance[start_index]
    kilometres = [0] # first in list of kilometre start times
    current_km = 0

    # move time zero to the start_index: values before start become negative
    for index in range(len(timestamp)):
        if csvmode:
            timestamp[index] -= starttime # csv data uses integer epoch offsets
        else:
            # negative timedeltas behave strangely, so reverse and negate
            if (timestamp[index] - starttime) < timedelta(0):
                timestamp[index] = -1 * (starttime - timestamp[index]).seconds
            else:
                timestamp[index] = (timestamp[index] - starttime).seconds

        # use actual distance prior to start and modulus 1km thereafter
        if distance[index] < startdist:
            km, m = divmod(startdist - distance[index], 1000)
            distance[index] = m/-1000
        else:
            km, m = divmod(distance[index]-startdist, 1000)
            distance[index] = m/1000
            if km > current_km:
                kilometres.append(timestamp[index])
                current_km = km

    def get_km(seconds):
        if seconds < 0: # report 0 pace for pre-start
            return 0, 0
        elif seconds >= kilometres[-1]: # report 0 pace for final part-kilometre
            return 0, len(kilometres)-1

        count = 0
        for km in kilometres[1:]: # list of kilometre start times
            if km <= seconds:
                count += 1
            else:
                return kilometres[count+1] - kilometres[count], count

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
                spd_anno.set_text("Time {:02d}:{:02d}\nSpeed {:.1f}km/h".format(minutes, seconds, pos[1]))
                fig.canvas.draw_idle()
            elif spd_vis:
                fig.canvas.draw_idle()

        if event.inaxes == dst_axes:
            cont, ind = dst_scat.contains(event) # mouse event on scatter obj?
            dst_anno.set_visible(cont)
            if cont:
                pos = dst_scat.get_offsets()[ind["ind"][0]]
                dst_anno.xy = pos
                minutes, seconds = divmod(int(pos[0]), 60)
                kmseconds, kmnumber = get_km(pos[0])
                paceminutes, paceseconds = divmod(kmseconds, 60)
                dst_anno.set_text("Time {:02d}:{:02d}\nDistance {:.2f}km\nPace {:02d}:{:02d}".format(minutes, seconds, kmnumber + pos[1], paceminutes, paceseconds))
                fig.canvas.draw_idle()
            elif dst_vis:
                fig.canvas.draw_idle()

    fig.canvas.mpl_connect("motion_notify_event", hover)
    # ANNOTATION END

    # SIMPLE START
    plt.tight_layout()
    plt.show()
    # SIMPLE END
