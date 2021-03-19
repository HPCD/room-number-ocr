#!/usr/bin/env python
#-*- coding:utf-8 -*-
"""
@author:abner
@file:get_red_rect.py
@ datetime:2020/10/23 15:51
@software: PyCharm
截取图片红色区域矩形框，即涂鸦区
"""
import cv2
import numpy as np
import logging
import uuid
import os
import datetime

dataset_dir = "./cut_region_img/"

def find_contours(src_img,gray_img):
    """
    给出原图和灰度图查找连通域
    cv2.findContours() 函数进行查找
    cv2.boundingRect获得坐标
    cv2.contourArea()获取面积
    """
    logging.info("Start find contours !!! ")

    # 过滤小于阈值的连通域
    threshold_area = 100
    # 查找连通域 必须是灰度图
    contours,_ = cv2.findContours(gray_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # 把所有的连通域显示出来
    # cv2.drawContours(src_img, contours, -1, (0, 255, 255), 2)
    # 查找最大连通域
    area = []
    max_area = 0
    img_path_list = []

    logging.info("contours num is : %s ",len(contours))
    epsilon = 20
    # 遍历所有的连通域
    for i in range(0, len(contours)):

        cnt = contours[i]
        # peri = cv2.arcLength(cnt, True)  # Calculating contour circumference
        approx = cv2.approxPolyDP(cnt, epsilon, True)

        if (len(approx)) < 4:
            continue
            # print("perit",peri)

        # 获得坐标框
        x, y, w, h = cv2.boundingRect(cnt)
        temp_are = (w)*(h)
        if temp_are > max_area:
            max_area = temp_are
            print(max_area,x,y,w,h)
            ob_x,ob_y,ob_w,ob_h = x, y, w, h

        # 获取面积
        ob_area = cv2.contourArea(cnt)
        # 面积大于1000才显示
        if ob_area > threshold_area:

            cut_img = src_img[y:y + h, x:x + w]

            now = datetime.datetime.now()

            time_dir = os.path.join(dataset_dir, str(now.strftime("%Y-%m-%d")))
            if not os.path.exists(time_dir):
                logging.info("Create dir for get red rect")
                os.mkdir(time_dir)
            logging.info("Save red region as image !!!")
            img_file = time_dir+"/" + str(uuid.uuid1()) + ".jpg"

            cv2.imwrite(img_file, cut_img)

            img_path_list.append(img_file)
            # print(img_file,"esle", len(approx))

            cv2.rectangle(src_img, (x, y), (x + w, y + h), (3, 122, 255), 4)


        area.append(cv2.contourArea(contours[i]))
        # if ob_area > max_area:
        #     # max_area = ob_area
        #     print("index ",i,max_area)

    # cv2.rectangle(src_img, (ob_x, ob_y), (ob_x + ob_w, ob_y + ob_h), (0, 0, 255), 4)
    logging.info("Return find contours !!!")
    return img_path_list

def extract_red_region(img_path):
    """
    返回找到的红色涂鸦区域
    :param img_path:
    :type img_path:
    :return:
    :rtype:
    """
    logging.info("Into extract_red_region")
    img = cv2.imread(img_path)

    # 转到HSV
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # 设置阈值
    l_blue = np.array([[0, 10, 120]])
    h_blue = np.array([15, 255, 255])
    low_range = np.array([0, 123, 100])
    high_range = np.array([5, 255, 255])
    # 构建掩模
    mask = cv2.inRange(hsv, l_blue, h_blue)
    # 进行位运算
    res = cv2.bitwise_and(img, img, mask=mask)

    gray = cv2.cvtColor(res, cv2.COLOR_BGR2GRAY)
    gray  = cv2.dilate(gray,cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)), iterations=1)



    logging.info("Return extract red region result !")
    return find_contours(img,gray)

if __name__ == '__main__':
    img_path = "D:/abner/project/dataset/QAOCR/2/113.jpg"
    # img_path = "D:/abner/project/pyproject/QAOCR/img/2020-11-03/eebd1782-1dad-11eb-8262-f875a4fc33a4.jpg"
    extract_red_region(img_path)