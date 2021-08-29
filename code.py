import os
import subprocess
import numpy as np
import cv2
import matplotlib.pyplot as plt
import time
import random
from PIL import Image
import pytesseract
from pytesseract.pytesseract import prepare
"""
模擬器:藍牛排 5 64bit
解析度:1920*1080

bell pos :[(25,85),(40,100)]
"""
#path
phone_y_bias = 150
bell = 'bell.jpg'
notjoin = 'notjoin.jpg'
join = 'join.jpg'
next_btu = 'next.jpg'
leave = 'leave.jpg'
prepare = 'prepare.jpg'
fail = 'fail.jpg'
redbtu = 'redbtu.jpg'


pytesseract.pytesseract.tesseract_cmd = r"C:/Program Files/Tesseract-OCR/tesseract.exe"

class pos:
    def __init__(self,x1,x2,y1,y2):
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1 + phone_y_bias
        self.y2 = y2 + phone_y_bias
        
bell_pos = pos(25,120,15,100)
missionInfo_pos = pos(330,815,600,655)
notjoin_pos = pos(80,500,1650,1750)
join_pos = pos(575,1000,1650,1750)
prepare_pos = pos(320,755,1420,1550)
finish_nextstep_pos = pos(375,700,1850,1930) 
leave_pos = pos(160,480,1850,1930)
redbtu_pos = pos(460,625,1690,1850)

mode = 'wait'

timeout = 500
threshold = 0.6
device_ip = 'L8AIB760R374YBF'


def adb_shell(cmd,device=None):
    if device is None:
        res = subprocess.Popen('adb '+cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,encoding='utf8')
    else:
        res = subprocess.Popen('adb -s '+device+' '+cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,encoding='utf8')
    result = res.stdout.read()  
    res.wait()  
    res.stdout.close() 
    if res.poll() == 0:
        return result.replace('\r\n','\n')
    else:
        return '-1'

