# importing libraries
import os
import cv2
# from PIL import Image
import datetime

# Checking the current directory path
# from src.DBConnection import iud
import subprocess

print(os.getcwd())

# Folder which contains all the images
# from which video is to be generated

path = r"static\dataset"





# Video Generating function




def generate_video(stringval):

    fn=datetime.datetime.now().strftime("%Y%m%d%H%M%S")

    fn1=fn+".mp4"

    fn=fn+".avi"
    video_name = "static/video/"+fn #'mygeneratedvideo.avi'
    # os.chdir("static")

    images = []
    for i in stringval:
        if i==" ":
            images.append("0.jpg")
        else:
            images.append(i+".jpg")

    # Array images should only consider
    # the image files ignoring others if any
    print(images)
    print(os.path.join(path, images[0]),"========================")
    frame = cv2.imread(os.path.join(path, images[0]))

    # setting the frame width, height width
    # the width, height of first image
    height, width, layers = frame.shape

    video = cv2.VideoWriter(video_name, 0, 1, (width, height))

    # Appending the images to the video one by one
    for image in images:
        video.write(cv2.imread(os.path.join(path, image)))

    # Deallocating memories taken for window creation



    cv2.destroyAllWindows()
    video.release()

    inputfile = video_name
    des="static/video/"
    print('[INFO] 1', inputfile)
    outputfile = os.path.join(des, fn1)
    subprocess.call(['ffmpeg', '-i', inputfile, outputfile])

    return fn1




