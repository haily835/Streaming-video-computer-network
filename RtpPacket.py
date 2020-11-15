import sys
from time import time
HEADER_SIZE = 12

class RtpPacket:	
	header = bytearray(HEADER_SIZE)
	
	def __init__(self):
		pass
		
	def encode(self, version, padding, extension, cc, seqnum, marker, pt, ssrc, payload):
		timestamp = int(time())
		header = bytearray(HEADER_SIZE)
		v = version << 6
		header[0] = v + cc

		# second byte
		header[1] = pt

		# third and forth byte
		header[2] = (seqnum >> 8) & 0xFF
		header[3] = seqnum & 0xFF

		part1 = (timestamp >> 16) & 0xFFFF
		part2 = timestamp  & 0xFFFF
		header[4] = (part1 >> 8) & 0xFF
		header[5] = part1 & 0xFF
		header[6] = (part2 >> 8) & 0xFF
		header[7] = part2 & 0xFF

		part1 = (ssrc >> 16) & 0xFFFF
		part2 = ssrc & 0xFFFF
		header[8] = (part1 >> 8) & 0xFF
		header[9] = part1 & 0xFF
		header[10] = (part2 >> 8) & 0xFF
		header[11] = part2 & 0xFF

		self.header = header
		self.payload = payload

	def decode(self, byteStream):
		"""Decode the RTP packet."""
		self.header = bytearray(byteStream[:HEADER_SIZE])
		self.payload = byteStream[HEADER_SIZE:]
	
	def version(self):
		"""Return RTP version."""
		return int(self.header[0] >> 6)
	
	def seqNum(self):
		"""Return sequence (frame) number."""
		seqNum = self.header[2] << 8 | self.header[3]
		return int(seqNum)
	
	def timestamp(self):
		"""Return timestamp."""
		timestamp = self.header[4] << 24 | self.header[5] << 16 | self.header[6] << 8 | self.header[7]
		return int(timestamp)
	
	def payloadType(self):
		"""Return payload type."""
		pt = self.header[1] & 127
		return int(pt)
	
	def getPayload(self):
		"""Return payload."""
		return self.payload
		
	def getPacket(self):
		"""Return RTP packet."""
		return self.header + self.payload
