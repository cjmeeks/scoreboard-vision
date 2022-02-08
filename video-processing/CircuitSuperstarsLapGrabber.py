from concurrent.futures.process import _chain_from_iterable_of_lists
import json
import pytesseract
from pytesseract import Output
import cv2
import time
import numpy as np
import re
from collections import Counter
import concurrent.futures
import itertools
import PySimpleGUI as sg
import json
import os
import csv
import sys
import Lap
from Processor import Processor

threads = 8

os.environ["PATH"] += os.pathsep + "C:\Program Files\Tesseract-OCR"

sg.theme('Material1')
layout = [
    [sg.Text('Video To Read'), sg.FileBrowse()],
    [sg.Text('Output file'), sg.FileBrowse()],
    [sg.Text('Choose output format')],
    [sg.Combo(['csv', 'json'], default_value='json', key='output_format')],
    [sg.Button('Ok'), sg.Button('Cancel')]
]

window = sg.Window('CSUP Result Reader', layout)

image_path = ''
outputFile = ''
output_format = ''
while True:
    event, values = window.read()
    if event == 'Ok':  # if user closes window or clicks cancel
        image_path = values['Browse']
        outputFile = values['Browse0']
        output_format = values['output_format']
        window.close()
        break
    if event == sg.WIN_CLOSED or event == 'Cancel':
        window.close()
        sys.exit(1)


def output(data, format, outputFile):
    if outputFile == '':
        outputFile = 'output.txt'
    if format == 'json':
        jsonString = json.dumps(data, indent=4, sort_keys=False)
        jsonFile = open(outputFile, "w")
        jsonFile.write(jsonString)
        jsonFile.close()
    if format == 'csv':
        f = open(outputFile, 'w', newline='')
        writer = csv.writer(f)
        headers = ["Laps", "Time"]
        laps = []
        for i in range(len(data)):
            laps.append(data[i].values())
        writer.writerow(headers)
        writer.writerows(laps)
    return data


processor = Processor(threads, image_path)
processor.read_frames()
output_laps = processor.process_video()
s = [127, 591, 923]

output_fuel = processor.process_frames_fuel(list(output_laps.get_lap_frames()))
output_laps = list(output_laps.toJson())
laps = []
for i in range(len(output_laps)):
    lapss = output_laps
    lap = lapss[i]
    lap['fuel'] = output_fuel[i]
    laps.append(lap)


output(laps, output_format, outputFile)

cv2.destroyAllWindows()
processor.video.release()

sg.PopupAutoClose('Done! Content exported to file: ' + outputFile)
