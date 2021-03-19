#!/usr/bin/env python
#-*- coding:utf-8 -*-
"""
@author:abner
@file:app.py.py
@ datetime:2020/8/17 9:58
@software: PyCharm

"""
import sys
import os

project_root = os.getcwd()
sys.path.append(project_root)
sys.path.append(project_root+"/src")
sys.path.append(project_root+'/src/ai/')
from flask import Flask,request
import json
import sys
import base64
import cv2
import numpy as np
import uuid
import datetime
import logging
from logging.handlers import TimedRotatingFileHandler
import re


import numpy as np

import cv2


from src.ai.paddle_ocr import predict
import os





#解决跨域
from flask_cors import CORS

app = Flask(__name__,static_url_path='/static')

from flask_request_params import bind_request_params
app.before_request(bind_request_params)
# 通过设置跨域完成，否则ajax请求success不执行
cors = CORS(app,supports_credentials=True)



def log():
    """
     save log file and console print
    :return:
    """
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    # fh = logging.FileHandler("hander.log")
    LOG_PATH = 'log/'
    fh = TimedRotatingFileHandler(filename=LOG_PATH+"room_num_ocr.txt", when="D", interval=1, backupCount=7)
    fh.suffix = "%Y-%m-%d_%H-%M.log"
    fh.extMatch = re.compile(r"^\d{4}-\d{2}-\d{2}_\d{2}-\d{2}.log$")
    ch = logging.StreamHandler()
    formatter = logging.Formatter(('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    logger.addHandler(fh)

def get_room_number_info(img_name):
    """
    门牌号码识别

    """
    info_dict = {}
    #获取识别结果
    src_dt_boxes, src_rec_res = predict(img_name)

    rec_length = len(src_rec_res)

    if rec_length == 0:
        return info_dict
    address = ""
    # 遍历所有的文本，结构化返回结果
    for line in src_rec_res:
        #组合
        address += line[0]
    return address



@app.route('/ai/room/ocr',methods=['POST'])
def get_room_number_ocr():
    """
    门牌号
    """
    dataset_dir = "./img/"
    try:

        logging.info("Get the request %s",request)
        data = request.get_data()
        params_data = json.loads(data)
        logging.info("json_data ")
        user_name = params_data['user_name']
        device_id = params_data['device_id']
        img_base64 = params_data['image']

        ##data:image/jpeg;base64,
        reg = r'^data:[a-z]+/[a-z]+;base64,'
        tag = re.findall(reg, img_base64)

        if len(tag)==1:
            img_base64 = img_base64.replace(tag[0], "")
            logging.info("new img_base64 %s",tag)


        if user_name is None:
            result = {"code": "E000","success":False, "message": "key error"}
            logging.info("key %s error", 'user_name')
            return json.dumps(result, ensure_ascii=False)

        if img_base64 is None:
            result = {"code": "E000", "success":False, "message": "key error"}
            logging.info("key image error")
            return json.dumps(result, ensure_ascii=False)

        if device_id is None:
            result = {"code": "E000", "success":False, "message": "key error"}
            logging.info("key device_id error")
            return json.dumps(result, ensure_ascii=False)


        # 1. save request info
        # 1M = 1024*1024 = 1038336
        img_mb = sys.getsizeof(img_base64) / 1038336
        #限定 10 M
        if img_mb > 10:
            result = {"code": "E000", "success":False, "message": "img is larger than 10 M"}
            logging.info("img > 10 M")
            return json.dumps(result, ensure_ascii=False)

        #decode image base64
        npstr = base64.b64decode(img_base64)
        img_array = np.frombuffer(npstr, np.uint8)
        nparr_re = cv2.imdecode(img_array, cv2.COLOR_RGB2BGR)
        img_id = str(uuid.uuid1())
        img_name = img_id + ".jpg"

        now = datetime.datetime.now()
        create_time = now.strftime("%Y-%m-%d %H:%M:%S")

        time_dir = os.path.join(dataset_dir, str(now.strftime("%Y-%m-%d")))
        # date as save image dir
        if not os.path.exists(time_dir):
            os.mkdir(time_dir)
        # save image on year-month-day
        save_img_name = time_dir + "/" + img_name
        logging.info("Decode request image and save !")
        cv2.imwrite(save_img_name, nparr_re)


        #预测结果
        room_number_info = get_room_number_info(save_img_name)
        #空结果直接返回
        if room_number_info is None:
            result = {"code": "E000", "success": True, "message": "success", "data": room_number_info}
            logging.info("result %s", result)
            return json.dumps(result, ensure_ascii=False)

        logging.info("Extract red region num is %s",room_number_info)


        result = {"code": "E000", "success": True, "message": "success", "data": {'content':room_number_info}}
        logging.info("result %s", result)
        return json.dumps(result, ensure_ascii=False)


    except Exception as e:
        logging.info(" error  %s", e)
        result = {"code": "E000", "success":False, "message": "error"}
        return json.dumps(result, ensure_ascii=False)


if __name__ == "__main__":
    log()
    app.run(host="0.0.0.0",port=32666,threaded=False)