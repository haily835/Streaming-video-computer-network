from tkinter import *
import tkinter.messagebox
import datetime
from PIL import Image, ImageTk
import socket, threading, sys, traceback, os

from RtpPacket import RtpPacket

CACHE_FILE_NAME = "cache-"
CACHE_FILE_EXT = ".jpg"

# Some request type constants
HEADER_REQUEST_TYPE_SETUP = "SETUP"
HEADER_REQUEST_TYPE_PAUSE = "PAUSE"
HEADER_REQUEST_TYPE_PLAY = "PLAY"
HEADER_REQUEST_TYPE_TEARDOWN = "TEARDOWN"
HEADER_REQUEST_TYPE_FORWARD = "FORWARD"
HEADER_REQUEST_TYPE_BACKWARD = "BACKWARD"
HEADER_REQUEST_TYPE_CHANGE = "CHANGE"
HEADER_REQUEST_TYPE_RESET = "RESET"

# Some request header key constants
HEADER_FIELD_SESSION = "Session"
HEADER_FIELD_CSEQ = "CSeq"
HEADER_FIELD_PROTOCOL = "RTSP/1.0"
HEADER_FIELD_RTP_OVER_UDP_PORT = "Transport: RTP/UDP; client_port="

class Client:
    INIT = 0
    READY = 1
    PLAYING = 2
    SWITCH = 3
    state = INIT
    
    SETUP = 0
    PLAY = 1
    PAUSE = 2
    TEARDOWN = 3
    FORWARD = 4
    BACKWARD = 5
    CHANGE = 6
    RESET = 7

    # Initiation.. NOT MODIFIED
    def __init__(self, master, serveraddr, serverport, rtpport, filename):
        self.master = master
        self.master.protocol("WM_DELETE_WINDOW", self.handler)
        self.currentTime = StringVar()
        self.lostRate = StringVar(value="0")
        self.createWidgets()
        self.serverAddr = serveraddr
        self.serverPort = int(serverport)
        self.rtpPort = int(rtpport)
        self.fileName = filename
        self.rtspSeq = 0
        self.sessionId = 0
        self.requestSent = -1
        self.teardownAcked = 0
        self.connectToServer()
        self.frameNbr = 0
        self.setupMovie()
        self.isSwitching = 0
        self.lostCnt = 0
        
    def createWidgets(self):
        """Build GUI."""
        # Create Setup button
        # self.setup = Button(self.master, width=20, padx=3, pady=3)
        # self.setup["text"] = "Setup"
        # self.setup["command"] = self.setupMovie
        # self.setup.grid(row=1, column=0, padx=2, pady=2)
        self.menu = Frame(self.master)
        self.menu.pack(side=BOTTOM)
        view = Frame(self.master)
        view.pack(side=TOP)
        # Create Play button      
        self.start = Button(self.menu, width=40, height=40, padx=3, pady=3, bg='white', activebackground='#00FFFF')
        playBtn = ImageTk.PhotoImage(Image.open('playbtn.png').resize((40, 40), Image.ANTIALIAS))
        self.start.config(image=playBtn)
        self.start.image = playBtn
        self.start["command"] = self.playMovie
        self.start.grid(row=1, column=1, padx=2, pady=2)
        
        # Create Pause button           
        self.pause = Button(self.menu, width=40, height=40, padx=3, pady=3, bg='white', activebackground='#00FFFF')
        pauseBtn = ImageTk.PhotoImage(Image.open('pauseBtn.png').resize((40, 40), Image.ANTIALIAS))
        self.pause.config(image=pauseBtn)
        self.pause["command"] = self.pauseMovie
        self.pause.image = pauseBtn
        self.pause.grid(row=1, column=2, padx=2, pady=2)
        
        # Create Teardown button
        self.teardown = Button(self.menu, width=40, height=40, padx=3, pady=3, bg='white', activebackground='#00FFFF')
        teardownBtn = ImageTk.PhotoImage(Image.open('teardownBtn.png').resize((40, 40), Image.ANTIALIAS))
        self.teardown.config(image=teardownBtn)
        self.teardown.image = teardownBtn
        self.teardown["command"] =  self.teardownMovie
        self.teardown.grid(row=1, column=3, padx=2, pady=2)
        

        # Create Backward button
        self.backward = Button(self.menu, width=40, height=40, padx=3, pady=3, bg='white', activebackground='#00FFFF')
        backwardBtn = ImageTk.PhotoImage(Image.open('backwardBtn.png').resize((40, 40), Image.ANTIALIAS))
        self.backward.config(image=backwardBtn)
        self.backward.image = backwardBtn
        self.backward["command"] = self.backwardMovie
        self.backward.grid(row=1, column=4, padx=2, pady=2)

        # Create Forward button
        self.forward = Button(self.menu, width=40, height=40, padx=3, pady=3, bg='white', activebackground='#00FFFF')
        forwardBtn = ImageTk.PhotoImage(Image.open('forwardBtn.png').resize((40, 40), Image.ANTIALIAS))
        self.forward.config(image=forwardBtn)
        self.forward.image = forwardBtn
        self.forward["command"] =  self.forwardMovie
        self.forward.grid(row=1, column=5, padx=2, pady=2)

        # Create Switch button
        self.switch = Button(self.menu, width=40, height=40, padx=3, pady=3, bg='white', activebackground='#00FFFF')
        switchBtn = ImageTk.PhotoImage(Image.open('switchBtn.png').resize((40, 40), Image.ANTIALIAS))
        self.switch.config(image=switchBtn)
        self.switch.image = switchBtn
        self.switch["command"] =  self.switchMovie
        self.switch.grid(row=1, column=6, padx=2, pady=2)

        # Create Reset button
        self.reset = Button(self.menu, width=40, height=40, padx=3, pady=3, bg='white', activebackground='#00FFFF')
        resetBtn = ImageTk.PhotoImage(Image.open('resetBtn.png').resize((40, 40), Image.ANTIALIAS))
        self.reset.config(image=resetBtn)
        self.reset.image = resetBtn
        self.reset["command"] =  self.resetConnect
        self.reset.grid(row=1, column=7, padx=2, pady=2)

        # Create a label to display the movie
        self.label = Label(view)
        self.label.pack()

        self.clock = Label(view, textvariable=self.currentTime)
        self.clock.pack(side=TOP)
        self.rate = Label(view, textvariable=self.lostRate)
        self.rate.pack(side=BOTTOM)
        
    
    def setupMovie(self):
        """Setup button handler."""
        if self.state == self.INIT:
            self.sendRtspRequest(self.SETUP)
        
    def resetConnect(self):
        if self.state == self.INIT:
            self.teardownAcked = 0
            self.rtspSeq = 0
            self.sessionId = 0
            self.requestSent = -1
            self.frameNbr = 0
            self.isSwitching = 0
            self.connectToServer()
            self.setupMovie()
            self.playMovie()

    def exitClient(self):
        """Teardown button handler."""
        self.sendRtspRequest(self.TEARDOWN)     
        self.master.destroy() # Close the gui window
        os.remove(CACHE_FILE_NAME + str(self.sessionId) + CACHE_FILE_EXT) # Delete the cache image from video

    def teardownMovie(self):
        self.sendRtspRequest(self.TEARDOWN)     
        # self.master.destroy() # Close the gui window
        os.remove(CACHE_FILE_NAME + str(self.sessionId) + CACHE_FILE_EXT) # Delete the cache image from video
    
    def pauseMovie(self):
        """Pause button handler."""
        if self.state == self.PLAYING:
            self.sendRtspRequest(self.PAUSE)
    
    def playMovie(self):
        """Play button handler."""
        if self.state == self.READY:
            # Create a new thread to listen for RTP packets
            threading.Thread(target=self.listenRtp).start()
            self.playEvent = threading.Event()
            self.playEvent.clear()
            self.sendRtspRequest(self.PLAY)
    
    def forwardMovie(self):
        if self.state == self.PLAYING:
            self.sendRtspRequest(self.FORWARD)

    def backwardMovie(self):
        if self.state == self.PLAYING:
            self.sendRtspRequest(self.BACKWARD)

    def switchMovie(self):
        self.sendRtspRequest(self.CHANGE)

    def listenRtp(self):        
        """Listen for RTP packets."""
        while True:
            try:
                data = self.rtpSocket.recv(20480)
                if data:
                    rtpPacket = RtpPacket()
                    rtpPacket.decode(data)
                    
                    currFrameNbr = rtpPacket.seqNum()
                    print("Current Seq Num: " + str(currFrameNbr))
                                        
                    if currFrameNbr > self.frameNbr or self.requestSent == self.BACKWARD: # Discard the late packet
                        self.currentTime.set("Total time: " + str(datetime.timedelta(seconds=self.frameNbr*0.05)))
                        if (currFrameNbr - self.frameNbr > 1):
                            self.lostCnt = self.lostCnt + currFrameNbr - self.frameNbr - 1
                        self.frameNbr = currFrameNbr
                        self.lostRate.set(value ="Lost rate: " + str(self.lostCnt/self.frameNbr * 100))
                        self.updateMovie(self.writeFrame(rtpPacket.getPayload()))

            except:
                # Stop listening upon requesting PAUSE or TEARDOWN
                if self.playEvent.isSet(): 
                    break
                
                # Upon receiving ACK for TEARDOWN request,
                # close the RTP socket
                if self.teardownAcked == 1:
                    self.rtpSocket.shutdown(socket.SHUT_RDWR)
                    self.rtpSocket.close()
                    break
                    
    def writeFrame(self, data):
        """Write the received frame to a temp image file. Return the image file."""
        cachename = CACHE_FILE_NAME + str(self.sessionId) + CACHE_FILE_EXT
        file = open(cachename, "wb")
        file.write(data)
        file.close()
        
        return cachename
    

    def updateMovie(self, imageFile):
        """Update the image file as video frame in the GUI."""
        photo = ImageTk.PhotoImage(Image.open(imageFile))
        self.label.configure(image = photo) 
        self.label.image = photo
    

    def connectToServer(self):
        """Connect to the Server. Start a new RTSP/TCP session."""
        self.rtspSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.rtspSocket.connect((self.serverAddr, self.serverPort))
        except:
            tkinter.messagebox.showwarning('Connection Failed', 'Connection to \'%s\' failed.' %self.serverAddr)
    
    def newRequest(self, request_type):
        """Build an RTSP Request header """
        request = "{} {} {}\n".format(request_type, self.fileName, HEADER_FIELD_PROTOCOL)
        request += "{}: {}\n".format(HEADER_FIELD_CSEQ, self.rtspSeq)
        if request_type == HEADER_REQUEST_TYPE_SETUP:
            request += "{} {}".format(HEADER_FIELD_RTP_OVER_UDP_PORT, self.rtpPort)
        else:
            request += "{}: {}".format(HEADER_FIELD_SESSION, self.sessionId)
        return request

    def sendRtspRequest(self, requestCode):
        """Send RTSP request to the server."""  

        # Setup request
        if requestCode == self.SETUP and self.state == self.INIT:
            threading.Thread(target=self.recvRtspReply).start()
            # Update RTSP sequence number.
            self.rtspSeq += 1
            # Write the RTSP request to be sent.
            request = self.newRequest(HEADER_REQUEST_TYPE_SETUP)
            # Keep track of the sent request.
            self.requestSent = self.SETUP

        # Play request
        elif requestCode == self.PLAY and self.state == self.READY:
            # Update RTSP sequence number.
            self.rtspSeq += 1
            # Write the RTSP request to be sent.
            request = self.newRequest(HEADER_REQUEST_TYPE_PLAY)
            # Keep track of the sent request.
            self.requestSent = self.PLAY

        # Forward request
        elif requestCode == self.FORWARD and self.state == self.PLAYING:
            # Update RTSP sequence number.
            self.rtspSeq += 1
            # Write the RTSP request to be sent.
            request = self.newRequest(HEADER_REQUEST_TYPE_FORWARD)
            # Keep track of the sent request.
            self.requestSent = self.FORWARD

        # Backward request
        elif requestCode == self.BACKWARD and self.state == self.PLAYING:
            # Update RTSP sequence number.
            self.rtspSeq += 1
            # Write the RTSP request to be sent.
            request = self.newRequest(HEADER_REQUEST_TYPE_BACKWARD)
            # Keep track of the sent request.
            self.requestSent = self.BACKWARD

        # Pause request
        elif requestCode == self.PAUSE and self.state == self.PLAYING:
            # Update RTSP sequence number.
            self.rtspSeq += 1
            # Write the RTSP request to be sent.
            request = self.newRequest(HEADER_REQUEST_TYPE_PAUSE)
            # Keep track of the sent request.
            self.requestSent = self.PAUSE
            
        # Teardown request
        elif requestCode == self.TEARDOWN and not self.state == self.INIT:
            # Update RTSP sequence number.
            self.rtspSeq += 1
            # Write the RTSP request to be sent.
            request = self.newRequest(HEADER_REQUEST_TYPE_TEARDOWN)
            # Keep track of the sent request.
            self.requestSent = self.TEARDOWN
        
        # Change request
        elif requestCode == self.CHANGE:
            # Update RTSP sequence number.
            self.rtspSeq += 1
            # Write the RTSP request to be sent.
            request = self.newRequest(HEADER_REQUEST_TYPE_CHANGE)
            # Keep track of the sent request.
            self.requestSent = self.CHANGE
        else:
            return
        
        # Send the RTSP request using rtspSocket.
        self.rtspSocket.send(request.encode())

        # Print the data sent to the console
        print('\nData sent:\n' + request)

    def recvRtspReply(self):
        """Receive RTSP reply from the server."""
        while True:
            reply = self.rtspSocket.recv(1024)
            
            if reply: 
                self.parseRtspReply(reply.decode("utf-8"))
                
            # Close the RTSP socket upon requesting Teardown
            if self.requestSent == self.TEARDOWN:
                self.rtspSocket.shutdown(socket.SHUT_RDWR)
                self.rtspSocket.close()
                break
            
                
    def parseRtspReply(self, data):
        """Parse the RTSP reply from the server."""
        lines = data.split('\n')
        seqNum = int(lines[1].split(' ')[1])
        
        # Process only if the server reply's sequence number is the same as the request's
        if seqNum == self.rtspSeq:
            session = int(lines[2].split(' ')[1])
            # New RTSP session ID
            if self.sessionId == 0:
                self.sessionId = session

            # Process only if the session ID is the same
            if self.sessionId == session:
                if int(lines[0].split(' ')[1]) == 200: 
                    if self.requestSent == self.SETUP:
                        # Update RTSP state.
                        self.state = self.READY

                        # Open RTP port.
                        self.openRtpPort()
                    elif self.requestSent == self.PLAY or self.requestSent == self.FORWARD or self.requestSent == self.BACKWARD:
                        self.state = self.PLAYING
                    elif self.requestSent == self.PAUSE:
                        self.state = self.READY
                        # The play thread exits. A new thread is created on resume.
                        self.playEvent.set()
                    elif self.requestSent == self.CHANGE:
                        self.state = self.SWITCH
                        # print(lines)
                        listfile = lines[3].split(' ')
                        listfile.pop()
                        for x in listfile:
                            if x == self.fileName:
                                idx = listfile.index(x)
                                if (idx != (len(listfile) - 1)):
                                    self.fileName = listfile[idx + 1]
                                else:
                                    self.fileName = listfile[0]
                                break
                        
                    elif self.requestSent == self.TEARDOWN:
                        self.state = self.INIT
                        # Flag the teardownAcked to close the socket.
                        self.teardownAcked = 1

    def openRtpPort(self):
        """Open RTP socket binded to a specified port."""
        # Create a new datagram socket to receive RTP packets from the server
        self.rtpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Set the timeout value of the socket to 0.5sec
        self.rtpSocket.settimeout(0.5)
        try:
            # Bind the socket to the address using the RTP port given by the client user
            self.rtpSocket.bind(('',self.rtpPort))
        except:
            tkinter.messagebox.showwarning('Unable to Bind', 'Unable to bind PORT=%d' %self.rtpPort)

    def handler(self):
        """Handler on explicitly closing the GUI window."""
        self.pauseMovie()
        if tkinter.messagebox.askokcancel("Quit?", "Are you sure you want to quit?"):
            self.exitClient()
        else: # When the user presses cancel, resume playing.
            self.playMovie()