from lib2to3.pgen2 import driver
from operator import index
import re
import json
from unittest import result
from numpy import empty
import pytesseract
from pytesseract import Output
import cv2
from datetime import datetime
import PySimpleGUI as sg
import os
import csv
from difflib import SequenceMatcher
from functools import partial
import numpy as np


class Driver:
    def __init__(self, name, time, gap, lap):
        self.name = name
        self.time = time
        self.gap = gap
        self.lap = lap


cars = ['Panther', 'Feather', 'Bonk', 'Storm', 'Osprey', 'Adgitator',
        'Brusso', 'Mantra', 'Piccino', 'Conquest', 'Vost', 'Loose Cannon']


def clean_driver_column(driver):
    # replace | with whitespace and split at whitespace to make a list
    driver_splitted = driver.replace("|", " ").split(" ")

    elements = []

    for element in reversed(driver_splitted):
        # > 3 to exclude all numbers, weird single characters and team tags
        # second condition so that names like "White Van Man" are not excluded as e.g. "Van" is not fully capitalized
        # and team tags are generally in upper case
        if len(element) > 3 or (len(element) == 3 and not element.isupper()):
            elements.append(element)

    # as we looped reversed, the first element should be either the name of the driver (most of the time) or the car name
    if len(elements) == 2:
        # probably first element is car, second driver name, so return driver
        return elements[1]
    elif len(elements) == 1:
        # jackpot
        return elements[0]
    else:
        # nick name probably consists of more than one word
        # we do not know, if the last one is a car name
        # so return all elements with len() > 3 in the correct order
        return " ".join([el for el in reversed(elements)])


def get_driver_info(infos, is_quali):
    driverInfo = []
    count = 0
    index = 0
    while index < len(infos):
        match = re.search("\d{1}:\d{2}.\d{3}", infos[index])
        if(match):
            count += 1
            if not is_quali and count == 3:
                count = 0
                info = infos[0:index + 1]
                driverInfo = info
                del infos[0:index + 1]
                index = 0
            if is_quali and count == 2:
                count = 0
                info = infos[0:index + 1]
                driverInfo = info
                del infos[0:index + 1]
                index = 0

        index += 1
    if driverInfo == []:
        driverInfo = infos
    print(driverInfo)
    return driverInfo


def clean_time(item):
    if not item == None:
        return re.sub('\,', '.', item)
    else:
        return "0"


def create_drivers(drivers, is_quali):
    newDrivers = []
    position = 1
    for driver in drivers:
        indexOfStats = []
        for car in cars:
            if car in driver:
                driver.remove(car)
        for item in driver:
            match = re.search("\d+(:|.)\d+.\d+", item)
            if(match):
                indexOfStats.append(driver.index(item))
        name = "Driver"
        time, gap, lap = '00:00.000', '00:00.000', '00:00.000'
        if len(driver) > 0:
            if len(indexOfStats) != 0:
                print()
                nameArray = driver[0:indexOfStats[0]]
                name = " ".join(nameArray)
                print(indexOfStats)
                print(driver)

                if is_quali:
                    lap = driver[indexOfStats[0]]
                    gap = driver[indexOfStats[1]]
                else:
                    if len(indexOfStats) == 1:
                        print('here------------------')
                        lap = driver[indexOfStats[0]]
                    else:
                        time = driver[indexOfStats[0]]
                        gap = driver[indexOfStats[1]] if 1 < len(
                            indexOfStats) else '00:00.000'
                        lap = driver[indexOfStats[2]] if 2 < len(
                            indexOfStats) else '00:00.000'
            else:
                nameArray = driver
                laptime = driver[len(driver) - 1]
                name = " ".join(nameArray)
                lap = laptime

        newDriver = {
            "position": position,
            "driver": clean_driver_column(re.sub('[^a-zA-Z0-9\\s]', '', name)),
            "time": clean_time(time),
            "gap": clean_time(gap),
            "lap": clean_time(lap),
        }
        position += 1
        newDrivers.append(newDriver)
    return newDrivers


