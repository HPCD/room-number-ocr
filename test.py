#!/usr/bin/env python
#-*- coding:utf-8 -*-
"""
@author:abner
@file:test.py
@ datetime:2021/3/18 18:20
@software: PyCharm

"""
import cv2
import base64
import requests
import datetime
import json

def test_roomnum_ocr():
    """
    车牌号码识别测试样例
    """
    # try:
    #     s = requests.session()
    #     s.keep_alive = False
    #     r = requests.get('https://api.github.com/events',verify=False,timeout=5)
    #     print("dffdf",r.text)
    # except Exception as e:
    #     print(e)
    car_img_path = 'D:\\abner\\project\\dataset\\room\\43.jpg'

    img = cv2.imread(car_img_path)
    img_encode = cv2.imencode('.jpg', img)[1]

    byte_image = str(base64.b64encode(img_encode))[2:-1]
    # print(byte_image)
    # post请求
    req = {"user_name": "yueyun", "device_id": "A1010", "image": byte_image}

    print(req)



    in_url = "https://open-api.gdii-yueyun.com/ai/room/oc"
    print("dfff")
    s = requests.session()
    s.keep_alive = False

    TOKEN = requests.post('https://open-api.gdii-yueyun.com/login',
                          json={"username": "AI", "password": "123456"},verify=False).json().get('data')
    # TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJBSSIsImV4cCI6MTYxNjE0ODY0MX0.rQ9jUzWRk7ERorEjSExs_JOWznD0lgZITgD85YyrOaQ"
    print("请求TOKEN！！")
    headers = {"AG-X-Access-Token": TOKEN, "Content-Type": 'application/json'}
    print(TOKEN)

    res = requests.post(in_url, headers=headers, json=req)
    stand_word = ["京NK2S29", "京PQV620", "京L·CM326"]

    # end_time = datetime.now()
    result = json.loads(res.text)
    print(result)
test_roomnum_ocr()