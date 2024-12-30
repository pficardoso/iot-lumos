import random
import re

import numpy as np
from matplotlib import pyplot as plt


def parse_line(line):
    pattern = re.compile(
        "(.+) Thread - Segments? (.+) - StartTime: (.+) - EndTime: (.+) - "
        "Duration: (.+) - Shift from previous iteration: (.+)"
    )
    re_match = pattern.match(line)
    thread, seg, st, et, delta, shift = re_match.groups()
    if thread == "Model":
        seg = seg.split(":")[1]

    return thread, int(seg), float(st), float(et), float(delta), float(shift)


def get_data_file(file_path):
    data = {}
    with open(file_path) as fin:
        for i, line in enumerate(fin.readlines()):
            if i == 0:
                thread, seg, st, et, delta, shift = parse_line(line)
                st_ref = st
            else:
                thread, seg, st, et, delta, shift = parse_line(line)

            st = st - st_ref
            et = et - st_ref
            data_seg = data.setdefault(int(seg), {})
            data_seg[thread] = {
                "seg": seg,
                "st": st,
                "et": et,
                "delta": delta,
                "shift": shift,
            }

    return data


def get_threads(data):
    threads = set()
    for seg_data in data.values():
        for key in seg_data.keys():
            threads.add(key)
    return threads


def plot_data(data, start_seg=None, end_seg=None):
    if not start_seg:
        start_seg = 1
    if not end_seg:
        end_seg = max(list(data.keys())) + 1
    else:
        end_seg = end_seg + 1

    first_seg_data, last_seg_data = data[start_seg], data[end_seg]

    threads_set = get_threads(data)
    thread_color = {
        thread_name: (random.random(), random.random(), random.random())
        for i, thread_name in enumerate(threads_set)
    }

    # define x_max and x_min (time)
    x_min = min([first_seg_data[thread]["st"] for thread in first_seg_data.keys()])
    x_max = max([last_seg_data[thread]["et"] for thread in last_seg_data.keys()])
    delta_x = 0.25

    # define y_max and y_min
    y_min, y_max = start_seg, end_seg
    delta_y = 1

    plt.figure()

    for seg in range(start_seg, end_seg):
        for thread in data[seg].keys():
            seg_start = data[seg][thread]["st"]
            seg_end = data[seg][thread]["et"]
            duration = seg_end - seg_start
            if duration <= 0.01:
                duration = 0.05
            plt.barh(
                y=seg,
                left=seg_start,
                width=duration,
                align="center",
                color=[thread_color[thread]],
            )

    plt.ylim((y_min - delta_y, y_max))
    plt.xlim(x_min, x_max)
    plt.xticks(np.arange(x_min, x_max, delta_x))
    plt.yticks(np.arange(y_min, y_max, delta_y))
    plt.ylabel("Segment ID")
    plt.xlabel("Seconds")

    plt.grid(axis="x")

    plt.show()


if __name__ == "__main__":
    path = "/workspace/personal/projects/lumos/print.segments.timestamps.debug.txt"
    data = get_data_file(path)
    plot_data(data, 1, 16)
