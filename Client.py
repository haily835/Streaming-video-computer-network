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
    
    # this function handle the click of user on SETUP button
    # Sent the SETUP request only if the current state is INIT
    def setupMovie(self):
        """Setup button handler."""
        if self.state == self.INIT:
            self.sendRtspRequest(self.SETUP)
    
    # this function handle the click of user on RESET button
    # it will reset the all attributes and reset the movie so that start another session
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

    # this function handles the click of user on close button
    # send a teardown request and close the app
    def exitClient(self):
        """Teardown button handler."""
        self.sendRtspRequest(self.TEARDOWN)     
        self.master.destroy() # Close the gui window
        os.remove(CACHE_FILE_NAME + str(self.sessionId) + CACHE_FILE_EXT) # Delete the cache image from video

    # this function handles the click of user on teardown button 
    # this funciton will send a teardown request and remove the cache file
    def teardownMovie(self):
        self.sendRtspRequest(self.TEARDOWN)     
        os.remove(CACHE_FILE_NAME + str(self.sessionId) + CACHE_FILE_EXT) # Delete the cache image from video
    
    # this function handles the click of user on pause button
    # send the pause request only if the current state is playing
    def pauseMovie(self):
        """Pause button handler."""
        if self.state == self.PLAYING:
            self.sendRtspRequest(self.PAUSE)
    
    # this function handles the click of user on play button
    # if the state is ready the it will create a new thread to listen on RTP packets, reset the flag (which will stop the loop) and send a play message
    def playMovie(self):
        """Play button handler."""
        if self.state == self.READY:
            # Create a new thread to listen for RTP packets
            threading.Thread(target=self.listenRtp).start()
            self.playEvent = threading.Event()
            self.playEvent.clear()
            self.sendRtspRequest(self.PLAY)
    
    # this function handles the click of user on forward button
    # send the forward request only if the current state is playing
    def forwardMovie(self):
        if self.state == self.PLAYING:
            self.sendRtspRequest(self.FORWARD)

    # this function handles the click of user on backward button
    # send the backward request only if the current state is playing
    def backwardMovie(self):
        if self.state == self.PLAYING:
            self.sendRtspRequest(self.BACKWARD)

    # this function handles the click of user on switch button
    # send the change request
    def switchMovie(self):
        self.sendRtspRequest(self.CHANGE)

    # create a while loop which continue to recive the rpt packet form the server
    # 1. Decode the packet
    # 2. Get the sequence number of this packet if it arrived late (less than the current frame) then ignore
    #     Get the total time by multiply the frameNum with the time that the server sent each image 0.05    
    # 3. However if the request sent is BACKWARD then accept the packet
    # 4. The loop will stop if the flag play event is set when user request PAUSE of TEARDOWN
    # 5. If the flag indicates TEARDOWN has been sent then close the rtp socket
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
                        self.frameNbr = currFrameNbr
                        self.updateMovie(self.writeFrame(rtpPacket.getPayload()))
                        self.currentTime.set(str(datetime.timedelta(seconds=self.frameNbr*0.05)))


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
    
    # receive the payload and write it to an image file used to update to the frame
    # create and return the fileName
    def writeFrame(self, data):
        """Write the received frame to a temp image file. Return the image file."""
        cachename = CACHE_FILE_NAME + str(self.sessionId) + CACHE_FILE_EXT
        file = open(cachename, "wb")
        file.write(data)
        file.close()
        
        return cachename
    
    # this function receive the image file name, and change the frame 
    def updateMovie(self, imageFile):
        """Update the image file as video frame in the GUI."""
        photo = ImageTk.PhotoImage(Image.open(imageFile))
        self.label.configure(image = photo) 
        self.label.image = photo
    
    # create a socket to connect to the server to send requests
    def connectToServer(self):
        """Connect to the Server. Start a new RTSP/TCP session."""
        self.rtspSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.rtspSocket.connect((self.serverAddr, self.serverPort))
        except:
            tkinter.messagebox.showwarning('Connection Failed', 'Connection to \'%s\' failed.' %self.serverAddr)
    
    # generate the string contains the request with suitable format
    def newRequest(self, request_type):
        """Build an RTSP Request header """
        request = "{} {} {}\n".format(request_type, self.fileName, HEADER_FIELD_PROTOCOL)
        request += "{}: {}\n".format(HEADER_FIELD_CSEQ, self.rtspSeq)
        if request_type == HEADER_REQUEST_TYPE_SETUP:
            request += "{} {}".format(HEADER_FIELD_RTP_OVER_UDP_PORT, self.rtpPort)
        else:
            request += "{}: {}".format(HEADER_FIELD_SESSION, self.sessionId)
        return request

    # send the rtsp request to server through the Rtsp socket 
    # check the requested code (which is generated when users click on buttons) and the current state
    # increase sequence number
    # keep track of the request has been sent
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

    # create a loop to receive the reply from the server
    # parse the reply
    # if the request has been sent is TEARDOWN then it will close the rtsp socket and stop the loop 
    def recvRtspReply(self):
        """Receive RTSP reply from the server."""
        while True:
            # buffer size is 1024
            reply = self.rtspSocket.recv(1024)
            
            if reply: 
                self.parseRtspReply(reply.decode("utf-8"))
                
            # Close the RTSP socket upon requesting Teardown
            if self.requestSent == self.TEARDOWN:
                self.rtspSocket.shutdown(socket.SHUT_RDWR)
                self.rtspSocket.close()
                break
            
    # this function is to parse the reply from the server
    # 1. Separate each line of the reply
    # 2. Get the sequence number in the second line at the second word of the reply
    # 3. Compare with the sequence number of the request and proccess only if they are the same 
    # 3.a. Get the session number at the third line of the reply
    # 3.b. If the sessionId is 0 (that is the case is when the setup request and the server return a random session Id) then assign the sessionId of the client
    # 3.c. Otherwise the sessionId of the server reply should be the same as the client:
    # 3.c. If reply code is 200 Ok (which is at the first line and the second word)
    # 3.c. If the request sent is SETUP: change state to READY and open rtp socket to receive the 
    # 3.c. If the request sent is PLAY or FORWARD or BACKWARD then change state to PLAYING
    # 3.c. If the request sent is PAUSE then change the state to READY and set the flag to stop the play listen
    # 3.c. If the request sent is CHANGE then change the state to SWITCH and from the reply get the list of videos file and then set the fileName to the file after the playing video in the list
    # 3.c. If the request sent is TEARDOWN then set state to INIT and raise the flag to close the rtp socket
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

    # Open the RTP socket to receive the packets contains frame over UDP,
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

    # 1. Pause the video
    # 2. Open a box for the user to confirm
    def handler(self):
        """Handler on explicitly closing the GUI window."""
        self.pauseMovie()
        if tkinter.messagebox.askokcancel("Quit?", "Are you sure you want to quit?"):
            self.exitClient()
        else: # When the user presses cancel, resume playing.
            self.playMovie()