def adb_screenshot(device):
    res = subprocess.Popen('adb -s '+device+' shell screencap -p', shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    result = res.stdout.read()  
    res.wait()  
    res.stdout.close() 
    if res.poll() == 0:
        return  cv2.imdecode(np.frombuffer(result.replace(b'\r\n',b'\n'), np.uint8), cv2.IMREAD_UNCHANGED)               
    else:
        return '-1'

def calculate(image1, image2):
    # 灰度直方圖算法
    # 計算單通道的直方圖的相似值
    hist1 = cv2.calcHist([image1], [0], None, [256], [0.0, 255.0])
    hist2 = cv2.calcHist([image2], [0], None, [256], [0.0, 255.0])
    # 計算直方圖的重合度
    degree = 0
    for i in range(len(hist1)):
        if hist1[i] != hist2[i]:
            degree = degree + \
                (1 - abs(hist1[i] - hist2[i]) / max(hist1[i], hist2[i]))
        else:
            degree = degree + 1
    degree = degree / len(hist1)
    return degree


def classify_hist_with_split(image1, image2, size=(256, 256)):
    # RGB每個通道的直方圖相似度
    # 將圖像resize後，分離爲RGB三個通道，再計算每個通道的相似值
    image1 = cv2.resize(image1, size)
    image2 = cv2.resize(image2, size)
    sub_image1 = cv2.split(image1)
    sub_image2 = cv2.split(image2)
    sub_data = 0
    for im1, im2 in zip(sub_image1, sub_image2):
        sub_data += calculate(im1, im2)
    sub_data = sub_data / 3
    return sub_data

def sim(img1,img2):
    return classify_hist_with_split(img1,img2)


def picture_cut(img,pos):
    #img[start_y:start_y+hight,start_x:start_x+width]
    if pos == 'bell':
        return img[bell_pos.y1:bell_pos.y2,bell_pos.x1:bell_pos.x2]
    elif pos == 'missionInfo':
        return img[missionInfo_pos.y1:missionInfo_pos.y2,missionInfo_pos.x1:missionInfo_pos.x2]
    elif pos == 'next':
        return img[finish_nextstep_pos.y1:finish_nextstep_pos.y2,finish_nextstep_pos.x1:finish_nextstep_pos.x2]
    elif pos == 'leave':
        return img[leave_pos.y1:leave_pos.y2,leave_pos.x1:leave_pos.x2]
    elif pos == 'redbtu':
        return img[redbtu_pos.y1:redbtu_pos.y2,redbtu_pos.x1:redbtu_pos.x2]
    else:
        return img

def random_touch_pos(pos):
    if pos == 'bell':
        return (random.randint(bell_pos.x1,bell_pos.x2),random.randint(bell_pos.y1,bell_pos.y2))
    elif pos == 'notjoin':
        return (random.randint(notjoin_pos.x1,notjoin_pos.x2),random.randint(notjoin_pos.y1,notjoin_pos.y2))
    elif pos == 'join':
        return (random.randint(join_pos.x1,join_pos.x2),random.randint(join_pos.y1,join_pos.y2))
    elif pos == 'next':
        return (random.randint(finish_nextstep_pos.x1,finish_nextstep_pos.x2),random.randint(finish_nextstep_pos.y1,finish_nextstep_pos.y2))
    elif pos == 'leave':
        return (random.randint(leave_pos.x1,leave_pos.x2),random.randint(leave_pos.y1,leave_pos.y2))
    elif pos == 'prepare':
        return (random.randint(prepare_pos.x1,prepare_pos.x2),random.randint(prepare_pos.y1,prepare_pos.y2))
    else:
        return (0,0)

def IsCorrectMission(img,missions):
    mission = picture_cut(img,'missionInfo')
    mission_text = OCR(mission)
    #plt.imshow(mission)
    #plt.show()
    print('OCR : '+mission_text)
    for temp in missions:
        if mission_text.find(temp) != -1:

            #光廢龍
            if temp == '伊魯梅塔雷伊':
                if mission_text.find('高級十') != -1:
                    return True

            if mission_text.find('超級') != -1:
                return True
            else:
                print('Error:不是超級')
                return False
    print('Error:關卡錯誤')
    return False

def OCR(image):
    text = pytesseract.image_to_string(cv2.resize(image,(500,50),interpolation=cv2.INTER_CUBIC), lang='chi_tra',config=r'--psm 6')
    return text



print(adb_shell('kill-server'))
print(adb_shell('version'))
print(adb_shell('connect '+device_ip))
print(adb_shell('devices'))
#read picture
Bell = cv2.imread(bell)
Notjoin = cv2.imread(notjoin)
Join = cv2.imread(join)
Next = cv2.imread(next_btu)
Leave = cv2.imread(leave)
Prepare = cv2.imread(prepare)
Fail = cv2.imread(fail)
Redbtu = cv2.imread(redbtu)


missions = ['遺跡魔像','爾之長','母親','不死族','伊魯梅塔雷伊']
count = 1

while True:
    time.sleep(0.87)



    if mode == 'wait':
        screenshot = adb_screenshot(device_ip)
        rate = sim(Bell,picture_cut(screenshot,'bell'))
        if rate <= threshold :        
            print('鈴鐺相似度:'+str(rate))
            time.sleep(0.1)
        else:
            print('鈴鐺相似度:'+str(rate)+' 任務辨識中...')
            mode = 'choose'
            ranX,ranY = random_touch_pos('bell')
            adb_shell('shell input tap '+str(ranX)+' '+str(ranY),device_ip)
    elif mode == 'choose':
        screenshot = adb_screenshot(device_ip)
        if IsCorrectMission(screenshot,missions):
            print('進入任務')
            ranX,ranY = random_touch_pos('join')
            adb_shell('shell input tap '+str(ranX)+' '+str(ranY),device_ip)
            time.sleep(2)
            ranX,ranY = random_touch_pos('prepare')
            adb_shell('shell input tap '+str(ranX)+' '+str(ranY),device_ip)
            mode = 'mission'
        else:
            print('拒絕任務')
            ranX,ranY = random_touch_pos('notjoin')
            adb_shell('shell input tap '+str(ranX)+' '+str(ranY),device_ip)
            mode = 'wait'
    elif mode == 'mission':
        screenshot = adb_screenshot(device_ip)
        im = picture_cut(screenshot,'next')
        rate = sim(Next,im)
        count += 1
        if count % 60 == 0:
            adb_shell('shell input tap 1 1',device_ip)#避免螢幕進入休眠 每60S?案一下螢幕
            count = 1
            time.sleep(0.5)
        if rate <= threshold:
            time.sleep(1)
            failsim = sim(Redbtu,picture_cut(screenshot,'redbtu'))
            if failsim >= threshold:
                print('進入失敗')
                mode = 'wait'
            #print('任務中'+str(rate))
        else:
            print('分數計算 '+str(rate))
            mode = 'score'
            ranX,ranY = random_touch_pos('next')
            adb_shell('shell input tap '+str(ranX)+' '+str(ranY),device_ip)
    elif mode == 'score':
        screenshot = adb_screenshot(device_ip)
        rate = sim(Next,picture_cut(screenshot,'next'))
        if rate <= threshold:
            time.sleep(0.1)
        else:
            print('分數結算 '+str(rate))
            mode = 'item'
            ranX,ranY = random_touch_pos('next')
            adb_shell('shell input tap '+str(ranX)+' '+str(ranY),device_ip)
    elif mode == 'item':
        screenshot = adb_screenshot(device_ip)
        rate = sim(Next,picture_cut(screenshot,'next'))
        if rate <= threshold:
            time.sleep(0.1)
        else:
            print('物品結算 '+str(rate))
            mode = 'leave'
            ranX,ranY = random_touch_pos('next')
            adb_shell('shell input tap '+str(ranX)+' '+str(ranY),device_ip)
    elif mode == 'leave':
        screenshot = adb_screenshot(device_ip)
        imm = picture_cut(screenshot,'leave')
        rate = sim(Leave,imm)
        if rate <= threshold:
            time.sleep(0.1)
        else:
            print('結束 '+str(rate))
            mode = 'wait'
            ranX,ranY = random_touch_pos('leave')
            adb_shell('shell input tap '+str(ranX)+' '+str(ranY),device_ip)
    


    
    

    

    


