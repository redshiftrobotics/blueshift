from v4l2_camera import Camera
import cv2
import numpy as np
import time

c = Camera("/dev/video0",1920,1080,4)

num_images = 100
start = time.time()
latency = 0

for i in range(num_images):
    frame = c.get_frame()
    latency += time.time() - frame.timestamp
    #print(len(img))
    #print(img)
    #cv2.imwrite("cam-" + str(i) + ".jpg",cv2.imdecode(np.array(list(img)),-1))
end = time.time()
print("total time:",end-start)
print("fps: ",num_images/(end-start))
print("average latency:", latency/num_images)