def output(result_drivers, quali_drivers, format, outputFile):
    if outputFile == '':
        outputFile = 'output.txt'
    if format == 'json':
        data = {}
        if result_drivers:
            data['results'] = result_drivers
        if quali_drivers:
            data['quali'] = quali_drivers
        jsonString = json.dumps(data, indent=4, sort_keys=False)
        jsonFile = open(outputFile, "w")
        jsonFile.write(jsonString)
        jsonFile.close()
    if format == 'csv':
        f = open(outputFile, 'w', newline='')
        writer = csv.writer(f)
        result_headers = dict(result_drivers[0]).keys()
        quali_headers = dict(quali_drivers[0]).keys()
        result_ds = []
        for i in range(len(result_drivers)):
            result_ds.append(dict(result_drivers[i]).values())
        quali_ds = []
        for i in range(len(quali_drivers)):
            quali_ds.append(dict(quali_drivers[i]).values())
        writer.writerow(result_headers)
        writer.writerows(result_ds)
        writer.writerow(quali_headers)
        writer.writerows(quali_ds)
    if format == 'csup-stats':
        combined_drivers = combine_drivers(result_drivers, quali_drivers)
        f = open(outputFile, 'w', newline='')
        writer = csv.writer(f)
        headers = dict(list(dict(combined_drivers).values())[0]).keys()
        drivers = []
        for key in dict(combined_drivers).keys():
            drivers.append(dict(combined_drivers[key]).values())
        writer.writerow(headers)
        writer.writerows(drivers)
    return result_drivers


