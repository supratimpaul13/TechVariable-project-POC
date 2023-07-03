from moviepy.editor import *

clip_1 = VideoFileClip("vid2.mp4").subclip(00, 10)
clip_2 = VideoFileClip("vid1.mp4").subclip(10, 18)
clip_3 = VideoFileClip("vid3.mp4").subclip(20, 30)
clip_4 = VideoFileClip("vid4.mp4").subclip(30, 40)


# creating arrays of two videos each row in order to split screen
comb = clips_array([[clip_1, clip_2],
                    [clip_3, clip_4]])

comb.write_videofile("SliptScreenVid3.mp4")