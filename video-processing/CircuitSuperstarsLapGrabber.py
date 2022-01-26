from concurrent.futures.process import _chain_from_iterable_of_lists
import json
import pytesseract
from pytesseract import Output
import cv2
import time
import numpy as np
import re
from collections import Counter
from datetime import datetime
import concurrent.futures
import itertools
import PySimpleGUI as sg
import json
import multiprocessing as mp


sg.theme('Material1')
layout = [
    [sg.Text('Video To Read'), sg.FileBrowse()],
    [sg.Text('Output file'), sg.FileBrowse()],
    [sg.Button('Ok'), sg.Button('Cancel')]
]

window = sg.Window('CSUP Result Reader', layout)

video = ''
outputFile = ''
while True:
    event, values = window.read()
    if event == 'Ok':  # if user closes window or clicks cancel
        video = values['Browse']
        outputFile = values['Browse0']
        window.close()
        break
    if event == sg.WIN_CLOSED or event == 'Cancel':
        window.close()

image_path = video
# image_path = 'D:\Renders\ICSTC LAPS.mov'
# image_path = 'D:\Renders\ICSTC LAPSmp4.mp4'
# image_path = 'F:\youtube\laps.mov'
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
    # cv2.imshow("Frame", thresh)
    # cv2.waitKey(1)
    count += 1

arrays = np.array_split(frames_to_process, 16)
print(arrays)

raw_results = []


def process_frames(arr):
    results = []
    fvs2 = cv2.VideoCapture(image_path)
    for index, frame_index in enumerate(arr):
        print("processing: " + str(index) +
              " of " + str(len(arr)))
        fvs2.set(1, frame_index)
        ret, frame = fvs2.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            frame = np.dstack([frame, frame, frame])
            ret, thresh = cv2.threshold(frame, 190, 255, cv2.THRESH_BINARY)

            data = pytesseract.image_to_data(
                thresh, config=myconfig, output_type=Output.DICT)

            for i in range(len(data['text'])):
                match = re.search("\d{1}:\d+(.|,)\d+", data['text'][i])
                # raw_results.append(data['text'][i])
                if(match):
                    print(data['text'][i])
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


# new_results = process_frames(frames_to_process)
new_results = []
sg.PopupNonBlocking('Processing Frames',
                    'Processing Frames. This WILL take some time. Another window will appear when done')

with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executor:
    new_results = list(executor.map(process_frames, arrays))

new_results = list(itertools.chain.from_iterable(new_results))

new_laps = get_laps_from_data(new_results)
counts = dict(Counter(get_laps_from_data(new_laps)))
print(counts)

new_laps = dict()
count_keys = list(counts.keys())
for i in range(len(counts)):
    new_laps[i] = count_keys[i]


jsonString = json.dumps(new_laps, indent=4, sort_keys=False)
jsonFile = open(
    outputFile, "w")
jsonFile.write(jsonString)
jsonFile.close()

jsonString = json.dumps(new_results, indent=4, sort_keys=False)
jsonFile = open(
    outputFile + "-raw.json", "w")
jsonFile.write(jsonString)
jsonFile.close()


cv2.destroyAllWindows()
fvs.release()

sg.PopupAutoClose('Done! Content exported to file: ' + outputFile)
