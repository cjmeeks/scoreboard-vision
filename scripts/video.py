"""Detect text in a video stored on GCS."""
from google.cloud import videointelligence
import json
import sys
args = sys.argv[1:]

fuel_uri = args[0]
tirewear_uri = args[1]
laptime_uri = args[2]
dataOutputFilePrefix = args[3]


video_client = videointelligence.VideoIntelligenceServiceClient()
features = [videointelligence.Feature.TEXT_DETECTION]

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

def filterLaptimes(annotations):
    laptimes = []
    for item in annotations:
        if(item['endTime'] - item['startTime'] > 1 ): 
            if not "LAP" in item["text"]:
                laptimes.append(item)
    laptimes.sort(key=lambda x: x["startTime"], reverse=False)
    return laptimes

    # Show the result for the first frame in this segment.

# fuelAnnotations = getDataFromVideo(fuel_uri)
# tireAnnotations = getDataFromVideo(tirewear_uri)

lapTimes = getDataFromVideo('gs://invitationalracerecap/blackandwhitelaps.mov')

# lapTimes = getDataFromVideo(laptime_uri)
# fuelAnnotations.sort(key=lambda x: x["startTime"], reverse=False)
# tireAnnotations.sort(key=lambda x: x["startTime"], reverse=False)

finalAnnotations = {
    'lapTimes': filterLaptimes(lapTimes),
    # 'fuel': fuelAnnotations,
    # 'tire': tireAnnotations,
}


jsonString = json.dumps(finalAnnotations)
jsonFile = open(dataOutputFilePrefix + "-data.json", "w")
jsonFile.write(jsonString)
jsonFile.close()