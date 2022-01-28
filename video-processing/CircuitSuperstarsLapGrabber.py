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

# image_path = video
# image_path = 'D:\Renders\ICSTC LAPS.mov'
# image_path = 'D:\Renders\ICSTC LAPSmp4.mp4'
# image_path = 'F:\youtube\laps.mov'
# outputFile = 'F:\youtube\\x.json'
# image_path = 'D:\Raw Videos\Circuit SuperStars\Jan21\ICS\Round 2\TC\RD2TCLaps.mov'
# image_path = 'D:\Raw Videos\Circuit SuperStars\Jan21\ICS\Round 2\AS\laps.mov'


fvs = cv2.VideoCapture(image_path)
time.sleep(0.1)
myconfig = r"--psm 7 --oem 3"
count = 0
frameCount = 0
toggle = False
frames_to_process = []
process_last = False


totalFrames = int(fvs.get(cv2.CAP_PROP_FRAME_COUNT))
while True:
    print(str(frameCount) + ":" + str(totalFrames))
    if process_last:
        break

    if not toggle:
        toggle = not toggle
        frameCount += 60
        if frameCount >= totalFrames:
            frameCount -= 60
            print(frameCount)
            process_last = True
        fvs.set(1, frameCount)
        count = 0
        continue
    if frameCount >= totalFrames:
        frameCount -= 60
        print(frameCount)
        fvs.set(1, frameCount)
    ret, frame = fvs.read()
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    frame = np.dstack([frame, frame, frame])
    ret, thresh = cv2.threshold(frame, 190, 255, cv2.THRESH_BINARY)
    frameCount += 1

    sg.one_line_progress_meter('Reading In Frames', frameCount, totalFrames)

    if toggle:
        if count >= 10:
            toggle = not toggle
        frames_to_process.append(frameCount)
    count += 1


arrays = np.array_split(frames_to_process, threads)
raw_results = []


def process_frames(arr):
    results = []
    fvs2 = cv2.VideoCapture(image_path)
    for index, frame_index in enumerate(arr):
        print("processing: " + str(index) +
              " of " + str(len(arr)))
        fvs2.set(1, frame_index)
        ret, frame = fvs2.read()
        frame = frame[160:200, 1770:1880]
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            ret, thresh = cv2.threshold(frame, 190, 255, cv2.THRESH_BINARY)
            cv2.imshow("cropped", thresh)
            cv2.waitKey(1)

            data = pytesseract.image_to_data(
                thresh, config=myconfig, output_type=Output.DICT)

            print(data['text'])
            for i in range(len(data['text'])):
                match = re.search("\d{1}:\d+(.|,)\d+", data['text'][i])
                # raw_results.append(data['text'][i])
                if(match):
                    results.append(data['text'][i])
    fvs2.release()
    return results


def get_laps_from_data(laps):
    new_laps = []
    for i in range(len(laps) - 2):
        # checking the conditions
        if laps[i] == laps[i + 1] and laps[i + 1] == laps[i + 2]:

            # printing the element as the
            # conditions are satisfied
            new_laps.append(laps[i])
    return new_laps


def clean_time(item):
    return re.sub('\,', '.', item)


# new_results = process_frames(frames_to_process)
new_results = []
sg.PopupNonBlocking('Processing Frames',
                    'Processing Frames. This WILL take some time. Another window will appear when done')

with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
    new_results = list(executor.map(process_frames, arrays))

new_results = list(itertools.chain.from_iterable(new_results))

new_laps = get_laps_from_data(new_results)
counts = dict(Counter(get_laps_from_data(new_laps)))

new_laps = []
count_keys = list(counts.keys())
for i in range(len(counts)):
    new_laps.append({
        "lap": i+1,
        "time": clean_time(count_keys[i])
    })
    # new_laps[i+1] = clean_time(count_keys[i])


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
        print(data)
        laps = []
        for i in range(len(data)):
            laps.append(data[i].values())
        writer.writerow(headers)
        writer.writerows(laps)
    return data


output(new_laps, output_format, outputFile)

cv2.destroyAllWindows()
fvs.release()

sg.PopupAutoClose('Done! Content exported to file: ' + outputFile)
