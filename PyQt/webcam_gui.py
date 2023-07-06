import sys
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, QHBoxLayout

import cv2

class CameraWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Create a central widget and a layout for buttons
        central_widget = QWidget(self)
        layout = QVBoxLayout(central_widget)

        # Create a label to display the camera feed
        self.label = QLabel(self)
        layout.addWidget(self.label)

        # Create buttons to open and stop the camera
        self.open_button = QPushButton("Open Camera", self)
        self.stop_button = QPushButton("Stop Camera", self)
        
        # Create a horizontal layout for the buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.open_button, alignment=Qt.AlignLeft)
        buttons_layout.addWidget(self.stop_button, alignment=Qt.AlignRight)
        
        # Add the buttons layout to the main layout
        layout.addLayout(buttons_layout)

        # Set the central widget and layout
        self.setCentralWidget(central_widget)

        # Connect button signals to their respective slots
        self.open_button.clicked.connect(self.open_camera)
        self.stop_button.clicked.connect(self.stop_camera)

        # Open the camera
        self.cap = cv2.VideoCapture(0)

        # Set the window title
        self.setWindowTitle("Camera")

        # Start the timer to display the camera feed
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(1)

        # Initialize a flag to check if camera is running
        self.camera_running = False

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
                # Convert the frame to RGB format
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # Create QImage from the RGB frame
                image = QImage(
                    frame_rgb.data, frame_rgb.shape[1], frame_rgb.shape[0],
                    QImage.Format_RGB888
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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CameraWindow()
    window.show()
    sys.exit(app.exec_())
