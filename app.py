from flask import Flask, render_template, Response
import cv2
import numpy as np
import dlib
import time
import random
import threading

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
camera = cv2.VideoCapture(0)
points = [(100, 150), (200, 400), (300, 270), (490, 310), (160, 450), (250, 350), (350, 250), (450, 350),
          (150, 190), (210, 310), (310, 280), (480, 320), (170, 440), (260, 340), (360, 240), (420, 340),
          (160, 130), (220, 320), (320, 290), (470, 330), (190, 430), (250, 330), (370, 230), (430, 330),
          (170, 150), (230, 330), (330, 250), (460, 340), (180, 420), (230, 320), (380, 220), (440, 320),
          (180, 130), (240, 340), (340, 260), (450, 350), (140, 410), (220, 310), (390, 210), (410, 310)
          ]
start = time.time()
random.shuffle(points)
respTime = 0
doneCheck = 0
counter =0
firstTime = True

app = Flask(__name__)


def distance(x1, y1, x2, y2):
    distance = ((((x2 - x1) ** 2) + ((y2 - y1) ** 2)) ** 0.5)
    return distance


def gen_frames2():  # generate frame by frame from camera
    global firstTime, respTime, doneCheck, counter# generate frame by frame from camera
    while True:
        # Capture frame-by-frame
        success, frame = camera.read()  # read the camera frame
        frame = cv2.flip(frame,1)# read the camera frame
        if not success:
            break
        else:
            gray = cv2.cvtColor(src=frame, code=cv2.COLOR_BGR2GRAY)
            faces = detector(gray)
            for face in faces:
                x1 = face.left()
                y1 = face.top()
                x2 = face.right()
                y2 = face.bottom()

                landmarks = predictor(image=gray, box=face)
                # for n in range(28, 36):
                x = landmarks.part(30).x
                y = landmarks.part(30).y
                cv2.circle(img=frame, center=(x, y), radius=3, color=(0, 255, 0), thickness=-1)
                if len(points) != 0:
                    cv2.circle(img=frame, center=points[0], radius=3, color=(184, 71, 192), thickness=5)
                    cv2.circle(img=frame, center=points[0], radius=3, color=(0, 0, 0), thickness=2)
                    a = points[0][0]
                    b = points[0][1]
                if (distance(x, y, a, b) < 50):
                    if len(points) != 0:
                        del points[0]
                        counter = counter + 1
                        respTime = (20/counter)
                        if (time.time() - start) == 20:
                            doneCheck = 1
                # if len(points) == 0:
                #     if firstTime:
                #         end = time.time()
                #         respTime = ((end - start)/18) * 10
                #         doneCheck = 1
                #         firstTime = False
                        # render_without_request(value=respTime)
                    # print(respTime)
                    # break
                    

            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show resul


from flask import Flask, render_template, Response
from scipy.spatial import distance as dist
from imutils.video import VideoStream
from imutils import face_utils
import argparse
import imutils
import time
import dlib
import cv2

app = Flask(__name__)

vs = cv2.VideoCapture(0)  

def eye_aspect_ratio(eye):
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])
    C = dist.euclidean(eye[0], eye[3])
    ear = (A + B) / (2.0 * C)
    return ear

EYE_AR_THRESH = 0.25
EYE_AR_CONSEC_FRAMES = 25
EYE_AR_BLINK_LOW = 1
EYE_AR_BLINK_HIGH = 8
numBlinks = 0
blinks = False
COUNTER = 0
drowsyWarning = False

print("[INFO] loading facial landmark predictor...")
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

(lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
(rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]

print("[INFO] starting video stream thread...")
time.sleep(1.0)


x = 0
blinkRate = 0
timerExit = False

def timer():
    global x, numBlinks, blinkRate
    while True:
        if timerExit:
            break
        time.sleep(1)
        x += 1
        blinkRate = (numBlinks * 60) / x


timerThread = threading.Thread(target=timer)

def gen_frames1():  # generate frame by frame from camera
    global EYE_AR_THRESH, EYE_AR_CONSEC_FRAMES, EYE_AR_BLINK_LOW, EYE_AR_BLINK_HIGH, numBlinks, blinks, COUNTER, drowsyWarning
    timerThread.start()
    while True:
        # Capture frame-by-frame
        success, frame = vs.read()  # read the camera frame
        frame = cv2.flip(frame,1)
        if not success:
            break
        else:
            frame = imutils.resize(frame, width=450)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        rects = detector(gray, 0)

        for rect in rects:
            shape = predictor(gray, rect)
            shape = face_utils.shape_to_np(shape)
            leftEye = shape[lStart:lEnd]
            rightEye = shape[rStart:rEnd]
            leftEAR = eye_aspect_ratio(leftEye)
            rightEAR = eye_aspect_ratio(rightEye)
            ear = (leftEAR + rightEAR) / 2.0
            leftEyeHull = cv2.convexHull(leftEye)
            rightEyeHull = cv2.convexHull(rightEye)
            cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
            cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)

            if ear < EYE_AR_THRESH:
                COUNTER += 1

                if EYE_AR_BLINK_LOW <= COUNTER <= EYE_AR_BLINK_HIGH:
                    blinks = True

                if COUNTER > EYE_AR_BLINK_HIGH:
                    blinks = False

                if COUNTER >= EYE_AR_CONSEC_FRAMES:
                    drowsyWarning = True
                    cv2.putText(frame, "DROWSINESS ALERT!", (10, 30),
                                cv2.FONT_HERSHEY_DUPLEX, 0.7, (255, 0, 0), 2)
            else:
                blinks = False
                if EYE_AR_BLINK_LOW <= COUNTER <= EYE_AR_BLINK_HIGH:
                    numBlinks += 1
                COUNTER = 0

            cv2.putText(frame, "EAR: {:.2f}".format(ear), (300, 30),
                        cv2.FONT_HERSHEY_DUPLEX, 0.7, (255, 0, 0), 2)
            cv2.putText(frame, "Blinks: {blinks}".format(blinks=numBlinks), (10, 90),
                        cv2.FONT_HERSHEY_DUPLEX, 0.7, (255, 0, 0), 2)
            cv2.putText(frame, "Blink Rate: {blinks}".format(blinks=round(blinkRate,2)), (10, 150),
                        cv2.FONT_HERSHEY_DUPLEX, 0.7, (255, 0, 0), 2)
            if blinks:
                cv2.putText(frame, "BLINK DETECTED!", (10, 120),
                            cv2.FONT_HERSHEY_DUPLEX, 0.7, (255, 0, 0), 2)

            if drowsyWarning:
                cv2.putText(frame, "DROWSY WARNING: TRUE", (10, 60),
                            cv2.FONT_HERSHEY_DUPLEX, 0.7, (255, 0, 0), 2)
            else:
                cv2.putText(frame, "DROWSY WARNING: FALSE", (10, 60),
                            cv2.FONT_HERSHEY_DUPLEX, 0.7, (255, 0, 0), 2)
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result

@app.route('/video_feed1')
def video_feed1():
    #Video streaming route. Put this in the src attribute of an img tag
    return Response(gen_frames1(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_feed2')
def video_feed2():
    #Video streaming route. Put this in the src attribute of an img tag
    return Response(gen_frames2(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')

@app.route('/back')
def back():
    return render_template('background.html')

@app.route('/loginPage')
def login():
    return render_template('loginPage.html')

@app.route('/dizzy')
def dizzi():
    return render_template('dizzy.html', value=doneCheck)

@app.route('/dizzy-result')
def dizziResult():
    import requests
    response = requests.post('https://events-api.notivize.com/applications/7a6f5ffc-85fe-4db3-9795-e8836c0fc791/event_flows/0be838ea-38b3-4179-9045-5d0c086e0d27/events', json = {
        'email': 'snaman431@gmail.com',
        'respTime': round(respTime,2),
        'unique_id1': time.time()
        })
    print(response)
    return render_template('dizzy-result.html', value=round(respTime,2) )

@app.route('/driving')
def driving():
    return render_template('driving.html')

@app.route('/thankyou')
def thankyou():
    return render_template('thankyou.html')


if __name__ == '__main__':
    app.run(threaded=True, port=5500)