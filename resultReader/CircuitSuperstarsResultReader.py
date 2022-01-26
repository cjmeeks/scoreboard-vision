from email import header
from email.mime import image
from PIL import Image
import sys

import pyocr
import pyocr.builders
import cv2
import re
import PySimpleGUI as sg
import json

sg.theme('Material1')
layout = [
    [sg.Text('Image To Read'), sg.FileBrowse()],
    [sg.Text('Output file'), sg.FileBrowse()],
    [sg.Button('Ok'), sg.Button('Cancel')]
]

window = sg.Window('CSUP Result Reader', layout)

imageInput = ''
outputFile = ''
while True:
    event, values = window.read()
    if event == 'Ok':  # if user closes window or clicks cancel
        imageInput = values['Browse']
        outputFile = values['Browse0']
        window.close()
        break
    if event == sg.WIN_CLOSED or event == 'Cancel':
        window.close()


image = imageInput


class ImageProcessor:
    tool = {}
    lang = 'eng'

    def __init__(self):
        tools = pyocr.get_available_tools()
        if len(tools) == 0:
            print("No OCR tool found")
            sys.exit(1)
        # The tools are returned in the recommended order of usage
        self.tool = tools[0]
        print("Will use tool '%s'" % (self.tool.get_name()))
        # Ex: Will use tool 'libtesseract'

        langs = self.tool.get_available_languages()
        print("Available languages: %s" % ", ".join(langs))
        self.lang = langs[0]
        print("Will use lang '%s'" % (self.lang))

    def process_image(self, image):
        return self.tool.image_to_string(
            image,
            lang="eng",
            builder=pyocr.builders.LineBoxBuilder()
        )

    def get_content(self, item):
        return re.sub('\,', '.', item.content)

    def process_results(self, results):
        items = list(map(self.get_content, results))
        header_indexes = {}
        content = {}

        for index, item in enumerate(items):
            match = re.search("DRIVER|GAP|TIME|BEST LAP|CAR", item)
            if match:
                print(match.group(0))
                header_indexes[match.group(0)] = index
        print(header_indexes)

        headers = list(header_indexes.keys())
        indexes = list(header_indexes.values())
        for index, header_index in enumerate(indexes):
            print(index)
            if index >= len(indexes) - 1:
                content[headers[index]] = items[header_index+1:len(items) - 1]
            else:
                content[headers[index]] = items[header_index +
                                                1:indexes[index + 1]]
        return content


img = cv2.imread(image)

ret, thresh = cv2.threshold(img, 200, 255, cv2.THRESH_BINARY)
thresh = cv2.cvtColor(thresh, cv2.COLOR_BGR2GRAY)
ret, thresh = cv2.threshold(thresh, 0, 255, cv2.THRESH_BINARY)

# cv2.imshow("img", thresh)
# cv2.waitKey(0)

img = Image.fromarray(thresh)

image_processor = ImageProcessor()

content = image_processor.process_image(img)
content = image_processor.process_results(content)

jsonString = json.dumps(content, indent=4, sort_keys=False)
jsonFile = open(outputFile, "w")
jsonFile.write(jsonString)
jsonFile.close()

sg.PopupAutoClose('Done! Content exported to file: ' + outputFile)
