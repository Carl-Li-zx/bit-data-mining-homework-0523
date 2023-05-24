import numpy as np
import pandas as pd
import copy
import math
from matplotlib import pyplot as plt

from .fp_tree import *

data_path = "datas/anonymous-msweb.data"
test_path = "datas/anonymous-msweb.test"
source = "www.microsoft.com"


def load_data():
    website_map = {}
    user_map = {}
    with open(data_path, 'r', encoding='utf-8') as f:
        datas = f.readlines()
    current_user = None
    for index, data in enumerate(datas):
        data = data.strip().split(",")
        if data[0] == "A":
            website_map[str(data[1])] = Website(data[1], eval(data[3]), eval(data[4]))
        elif data[0] == "C":
            if current_user is not None:
                user_map[str(current_user.id)] = copy.deepcopy(current_user)
            current_user = User(data[2], [])
        elif data[0] == "V":
            current_user.visits.append(data[1])
            website_map[str(data[1])].visit_times += 1
            website_map[str(data[1])].visitors.append(current_user.id)
        else:
            continue
    user_map[str(current_user.id)] = copy.deepcopy(current_user)
    return website_map, user_map


def prepare_fp_data(website_map: dict, user_map: dict, show_website=10, bins=20):
    sorted_website = sorted(website_map.items(), key=lambda x: x[1].visit_times)
    print(f"最常被访问的{show_website}个页面:")
    for i in range(show_website):
        website = sorted_website[-i - 1][1]
        print(f"visit times = {website.visit_times}\turl={source + website.url}")
    visits = [item[1].visit_times for item in sorted_website]
    draw_histogram(visits, bins)
    for i in range(len(sorted_website)):
        if sorted_website[i][1].visit_times > 10:
            break
    dropped_website = sorted_website[:i]
    dropped_website_id = [item[0] for item in dropped_website]
    sorted_website = sorted_website[i:]
    webid_frequent_map = {}
    popped_user = []
    for item in sorted_website:
        webid_frequent_map[item[0]] = item[1].visit_times
    for id, user in user_map.items():
        p=[]
        for v in user.visits:
            if v in dropped_website_id:
                p.append(v)
        for v in p:
            user.visits.pop(user.visits.index(v))
        if len(user.visits) == 0:
            popped_user.append(id)
        else:
            user.visits = sorted(user.visits, key=lambda x: webid_frequent_map[x], reverse=True)

    for id in popped_user:
        user_map.pop(id)
    return dict(sorted_website), user_map


def draw_histogram(data: list, bins):
    def count_values_in_intervals(data, num_intervals):
        min_value = np.min(data)
        max_value = np.max(data)
        interval_width = math.ceil((max_value - min_value) / num_intervals)

        # intervals = [min_value + i * interval_width for i in range(num_intervals + 1)]
        intervals = np.array(
            [0, 1, 2, 3, 5, 7, 10, 20, 30, 50, 70, 100, 200, 300, 500, 800, 1000, 2000, 5000, 10000, 20000])
        counts = np.zeros(num_intervals, dtype=int)

        for i in range(num_intervals):
            counts[i] = ((data >= intervals[i]) & (data < intervals[i + 1])).sum()

        return counts, intervals

    counts, intervals = count_values_in_intervals(data, bins)
    plt.bar(range(bins), counts)
    l = []
    for i in range(bins):
        l.append(f"{intervals[i]}-{intervals[i + 1]}")
    plt.xticks(range(bins), l, rotation=90)
    plt.xlabel('Intervals')
    plt.ylabel('Frequency')
    plt.title('Histogram of Data')
    for i, count in enumerate(counts):
        plt.text(i, count, str(count), ha='center', va='bottom')
    plt.show()
