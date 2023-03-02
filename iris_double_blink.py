import math
import mediapipe as mp
import numpy as np
import cv2 as cv
import time

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import QTimer

import serial
import time

global port
port = serial.Serial("/dev/rfcomm2", baudrate=9600)

# variables
global counter
global final_counter
global blink_time
global blink_list
global count
counter = 0
final_counter = 0
blink_time = [0 ,0]
blink_list = []
count =0
mp_face_mesh = mp.solutions.face_mesh
LEFT_EYE = [362, 382, 381, 380, 374, 373, 390,
            249, 263, 466, 388, 387, 386, 385, 384, 398]

RIGHT_EYE = [33, 7, 163, 144, 145, 153, 154,
             155, 133, 173, 157, 158, 159, 160, 161, 246]
LEFT_IRIS = [469, 470, 471, 472]
RIGHT_IRIS = [474, 475, 476, 477]

# L_H_LEFT = [33]  # right eye right most landmark
# L_H_RIGHT = [133]  # right eye left most landmark
# R_H_LEFT = [362]  # left eye right most landmark
# R_H_RIGHT = [263]  # left 

# R_UP = [159]
# R_DOWN = [145]
L_H_LEFT = 33  # right eye right most landmark
L_H_RIGHT = 133  # right eye left most landmark
R_H_LEFT = 362  # left eye right most landmark
R_H_RIGHT = 263  # left 

R_UP = 159
R_DOWN = 145
landmarks = []

