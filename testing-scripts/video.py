"""Detect text in a video stored on GCS."""
import json
import sys
import pytesseract
from pytesseract import Output
import PIL.Image
import cv2
from threading import Thread
from queue import Queue
import time


class FileVideoStream:
    def __init__(self, path, queueSize=128):
        # initialize the file video stream along with the boolean
        # used to indicate if the thread should be stopped or not
        self.stream = cv2.VideoCapture(path)
        self.stopped = False
        # initialize the queue used to store frames read from
        # the video file
        self.Q = Queue(maxsize=queueSize)

    def start(self):
        # start a thread to read frames from the file video stream
        t = Thread(target=self.update, args=())
        t.daemon = True
        t.start()
        return self

    def update(self):
        # keep looping infinitely
        while True:
            # if the thread indicator variable is set, stop the
            # thread
            if self.stopped:
                return
            # otherwise, ensure the queue has room in it
            if not self.Q.full():
                # read the next frame from the file
                (grabbed, frame) = self.stream.read()
                # if the `grabbed` boolean is `False`, then we have
                # reached the end of the video file
                if not grabbed:
                    self.stop()
                    return
                # add the frame to the queue
                self.Q.put(frame)

    def read(self):
        # return next frame in the queue
        return self.Q.get()

    def more(self):
        # return True if there are still frames in the queue
        return self.Q.qsize() > 0

    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True


fvs = FileVideoStream('F:\Youtube/laps-test.mov').start()
time.sleep(1.0)

while fvs.more():
    # grab the frame from the threaded video file stream, resize
    # it, and convert it to grayscale (while still retaining 3
    # channels)
    frame = fvs.read()
    frame = imutils.resize(frame, width=450)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    frame = np.dstack([frame, frame, frame])
    # display the size of the queue on the frame
    cv2.putText(frame, "Queue Size: {}".format(fvs.Q.qsize()),
                (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    # show the frame and update the FPS counter
    cv2.imshow("Frame", frame)
    cv2.waitKey(1)
    fps.update()

testVideo = 'F:\Youtube/laps-test.mov'
video = cv2.VideoCapture(testVideo)
myconfig = r"--psm 6 --oem 3"

while True:
    ret, frame = video.read()

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    ret2, thresh = cv2.threshold(frame, 190, 255, cv2.THRESH_BINARY)

    data = pytesseract.image_to_data(
        thresh, config=myconfig, output_type=Output.DICT)
    isGood = False
    amount_boxes = len(data['text'])
    for i in range(amount_boxes):
        if float(data['conf'][i]) > 5:
            isGood = True
            print(data['text'][i])
    if ret:
        cv2.imshow('test', thresh)
    else:
        break
    k = cv2.waitKey(10)
    if k == ord('q'):
        break

cv2.destroyAllWindows()


args = sys.argv[1:]

fuel_uri = args[0]
# tirewear_uri = args[1]
# laptime_uri = args[2]
# dataOutputFilePrefix = args[3]


# video_client = videointelligence.VideoIntelligenceServiceClient()
# features = [videointelligence.Feature.TEXT_DETECTION]

# overall method - getDataFromVideo
# getDataFromAnnotations

def getDataFromAnnotations(text_annotations):
    annotations = []
    for text_annotation in text_annotations:
        text = "\nText: {}".format(text_annotation.text)

        # Get the first text segment
        text_segment = text_annotation.segments[0]
        start_time = text_segment.segment.start_time_offset
        end_time = text_segment.segment.end_time_offset
        vertices = []
        frame = text_segment.frames[0]
        for vertex in frame.rotated_bounding_box.vertices:
            vertices.append({'x': vertex.x, 'y': vertex.y})
        annotation = {
            'text': text_annotation.text,
            'startTime': start_time.seconds + start_time.microseconds * 1e-6,
            'endTime': end_time.seconds + end_time.microseconds * 1e-6,
        }
        annotations.append(annotation)
    return annotations


def getDataFromVideo(uri):
    operation = video_client.annotate_video(
        request={"features": features, "input_uri": uri}
    )

    print("\nProcessing video for text detection.")
    result = operation.result(timeout=600)

    # The first result is retrieved because a single video was processed.
    annotation_result = result.annotation_results[0]
    return getDataFromAnnotations(annotation_result.text_annotations)

# def filterLaptimes(annotations):
#     laptimes = []
#     for item in annotations:
#         if(item['endTime'] - item['startTime'] > 1 ):
#             if not "LAP" in item["text"]:
#                 laptimes.append(item)
#     laptimes.sort(key=lambda x: x["startTime"], reverse=False)
#     return laptimes

    # Show the result for the first frame in this segment.

# fuelAnnotations = getDataFromVideo(fuel_uri)
# tireAnnotations = getDataFromVideo(tirewear_uri)

# lapTimes = getDataFromVideo('gs://invitationalracerecap/blackandwhitelaps.mov')

# lapTimes = getDataFromVideo(laptime_uri)
# fuelAnnotations.sort(key=lambda x: x["startTime"], reverse=False)
# tireAnnotations.sort(key=lambda x: x["startTime"], reverse=False)

# finalAnnotations = {
#     'lapTimes': filterLaptimes(lapTimes),
#     # 'fuel': fuelAnnotations,
#     # 'tire': tireAnnotations,
# }


# jsonString = json.dumps(finalAnnotations)
# jsonFile = open(dataOutputFilePrefix + "-data.json", "w")
# jsonFile.write(jsonString)
# jsonFile.close()
