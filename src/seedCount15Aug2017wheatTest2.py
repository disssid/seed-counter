import cv2
import numpy as np
import imutils
import math
import time
import Seed
import sys

############################################################################
# open the video file and text file to log coordinates                     #
############################################################################
cap = cv2.VideoCapture("../test-videos/translucent-plain/fast/seed-counter-wheat.mp4")

try:
    cap = cv2.VideoCapture("../test-videos/translucent-plain/" + sys.argv[4] + "/seed-counter-" + sys.argv[3] + ".mp4")
except IndexError:
    pass

f1 = open('./coords.txt', 'w+')
############################################################################
# initialize variables                                                     #
############################################################################
num_seeds = 0     # number of seeds
areaL = 400       # the lowest number of pixels that represents a seed
areaH = 8000      # the highest number of pixels that represent a seed
denoise = 50      # used for Gaussian blur
delay_time = 0    # amount of time delay between frames (sec)
firstFrame = None # first frame used as background

try:
    areaL = sys.argv[1]
except IndexError:
    pass

try:
    areaH = sys.argv[2]
except IndexError:
    pass
    
w_v = int(cap.get(3)) #get width of the video
h_v = int(cap.get(4)) #get height of the video
print("Video width: ", w_v, ", video height: ", h_v)
print("areaL : ", areaL, ", areaH : ", areaH)
down_limit = int(0.9*h_v) # process contours from 0 down to this line (previously used due to seeds bouncing back) 

font = cv2.FONT_HERSHEY_SIMPLEX

seeds = []            # array of seeds
sid = 1               # seed id           
fc = 0                # frame count
minDist = w_v+h_v     # minimum distance between contour and a seed

ave_flow_rate = 0     # average seed flow rate in pixels per frame
ave_flow_count = 0    # number of samples counted to compute average flow rate
total_flow = 0        # total flow for all samples

ave_area = 0          # average size of contours in pixels
ave_area_count = 0
total_area = 0

MAX_FRAME = 440       # last frame to record information for
MIN_FRAME = 230       # first frame to record information for
VERBOSE = False        # output intermediate images
FINAL_FRAME = False    # output final image frame with seeds and contours noted on original image
NEW_THRESHOLD = 200   # minimum size for contour to be considered as a seed
PREDICT_ON = False     # mark predicted locations on images output
MOD_VAL = 1           # process frames with fc % MOD_VAL == MOD_OFFSET (if MOD_VAL=1, MOD_OFFSET=0, then process all)
MOD_OFFSET = 0
FRAME_PATH = "../frames" #the directory location to store different frames

