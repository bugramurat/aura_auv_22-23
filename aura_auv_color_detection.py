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
    size = (640, 480)
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
            while (True):
                if firstTime:
                    print('First time launching...')
                # # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ARDUINO~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                    time.sleep(0.1)  # wait for arduino to answer
                    while arduino.inWaiting() == 0:
                        pass
                    if arduino.inWaiting() > 0:
                        depth = arduino.readline()
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
                        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                        # define mask
                        red_lower = np.array([156, 0, 125], np.uint8)
                        red_upper = np.array([196, 158, 255], np.uint8)
                        red_mask = cv2.inRange(hsv, red_lower, red_upper)
                        kernal = np.ones((5, 5), "uint8")
                        # For red color
                        red_mask = cv2.dilate(red_mask, kernal)
                        red = cv2.bitwise_and(frame, frame, mask=red_mask)
                        # Creating contour to track red color
                        contours_red, hierarchy_red = cv2.findContours(red_mask,
                                                                       cv2.RETR_TREE,
                                                                       cv2.CHAIN_APPROX_SIMPLE)

                        line_x = 0
                        area_red = 0

                        for cnt_red in contours_red:
                            area_red = cv2.contourArea(cnt_red)
                            if area_red > 500:
                                (x, y, w, h) = cv2.boundingRect(cnt_red)
                                bb_width = w
                                bb_height = h
                                frame = cv2.rectangle(
                                    frame, (x, y), (x+w, y+h), (0, 255, 0), 4)

                                cv2.putText(frame, str(area_red), (x, y),
                                            cv2.FONT_HERSHEY_SIMPLEX, 1.0,
                                            (0, 255, 0), 2)

                                line_x = int((x + x + w) / 2)
                                line_y = int((y + y + h) / 2)

                                print(str(area_red))

                                if (x_medium+100 >= line_x >= x_medium-100 and area_red >= 80000):
                                    print('sit\n')
                                    arduino.write(b'5')
                                    # arduino kodunda 47s delay oldugu icin
                                    time.sleep(47)
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
                        cv2.imshow("RED", frame)
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
