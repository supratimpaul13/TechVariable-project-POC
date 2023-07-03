from moviepy.editor import *

clip1 = VideoFileClip("merge/vid2.mp4")

def ask():
    time = int (input("Enter the time in seconds: "));
    return time

clip1.save_frame("screenshot/test.jpg", t=ask())