import imutils
import math
import time

import Seed
import cv2
import numpy as np


######################################################################################
# read the video file and open file to write coordinates                             #
######################################################################################
cap = cv2.VideoCapture("./Input/CornAug9Video1.mp4")
f1 = open('./coords.txt', 'w+')
######################################################################################
# initialize variables                                                               #
######################################################################################
num_seeds = 0 # number of seeds
areaL = 400   # the lowest number of pixels that represents a seed (was 800, reduce due to erosion)

areaH = 8000  # the highest number of pixels that represent a seed

#give the user to input
#areaL = input("Please input areaL(min area of your object,default is 800):")
#should input of noise decreasing, bigger the number, less noise  
#denoise = input("Please input threshold to decrease noise (the bigger, noise will decrease,default is 40):")
denoise = 50 #MLN was 40
#delay_time = input("Input delay_time: ")
delay_time = 0
# initialize the first frame in the video stream
firstFrame = None

w_v = int(cap.get(3)) #get width of the video
h_v = int(cap.get(4)) #get height of the video
print("Video width: ", w_v, ", video height: ", h_v)

line_down2 = 600   # line2 to detect seeds
down_limit = int(9*h_v/10) 

font = cv2.FONT_HERSHEY_SIMPLEX
seeds = []
max_seeds_num = 5000
sid = 1
fc = 0
minDist = 9999.0

ave_flow_rate = 0
ave_flow_count = 0
total_flow = 0

###################################################################################### 
# Background subtraction                                                             #
###################################################################################### 
num_frame = 0               
while(cap.isOpened()):
    num_frame +=1
    ret, frame = cap.read()   #read a frame

    try:
        cv2.imwrite(str(fc) + "_1_frame.png", frame)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)   # convert to grayscale
        cv2.imwrite(str(fc) + "_2_gray_frame.png", gray)
        gray = cv2.GaussianBlur(gray, (5, 5), 0)       # gaussian blur to reduce noise #MLN was (21,21)
        cv2.imwrite(str(fc) + "_3_blur_frame.png", gray)

        # if this is the first frame, just initialize it and continue
        if firstFrame is None:
            firstFrame = gray
            continue

        # otherwise, compute the absolute difference between the current frame and first frame
        frame2 = cv2.absdiff(firstFrame,gray)        
        cv2.imwrite(str(fc) + "_4_absdiff_frame.png", frame2)

        ret,thresh1 = cv2.threshold(frame2,int(denoise),255,cv2.THRESH_BINARY) # decrease the noise
        cv2.imwrite(str(fc) + "_5_thresh_frame.png", thresh1)
        kernel = np.ones((5,5),np.uint8)

        #opening = cv2.erode(thresh1, kernel, iterations=1)
        #thresh1 = cv2.erode(thresh1, kernel, iterations=1)
        
        opening = cv2.morphologyEx(thresh1, cv2.MORPH_OPEN, kernel)
        cv2.imwrite(str(fc) + "_6_opening_frame.png", opening)
        #closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel)
        #cv2.imwrite(str(fc) + "_7_closing_frame.png", closing)

    # if there are no more frames, output number of seeds           
    except:
        #print("EOF")
        print('Number of seeds: ',num_seeds)
        break
    
    ##################################################################################
    # find contours and draw countour of each seed                                   #
    ##################################################################################
    #_, contours0, hierarchy = cv2.findContours(closing,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE) # detect contours

    _, contours0, hierarchy = cv2.findContours(opening,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE) # detect contours

    # compute predicted seed locations based on linear interpolation of previous two or three locations using downward trajectory
    
    for i in seeds:
            px = i.getX()
            if (ave_flow_rate > 0):
                py = i.getY() + ave_flow_rate
            else:
                py = i.getY() + 34
            i.setPX(px)
            i.setPY(py)
