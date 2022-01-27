import re
import json
import pytesseract
from pytesseract import Output
import cv2
from datetime import datetime
import PySimpleGUI as sg
import os
import csv

os.environ["PATH"] += os.pathsep + "C:\Program Files\Tesseract-OCR"
# window
sg.theme('Material1')

layout = [
    [sg.Text('Image To Read'), sg.FileBrowse()],
    [sg.Text('Output file'), sg.FileBrowse()],
    [sg.Text('Choose output format')],
    [sg.Combo(['csv', 'json'], default_value='json', key='output_format')],
    [sg.Button('Ok'), sg.Button('Cancel')]
]

window = sg.Window('CSUP Result Reader', layout)

imageInput = ''
outputFile = ''
outputFormat = ''
while True:
    event, values = window.read()
    if event == 'Ok':  # if user closes window or clicks cancel
        imageInput = values['Browse']
        outputFile = values['Browse0']
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


def get_driver_info(infos):
    driverInfo = []
    count = 0
    index = 0
    while index < len(infos):
        match = re.search("\d{1}:\d{2}.\d{3}", infos[index])
        if(match):
            count += 1
            if (count == 3):
                count = 0
                info = infos[0:index + 1]
                driverInfo.append(info)
                del infos[0:index + 1]
                index = 0
        index += 1
    return driverInfo


def clean_time(item):
    return re.sub('\,', '.', item)


def create_drivers(drivers):
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
        time = statsArray[0]
        gap = statsArray[1]
        lap = statsArray[2]
        newDriver = {
            "position": position,
            "driver": re.sub('[^a-zA-Z0-9\\|\\s]', '', name),
            "time": clean_time(time),
            "gap": clean_time(gap),
            "lap": clean_time(lap),
        }
        position += 1
        newDrivers.append(newDriver)
    return newDrivers


def output(data, format):
    if format == 'json':
        jsonString = json.dumps(data, indent=4, sort_keys=False)
        jsonFile = open(outputFile, "w")
        jsonFile.write(jsonString)
        jsonFile.close()
    if format == 'csv':
        f = open(outputFile, 'w', newline='')
        writer = csv.writer(f)
        headers = dict(data[0]).keys()
        drivers = []
        for i in range(len(data)):
            drivers.append(dict(data[i]).values())
        writer.writerow(headers)
        writer.writerows(drivers)
    return data


def read_and_process():
    myconfig = r"--psm 6 --oem 3"

    img = cv2.imread(imageInput)

    ret, thresh = cv2.threshold(img, 210, 255, cv2.THRESH_BINARY)
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


arrays = read_and_process()
output(create_drivers(get_driver_info(arrays)), outputFormat)