def on_trackbar(val):
    print(val)
    # img = cv2.imread(
    #     "C:/Users/cjmeeks/dev/scoreboard-vision/images/ICS/3-as.png")
    ret, thresh = cv2.threshold(img, val, 255, cv2.THRESH_BINARY)
    thresh = cv2.cvtColor(thresh, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(thresh, 0, 255, cv2.THRESH_BINARY)
    cv2.imshow("test", thresh)


def read_and_process(image_input):
    print(image_input)
    myconfig = r"--psm 6 --oem 3"
    global img
    img = cv2.imread(image_input)

    cv2.namedWindow("test")
    cv2.createTrackbar("threshhold", "test", 0, 255, on_trackbar)
    t_value = 100
    on_trackbar(t_value)

    while(1):
        k = cv2.waitKey(1)
        if k == 27:
            break

        t_value = cv2.getTrackbarPos("threshhold", "test")
        # thresh = cv2.cvtColor(thresh, cv2.COLOR_BGR2GRAY)
        # ret, thresh = cv2.threshold(thresh, 0, 255, cv2.THRESH_BINARY)
        # cv2.imshow("test", thresh)
        # cv2.waitKey(0)
    cv2.destroyAllWindows()
    print(t_value)
    ret, thresh = cv2.threshold(img, t_value, 255, cv2.THRESH_BINARY)
    thresh = cv2.cvtColor(thresh, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(thresh, 0, 255, cv2.THRESH_BINARY)

    dataHSV = pytesseract.image_to_data(
        thresh, config=myconfig, output_type=Output.DICT)

    texts = dataHSV['text']
    print(texts)
    lineNums = dataHSV['line_num']

    # print(dataHSV)

    # print(texts)
    newTexts = []
    lines = {
        0: [],
        1: [],
        2: [],
        3: [],
        4: [],
        5: [],
        6: [],
        7: [],
        8: [],
        9: [],
        10: [],
        11: [],
        12: [],
        13: [],
        14: [],
        15: [],
        16: [],
        17: [],
        18: [],
        19: [],
        20: [],

    }

    amount_boxes = len(texts)
    for i in range(amount_boxes):
        lines[lineNums[i]].append(texts[i])

    return lines


def convert_time_to_seconds(time):
    date_time = datetime.strptime(time, "%M:%S.%f")

    a_timedelta = date_time - datetime(1900, 1, 1)
    return a_timedelta.total_seconds()


def convert_drivers_csup_stats(list, is_quali):
    new_list = []
    for i in range(len(list)):
        if is_quali:

            new_list.append({
                'driver': list[i]['driver'],
                'quali_position': list[i]['position'],
                # need function here
                'quali_lap_time_seconds': convert_time_to_seconds(list[i]['lap']),
            })
        else:
            new_list.append({
                'driver': list[i]['driver'],
                # need function here
                'race_time_seconds': convert_time_to_seconds(list[i]['time']),
                # need function here
                'fastest_lap_seconds': convert_time_to_seconds(list[i]['lap']),
                'position': list[i]['position'],
            })
    return new_list


def make_driver_object(x):
    obj = {}
    for i in range(len(x)):
        driver = x[i]
        obj[driver['driver']] = driver
    return obj


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


def find_most_similar(key, list):
    maxSim = 0
    maxName = ''
    for driver in dict(list).keys():
        sim = similar(key, driver)
        if sim > maxSim:
            maxSim = sim
            maxName = driver
    return maxName


def combine_drivers(result, quali):
    # new format = driver,quali_lap_time_seconds,quali_position,race_time_seconds,lappings,fastest_lap_seconds,gets_points_for_fastest_lap ,position
    result = make_driver_object(result)
    quali = make_driver_object(quali)
    new_d = {}
    for key in dict(result).keys():
        result_driver = result[key]
        quali_driver_name = find_most_similar(key, quali)
        quali_driver = quali[quali_driver_name]
        new_d[result_driver['driver']] = {
            'driver': result_driver['driver'],
            # need function here
            'quali_lap_time_seconds': convert_time_to_seconds(quali_driver['lap']),
            'quali_position': quali_driver['position'],
            # need function here
            'race_time_seconds': convert_time_to_seconds(result_driver['time']),
            'lappings': '0',
            # need function here
            'fastest_lap_seconds': convert_time_to_seconds(result_driver['lap']),
            'gets_points_for_fastest_lap': False,
            'position': result_driver['position'],  # need function here
        }
    fl_name = find_fastest_lap(new_d)
    driver = new_d[fl_name]
    driver['gets_points_for_fastest_lap'] = True
    new_d[fl_name] = driver
    return new_d


def find_fastest_lap(drivers):
    minLap = 100
    minName = ''
    for driver in dict(drivers).keys():
        lap = float(drivers[driver]['fastest_lap_seconds'])
        if lap < minLap:
            minLap = lap
            minName = driver
    return minName


def find_header_row(lines):
    i = 0
    print(lines)
    for line in list(lines):
        for el in line:
            print(el)
            if el in ["POS", 'DRIVER', "CAR", "TIME", "GAP", "BEST", "PILOTE", "VOITURE", "FAHRER", "FAHRZEUG", "ZEIT", "BESTE", "ABSTAND", "RUNDE"]:
                return i + 1
        i += 1
    return 3


def main():
    result_drivers = None
    if result_input:
        lines = read_and_process(result_input)
        lines = lines.values()
        firstDriverIndex = find_header_row(lines)
        drivers = []
        for infos in list(lines)[firstDriverIndex:firstDriverIndex + 12]:
            drivers.append(get_driver_info(infos, False))
        result_drivers = create_drivers(
            drivers, False)

    quali_drivers = None
    if quali_input:
        quali_arrays = read_and_process(quali_input)
        quali_drivers = create_drivers(
            get_driver_info(quali_arrays, True), True)

    output(result_drivers, quali_drivers, outputFormat, outputFile)


while(True):
    os.environ["PATH"] += os.pathsep + "C:\Program Files\Tesseract-OCR"
    # window
    sg.theme('Material1')

    layout = [
        [sg.Text('Result Image To Read'), sg.FileBrowse()],
        [sg.Text('Qualification Image To Read'), sg.FileBrowse()],
        [sg.Text('Output file'), sg.FileBrowse()],
        [sg.Text('Choose output format')],
        [sg.Combo(['csv', 'json', 'csup-stats'],
                  default_value='json', key='output_format')],
        [sg.Button('Ok'), sg.Button('Cancel')]
    ]

    window = sg.Window('CSUP Result Reader', layout)

    result_input = None
    quali_input = None
    outputFile = ''
    outputFormat = ''
    while True:
        event, values = window.read()
        if event == 'Ok':  # if user closes window or clicks cancel
            result_input = values['Browse']
            quali_input = values['Browse0']
            outputFile = values['Browse1']
            outputFormat = values['output_format']
            window.close()
            break
        if event == sg.WIN_CLOSED or event == 'Cancel':
            window.close()
            exit(0)
    main()
