#!/usr/bin/env python3

from av.video.frame import VideoFrame
import numpy as np
import cv2
v=VideoFrame(5,5)
a=v.to_ndarray(format="bgr24")
print(a)


bottom_frame = np.full(shape=[80, 800, 3], fill_value=1)
#cv2.imshow("aaa",a)

cv2.imshow("aaa",bottom_frame)
cv2.waitKey(0)
cv2.destroyAllWindows()

