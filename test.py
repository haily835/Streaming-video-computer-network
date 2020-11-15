import cv2
from tkinter import *
from PIL import Image, ImageTk
import io

# data = self.file.read(5) # Get the framelength from the first 5 bits
# if data: 
# 	framelength = int(data)
# 	# Read the current frame
# 	data = self.file.read(framelength)
# 	self.frameNum += 1
# 	self.currdata = data
# return data
cam = cv2.VideoCapture("movie2.mjpeg")
ret,frame = cam.read()
cv2.imwrite("img1.jpg", frame) 

im = cv2.imread('img1.jpg')
im_resize = cv2.resize(im, (200, 200))

is_success, im_buf_arr = cv2.imencode(".jpg", im_resize)
byte_im = im_buf_arr.tobytes()
file = open('img.jpg', "wb")
file.write(byte_im)
root = Tk()
photo = ImageTk.PhotoImage(Image.open('img.jpg'))

label = Label(root)
label.configure(image = photo)
label.image = photo
label.pack()
root.mainloop()