#            print('Seed (early) ', i, ' predicted x: ', px, ', y: ', py)

    # for each contour in the current frame
    cv2.drawContours(frame, contours0, -1, (255,0,0), 1)

    for cnt in contours0:
        area = cv2.contourArea(cnt)    # get the area of every contour, that is the area of the seed
        M = cv2.moments(cnt)           # get the moments to compute centroid

        # if the area is too small or too large, skip this contour
        if area< int(areaL) or area> int(areaH) :   
            continue

        # if the object fit our requirement then draw center of contour       
        cx = int(M['m10']/M['m00'])
        cy = int(M['m01']/M['m00'])
        cv2.circle(frame,(cx,cy), 16, (0,0,0), -1)

        # get the bounding rectangle and draw around the seed
        # x,y,w,h = cv2.boundingRect(cnt)
        # frame = cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2) 
        new = True   # treat as a new seed unless it follows an existing seed
        minDist = 9999.0
        minSeed = -1

        # determine if seed is new, within 5 added
        for i in seeds:
            if (cy > i.getY()-10) and (i.getState()<3):
                px = i.getPX()
                py = i.getPY()
                dist = long(math.sqrt((px-cx)*(px-cx)+(py-cy)*(py-cy)))
                if (dist<minDist):
                    minDist = dist
                    minSeed = i
                    new = False
#mln was 120
        if (minDist > 100):
            new = True
            
        if (new == False):
#            print('Min seed: ', minSeed.getId(), ' x: ', minSeed.getX(), ', y: ', minSeed.getY(), ' cx: ', cx, ', cy: ', cy)
            minSeed.fc = fc
#
            ave_flow_count +=1
            total_flow += (cy - minSeed.y)
            ave_flow_rate = total_flow/ave_flow_count
#                
            minSeed.updateCoords(cx,cy)
            minSeed.setPX(cx)  #MLN NEW
            minSeed.setPY(cy)  #MLN NEW

#mln was 100
        if (new == True) and (cy <= 600):
            p = Seed.MySeed(sid,cx,cy,max_seeds_num,fc)
            seeds.append(p)
            sid +=1
            num_seeds +=1

    ##################################################################################
    # output current seed count and seed positions                                   #
    ##################################################################################
    for i in seeds:
        i.setState(1)
        if (i.fc < fc):
            if (i.getY()<600) and (i.getX() < 2000) and (i.getY()>0) and (i.getX()>0):
                px = i.getX()
                py = i.getY()+30
                # f1.write(str(i.tracks[-1][0]) + ", " + str(i.tracks[-1][1]) + " to " + str(i.getX()) + ", " + str(i.getY()) + " -> " + str(px) + ", " + str(py) + "\n")
                i.fc = fc
                i.updateCoords(px,py)
                i.setState(2)
                # print('Not found seed: ', i.getId(), ', x: ', i.getX(), ', y: ', i.getY())
            else:
                px = i.getX()
                py = h_v - 1
                i.updateCoords(px,py)
                i.setDone()
                i.setState(3)
                # f1.write("Finish: " + str(i.getId()) + ": " + str(len(i.getTracks())) + "\n")
                
    for i in seeds:
        textSize = cv2.getTextSize(str(i.getId()), font, 0.5, 1)[0]
        if (i.getState()==2):
            cv2.circle(frame,(cx,cy), 16, (100,0,100), -1)

        cv2.putText(frame, str(i.getId()),(i.getX()-textSize[0]/2,i.getY()+textSize[1]/2),font,0.5,i.getRGB(),1,cv2.LINE_AA)
        if (i.getState()<3):
            f1.write(str(i.getId()) + ", " + str(i.getX()) + ", " + str(i.getY()) + ", " + str(i.getState()) + "\n")

    str_down2 = 'Frame: ' + str(fc) + ', Count: '+ str(num_seeds) + ', Ave Flow Rate: ' + str(ave_flow_rate)
    cv2.putText(frame, str_down2 ,(10,line_down2-20),font,0.8,(255,0,0),1,cv2.LINE_AA)
    
    frame = cv2.line(frame, (0,line_down2), (w_v,line_down2), (0,255,0), thickness=2) #draw a green line at midpoint

    cv2.imshow('Seed Count Application',frame)
    if (fc>155):
        cv2.imwrite(str(fc) + "_8_frame.png", frame)
        time.sleep(float(delay_time))
    fc = fc+1
    
    #Abort and exit with 'Q' or ESC
    k = cv2.waitKey(30) & 0xff
    if k == 27:
        break
    
cap.release() #release video file
cv2.destroyAllWindows() #close all openCV windows
