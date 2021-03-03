from flask import Flask, render_template, Response
import cv2
import numpy as np
import dlib
import time
import random

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
camera = cv2.VideoCapture(1)
points = [(100, 150), (200, 400), (300, 270), (400, 300), (150, 400), (250, 300), (350, 200), (450, 350)]
start = time.time()
random.shuffle(points)

app = Flask(_name_)


def distance(x1, y1, x2, y2):
    distance = ((((x2 - x1) * 2) + ((y2 - y1) * 2)) ** 0.5)
    return distance


def gen_frames2():  # generate frame by frame from camera
    while True:
        # Capture frame-by-frame
        success, frame = camera.read()  # read the camera frame
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
                if len(points) == 0:
                    end = time.time()
                    break

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

app = Flask(_name_)

vs = cv2.VideoCapture(1)  # use 0 for web camera
#  for cctv camera use rtsp://username:password@ip_address:554/user=username_password='password'_channel=channel_number_stream=0.sdp' instead of camera
# for local webcam use cv2.VideoCapture(0)

def eye_aspect_ratio(eye):
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])
    C = dist.euclidean(eye[0], eye[3])
    ear = (A + B) / (2.0 * C)
    return ear


# ap = argparse.ArgumentParser()
# ap.add_argument("-p", "--shape-predictor", default="shape_predictor_68_face_landmarks.dat",
#                 help="path to facial landmark predictor")
# ap.add_argument("-w", "--webcam", type=int, default=1,
#                 help="index of webcam on system")
# args = vars(ap.parse_args())

EYE_AR_THRESH = 0.20
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
# vs = VideoStream(src=args["webcam"]).start()
time.sleep(1.0)


def gen_frames1():  # generate frame by frame from camera
    global EYE_AR_THRESH, EYE_AR_CONSEC_FRAMES, EYE_AR_BLINK_LOW, EYE_AR_BLINK_HIGH, numBlinks, blinks, COUNTER, drowsyWarning
    while True:
        # Capture frame-by-frame
        success, frame = vs.read()  # read the camera frame
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
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                else:
                    blinks = False
                    if EYE_AR_BLINK_LOW <= COUNTER <= EYE_AR_BLINK_HIGH:
                        numBlinks += 1
                    COUNTER = 0

                cv2.putText(frame, "EAR: {:.2f}".format(ear), (300, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                cv2.putText(frame, "Blinks: {blinks}".format(blinks=numBlinks), (10, 90),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                if blinks:
                    cv2.putText(frame, "BLINK DETECTED!", (10, 120),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

                if drowsyWarning:
                    cv2.putText(frame, "DROWSY WARNING: TRUE", (10, 60),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                else:
                    cv2.putText(frame, "DROWSY WARNING: FALSE", (10, 60),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
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

@app.route('/loginPage')
def login():
    return render_template('loginPage.html')

@app.route('/dizzy')
def dizzi():
    return render_template('dizzy.html')

@app.route('/dizzy-result')
def dizziResult():
    return render_template('dizzy-result.html')

@app.route('/driving')
def driving():
    return render_template('driving.html')

@app.route('/thankyou')
def thankyou():
    return render_template('thankyou.html')


if __name__ == '__main__':
    app.run(threaded=True, port=5000)