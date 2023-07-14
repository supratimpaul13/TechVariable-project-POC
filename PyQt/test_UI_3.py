import sys
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, QHBoxLayout, QSlider, QSizePolicy, QStyle, QFileDialog
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import QUrl

import cv2
import mediapipe as mp
import pyautogui
import time
import numpy as np


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Main Window")
        self.setGeometry(100, 100, 1200, 600)

        # Create a central widget and a layout for buttons
        central_widget = QWidget(self)
        layout = QHBoxLayout(central_widget)

        # Create the left side (webcam) widget
        self.camera_widget = CameraWindow()
        layout.addWidget(self.camera_widget)

        # Create the right side (video player) widget
        self.video_widget = VideoPlayerWindow()
        layout.addWidget(self.video_widget)

        # Pass the video widget reference to the camera widget
        self.camera_widget.set_video_widget(self.video_widget)

        # Set the central widget and layout
        self.setCentralWidget(central_widget)


class CameraWindow(QWidget):
    def __init__(self):
        super().__init__()

        # Create a label to display the camera feed
        self.label = QLabel(self)

        # Create buttons to open and stop the camera
        self.open_button = QPushButton("Open Camera", self)
        self.stop_button = QPushButton("Stop Camera", self)

        # Create a vertical layout for the camera widget
        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.addWidget(self.open_button)
        layout.addWidget(self.stop_button)

        # Connect button signals to their respective slots
        self.open_button.clicked.connect(self.open_camera)
        self.stop_button.clicked.connect(self.stop_camera)

        # Open the camera
        self.cap = cv2.VideoCapture(0)

        # Start the timer to display the camera feed
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(1)

        # Initialize a flag to check if camera is running
        self.camera_running = False

        # Initialize hand gesture variables
        self.hand_obj = mp.solutions.hands.Hands(max_num_hands=1)
        self.start_init = False
        self.prev = -1

        # Store a reference to the video widget
        self.video_widget = None

    def set_video_widget(self, video_widget):
        self.video_widget = video_widget

    def open_camera(self):
        # Check if the camera is already running
        if not self.camera_running:
            self.cap = cv2.VideoCapture(0)
            self.camera_running = True

    def stop_camera(self):
        # Check if the camera is running
        if self.camera_running:
            self.cap.release()
            self.camera_running = False

    def update_frame(self):
        # Check if the camera is running
        if self.camera_running:
            # Read frame from the camera
            ret, frame = self.cap.read()

            if ret:
                # Process frame for hand gesture recognition
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                res = self.hand_obj.process(frame_rgb)

                if res.multi_hand_landmarks:
                    hand_keypoints = res.multi_hand_landmarks[0]
                    cnt = self.count_fingers(hand_keypoints)

                    if not (self.prev == cnt):
                        if not self.start_init:
                            self.start_init = time.time()
                            self.start_init = True
                        elif (time.time() - self.start_init) > 1:
                            if cnt == 1:
                                pyautogui.press("right")
                            elif cnt == 2:
                                if self.video_widget:
                                    self.video_widget.play_video()
                            elif cnt == 3:
                                pyautogui.press("up")
                            elif cnt == 4:
                                pyautogui.press("down")
                            elif cnt == 5:
                                pyautogui.press("space")
                            self.prev = cnt
                            self.start_init = False

                    mp.solutions.drawing_utils.draw_landmarks(
                        frame, hand_keypoints, mp.solutions.hands.HAND_CONNECTIONS
                    )

                # Convert the frame to RGB format
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # Create QImage from the RGB frame
                image = QImage(
                    frame_rgb.data,
                    frame_rgb.shape[1],
                    frame_rgb.shape[0],
                    QImage.Format_RGB888,
                )

                # Create QPixmap from the QImage
                pixmap = QPixmap.fromImage(image)

                # Set the pixmap on the label to display the camera feed
                self.label.setPixmap(pixmap)
                self.label.setScaledContents(True)
                self.label.setMinimumSize(1, 1)

    def keyPressEvent(self, event):
        # Press 'Esc' key to close the application
        if event.key() == Qt.Key_Escape:
            self.close()

    @staticmethod
    def count_fingers(lst):
        cnt = 0
        thresh = (lst.landmark[0].y * 100 - lst.landmark[9].y * 100) / 2

        if (lst.landmark[5].y * 100 - lst.landmark[8].y * 100) > thresh:
            cnt += 1
        if (lst.landmark[9].y * 100 - lst.landmark[12].y * 100) > thresh:
            cnt += 1
        if (lst.landmark[13].y * 100 - lst.landmark[16].y * 100) > thresh:
            cnt += 1
        if (lst.landmark[17].y * 100 - lst.landmark[20].y * 100) > thresh:
            cnt += 1
        if (lst.landmark[5].x * 100 - lst.landmark[4].x * 100) > 5:
            cnt += 1

        return cnt


class VideoPlayerWindow(QWidget):
    def __init__(self):
        super().__init__()

        # Create Media player object
        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)

        # Create Video widget object
        self.videowidget = QVideoWidget()

        # Create open button
        openBtn = QPushButton("Open Video")
        openBtn.clicked.connect(self.open_file)

        # Create button for playing
        self.playBtn = QPushButton()
        self.playBtn.setEnabled(False)
        self.playBtn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.playBtn.clicked.connect(self.play_video)

        # Create slider
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 0)
        self.slider.sliderMoved.connect(self.set_position)

        # Create label
        self.label = QLabel()
        self.label.setSizePolicy(
            QSizePolicy.Preferred, QSizePolicy.Maximum
        )

        # Create Hbox layout
        hboxLayout = QHBoxLayout()
        hboxLayout.setContentsMargins(0, 0, 0, 0)

        # Set widget to the hbox layout
        hboxLayout.addWidget(openBtn)
        hboxLayout.addWidget(self.playBtn)
        hboxLayout.addWidget(self.slider)

        # Create vbox layout
        vboxLayout = QVBoxLayout()
        vboxLayout.addWidget(self.videowidget)
        vboxLayout.addLayout(hboxLayout)
        vboxLayout.addWidget(self.label)

        self.setLayout(vboxLayout)

        self.mediaPlayer.setVideoOutput(self.videowidget)

        # Media player signals
        self.mediaPlayer.stateChanged.connect(self.mediastate_change)
        self.mediaPlayer.positionChanged.connect(self.position_changed)
        self.mediaPlayer.durationChanged.connect(self.duration_changed)

    def open_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open Video")
        if filename != "":
            self.mediaPlayer.setMedia(
                QMediaContent(QUrl.fromLocalFile(filename))
            )
            self.playBtn.setEnabled(True)

    def play_video(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
        else:
            self.mediaPlayer.play()

    def mediastate_change(self, state):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.playBtn.setIcon(
                self.style().standardIcon(QStyle.SP_MediaPause)
            )
        else:
            self.playBtn.setIcon(
                self.style().standardIcon(QStyle.SP_MediaPlay)
            )

    def position_changed(self, position):
        self.slider.setValue(position)

    def duration_changed(self, duration):
        self.slider.setRange(0, duration)

    def set_position(self, position):
        self.mediaPlayer.setPosition(position)

    def handle_errors(self):
        self.playBtn.setEnabled(False)
        self.label.setText("Error: " + self.mediaPlayer.errorString)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
