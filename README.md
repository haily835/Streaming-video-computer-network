# streamer
A python3 video streaming client and server with RSTP and RTP
python Server.py 1025
python ClientLauncher.py 127.0.0.1 1025 1025 movie.Mjpeg

> Note that you have to increase the size of the maximum allowed UDP datagram for this to work, on MacOS this can be done as follows: 

```
$ sudo sysctl -w net.inet.udp.maxdgram=65535
net.inet.udp.maxdgram: 9216 -> 65535`
```
