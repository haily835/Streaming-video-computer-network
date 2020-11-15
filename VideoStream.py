import cv2
class VideoStream:
	def __init__(self, filename):
		self.filename = filename
		try:
			self.file = cv2.VideoCapture(filename)
		except:
			raise IOError
		self.frameNum = 0
		
	def nextFrame(self):
		"""Get next frame."""
		# data = self.file.read(5) # Get the framelength from the first 5 bits
		# if data: 
		# 	framelength = int(data)
		# 	# Read the current frame
		# 	data = self.file.read(framelength)
		# 	self.frameNum += 1
		# 	self.currdata = data
		# return data
		ret,frame = self.file.read()
		is_success, im_buf_arr = cv2.imencode(".jpg", frame)
		byte_im = im_buf_arr.tobytes()
		self.frameNum += 1
		self.currdata = byte_im
		return byte_im

	def lastFrame(self):
		# self.file.close()
		# self.file = open(self.filename, 'rb')
		
		# if (self.frameNum - 20 > 0):
		# 	for x in range(0, self.frameNum - 20):
		# 		data = self.file.read(5) # Get the framelength from the first 5 bits
		# 		if data: 
		# 			framelength = int(data)
		# 			# Read the current frame
		# 			data = self.file.read(framelength)
		# 			self.currdata = data
		# 	self.frameNum = self.frameNum - 20
		# 	return data
		# else:
		# 	return self.currdata

		self.file.release()
		self.file = cv2.VideoCapture(self.filename)
		if (self.frameNum - 50 > 0):
			for x in range(0, self.frameNum - 50):
				self.file.read()
			ret,frame = self.file.read()
			is_success, im_buf_arr = cv2.imencode(".jpg", frame)
			byte_im = im_buf_arr.tobytes()
			self.currdata = byte_im
			self.frameNum = self.frameNum - 20
			return self.currdata
		else:
			return self.currdata
		

	def frameNbr(self):
		"""Get frame number."""
		return self.frameNum