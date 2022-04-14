import cv2
import PySimpleGUI as sg
import numpy as np
import pytesseract
from pytesseract import Output
import Lap
import re
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


class Processor:
    def __init__(self, threads, video_path):
        self.threads = threads
        self.video_path = video_path
        self.config = r"--psm 6 --oem 3"
        self.count = 0
        self.frameCount = 0
        self.toggle = False
        self.frames_to_process = []
        self.process_last = False
        self.video = cv2.VideoCapture(video_path)

    def read_frames(self):
        totalFrames = int(self.video.get(cv2.CAP_PROP_FRAME_COUNT))
        while True:
            print(str(self.frameCount) + ":" + str(totalFrames))
            if self.process_last:
                break

            if not self.toggle:
                self.toggle = not self.toggle
                self.frameCount += 60
                if self.frameCount >= totalFrames:
                    self.frameCount -= 60
                    print(self.frameCount)
                    self.process_last = True
                self.video.set(1, self.frameCount)
                self.count = 0
                continue
            if self.frameCount >= totalFrames:
                self.frameCount -= 60
                print(self.frameCount)
                self.video.set(1, self.frameCount)
            ret, frame = self.video.read()
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            frame = np.dstack([frame, frame, frame])
            ret, thresh = cv2.threshold(frame, 190, 255, cv2.THRESH_BINARY)
            self.frameCount += 1

            sg.one_line_progress_meter(
                'Reading In Frames', self.frameCount, totalFrames)

            if self.toggle:
                if self.count >= 5:
                    self.toggle = not self.toggle
                self.frames_to_process.append(self.frameCount)
            self.count += 1

    def process_frames(self, arr):
        results = []
        fvs2 = cv2.VideoCapture(self.video_path)
        for index, frame_index in enumerate(arr):
            print("processing: " + str(index) +
                  " of " + str(len(arr)))
            fvs2.set(1, frame_index)
            ret, frame = fvs2.read()
            frame = frame[160:200, 1750:1880]
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                ret, thresh = cv2.threshold(frame, 190, 255, cv2.THRESH_BINARY)

                data = pytesseract.image_to_data(
                    thresh, config=self.config, output_type=Output.DICT)

                for i in range(len(data['text'])):
                    match = re.search("\d{1}:\d+(.|,)\d+", data['text'][i])
                    if(match):
                        results.append(Lap.Lap(frame_index, data['text'][i]))
        fvs2.release()
        return results

    def process_video(self):
        arrays = np.array_split(self.frames_to_process, self.threads)

        new_results = []
        sg.PopupNonBlocking('Processing Frames',
                            'Processing Frames. This WILL take some time. Another window will appear when done')

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.threads) as executor:
            new_results = list(executor.map(self.process_frames, arrays))

        new_results = list(itertools.chain.from_iterable(new_results))
        new_laps = self.get_laps_from_data(Lap.Laps(new_results))
        return new_laps.to_laps_object()

    def get_fuel_from_frame(self, frame):
        frame = frame[1020:1040, 160:190]

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        ret, thresh = cv2.threshold(frame, 230, 240, cv2.THRESH_BINARY)
        kernel = np.ones((1, 1), np.uint8)
        erosion = cv2.erode(thresh, kernel, iterations=1)
        # cv2.imshow("cropped", erosion)
        # cv2.waitKey(0)

        data = pytesseract.image_to_data(
            erosion, config=r"--psm 6 --oem 3", output_type=Output.DICT)
        print(data['text'])
        return data['text'][len(data['text']) - 1]

    def get_tire_from_frame(self, frame):
        frame = frame[1020:1040, 250:280]

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        ret, thresh = cv2.threshold(frame, 230, 240, cv2.THRESH_BINARY)
        kernel = np.ones((1, 1), np.uint8)
        erosion = cv2.erode(thresh, kernel, iterations=1)
        cv2.imshow("cropped", erosion)
        cv2.waitKey(0)

        data = pytesseract.image_to_data(
            erosion, config=r"--psm 6 --oem 3", output_type=Output.DICT)
        print(data['text'])
        return data['text'][len(data['text']) - 1]

    def get_laps_from_data(self, laps):
        new_laps = []
        i = 0
        while i < len(laps.laps) - 2:
            if laps.laps[i].lap_time == laps.laps[i + 1].lap_time and laps.laps[i + 1].lap_time == laps.laps[i + 2].lap_time:
                new_laps.append(laps.laps[i])
            i += 3

        new_laps = Lap.Laps(new_laps)
        laps = dict(new_laps.to_laps_object())
        keys = list(laps.keys())
        ls = []
        for i in range(len(keys)):
            key = keys[i]
            fvs3 = cv2.VideoCapture(self.video_path)
            fvs3.set(1, int(laps[key]['frame']))

            ret, frame = fvs3.read()
            l = Lap.Lap(laps[key]['frame'], key)
            l.fuel = self.get_fuel_from_frame(frame)
            l.tire = self.get_tire_from_frame(frame)
            l.lap = i + 1
            ls.append(l)

        return Lap.Laps(ls)

    def clean_time(self, item):
        return re.sub('\,', '.', item)

    def clean_fuel(self, item):
        return re.sub('[^0-9]', '', item)
