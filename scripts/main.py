import re
import json
import pytesseract
from pytesseract import Output
import PIL.Image
import cv2


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
    print(infos)
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
        print(driver)
        nameArray = driver[0:indexOfStats]
        statsArray = driver[indexOfStats:len(driver)]
        name = " ".join(nameArray)
        time = statsArray[0]
        gap = statsArray[1]
        lap = statsArray[2]
        newDriver = {
            "position": position,
            "name": re.sub('\d+(\s|\.)', '', name),
            "time": time,
            "gap": gap,
            "lap": lap,

        }
        position += 1
        newDrivers.append(newDriver)
    return newDrivers


myconfig = r"--psm 6 --oem 3"

img = cv2.imread("../images/ICSTCF.png")

ret, thresh = cv2.threshold(img, 190, 255, cv2.THRESH_BINARY)

gray = cv2.cvtColor(thresh, cv2.COLOR_BGR2GRAY)
height, width, _ = img.shape

dataHSV = pytesseract.image_to_data(
    thresh, config=myconfig, output_type=Output.DICT)

texts = dataHSV['text']

newTexts = []


amount_boxes = len(texts)
for i in range(amount_boxes):
    if(texts[i] != ''):
        newTexts.append(texts[i])
# # Instantiates a client
# client = vision.ImageAnnotatorClient()

# # The name of the image file to annotate
# file_name = os.path.abspath('tira.png')

# # Loads the image into memory
# with io.open(file_name, 'rb') as image_file:
#     content = image_file.read()

# image = vision.Image(content=content)

# # Performs label detection on the image file
# response = client.text_detection(image=image)
# texts = response.text_annotations

arrays = []

for text in newTexts:
    arrays.append(text)
    # print('\n"{}"'.format(text.description))

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

jsonString = json.dumps(create_drivers(
    get_driver_info(arrays)), indent=4, sort_keys=False)
jsonFile = open("x.json", "w")
jsonFile.write(jsonString)
jsonFile.close()
print(arrays)
print(json.dumps(create_drivers(get_driver_info(arrays)), indent=4, sort_keys=False))