class Ui_MainWindow(object):

    def setupUi(self, MainWindow):
        self.frame = None
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        MainWindow.setLayoutDirection(QtCore.Qt.LeftToRight)
        # MainWindow.setAnimated(True)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        # Font
        font = QtGui.QFont()
        font.setPointSize(16)
        # frame
        self.imgLabel = QtWidgets.QLabel(self.centralwidget)
        self.imgLabel.setGeometry(QtCore.QRect(150, 30, 521, 381))
        self.imgLabel.setMinimumSize(QtCore.QSize(4, 0))
        self.imgLabel.setMaximumSize(QtCore.QSize(640, 480))
        self.imgLabel.setText("")
        self.imgLabel.setObjectName("imgLabel")

        # Start Button
        self.pushButton1 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton1.setGeometry(QtCore.QRect(400, 500, 111, 41))
        self.pushButton1.setObjectName("Start camera")
        self.pushButton1.clicked.connect(self.imdisplay)
        # self.pushButton1.clicked.connect(self.start_cam)

        # Stop button
        self.pushButton2 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton2.setGeometry(QtCore.QRect(550, 500, 111, 41))
        self.pushButton2.setObjectName("Stop camera")
        self.pushButton2.clicked.connect(self.stop_cam)

        # text(iris_pos)
        self.text_label = QtWidgets.QLabel(self.centralwidget)
        self.text_label.setFont(font)
        self.text_label.setGeometry(QtCore.QRect(280, 500, 110, 41))
        self.text_label.setLayoutDirection(QtCore.Qt.LeftToRight)

        # text(no. of blinks)
        self.text_label2 = QtWidgets.QLabel(self.centralwidget)
        self.text_label2.setFont(font)
        self.text_label2.setGeometry(QtCore.QRect(20, 500, 200, 41))
        self.text_label2.setLayoutDirection(QtCore.Qt.LeftToRight)

        # text (blink)
        self.text_label1 = QtWidgets.QLabel(self.centralwidget)
        self.text_label1.setFont(font)
        self.text_label1.setGeometry(QtCore.QRect(180, 500, 200, 41))
        self.text_label1.setLayoutDirection(QtCore.Qt.LeftToRight)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        self._translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(self._translate("MainWindow", "MainWindow"))
        self.pushButton1.setText(self._translate("MainWindow", "Start Cam"))
        self.pushButton2.setText(self._translate("MainWindow", "Stop Cam"))

    def imdisplay(self):

        self.imgLabel.show()
        self.cap = cv.VideoCapture(0)
        while True:
            ret, self.frame = self.cap.read()
            if not ret:
                break
            self.frame = cv.flip(self.frame, 1)

            # algorithm
            with mp_face_mesh.FaceMesh(max_num_faces=1,
                                       refine_landmarks=True,
                                       min_detection_confidence=0.5,
                                       min_tracking_confidence=0.5
                                       ) as face_mesh:
                rgb_frame = cv.cvtColor(self.frame, cv.COLOR_BGR2RGB)
                img_h, img_w = self.frame.shape[:2]
                results = face_mesh.process(rgb_frame)
                if results.multi_face_landmarks:
                    mesh_points0 = np.array([tuple(np.multiply([p.x, p.y], [img_w, img_h]).astype(int).ravel()) for p in results.multi_face_landmarks[0].landmark])
                    mesh_points = [tuple(np.multiply([p.x, p.y], [img_w, img_h]).astype(int).ravel()) for p in results.multi_face_landmarks[0].landmark]
                    #print(results.multi_face_landmarks)
                    #print(mesh_points)
                    
                    (l_cx, l_cy), l_radius = cv.minEnclosingCircle(mesh_points0[LEFT_IRIS])
                    (r_cx, r_cy), r_radius = cv.minEnclosingCircle(mesh_points0[RIGHT_IRIS])
                    
                    center_left = tuple(np.array([l_cx, l_cy], dtype=np.int32))
                    center_right = tuple(np.array([r_cx, r_cy], dtype=np.int32))

                    # print(mesh_points[R_UP], mesh_points[R_DOWN],mesh_points[R_H_RIGHT], mesh_points[R_H_LEFT])

                    cv.circle(self.frame, center_left, int(l_radius),
                              (255, 0, 255), 1, cv.LINE_AA)
                    cv.circle(self.frame, center_right, int(r_radius),
                              (255, 0, 255), 1, cv.LINE_AA)
                    iris_pos, ratio = self.iris_position(center_right, mesh_points[R_UP], mesh_points[R_DOWN],mesh_points[R_H_RIGHT], mesh_points[R_H_LEFT])
                    
                    blink, no_blinks = self.blink_status(mesh_points[R_UP], mesh_points[R_DOWN])
                    self.text_label.setText(iris_pos)
                    print "DIGITAL LOGIC -- > SENDING..."
                    port.write(str(3))
                    rcv = port.readline()
                    if rcv:
                        print(rcv)                   
                    
                    self.text_label1.setText(str(self.double_blink(blink)))
                    total_blinks = str(no_blinks)
                    toarduino(port, status)
                    blinks = "total blinks: " + total_blinks
                    #print(blinks)
                    self.text_label2.setText(blinks)

                    cv.putText(self.frame, f"Iris pos: {iris_pos}", (
                        30, 30), cv.FONT_HERSHEY_PLAIN, 1.2, (0, 255, 0), 1, cv.LINE_AA)

            self.displayImage(self.frame, 1)

            self.key = cv.waitKey(1)

    def toarduino(port,status):
        # reading and writing data from and to arduino serially.                                      
        # rfcomm0 -> this could be different
        print "DIGITAL LOGIC -- > SENDING..."
        port.write(self.status)
        rcv = port.readline()
        if rcv:
            print(rcv)


    def stop_cam(self):
        self.imgLabel.hide()
        self.cap.release()

    def displayImage(self, img, window=1):
        qformat = QImage.Format_Indexed8
        if len(img.shape) == 3:
            if img.shape[2] == 4:
                qformat = QImage.Format_RGBA8888
            else:
                qformat = QImage.Format_RGB888
        outImage = QImage(img, img.shape[1],
                          img.shape[0], img.strides[0], qformat)
        outImage = outImage.rgbSwapped()

        if window == 1:
            self.imgLabel.setPixmap(QPixmap.fromImage(outImage))
            self.imgLabel.setScaledContents(True)

    def euclidean_distance(self, point1, point2):
        #print(point1, point2)
        x1, y1 = point1
        x2, y2 = point2
        self.distance = math.sqrt((x2 - x1)**2 + (y2-y1)**2)
        return self.distance

    
    def double_blink(self, blink_status, interval=1):
        global blink_time
        global blink_list
        global count

        current_status = blink_status            

        if current_status == "blink":
            blink_time.append(time.time())
            count+=1

            if count==2:
                current_time = time.time()
                print('time: ', current_time - blink_time[-1])
                
                if time.time() - blink_time[-1] <= 0.5:
                    print("double blink")
                    blink_list.append("blink")
                    blink_time.append(current_time)
                    count = 0
                    return "double blink"
                else:
                    return blink_status            
            else:
                return blink_status
        else:
            return blink_status


    def blink_status(self, down_point, up_point):
        global counter
        global final_counter
        total_vert_distance = self.euclidean_distance(down_point, up_point)

        if (total_vert_distance < 6):
            counter += 1
            return "blink", final_counter
        else:
            if counter > 0:
                final_counter += 1
                counter = 0
            return "no blink", final_counter    

    def iris_position(self, iris_center, up_point, down_point, right_point, left_point):
        center_to_right_dist = self.euclidean_distance(
            iris_center, right_point)
        total_distance = self.euclidean_distance(right_point, left_point)

        ratio = center_to_right_dist/total_distance

        diff = down_point[1]-up_point[1]
        #print(diff)
        if diff< 9:
            iris_position = "down"
        elif diff > 12:
            iris_position = "up"
        elif ratio > 0.42 and ratio <= 0.57:
            iris_position = "center"
        elif ratio <= 0.42:
            iris_position = "right"
        else:
            iris_position = "left"
        ratio_vertical = diff
        return iris_position, ratio_vertical


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