############################################################################ 
# Process frames                                                           #
############################################################################ 
num_frame = 0               
while(cap.isOpened()):
    num_frame +=1
    ret, frame = cap.read()   #read a frame

    try:
        # only to rotate
        # frame = imutils.rotate(frame, 270)

        if (fc>=MIN_FRAME) and (fc<=MAX_FRAME) and (VERBOSE==True):
            cv2.imwrite(FRAME_PATH + "normal/" + str(fc) + "_1_frame.png", frame)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)   # convert to grayscale
        if (fc>=MIN_FRAME) and (fc<=MAX_FRAME) and (VERBOSE==True):
            cv2.imwrite(FRAME_PATH + "grayscale/" + str(fc) + "_2_gray_frame.png", gray)
        gray = cv2.GaussianBlur(gray, (5, 5), 0)       # small Gaussian blur to reduce noise
        if (fc>=MIN_FRAME) and (fc<=MAX_FRAME) and (VERBOSE==True):
            cv2.imwrite(FRAME_PATH + "blur/" + str(fc) + "_3_blur_frame.png", gray)

        # if this is the first frame, just initialize firstFrame and continue
        if firstFrame is None:
            firstFrame = gray
            continue

        # otherwise, compute the absolute difference between the current frame and firstFrame
        frame2 = cv2.absdiff(firstFrame,gray)        
        if (fc>=MIN_FRAME) and (fc<=MAX_FRAME) and (VERBOSE==True):
            cv2.imwrite(FRAME_PATH + "absdiff/" + str(fc) + "_4_absdiff_frame.png", frame2)

        # compute binary threshold, bits 0-denoise are black, (denoise+1) to 255 are white.
        ret,thresh1 = cv2.threshold(frame2,int(denoise),255,cv2.THRESH_BINARY)

        # other thresholding algorithms perform about the same...
        # thresh2 = cv2.adaptiveThreshold(frame2,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,\
        #    cv2.THRESH_BINARY,11,2)

        if (fc>=MIN_FRAME) and (fc<=MAX_FRAME) and (VERBOSE==True):
            cv2.imwrite(FRAME_PATH + "threshold/" + str(fc) + "_5_thresh_frame.png", thresh1)
        kernel = np.ones((5,5),np.uint8)

        # eroding doesn't help much...
        # opening = cv2.erode(thresh1, kernel, iterations=1)
        # thresh1 = cv2.erode(thresh1, kernel, iterations=1)
        
        opening = cv2.morphologyEx(thresh1, cv2.MORPH_OPEN, kernel)
        if (fc>=MIN_FRAME) and (fc<=MAX_FRAME) and (VERBOSE==True):
            cv2.imwrite(FRAME_PATH + "opening/" + str(fc) + "_6_opening_frame.png", opening)

    # if there are no more frames, output number of seeds           
    except:
        #print("EOF")
        print('Number of seeds: ',num_seeds)
        print('Average Area: ', ave_area)
        break
    
    ########################################################################
    # find contours and draw countour of each seed                         #
    ########################################################################
    #_, contours0, hierarchy = cv2.findContours(closing,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE) # detect contours

    _, contours0, hierarchy = cv2.findContours(opening,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE) # detect contours

    # compute predicted seed locations based on previous location and average flow rate

    if (fc%MOD_VAL==MOD_OFFSET):
        for i in seeds:
            px = i.getX()
            if (ave_flow_rate > 0):
                py = i.getY() + ave_flow_rate
            else:
                py = i.getY() + 34 # this value could be estimated based on previous runs, or just use 1
            i.setPX(px)
            i.setPY(py)
            if (i.done==False):
                i.age_one()
                print('Seed: ', i.getId(), ' predicted x: ', px, ', y: ', py, ', age: ', i.age, ', updates: ', i.updates)

                # if seed has aged too much while not being assigned to a contour, then kill it and remove it from the count
                # seed.age is number of frames since the seed was assigned, and seed.updates is the number of times assigned
                if ((i.age >= i.max_age) and (i.age > i.updates + 4) and (i.updates < i.max_age)):
                    num_seeds -=1
                    i.setDone()
                    print('Seed: ', i.getId(), ' REMOVED')
                    # note removed seed on the output image
                    if (PREDICT_ON == True):
                        cv2.circle(frame,(px,py), 4, (0, 0, 64), -1) 
                        cv2.putText(frame, str(i.getId()),(px+textSize[0]/2,py+textSize[1]/2),font,0.5,(255,255,255),1,cv2.LINE_AA)
                else:
                    # note predicted location on the output image
                    if (PREDICT_ON == True):
                        cv2.circle(frame,(px,py), 4, (125, 0, 64), -1) 
                        cv2.putText(frame, str(i.getId()),(px+textSize[0]/2,py+textSize[1]/2),font,0.5,(255,255,255),1,cv2.LINE_AA)

        # for each contour in the current frame
        cv2.drawContours(frame, contours0, -1, (255,0,0), 1)

        if (ave_flow_rate > 0):
            NEW_THRESHOLD = 4 * ave_flow_rate
            
        for cnt in contours0:
            area = cv2.contourArea(cnt)    # get the area of every contour, that is the area of the seed
            M = cv2.moments(cnt)           # get the moments to compute centroid

            # if the area is too small or too large, skip this contour
            if area< int(areaL) or area> int(areaH) :   
                continue

            # if the object fit our requirement then draw center of contour in black      
            cx = int(M['m10']/M['m00'])
            cy = int(M['m01']/M['m00'])
            cv2.circle(frame,(cx,cy), 10, (0,0,0), -1)

            print('Contour: ', cx, ', ', cy)
            
            # get the bounding rectangle and draw around the seed
            # x,y,w,h = cv2.boundingRect(cnt)
            # frame = cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2) 
            new = True   # treat as a new seed unless it follows an existing seed
            minDist = w_v+h_v # initialize the minimum distance as width + height - this will be more than any Euclidean distance
            minSeed = -1      # initialize closest seed to non seed (-1)

            # determine if seed is new, within 5 added
            for i in seeds:
                # if seed has been removed, don't consider it
                if (i.done == True):
                    continue
                # if contour is below or nearly below current seed and seed is not done and not marked (i.fc==fc) then consider it.
                if (cy > i.getY()-10) and (i.getState()<3) and (i.fc < fc):
                    px = i.getPX()
                    py = i.getPY()
                    dist = long(math.sqrt((px-cx)*(px-cx)+(py-cy)*(py-cy)))
                    if (dist<minDist):
                        minDist = dist
                        minSeed = i
                        new = False

            if (minDist > NEW_THRESHOLD):
                new = True
            
            if (new == False):
                # print('Min seed: ', minSeed.getId(), ' x: ', minSeed.getX(), ', y: ', minSeed.getY(), ' cx: ', cx, ', cy: ', cy)
                minSeed.fc = fc # mark the seed as assigned to a contour

                ave_flow_count +=1
                total_flow += (cy - minSeed.y) # distance traveled
                ave_flow_rate = total_flow/ave_flow_count

                ave_area_count +=1
                total_area += int(area)
                ave_area = total_area/ave_area_count

                minSeed.updateCoords(cx,cy) # set the current x and y values of the seed

            if (new == True) and (cy <= down_limit):
                p = Seed.MySeed(sid,cx,cy,8,fc) # create a new seed and append it to the list
                p.setPX(cx)
                p.setPY(cy)
                seeds.append(p)
                sid +=1
                num_seeds +=1

        ########################################################################
        # output current seed count and seed positions                         #
        ########################################################################
        for i in seeds:
            i.setState(1)
            if (i.fc < fc):
                if (i.getY()<=down_limit) and (i.getY()>0) and (i.getX()>0):
                    px = i.getX()
                    py = i.getY()+30
                    i.updatePrediction(px,py)
                    i.fc = fc
                    i.setState(2)
                else:
                    px = i.getX()
                    py = h_v - 1
                    i.updatePrediction(px,py)
                    i.setDone()
                    i.setState(3)
                
        for i in seeds:
            textSize = cv2.getTextSize(str(i.getId()), font, 0.5, 1)[0]
            px = i.getPX()
            py = i.getPY()
            if (i.getState()<2):
                #cv2.circle(frame,(cx,cy), 10, (100,0,100), -1)
                cv2.putText(frame, str(i.getId()),(i.getX()-textSize[0]/2,i.getY()+textSize[1]/2),font,0.5,(0,255,0),1,cv2.LINE_AA)

            if (i.getState()<3):
                f1.write(str(i.getId()) + ", " + str(i.getX()) + ", " + str(i.getY()) + ", " + str(i.getState()) + "\n")

        str_down2 = 'Frame: ' + str(fc) + ', Count: '+ str(num_seeds) + ', Ave Flow Rate: ' + str(ave_flow_rate) + ', Ave Area: ' + str(ave_area)
        cv2.putText(frame, str_down2 ,(10,down_limit-20),font,0.8,(255,0,0),1,cv2.LINE_AA)
    
        frame = cv2.line(frame, (0,down_limit), (w_v,down_limit), (0,255,0), thickness=2) #draw a green line at midpoint

        cv2.imshow('Seed Count Application',frame)
        if (fc>=MIN_FRAME) and (fc<=MAX_FRAME) and ((FINAL_FRAME==True) or (VERBOSE==True)):
            cv2.imwrite(FRAME_PATH + "predictedframe/" + str(fc) + "_7_frame.png", frame)

        time.sleep(float(delay_time))

    fc = fc+1
    
    #Abort and exit with 'Q' or ESC
    k = cv2.waitKey(30) & 0xff
    if k == 27:
        break
    
cap.release() #release video file
cv2.destroyAllWindows() #close all openCV windows
