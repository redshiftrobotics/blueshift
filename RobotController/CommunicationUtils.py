import simplejson as json
import time
import socket
import base64
import cv2
import time

CAM_PORT = 6666
CNTLR_PORT = 6665
SNSR_PORT = 6664
AIR_PORT = 6663

EARTH_IP = '169.254.219.238'
WATER_IP = '169.254.210.218'

SIMPLE_EARTH_IP = "localhost"

def packet(tag="",data="",timestamp=0,metadata="",highPriority=False):
	dataPacket = {
		"tag": tag,
		"data": data,
		"timestamp": float(timestamp),
		"metadata": metadata,
		"highPriority": highPriority
	}
	return dataPacket

def sendMsg(sckt, pckt):
	""" Send a JSON message through a socket

		Arguments:
			sckt: socket to send data through
			pckt: packet to be sent

		Returns:
			The sent message
	"""
	data = json.dumps(pckt)
	msgLen = len(data)
	msg = str(msgLen)+data
	sckt.sendall(msg.encode())
	return msg

def recvMsg(conn,timeout=2):
	""" Recieve a JSON message from a socket

		Messages should be formatted as msgLength|messageContents

		Arguments:
			conn: the socket to receive data through
			timeout: (optional) the maximum amount of time to wait before canceling

		Returns:
			The received message
	"""
	lengthMarker = b'|'
	numChars = 2

	now = time.time()
	lastChar = conn.recv(numChars, socket.MSG_PEEK)[-1:]
	while(lastChar != lengthMarker):
		numChars += 1
		lastChar = conn.recv(numChars, socket.MSG_PEEK)[-1:]

	bMsgLength = conn.recv(numChars, socket.MSG_PEEK)
	iMsgLength = int(bMsgLength[:-1])
	iTotalLength = iMsgLength+len(bMsgLength)
	while(len(conn.recv(iTotalLength, socket.MSG_PEEK))<iTotalLength):
		time.sleep(0.001)
		if (time.time()-now) > timeout:
			raise Exception("recvMsg Timeout of {} was reached".format(timeout))

	conn.recv(numChars)
	recv = conn.recv(iMsgLength-1)
	return json.loads(str(recv.decode()))

def encodeImage(image):
    """ Encodes an image in Base64

        Arguemnts:
            image: image to encode

        Returns:
            The Base64 encoded image
    """
    retval, bffr = cv2.imencode('.jpg', image)
    return bffr.tobytes()

def clearQueue(qToClear, debug=False):
	if debug:
		print("Left in Queue:")
	while not qToClear.empty():
		if debug:
			print(qToClear.get())
		else:
			qToClear.get()
