from time import sleep
import time
import cv2
import numpy as np
import serial
import datetime

try:
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~depth analysis~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    firstTime = True
    depth = 0
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~depth analysis~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~OPENCV~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    x_medium = 320
    y_medium = 240
    size = (640,480)
    capture = cv2.VideoCapture(0)
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~OPENCV~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~CAM RECORDING~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    t = datetime.datetime(2000, 1, 1, 0, 0)
    date_update = str((datetime.datetime.now()-t).total_seconds())
    video_cod = cv2.VideoWriter_fourcc(*'XVID')
    video_output = cv2.VideoWriter(f'{date_update}.avi',
                        video_cod,
                        30,
                        size)
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~CAM RECORDING~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ARDUINO~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    with serial.Serial("/dev/ttyUSB0", 9600, timeout=1) as arduino:
        time.sleep(0.1)  # wait for serial to open
        if arduino.isOpen():
            arduino.setDTR(False)
            time.sleep(1)
            arduino.flushInput()
            arduino.setDTR(True)
            time.sleep(2)
            print("{} connected!".format(arduino.port))
            # capture frames from the camera
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ARDUINO~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            while(True):
                if firstTime:
                    print('firsttime girdi')
                # # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ARDUINO~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                    time.sleep(0.1)  # wait for arduino to answer
                    while arduino.inWaiting() == 0:
                        pass
                    if arduino.inWaiting() > 0:
                        depth = arduino.readline()
                        startDepth = depth
                        print('Start depth: ' + str(depth))
                    arduino.write(b'8')
                    time.sleep(5)
                # # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ARDUINO~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                    time.sleep(0.1)  # wait for arduino to answer
                    print('..#.. The AUV fixing at the calculated depth...')
                    firstTime = False
                else:	
                    ret, frame = capture.read()
                    if ret:
                        grayFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                        blurFrame = cv2.medianBlur(grayFrame, 5)

                        circles = cv2.HoughCircles(blurFrame,cv2.HOUGH_GRADIENT,1,700,
                                                    param1=180,param2=5,minRadius=25,maxRadius=400)

                        line_x =0
                        area_circle = 0

                        if circles is not None:
                            circles = np.uint16(np.around(circles))
                            for i in circles[0,:]:
                                # draw the outer circle
                                cv2.circle(frame,(i[0],i[1]),i[2],(0,255,0),2)
                                # draw the center of the circle
                                cv2.circle(frame,(i[0],i[1]),2,(0,0,255),3)

                                line_x = int(i[0])
                                line_y = int(i[1])
                                area_circle = int(3.14 * (i[2]*i[2]))

                                print(str(area_circle))

                                cv2.putText(frame, str(area_circle), (line_x, line_y),
                                            cv2.FONT_HERSHEY_SIMPLEX, 1.0,
                                            (0, 255, 0), 2)

                                if (x_medium+100 >= line_x >= x_medium-100 and area_circle >= 100000):
                                    print('go\n')
                                    arduino.write(b'5')
                                    time.sleep(47) # arduino kodunda 47s delay oldugu icin
                                elif (x_medium+100 >= line_x >= x_medium-100):
                                    print('center\n')
                                    arduino.write(b'1')
                                elif (line_x > x_medium+100):
                                    print('->>>  right\n')
                                    arduino.write(b'3')
                                elif (line_x < x_medium-100):
                                    print('<<<-  left\n')
                                    arduino.write(b'2')

                                
                        else:
                            print('null\n')
                            arduino.write(b'7')

                        video_output.write(frame)
                        cv2.imshow("DAIRE", frame)
                    # # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ARDUINO~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                        time.sleep(0.1)  # wait for arduino to answer
                        while arduino.inWaiting() == 0:
                            pass
                        if arduino.inWaiting() > 0:
                            depth = arduino.readline()
                            print('Depth: ' + str(depth))
                        arduino.flushInput()  # remove data after reading
                        time.sleep(0.1)
                    # # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ARDUINO~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                        k = cv2.waitKey(1) & 0xFF
                        if k == 27:
                            break
    capture.release()
    video_output.release()
    cv2.destroyAllWindows()
except KeyboardInterrupt:
        print('Interrupted... \n Vehicle is closing...')
        arduino.write(b'4')
