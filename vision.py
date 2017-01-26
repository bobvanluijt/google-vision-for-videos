APIKEY       = ''     # Set Google Vision API KEY
OUTPUT_VIDEO = '.avi' # Output as AVI file
INPUT_VIDEO  = ''     # Input video (mov, avi, mp4, etc)

##
# Process video
##
import cv2
import io
import os
import requests
import base64
import json
import sys

# Function to make output text more readable
def makeLikelyText(i):
    if i == "VERY_LIKELY":
        return "absolutly"
    elif i == "LIKELY":
        return "probably"
    elif i == "POSSIBLE":
        return "maybe"
    elif i == "UNLIKELY":
        return "probably not"
    else:
        return "not"

# Load the input video
vidcap = cv2.VideoCapture(INPUT_VIDEO)

# Set output codec
fourcc = cv2.cv.CV_FOURCC('M', 'J', 'P', 'G')

# Create the output video
outputvid = cv2.VideoWriter(OUTPUT_VIDEO, fourcc, int(vidcap.get(cv2.cv.CV_CAP_PROP_FPS)), (int(vidcap.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH)), int(vidcap.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT))), True)

# Count the number of frames
count = 0

# Load succes?
success = True

# Run through all frames
while success:
    success, image = vidcap.read()

    # Print current status
    print('Process frame: ', count, ' of ', int(vidcap.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT)))

    # Save image to temp jpg file
    cv2.imwrite("__tmp.jpg", image)

    # Open the jpg file for base64 encoding
    with open("__tmp.jpg", "rb") as temp_image_file:
        encoded_image = base64.b64encode(temp_image_file.read())

    # Remove the file, it is not needed anymore
    os.remove("__tmp.jpg")

    # Do the API callable for faces when even
    if (count % 2 == 0):
        RESTdata = '{ "requests": [{"image":{"content": "' + encoded_image + '" },"features": [{"type":"FACE_DETECTION"}]}] }'
        RESTresponse = requests.post("https://vision.googleapis.com/v1/images:annotate?key=" + APIKEY, data=RESTdata)
        RESTresultFaces = RESTresponse.json()

    # Do the API callable for labels
    if (count % 2 == 0):
        RESTdata = '{ "requests": [{"image":{"content": "' + encoded_image + '" },"features": [{"type":"LABEL_DETECTION"}]}] }'
        RESTresponse = requests.post("https://vision.googleapis.com/v1/images:annotate?key=" + APIKEY, data=RESTdata)
        RESTresultLabels = RESTresponse.json()

    # Do the API callable for text
    if (count % 2 == 0):
        RESTdata = '{ "requests": [{"image":{"content": "' + encoded_image + '" },"features": [{"type":"TEXT_DETECTION"}]}] }'
        RESTresponse = requests.post("https://vision.googleapis.com/v1/images:annotate?key=" + APIKEY, data=RESTdata)
        RESTresultText = RESTresponse.json()

    # process the text
    try:
        if 'textAnnotations' in RESTresultText['responses'][0]:
            for text in RESTresultText['responses'][0]['textAnnotations']:
                # Draw text outline - line 1
                cv2.line(image, (   text['boundingPoly']['vertices'][0]['x'],
                                    text['boundingPoly']['vertices'][0]['y']),
                                (   text['boundingPoly']['vertices'][1]['x'],
                                    text['boundingPoly']['vertices'][1]['y']),
                                    (255, 0, 255))
                
                # Draw text outline - line 2
                cv2.line(image, (   text['boundingPoly']['vertices'][1]['x'],
                                    text['boundingPoly']['vertices'][1]['y']),
                                (   text['boundingPoly']['vertices'][2]['x'],
                                    text['boundingPoly']['vertices'][2]['y']),
                                    (255, 0, 255))
                
                # Draw text outline - line 3
                cv2.line(image, (   text['boundingPoly']['vertices'][2]['x'],
                                    text['boundingPoly']['vertices'][2]['y']),
                                (   text['boundingPoly']['vertices'][3]['x'],
                                    text['boundingPoly']['vertices'][3]['y']),
                                    (255, 0, 255))

                # Draw text outline - line 4
                cv2.line(image, (   text['boundingPoly']['vertices'][3]['x'],
                                    text['boundingPoly']['vertices'][3]['y']),
                                (   text['boundingPoly']['vertices'][0]['x'],
                                    text['boundingPoly']['vertices'][0]['y']),
                                    (255, 0, 255))

                # Add desc text
                cv2.putText(image, text['description'], (text['boundingPoly']['vertices'][0]['x'], text['boundingPoly']['vertices'][0]['y']), cv2.FONT_HERSHEY_PLAIN, 1.5, (255,0,255), 2)
    except:
        pass # pass if something misses in this frame

    # Process the labels
    try:
        if 'labelAnnotations' in RESTresultLabels['responses'][0]:
            labels = list()
            for label in RESTresultLabels['responses'][0]['labelAnnotations']:
                label_final = label['description'] + ' (' + str(int((label['score']*100))) + '%) - '
                labels.append(label_final[:-2])
        
            # Sort 
            labels.sort()

            cv2.putText(image, ' '.join(labels), (4, 42), cv2.FONT_HERSHEY_PLAIN, 2, (0,0,255), 2)
    except:
        pass # pass if something misses in this frame

    # Loop through all the found faces
    try:
        if 'faceAnnotations' in RESTresultFaces['responses'][0]:
            for singleFace in RESTresultFaces['responses'][0]['faceAnnotations']:
                
                # Draw face outline - line 1
                cv2.line(image, (   singleFace['boundingPoly']['vertices'][0]['x'],
                                    singleFace['boundingPoly']['vertices'][0]['y']),
                                (   singleFace['boundingPoly']['vertices'][1]['x'],
                                    singleFace['boundingPoly']['vertices'][1]['y']),
                                    (0, 255, 0))
                
                # Draw face outline - line 2
                cv2.line(image, (   singleFace['boundingPoly']['vertices'][1]['x'],
                                    singleFace['boundingPoly']['vertices'][1]['y']),
                                (   singleFace['boundingPoly']['vertices'][2]['x'],
                                    singleFace['boundingPoly']['vertices'][2]['y']),
                                    (0, 255, 0))
                
                # Draw face outline - line 3
                cv2.line(image, (   singleFace['boundingPoly']['vertices'][2]['x'],
                                    singleFace['boundingPoly']['vertices'][2]['y']),
                                (   singleFace['boundingPoly']['vertices'][3]['x'],
                                    singleFace['boundingPoly']['vertices'][3]['y']),
                                    (0, 255, 0))

                # Draw face outline - line 4
                cv2.line(image, (   singleFace['boundingPoly']['vertices'][3]['x'],
                                    singleFace['boundingPoly']['vertices'][3]['y']),
                                (   singleFace['boundingPoly']['vertices'][0]['x'],
                                    singleFace['boundingPoly']['vertices'][0]['y']),
                                    (0, 255, 0))

                # Add head text
                cv2.putText(image, makeLikelyText(singleFace['joyLikelihood']) + " joyful", (singleFace['boundingPoly']['vertices'][0]['x'], singleFace['boundingPoly']['vertices'][0]['y']), cv2.FONT_HERSHEY_PLAIN, 1.5, (0,255,0), 2)
                cv2.putText(image, makeLikelyText(singleFace['angerLikelihood']) + " angry", (singleFace['boundingPoly']['vertices'][0]['x'], singleFace['boundingPoly']['vertices'][0]['y']-25), cv2.FONT_HERSHEY_PLAIN, 1.5, (0,255,0), 2)
                cv2.putText(image, makeLikelyText(singleFace['surpriseLikelihood']) + " surprised", (singleFace['boundingPoly']['vertices'][0]['x'], singleFace['boundingPoly']['vertices'][0]['y']-50), cv2.FONT_HERSHEY_PLAIN, 1.5, (0,255,0), 2)
                cv2.putText(image, makeLikelyText(singleFace['sorrowLikelihood']) + " sorrow", (singleFace['boundingPoly']['vertices'][0]['x'], singleFace['boundingPoly']['vertices'][0]['y']-75), cv2.FONT_HERSHEY_PLAIN, 1.5, (0,255,0), 2)
                cv2.putText(image, makeLikelyText(singleFace['headwearLikelihood']) + " wearing a hat", (singleFace['boundingPoly']['vertices'][0]['x'], singleFace['boundingPoly']['vertices'][0]['y']-100), cv2.FONT_HERSHEY_PLAIN, 1.5, (0,255,0), 2)

                # Add landmarks (like; nose, eyes, etc)
                for landmark in singleFace['landmarks']:
                    if landmark['type'] in ['MOUTH_CENTER',  'NOSE_TIP', 'LEFT_EYE_PUPIL', 'RIGTH_EYE_PUPIL', 'FOREHEAD_GLABELLA']:
                        cv2.putText(image, landmark['type'], (int(landmark['position']['x']), int(landmark['position']['y'])), cv2.FONT_HERSHEY_PLAIN, 1, (255,0,0), 1)
    except:
        pass # pass if something misses in this frame

    # Write all images to the output video
    outputvid.write(image)
    
    # Counter for frames in movie +1
    count += 1

    # flush outputvid
    sys.stdout.flush()

    # Set this if you want the video to render prematurely
    if count == 3341:
        break

# Wrap everything up
cv2.destroyAllWindows()
outputvid.release()