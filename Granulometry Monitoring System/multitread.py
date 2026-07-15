# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

import os
import sys
import time

import cv2
from PySide6.QtCore import Qt, QThread, Signal, Slot
from PySide6.QtGui import QAction, QImage, QKeySequence, QPixmap
from PySide6.QtWidgets import (QApplication, QComboBox, QGroupBox,
                               QHBoxLayout, QLabel, QMainWindow, QPushButton,
                               QSizePolicy, QVBoxLayout, QWidget)

video_size_w = 1280
video_size_h = 720
class Thread(QThread):
    updateFrame = Signal(QImage)

    def __init__(self, parent=None):
        QThread.__init__(self, parent)
        self.trained_file = None
        self.status = True
        self.cap = True

    def set_file(self, fname):
        # The data comes with the 'opencv-python' module
        self.trained_file = os.path.join(cv2.data.haarcascades, fname)

    def run(self):

        url = 'Images/timer.mp4'
        self.cap = cv2.VideoCapture(url)

        """
        frame_rate = 10
        prev = 0
        
        while capturing:
        
            time_elapsed = time.time() - prev
            res, image = cap.read()
        
            if time_elapsed > 1./frame_rate:
                prev = time.time()
        
                # Do something with your image here.
                process_image()
        
        
        
        
        """
        while self.status:
            cascade = cv2.CascadeClassifier(self.trained_file)
            ret, frame = self.cap.read()

            if not ret:
                continue


            resize_frame=cv2.resize(frame, (video_size_w,video_size_h), interpolation=cv2.INTER_LINEAR)

            #resize_frame = cv2.resize(frame, (0, 0), fx=0.1, fy=0.1)
            # Reading frame in gray scale to process the pattern
            gray_frame = cv2.cvtColor(resize_frame, cv2.COLOR_BGR2GRAY)
            #detections = cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))



            # Drawing green rectangle around the pattern
            #for (x, y, w, h) in detections:
            #    pos_ori = (x, y)
            #    pos_end = (x + w, y + h)
            #    color = (0, 255, 0)
            #    cv2.rectangle(frame, pos_ori, pos_end, color, 2)






            # Reading the image in RGB to display it
            color_frame = cv2.cvtColor(resize_frame, cv2.COLOR_BGR2RGB)
            # Creating and scaling QImage
            h, w, ch = color_frame.shape
            img = QImage(color_frame.data, w, h, ch * w, QImage.Format_RGB888)
            scaled_img = img.scaled(video_size_w, video_size_h, Qt.KeepAspectRatio)

            # Emit signal
            self.updateFrame.emit(scaled_img)
        sys.exit(-1)


class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        # Title and dimensions
        self.setWindowTitle("Patterns detection")
        self.setGeometry(0, 0, 1280, 720)

        # Main menu bar
        self.menu = self.menuBar()
        self.menu_file = self.menu.addMenu("Exit")
        exit = QAction("Exit", self, triggered=qApp.quit)  # noqa: F821
        self.menu_file.addAction(exit)

        # Create a label for the display

        self.label = QLabel(self)
        self.label.setFixedSize(video_size_w, video_size_h)

        self.label1 = QLabel(self)
        self.label1.setFixedSize(video_size_w/2, video_size_h/2)


        # Thread in charge of updating the image
        self.th = Thread(self)
        self.th.finished.connect(self.close)
        self.th.updateFrame.connect(self.setImage)

        # Model group
        self.group_model = QGroupBox("Trained model")
        self.group_model.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        model_layout = QHBoxLayout()

        self.combobox = QComboBox()
        path_dir=r'AiModules'
        for pt_file in os.listdir(path_dir):
            if pt_file.endswith(".pt"):
                self.combobox.addItem(pt_file)

        model_layout.addWidget(QLabel("File:"), 10)
        model_layout.addWidget(self.combobox, 90)
        self.group_model.setLayout(model_layout)

        # Buttons layout
        buttons_layout = QHBoxLayout()
        self.button1 = QPushButton("Start")
        self.button2 = QPushButton("Stop/Close")
        self.button1.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.button2.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        buttons_layout.addWidget(self.button2)
        buttons_layout.addWidget(self.button1)

        right_layout = QHBoxLayout()
        right_layout.addWidget(self.group_model, 1)
        right_layout.addLayout(buttons_layout, 1)

        # Main layout
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.label1)
        layout.addLayout(right_layout)

        # Central widget
        widget = QWidget(self)
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        # Connections
        self.button1.clicked.connect(self.start)
        self.button2.clicked.connect(self.kill_thread)
        self.button2.setEnabled(False)
        self.combobox.currentTextChanged.connect(self.set_model)

    @Slot()
    def set_model(self, text):
        self.th.set_file(text)

    @Slot()
    def kill_thread(self):
        print("Finishing...")
        self.button2.setEnabled(False)
        self.button1.setEnabled(True)
        self.th.cap.release()
        cv2.destroyAllWindows()
        self.status = False
        self.th.terminate()
        # Give time for the thread to finish
        time.sleep(1)

    @Slot()
    def start(self):
        print("Starting...")
        self.button2.setEnabled(True)
        self.button1.setEnabled(False)
        self.th.set_file(self.combobox.currentText())
        self.th.start()

    @Slot(QImage)
    def setImage(self, image):
        self.label.setPixmap(QPixmap.fromImage(image).scaled(self.label.size(),Qt.KeepAspectRatio))
        self.label1.setPixmap(QPixmap.fromImage(image).scaled(self.label1.size(),Qt.KeepAspectRatio))


if __name__ == "__main__":
    app = QApplication()
    w = Window()
    w.show()
    sys.exit(app.exec())