from lib2to3.pgen2 import driver
import re
import json
from unittest import result
import pytesseract
from pytesseract import Output
import cv2
from datetime import datetime
import PySimpleGUI as sg
import os
import csv
from difflib import SequenceMatcher

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
        break


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
                driverInfo.append(info)
                del infos[0:index + 1]
                index = 0
            if is_quali and count == 2:
                count = 0
                info = infos[0:index + 1]
                driverInfo.append(info)
                del infos[0:index + 1]
                index = 0
        index += 1
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
        indexOfStats = 0
        for car in cars:
            if car in driver:
                driver.remove(car)
        for item in driver:
            match = re.search("\d{1}:\d{2}.\d{3}", item)
            if(match):
                indexOfStats = driver.index(item)
                break
        nameArray = driver[0:indexOfStats]
        statsArray = driver[indexOfStats:len(driver)]
        name = " ".join(nameArray)

        time, gap, lap = None, None, None
        if is_quali:
            lap = statsArray[0]
            gap = statsArray[1]
        else:
            time = statsArray[0]
            gap = statsArray[1]
            lap = statsArray[2]

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
        # quali_drivers = convert_drivers_csup_stats(quali_drivers, True)
        # result_drivers = convert_drivers_csup_stats(result_drivers, False)
        combined_drivers = combine_drivers(result_drivers, quali_drivers)
        f = open(outputFile, 'w', newline='')
        writer = csv.writer(f)
        headers = dict(list(dict(combined_drivers).values())[0]).keys()
        drivers = []
        for key in dict(combined_drivers).keys():
            drivers.append(dict(combined_drivers[key]).values())
        # for i in range(len(result_drivers)):
        #     result_ds.append(dict(result_drivers[i]).values())
        # quali_ds = []
        # for i in range(len(quali_drivers)):
        #     quali_ds.append(dict(quali_drivers[i]).values())
        writer.writerow(headers)
        writer.writerows(drivers)
    return result_drivers


def read_and_process(image_input):
    myconfig = r"--psm 6 --oem 3"

    img = cv2.imread(image_input)

    ret, thresh = cv2.threshold(img, 230, 255, cv2.THRESH_BINARY)
    # cv2.imshow("test", thresh)
    # cv2.waitKey(0)
    thresh = cv2.cvtColor(thresh, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(thresh, 0, 255, cv2.THRESH_BINARY)

    dataHSV = pytesseract.image_to_data(
        thresh, config=myconfig, output_type=Output.DICT)

    texts = dataHSV['text']
    newTexts = []

    amount_boxes = len(texts)
    for i in range(amount_boxes):
        if(texts[i] != ''):
            newTexts.append(texts[i])

    arrays = []
    for text in newTexts:
        arrays.append(text)

    headers = []
    for el in arrays:
        if el in ["POS", 'DRIVER', "TIME", "GAP", "BEST"]:
            if el == "BEST":
                headers.append("BEST LAP")
            else:
                headers.append(el)
    arrays.index("LAP")
    del arrays[0:arrays.index("LAP")]
    arrays.pop(0)
    return arrays


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


def make_driver_object(list):
    obj = {}
    for i in range(len(list)):
        driver = list[i]
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


result_drivers = None
if result_input:
    result_arrays = read_and_process(result_input)
    result_drivers = create_drivers(
        get_driver_info(result_arrays, False), False)

quali_drivers = None
if quali_input:
    quali_arrays = read_and_process(quali_input)
    quali_drivers = create_drivers(get_driver_info(quali_arrays, True), True)


combine_drivers(result_drivers, quali_drivers)

output(result_drivers, quali_drivers, outputFormat, outputFile)
