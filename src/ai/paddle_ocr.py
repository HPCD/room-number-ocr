#!/usr/bin/env python
#-*- coding:utf-8 -*-
"""
@author:abner
@file:paddle_ocr.py
@ datetime:2020/10/29 11:05
@software: PyCharm

"""
import sys
import os
__dir__ = os.path.dirname(os.path.abspath(__file__))
sys.path.append(__dir__)
sys.path.append(os.path.abspath(os.path.join(__dir__, '../..')))
sys.path.append(os.path.abspath(os.path.join(__dir__, './ocr_paddle/')))
sys.path.append(os.path.abspath(os.path.join(__dir__, './ocr_paddle/ppocr')))

from src.ai.ocr_paddle import predict_cls
from src.ai.ocr_paddle import predict_det
from src.ai.ocr_paddle import predict_rec

import numpy as np
import cv2
import copy
import logging

from src.ai.text_recognizer import  predict_rec as predict_big_rec
from src.ai.text_recognizer import utility
class TextSystem(object):
    def __init__(self):
        self.text_detector = predict_det.TextDetector()
        # self.text_recognizer = predict_rec.TextRecognizer()
        #更换新的识别模型
        self.text_recognizer = predict_big_rec.TextRecognizer(utility.parse_args())
        use_angle_cls = False
        self.use_angle_cls = use_angle_cls
        if self.use_angle_cls:
            self.text_classifier = predict_cls.TextClassifier()

    def get_rotate_crop_image(self, img, points):
        '''
        img_height, img_width = img.shape[0:2]
        left = int(np.min(points[:, 0]))
        right = int(np.max(points[:, 0]))
        top = int(np.min(points[:, 1]))
        bottom = int(np.max(points[:, 1]))
        img_crop = img[top:bottom, left:right, :].copy()
        points[:, 0] = points[:, 0] - left
        points[:, 1] = points[:, 1] - top
        '''
        img_crop_width = int(
            max(
                np.linalg.norm(points[0] - points[1]),
                np.linalg.norm(points[2] - points[3])))
        img_crop_height = int(
            max(
                np.linalg.norm(points[0] - points[3]),
                np.linalg.norm(points[1] - points[2])))
        pts_std = np.float32([[0, 0], [img_crop_width, 0],
                              [img_crop_width, img_crop_height],
                              [0, img_crop_height]])
        M = cv2.getPerspectiveTransform(points, pts_std)
        dst_img = cv2.warpPerspective(
            img,
            M, (img_crop_width, img_crop_height),
            borderMode=cv2.BORDER_REPLICATE,
            flags=cv2.INTER_CUBIC)
        dst_img_height, dst_img_width = dst_img.shape[0:2]
        if dst_img_height * 1.0 / dst_img_width >= 1.5:
            dst_img = np.rot90(dst_img)
        return dst_img

    def print_draw_crop_rec_res(self, img_crop_list, rec_res):
        bbox_num = len(img_crop_list)
        for bno in range(bbox_num):
            cv2.imwrite("./output/img_crop_%d.jpg" % bno, img_crop_list[bno])
            print(bno, rec_res[bno])

    def compute_iou(self,rec1, rec2):
        """
        computing IoU
        :param rec1: (y0, x0, y1, x1), which reflects
                (top, left, bottom, right)
        :param rec2: (y0, x0, y1, x1)
        :return: scala value of IoU
        """
        # computing area of each rectangles
        S_rec1 = (rec1[2] - rec1[0]) * (rec1[3] - rec1[1])
        S_rec2 = (rec2[2] - rec2[0]) * (rec2[3] - rec2[1])

        # computing the sum_area
        sum_area = S_rec1 + S_rec2

        # find the each edge of intersect rectangle

        left_line = max(rec1[1], rec2[1])
        right_line = min(rec1[3], rec2[3])
        top_line = max(rec1[0], rec2[0])
        bottom_line = min(rec1[2], rec2[2])

        # judge if there is an intersect
        if left_line >= right_line or top_line >= bottom_line:
            return 0
        else:
            intersect = (right_line - left_line) * (bottom_line - top_line)
            return (intersect / (sum_area - intersect)) * 1.0

    def filter_boxes(self,std_boxes,dt_boxes):
        thresh = 0.0
        re_boxes = []
        for boxes in dt_boxes:
            xmin = boxes[0][0]
            xmax = boxes[1][0]
            ymin = boxes[0][1]
            ymax = boxes[2][1]
            rect1 = [ymin,xmin,ymax,xmax]
            for st_box in std_boxes:
                sxmin = st_box[0][0]
                sxmax = st_box[1][0]
                symin = st_box[0][1]
                symax = st_box[2][1]
                rect2 = [symin, sxmin, symax, sxmax]
                iou = self.compute_iou(rect1, rect2)
                if iou > thresh:
                    re_boxes.append(boxes)
                print(iou)

        return np.array(re_boxes,dtype=np.float32)


    def __call__(self, img):
        ori_im = img.copy()
        dt_boxes, elapse = self.text_detector(img)
        print("dt_boxes num : {}, elapse : {}".format(len(dt_boxes), elapse))
        if dt_boxes is None:
            return None, None
        img_crop_list = []

        dt_boxes = sorted_boxes(dt_boxes)
        # self.filter_boxes(std_boxes,dt_boxes)

        for bno in range(len(dt_boxes)):
            tmp_box = copy.deepcopy(dt_boxes[bno])
            img_crop = self.get_rotate_crop_image(ori_im, tmp_box)
            # cv2.imshow("dfdg",img_crop)
            # cv2.waitKey(0)
            img_crop_list.append(img_crop)
        if self.use_angle_cls:
            img_crop_list, angle_list, elapse = self.text_classifier(
                img_crop_list)
            # print("cls num  : {}, elapse : {}".format(
            #     len(img_crop_list), elapse))
        rec_res, elapse = self.text_recognizer(img_crop_list)

        return dt_boxes, rec_res



def sorted_boxes(dt_boxes):
    """
    Sort text boxes in order from top to bottom, left to right
    args:
        dt_boxes(array):detected text boxes with shape [4, 2]
    return:
        sorted boxes(array) with shape [4, 2]
    """
    num_boxes = dt_boxes.shape[0]
    sorted_boxes = sorted(dt_boxes, key=lambda x: (x[0][1], x[0][0]))
    _boxes = list(sorted_boxes)

    for i in range(num_boxes - 1):
        if abs(_boxes[i + 1][0][1] - _boxes[i][0][1]) < 10 and \
                (_boxes[i + 1][0][0] < _boxes[i][0][0]):
            tmp = _boxes[i]
            _boxes[i] = _boxes[i + 1]
            _boxes[i + 1] = tmp
    return _boxes


text_sys = TextSystem()

def predict(image_path):
    """
    检测结果：文字区域检测和字符检测
    """
    logging.info("predict image")

    img = cv2.imread(image_path)
    dt_boxes,rec_res = text_sys(img)

    return dt_boxes,rec_res


def test():
    img_path =  "D:/abner/project/dataset/idcard/VOC2007/JPEGImages/20.jpg"
    predict(img_path)
resutl_file = open('room_rec.txt','w')
def test_image():
    root = "D:/abner/project/dataset/room/"
    files = os.listdir(root)
    for file in files:
        img_path = os.path.join(root, file)
        _,text  = predict(img_path)
        s = ''
        for l in text:
            s +=" "+ l[0]
        print("result",text )
        resutl_file.write(file+" "+str(s)+'\n')


if __name__ == '__main__':
    test()
    # test_image()
