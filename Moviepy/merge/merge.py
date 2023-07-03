from moviepy.editor import *

clip1 = VideoFileClip("merge/vid2.mp4").subclip(25, 45)
clip2 = VideoFileClip("merge/vid3.mp4").subclip(48, 72)

clip2 = clip2.set_position((45, 150))

final_vid = concatenate_videoclips([clip1, clip2])
final_vid.write_videofile("merge/merged_vid.mp4")