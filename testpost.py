#!/usr/bin/env python
#-*- coding:utf-8 -*-
"""
@author:abner
@file:testpost.py
@ datetime:2020/8/26 16:45
@software: PyCharm

"""
import cv2
import base64
import requests
import unittest
from datetime import  datetime
import json
import os
#内部测试地址
in_url_ip = "http://10.74.150.75:32666"
 # 测试环境外部访问地址
# out_url_ip = "http://ai.gdii-yueyun.com:30067/"
# out_url_ip ="http://10.16.153.31:32488/"
out_url_ip = "http://ai.gdii-yueyun.com:30092"
docker_ip = "http://10.16.153.36:32088/"
ip = "http://10.200.117.108:32088/"


class DriverLicenseRequestUnitTest(unittest.TestCase):

    def test_roomnum_ocr(self):
        """
        车牌号码识别测试样例
        """

        car_img_path = 'D:\\abner\\project\\dataset\\room\\43.jpg'

        img = cv2.imread(car_img_path)
        img_encode = cv2.imencode('.jpg', img)[1]

        byte_image = str(base64.b64encode(img_encode))[2:-1]
        # print(byte_image)
        #post请求
        req = {"user_name": "yueyun", "device_id": "A1010", "image": byte_image}

        print(req)
        start_time = datetime.now()


        in_url = docker_ip+"/ai/room/ocr"

        in_url = "https://open-api.gdii-yueyun.com/ai/room/ocr"
        print("dfff")
        TOKEN = requests.post('https://open-api.gdii-yueyun.com/login',
                              json={"username": "AI", "password": "123456"},verify=True).json().get('data')

        print("请求TOKEN！！")
        headers = {"AG-X-Access-Token": TOKEN, "Content-Type": 'application/json'}
        print(TOKEN)

        res = requests.post(in_url,headers=headers, json=req)

        result = json.loads(res.text)
        print(result)





if __name__ == "__main__":
    unittest.main()
