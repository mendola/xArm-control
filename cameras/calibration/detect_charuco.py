import time
import cv2
import numpy as np
import pdb
import sys

def find_charuco(fname):
    allCorners = []
    allIds = []
    dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)

    board = cv2.aruco.CharucoBoard_create(3,3,.025,.0125,dictionary)
    #full_img = board.draw((200*3,200*3))
    full_img = cv2.imread(fname,cv2.IMREAD_GRAYSCALE) #board.draw((200*3,200*3))

   # sub_imgs = np.array([full_img[200:399,400:599],full_img[200:399,0:199],full_img[400:599,200:399],full_img[0:199,200:399]])
    #cv2.imwrite("charucos.png",img)

    corners, ids, somthing_else = cv2.aruco.detectMarkers(full_img,board.dictionary)

    #if len(corners[0]) > 0:
    #    res2 = cv2.aruco.interpolateCornersCharuco(corners[0],corners[1],full_img,board)
    #    if res2[1] is not None and res2[2] is not None and len(res2[1])>3:
    #        allCorners.append(res2[1])
    #        allIds.append(res2[2])
    cv2.aruco.drawDetectedMarkers(full_img,corners, ids)
    print("Found %d markers." % len(corners))
    cv2.imshow("charuco",full_img)
    cv2.waitKey(0)
    pdb.set_trace()
    cv2.destroy
    

if __name__ == "__main__":
    find_charuco(sys.argv[1])
