import pytesseract
from pytesseract import Output
import PIL.Image
import cv2


myconfig = r"--psm 11 --oem 3"

img = cv2.imread("../images/direct.png")

ret, thresh = cv2.threshold(img, 190, 255, cv2.THRESH_BINARY)

gray = cv2.cvtColor(thresh, cv2.COLOR_BGR2GRAY)
height, width, _ = img.shape

dataHSV = pytesseract.image_to_data(
    thresh, config=myconfig, output_type=Output.DICT)


# print(dataHSV['text'])
newText = {}


amount_boxes = len(dataHSV['text'])
for i in range(amount_boxes):
    if(dataHSV['text'][i] != ''):
        newText[i] = dataHSV['text'][i]

print(list(newText.values()))
for i in range(amount_boxes):
    if float(dataHSV['conf'][i]) > 5:
        (x, y, width, height) = (
            dataHSV['left'][i], dataHSV['top'][i], dataHSV['width'][i], dataHSV['height'][i])
        img = cv2.rectangle(
            img, (x, y), (x+width, y+height), (0, 255, 0), 1)

# boxes = pytesseract.image_to_boxes(img, config=myconfig)
# for box in boxes.splitlines():
#     box = box.split(" ")
#     img = cv2.rectangle(
#         img, (int(box[1]), height - int(box[2])), (int(box[3]), height - int(box[4])), (0, 255, 0), 2)
# cv2.imshow("img", img)
# cv2.imshow("gray", gray)
# cv2.imshow("thresh", thresh)
# cv2.waitKey(0)
# print(boxes)

# text = pytesseract.image_to_string(
#     PIL.Image.open("../images/Race4F.png"), config=myconfig)
# print(text)
