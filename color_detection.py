
from collections import deque
from imutils.video import VideoStream
import numpy as np
import argparse
import cv2
import imutils
import time
import paho.mqtt.client as mqtt

import math

hata=[]

kamera=cv2.VideoCapture(0)


dusuk_sari=np.array([20,50,50])
yuksek_sari=np.array([40,255,255])

dusuk_mavi=np.array([90,50,50])
yuksek_mavi=np.array([125,255,255])

dusuk_kirmizi=np.array([2,50,50])
yuksek_kirmizi=np.array([10,255,255])

pts = deque()
counter = 0
(dX, dY) = (0, 0)
direction = ""

def orantısal_degisim(goruntu,yuzde=75):
    genislik=int(goruntu.shape[1]+40)
    uzunluk=int(goruntu.shape[0])
    boyut=(genislik,uzunluk)
    return cv2.resize(goruntu,boyut,interpolation=cv2.INTER_AREA)

def sari_tespit(sari,kare):
    cnts = cv2.findContours(sari.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)

    center = None

    if len(cnts) > 0:
        # find the largest contour in the mask, then use
        # it to compute the minimum enclosing circle and
        # centroid
        c = max(cnts, key=cv2.contourArea)
        global s_radius
        global w_yellow
        ((x, y), s_radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        
        try:
            w_yellow=int(M["m10"] / M["m00"])
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
        except ZeroDivisionError as hata:
            print("Moment noktaları 0")



        #print("Sarı Nesne Yarıçapı",s_radius)



    try:
        if s_radius > 10:
            # draw the circle and centroid on the frame,
            # then update the list of tracked points
            cv2.circle(kare, (int(x), int(y)), int(s_radius),
                       (0, 255, 255), 2)
            cv2.circle(kare, center, 5, (0, 0, 255), -1)
            pts.appendleft(center)
    except:
        print("Sarı Nesne Bulunamadı")



def mavi_tespit(mavi,kare):
    cnts = cv2.findContours(mavi.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)

    center = None

    if len(cnts) > 0:
        # find the largest contour in the mask, then use
        # it to compute the minimum enclosing circle and
        # centroid
        c = max(cnts, key=cv2.contourArea)
        global m_radius
        global w_blue
        ((x, y), m_radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        
        try:
            w_blue=int(M["m10"] / M["m00"])
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
        except ZeroDivisionError as hata:
            print("Moment noktaları 0")


        #print("Mavi Nesne Yarıçapı",m_radius)



    try:
        if m_radius > 1:
            # draw the circle and centroid on the frame,
            # then update the list of tracked points
            cv2.circle(kare, (int(x), int(y)), int(m_radius),
                       (0, 255, 255), 2)
            cv2.circle(kare, center, 5, (0, 0, 255), -1)
            pts.appendleft(center)
    except:
        print("Mavi Nesne Bulunamadı")


def kirmizi_tespit(kirmizi,kare):
    cnts = cv2.findContours(kirmizi.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)

    center = None

    if len(cnts) > 0:
        # find the largest contour in the mask, then use
        # it to compute the minimum enclosing circle and
        # centroid
        c = max(cnts, key=cv2.contourArea)
        global k_radius
        global w_red
        ((x, y), k_radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        
        try:
            w_red=int(M["m10"] / M["m00"])
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
        
        except ZeroDivisionError as hata:
        
            print("Moment noktaları 0")





        #print("Kırmızı Nesne Yarıçapı",k_radius)



    try:
        if k_radius > 1:
            # draw the circle and centroid on the frame,
            # then update the list of tracked points
            cv2.circle(kare, (int(x), int(y)), int(k_radius),
                       (0, 255, 255), 2)
            cv2.circle(kare, center, 5, (0, 0, 255), -1)
            pts.appendleft(center)
    except:
        print("Kırmızı Nesne Bulunamadı")







def main():
    while True:
        ret,kare=kamera.read()



        kare=orantısal_degisim(kare)
        
        gri_kare=cv2.cvtColor(kare,cv2.COLOR_BGR2GRAY)

        hsv=cv2.cvtColor(kare,cv2.COLOR_BGR2HSV)

        sari=cv2.inRange(hsv,dusuk_sari,yuksek_sari)
        mavi=cv2.inRange(hsv,dusuk_mavi,yuksek_mavi)
        kirmizi = cv2.inRange(hsv, dusuk_kirmizi, yuksek_kirmizi)

        cv2.imshow("HSV UZAYI",hsv)
        cv2.imshow("Maske",sari)
        cv2.imshow("Maske", mavi)
        cv2.imshow("Maske", kirmizi)



        sari_tespit(sari,kare)

        mavi_tespit(mavi,kare)

        kirmizi_tespit(kirmizi,kare)

        yellow_distance=4200/s_radius
        red_distance=4200/k_radius
        blue_distance=4200/m_radius
        
        print("Sarı nesne Uzaklık",yellow_distance)
        print("mavi nesne uzaklık",blue_distance)
        print("Kırmızı nesne uzaklık",red_distance)

        red_priority=math.sqrt((5**2)+red_distance**2)
        blue_priority=math.sqrt((10**2)+blue_distance**2)
        yellow_priority=math.sqrt((15**2)+yellow_distance**20)
        client = mqtt.Client()
        client.connect("mqtt.thingspeak.com", 1883, 60)
        channelId = "798955"  
        api_key = 'UZGXGZ34RRLWP3AU'
        data_1 = red_priority
        data_2 = yellow_priority
        data_3 = blue_priority
        publish_path = "channels/" + channelId + "/publish/" + api_key
        publish_data = "field1=" + str(data_1) + "&field2=" + str(data_2)+ "&field3=" + str(data_3)
        client.publish(publish_path, publish_data)
        client.loop(2)

        # print("Sarı nesne Uzaklık", yellow_priority)
        # print("mavi nesne uzaklık", blue_priority)
        # print("Kırmızı nesne uzaklık", red_priority)

        priority_ofobject=[red_priority,blue_priority,yellow_priority]

        if min(priority_ofobject)==red_priority:
            kirmizi_tespit(kirmizi,kare)
            print("RED OBJECT PRIORITY")

            if w_red > 350:
                print("Kırmızı Nesne Solda","Mesafe: {}".format(red_distance))



            elif w_red < 250:
                print("Kırmızı Nesne Sağda","Mesafe: {}".format(red_distance))


            else:
                print("Kırmızı Nesne Ortada","Mesafe: {}".format(red_distance))

        elif min(priority_ofobject)==blue_priority:
            mavi_tespit(mavi,kare)
            print("BLUE OBJECT PRIORITY")
            if w_red > 350:
                print("Mavi Nesne Solda","Mesafe: {}".format(blue_distance))



            elif w_red < 250:
                print("Mavi Nesne Sağda","Mesafe: {}".format(blue_distance))


            else:
                print("Mavi Nesne Ortada","Mesafe: {}".format(blue_distance))

        elif min(priority_ofobject)==yellow_priority:
            sari_tespit(sari,kare)
            print("YELLOW OBJECT PRIORITY")
            if w_red > 350:
                print("Sari Nesne Solda","Mesafe: {}".format(yellow_distance))



            elif w_red < 250:
                print("Sari Nesne Sağda","Mesafe: {}".format(yellow_distance))


            else:
                print("Sari Nesne Ortada","Mesafe: {}".format(yellow_distance))

        else:
            kirmizi_tespit(kirmizi, kare)
            print("RED OBJECT PRIORITY")

            if w_red > 350:
                print("Kırmızı Nesne Solda", "Mesafe: {}".format(red_distance))



            elif w_red < 250:
                print("Kırmızı Nesne Sağda", "Mesafe: {}".format(red_distance))


            else:
                print("Kırmızı Nesne Ortada", "Mesafe: {}".format(red_distance))


        cv2.imshow("ekran",kare)

        if cv2.waitKey(25) & 0xFF==ord('q'):
            break

    kamera.release()
    cv2.destroyWindow()

if __name__ == '__main__':
    main()
  