# assumption: camera is fixed
# How?: only image processing, no model required
# ToDo: locate all parking spaces and figure out if they are vacant or not
# we plan to manually select region of interests beacuse parking spaces are not uniform
# and camera is not at perfect birds eye view.
# Contour detection has overhead, so we have not used it in this particular use case

import cv2
import pickle
import cvzone
import numpy as np

# Video feed
cap = cv2.VideoCapture('carPark.mp4')

with open('CarParkPos', 'rb') as f:
    posList = pickle.load(f)

width, height = 107, 48


def checkParkingSpace(inputImage):
    spaceCounter = 0

    for pos in posList:
        x, y = pos

        imgCrop = inputImage[y:y + height, x:x + width]
        # cv2.imshow(str(x * y), imgCrop)#to find out individual images of the parking slots
        count = cv2.countNonZero(imgCrop)


        if count < 900:
            color = (0, 255, 0)
            thickness = 5
            spaceCounter += 1
        else:
            color = (0, 0, 255)
            thickness = 2

        cv2.rectangle(img, pos, (pos[0] + width, pos[1] + height), color, thickness)

        cvzone.putTextRect(img, str(count), (x, y + height - 3), scale=0.8,
                           thickness=2, offset=0, colorR=color)

    cvzone.putTextRect(img, f'Free: {spaceCounter}/{len(posList)}', (100, 50), scale=2,
                           thickness=2, offset=20, colorR=(0,0,0))
while True:

    if cap.get(cv2.CAP_PROP_POS_FRAMES) == cap.get(cv2.CAP_PROP_FRAME_COUNT):
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        #check if current frame = total frame - reset the frames, looping of the video

    success, img = cap.read()
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    imgBlur = cv2.GaussianBlur(imgGray, (3, 3), 1)
    imgThreshold = cv2.adaptiveThreshold(imgBlur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                         cv2.THRESH_BINARY_INV, 25, 16)
    imgMedian = cv2.medianBlur(imgThreshold, 5)#getting rid of salt pepper noise
    kernel = np.ones((3, 3), np.uint8)#kernel for dilate
    imgDilate = cv2.dilate(imgMedian, kernel, iterations=1) #thin to thick

    checkParkingSpace(imgDilate)
    cv2.imshow("Image", img)
    # cv2.imshow("ImageBlur", imgBlur)
    # cv2.imshow("ImageThres", imgMedian)
    if cv2.waitKey(10) & 0xFF == ord('q'):
        break