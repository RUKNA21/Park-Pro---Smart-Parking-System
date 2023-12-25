#Make list of all parking spaces

import cv2
import pickle 
# to save positions of all parking spaces in order to bring it back to main.py

width, height = 18, 8 
# first found height, width for leftmost parking space by hit and trial

try:
    with open('CarParkPos', 'rb') as f:
        posList = pickle.load(f)
except:
    posList = []


def mouseClick(events, x, y, flags, params):
    if events == cv2.EVENT_LBUTTONDOWN:
        posList.append((x, y))
    if events == cv2.EVENT_RBUTTONDOWN:
        for i, pos in enumerate(posList):
            x1, y1 = pos
            if x1 < x < x1 + width and y1 < y < y1 + height:
                posList.pop(i)

    with open('CarParkPos', 'wb') as f:
        pickle.dump(posList, f)


while True:
    img = cv2.imread('carParkImg1.png')
    for pos in posList:
        cv2.rectangle(img, pos, (pos[0] + width, pos[1] + height), (255, 255, 255), 1)

    cv2.imshow("Image", img)
    cv2.setMouseCallback("Image", mouseClick)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break