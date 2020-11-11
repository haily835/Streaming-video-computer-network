# rtpPacket = RtpPacket()
		
# 		rtpPacket.encode(version, padding, extension, cc, seqnum, marker, pt, ssrc, payload)
		
# 		return rtpPacket.getPacket()

from time import time
class RtpPacket:
    
    def __init__(self):
        self.header = bytearray(12)

    def encode(self, version, padding, extension, cc, seqnum, marker, pt, ssrc, payload):
        v = version << 6
        self.header[0] = v + cc

        # second byte
        self.header[1] = pt

        # third and forth byte
        self.header[2] = (seqnum >> 8) & 0xFF
        self.header[3] = seqnum & 0xFF
        
        timestamp = int(time())
        self.time_stamp = timestamp
        part1 = (timestamp >> 16) & 0xFFFF
        part2 = timestamp  & 0xFFFF
        self.header[4] = (part1 >> 8) & 0xFF
        self.header[5] = part1 & 0xFF
        self.header[6] = (part2 >> 8) & 0xFF
        self.header[7] = part2 & 0xFF

        part1 = (ssrc >> 16) & 0xFFFF
        part2 = ssrc & 0xFFFF
        self.header[8] = (part1 >> 8) & 0xFF
        self.header[9] = part1 & 0xFF
        self.header[10] = (part2 >> 8) & 0xFF
        self.header[11] = part2 & 0xFF
        

    def decode(self, byteStream):
        """Decode the RTP packet."""
        self.header = bytearray(byteStream[:12])
        self.payload = byteStream[12:]
    
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