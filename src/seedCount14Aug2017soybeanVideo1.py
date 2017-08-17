import cv2
import numpy as np
import imutils
import math
import time
import Seed
######################################################################################
# read the video file and open file to write coordinates                             #
######################################################################################
cap = cv2.VideoCapture("../test-videos/normal/seed-counter-brown-seeds.mp4")
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
denoise = 40 #MLN was 50 - denoise helps with low light, but still problematic...
#delay_time = input("Input delay_time: ")
delay_time = 0
# initialize the first frame in the video stream
firstFrame = None
dst = None

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

ave_area = 0
ave_area_count = 0
total_area = 0

MAX_FRAME = 510
MIN_FRAME = 80

frmPath_normal = "../frames/normal/"
frmPath_grayscale = "../frames/grayscale/"
frmPath_blur = "../frames/blur/"
frmPath_absdiff = "../frames/absdiff/"
frmPath_threshold = "../frames/threshold/"
frmPath_opening = "../frames/opening/"
frmPath_predicted = "../frames/predictedframe/"
###################################################################################### 
# Background subtraction                                                             #
###################################################################################### 
num_frame = 0               
while(cap.isOpened()):
    num_frame +=1
    ret, frame = cap.read()   #read a frame

    try:
        # only to rotate
        # frame = imutils.rotate(frame, 270)

        if (fc>=MIN_FRAME) and (fc<=MAX_FRAME):
            cv2.imwrite(frmPath_normal + str(fc) + "_1_frame.png", frame)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)   # convert to grayscale
        if (fc>=MIN_FRAME) and (fc<=MAX_FRAME):
            cv2.imwrite(frmPath_grayscale + str(fc) + "_2_gray_frame.png", gray)
        gray = cv2.GaussianBlur(gray, (5, 5), 0)       # gaussian blur to reduce noise #MLN was (21,21)
        if (fc>=MIN_FRAME) and (fc<=MAX_FRAME):
            cv2.imwrite(frmPath_blur + str(fc) + "_3_blur_frame.png", gray)

        # if this is the first frame, just initialize it and continue
        if firstFrame is None:
            firstFrame = gray
            continue

        # otherwise, compute the absolute difference between the current frame and first frame
        frame2 = cv2.absdiff(firstFrame,gray)        
        if (fc>=MIN_FRAME) and (fc<=MAX_FRAME):
            cv2.imwrite(frmPath_absdiff + str(fc) + "_4_absdiff_frame.png", frame2)

        ret,thresh1 = cv2.threshold(frame2,int(denoise),255,cv2.THRESH_BINARY)

        #thresh2 = cv2.adaptiveThreshold(frame2,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,\
        #    cv2.THRESH_BINARY,11,2)

        if (fc>=MIN_FRAME) and (fc<=MAX_FRAME):
            cv2.imwrite(frmPath_threshold + str(fc) + "_5_thresh_frame.png", thresh1)
        kernel = np.ones((5,5),np.uint8)

        # opening = cv2.erode(thresh1, kernel, iterations=1)
        #thresh1 = cv2.erode(thresh1, kernel, iterations=1)
        
        opening = cv2.morphologyEx(thresh1, cv2.MORPH_OPEN, kernel)
        if (fc>=MIN_FRAME) and (fc<=MAX_FRAME):
            cv2.imwrite(frmPath_opening + str(fc) + "_6_opening_frame.png", opening)

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

    if (True):
        for i in seeds:
            px = i.getX()
            if (ave_flow_rate > 0):
                py = i.getY() + ave_flow_rate
            else:
                py = i.getY() + 34
            i.setPX(px)
            i.setPY(py)
            if (i.done==False):
                i.age_one()
                print('Seed: ', i.getId(), ' predicted x: ', px, ', y: ', py, ', age: ', i.age, ', updates: ', i.updates)

                if ((i.age == i.max_age) and (i.age > i.updates + 4)):
                    num_seeds -=1
                    i.setDone()
                    print('Seed: ', i.getId(), ' REMOVED')
                    cv2.circle(frame,(px,py), 4, (0, 0, 64), -1) 
                    cv2.putText(frame, str(i.getId()),(px+textSize[0]/2,py+textSize[1]/2),font,0.5,(255,255,255),1,cv2.LINE_AA)
                else:
                    cv2.circle(frame,(px,py), 4, (125, 0, 64), -1) 
                    cv2.putText(frame, str(i.getId()),(px+textSize[0]/2,py+textSize[1]/2),font,0.5,(255,255,255),1,cv2.LINE_AA)

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
            cv2.circle(frame,(cx,cy), 10, (0,0,0), -1)

            print('Contour: ', cx, ', ', cy)
            
            # get the bounding rectangle and draw around the seed
            # x,y,w,h = cv2.boundingRect(cnt)
            # frame = cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2) 
            new = True   # treat as a new seed unless it follows an existing seed
            minDist = 9999.0
            minSeed = -1

            # determine if seed is new, within 5 added
            for i in seeds:
                if (i.done == True):
                    continue
                if (cy > i.getY()-10) and (i.getState()<3) and (i.fc < fc):
                    px = i.getPX()
                    py = i.getPY()
                    dist = long(math.sqrt((px-cx)*(px-cx)+(py-cy)*(py-cy)))
                    if (dist<minDist):
                        minDist = dist
                        minSeed = i
                        new = False

            #mln was 100 for 120 fps
            if (minDist > 200):
                new = True
            
            if (new == False):
                # print('Min seed: ', minSeed.getId(), ' x: ', minSeed.getX(), ', y: ', minSeed.getY(), ' cx: ', cx, ', cy: ', cy)
                minSeed.fc = fc

                ave_flow_count +=1
                total_flow += (cy - minSeed.y)
                ave_flow_rate = total_flow/ave_flow_count

                ave_area_count +=1
                total_area += int(area)
                ave_area = total_area/ave_area_count

                minSeed.updateCoords(cx,cy)
                #minSeed.setPX(cx)  #MLN NEW
                #minSeed.setPY(cy)  #MLN NEW

            if (new == True) and (cy <= 600):
                p = Seed.MySeed(sid,cx,cy,8,fc)
                p.setPX(cx)
                p.setPY(cy)
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
                    # f1.write(str(i.tracks[-1][0]) + ", " + str(i.tracks[-1][1]) + " to " + str(i.getX()) +
                    ## ", " + str(i.getY()) + " -> " + str(px) + ", " + str(py) + "\n")
                    i.fc = fc
                    i.updatePrediction(px,py)
                    i.setState(2)
                    # print('Not found seed: ', i.getId(), ', x: ', i.getX(), ', y: ', i.getY())
                else:
                    px = i.getX()
                    py = h_v - 1
                    i.updatePrediction(px,py)
                    i.setDone()
                    i.setState(3)
                    # f1.write("Finish: " + str(i.getId()) + ": " + str(len(i.getTracks())) + "\n")
                
        for i in seeds:
            textSize = cv2.getTextSize(str(i.getId()), font, 0.5, 1)[0]
            px = i.getPX()
            py = i.getPY()
            if (i.getState()<2):
                cv2.circle(frame,(cx,cy), 10, (100,0,100), -1)
                cv2.putText(frame, str(i.getId()),(i.getX()-textSize[0]/2,i.getY()+textSize[1]/2),font,0.5,(0,255,0),1,cv2.LINE_AA)

            if (i.getState()<3):
                f1.write(str(i.getId()) + ", " + str(i.getX()) + ", " + str(i.getY()) + ", " + str(i.getState()) + "\n")

        str_down2 = 'Frame: ' + str(fc) + ', Count: '+ str(num_seeds) + ', Ave Flow Rate: ' + str(ave_flow_rate) + ', Ave Area: ' + str(ave_area)
        cv2.putText(frame, str_down2 ,(10,line_down2-20),font,0.8,(255,0,0),1,cv2.LINE_AA)
    
        frame = cv2.line(frame, (0,line_down2), (w_v,line_down2), (0,255,0), thickness=2) #draw a green line at midpoint

        cv2.imshow('Seed Count Application',frame)
        if (fc>=MIN_FRAME) and (fc<=MAX_FRAME):
            cv2.imwrite(frmPath_predicted + str(fc) + "_7_frame.png", frame)
            time.sleep(float(delay_time))

    fc = fc+1
    
    #Abort and exit with 'Q' or ESC
    k = cv2.waitKey(30) & 0xff
    if k == 27:
        break
    
cap.release() #release video file
cv2.destroyAllWindows() #close all openCV windows
