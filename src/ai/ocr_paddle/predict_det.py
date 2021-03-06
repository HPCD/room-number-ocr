# Copyright (c) 2020 PaddlePaddle Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import os
import sys
__dir__ = os.path.dirname(os.path.abspath(__file__))
sys.path.append(__dir__)
sys.path.append(os.path.abspath(os.path.join(__dir__, '../..')))

import cv2
import copy
import numpy as np
import math
import time
import sys

import paddle.fluid as fluid

import src.ai.ocr_paddle.utility as utility
from src.ai.ocr_paddle.ppocr.utility import initial_logger
logger = initial_logger()
from  src.ai.ocr_paddle.ppocr.utility import get_image_file_list, check_and_read_gif
from src.ai.ocr_paddle.ppocr.data.det.sast_process import SASTProcessTest
from src.ai.ocr_paddle.ppocr.data.det.east_process import EASTProcessTest
from src.ai.ocr_paddle.ppocr.data.det.db_process import DBProcessTest
from src.ai.ocr_paddle.ppocr.postprocess.db_postprocess import DBPostProcess
from src.ai.ocr_paddle.ppocr.postprocess.east_postprocess import EASTPostPocess
from src.ai.ocr_paddle.ppocr.postprocess.sast_postprocess import SASTPostProcess
from paddle.fluid.core import AnalysisConfig

class TextDetector(object):
    def __init__(self, det_algorithm='DB',det_max_side_len=960,
                 det_db_thresh=0.3,det_db_box_thresh=0.5,
                 det_db_unclip_ratio=1.6,det_east_score_thresh=0.8,
                 det_east_cover_thresh=0.1,det_east_nms_thresh=0.2,
                 det_sast_score_thresh=0.5,det_sast_nms_thresh=0.2,
                 det_sast_polygon=False,use_pdserving=False,
                 use_zero_copy_run=False):
        max_side_len = det_max_side_len
        self.det_algorithm = det_algorithm
        preprocess_params = {'max_side_len': max_side_len}
        postprocess_params = {}

        if self.det_algorithm == "DB":
            self.preprocess_op = DBProcessTest(preprocess_params)
            postprocess_params["thresh"] = det_db_thresh
            postprocess_params["box_thresh"] = det_db_box_thresh
            postprocess_params["max_candidates"] = 1000
            postprocess_params["unclip_ratio"] = det_db_unclip_ratio
            self.postprocess_op = DBPostProcess(postprocess_params)
        elif self.det_algorithm == "EAST":
            self.preprocess_op = EASTProcessTest(preprocess_params)
            postprocess_params["score_thresh"] = det_east_score_thresh
            postprocess_params["cover_thresh"] = det_east_cover_thresh
            postprocess_params["nms_thresh"] = det_east_nms_thresh
            self.postprocess_op = EASTPostPocess(postprocess_params)
        elif self.det_algorithm == "SAST":
            self.preprocess_op = SASTProcessTest(preprocess_params)
            postprocess_params["score_thresh"] = det_sast_score_thresh
            postprocess_params["nms_thresh"] = det_sast_nms_thresh
            self.det_sast_polygon = det_sast_polygon
            if self.det_sast_polygon:
                postprocess_params["sample_pts_num"] = 6
                postprocess_params["expand_scale"] = 1.2
                postprocess_params["shrink_ratio_of_width"] = 0.2
            else:
                postprocess_params["sample_pts_num"] = 2
                postprocess_params["expand_scale"] = 1.0
                postprocess_params["shrink_ratio_of_width"] = 0.3
            self.postprocess_op = SASTPostProcess(postprocess_params)
        else:
            logger.info("unknown det_algorithm:{}".format(self.det_algorithm))
            sys.exit(0)
        if use_pdserving is False:
            self.use_zero_copy_run = use_zero_copy_run
            self.predictor, self.input_tensor, self.output_tensors =\
                utility.create_predictor(mode="det")

    def order_points_clockwise(self, pts):
        """
        reference from: https://github.com/jrosebr1/imutils/blob/master/imutils/perspective.py
        # sort the points based on their x-coordinates
        """
        xSorted = pts[np.argsort(pts[:, 0]), :]

        # grab the left-most and right-most points from the sorted
        # x-roodinate points
        leftMost = xSorted[:2, :]
        rightMost = xSorted[2:, :]

        # now, sort the left-most coordinates according to their
        # y-coordinates so we can grab the top-left and bottom-left
        # points, respectively
        leftMost = leftMost[np.argsort(leftMost[:, 1]), :]
        (tl, bl) = leftMost

        rightMost = rightMost[np.argsort(rightMost[:, 1]), :]
        (tr, br) = rightMost

        rect = np.array([tl, tr, br, bl], dtype="float32")
        return rect

    def clip_det_res(self, points, img_height, img_width):
        for pno in range(points.shape[0]):
            points[pno, 0] = int(min(max(points[pno, 0], 0), img_width - 1))
            points[pno, 1] = int(min(max(points[pno, 1], 0), img_height - 1))
        return points

    def filter_tag_det_res(self, dt_boxes, image_shape):
        img_height, img_width = image_shape[0:2]
        dt_boxes_new = []
        for box in dt_boxes:
            box = self.order_points_clockwise(box)
            box = self.clip_det_res(box, img_height, img_width)
            rect_width = int(np.linalg.norm(box[0] - box[1]))
            rect_height = int(np.linalg.norm(box[0] - box[3]))
            if rect_width <= 3 or rect_height <= 3:
                continue
            dt_boxes_new.append(box)
        dt_boxes = np.array(dt_boxes_new)
        return dt_boxes

    def filter_tag_det_res_only_clip(self, dt_boxes, image_shape):
        img_height, img_width = image_shape[0:2]
        dt_boxes_new = []
        for box in dt_boxes:
            box = self.clip_det_res(box, img_height, img_width)
            dt_boxes_new.append(box)
        dt_boxes = np.array(dt_boxes_new)
        return dt_boxes

    def __call__(self, img):
        ori_im = img.copy()
        im, ratio_list = self.preprocess_op(img)
        if im is None:
            return None, 0
        im = im.copy()
        starttime = time.time()
        if self.use_zero_copy_run:
            self.input_tensor.copy_from_cpu(im)
            self.predictor.zero_copy_run()
        else:
            im = fluid.core.PaddleTensor(im)
            self.predictor.run([im])
        outputs = []
        for output_tensor in self.output_tensors:
            output = output_tensor.copy_to_cpu()
            outputs.append(output)
        outs_dict = {}
        if self.det_algorithm == "EAST":
            outs_dict['f_geo'] = outputs[0]
            outs_dict['f_score'] = outputs[1]
        elif self.det_algorithm == 'SAST':
            outs_dict['f_border'] = outputs[0]
            outs_dict['f_score'] = outputs[1]
            outs_dict['f_tco'] = outputs[2]
            outs_dict['f_tvo'] = outputs[3]
        else:
            outs_dict['maps'] = outputs[0]

        dt_boxes_list = self.postprocess_op(outs_dict, [ratio_list])
        dt_boxes = dt_boxes_list[0]
        if self.det_algorithm == "SAST" and self.det_sast_polygon:
            dt_boxes = self.filter_tag_det_res_only_clip(dt_boxes, ori_im.shape)
        else:
            dt_boxes = self.filter_tag_det_res(dt_boxes, ori_im.shape)
        elapse = time.time() - starttime
        return dt_boxes, elapse

def create_predictor(det_model_dir,cls_model_dir,rec_model_dir, mode):
    """
    create predictor for inference
    :param args: params for prediction engine
    :param mode: mode
    :return: predictor
    """
    if mode == "det":
        model_dir = det_model_dir
    elif mode == 'cls':
        model_dir = cls_model_dir
    elif mode == 'rec':
        model_dir = rec_model_dir
    else:
        raise ValueError(
            "'mode' of create_predictor() can only be one of ['det', 'cls', 'rec']"
        )

    if model_dir is None:
        logger.info("not find {} model file path {}".format(mode, model_dir))
        sys.exit(0)
    model_file_path = model_dir + "/model"
    params_file_path = model_dir + "/params"
    if not os.path.exists(model_file_path):
        logger.info("not find model file path {}".format(model_file_path))
        sys.exit(0)
    if not os.path.exists(params_file_path):
        logger.info("not find params file path {}".format(params_file_path))
        sys.exit(0)

    config = AnalysisConfig(model_file_path, params_file_path)

    if args.use_gpu:
        config.enable_use_gpu(args.gpu_mem, 0)
    else:
        config.disable_gpu()
        config.set_cpu_math_library_num_threads(6)
        if args.enable_mkldnn:
            # cache 10 different shapes for mkldnn to avoid memory leak
            config.set_mkldnn_cache_capacity(10)
            config.enable_mkldnn()

    # config.enable_memory_optim()
    config.disable_glog_info()

    if args.use_zero_copy_run:
        config.delete_pass("conv_transpose_eltwiseadd_bn_fuse_pass")
        config.switch_use_feed_fetch_ops(False)
    else:
        config.switch_use_feed_fetch_ops(True)

    predictor = create_paddle_predictor(config)
    input_names = predictor.get_input_names()
    for name in input_names:
        input_tensor = predictor.get_input_tensor(name)
    output_names = predictor.get_output_names()
    output_tensors = []
    for output_name in output_names:
        output_tensor = predictor.get_output_tensor(output_name)
        output_tensors.append(output_tensor)
    return predictor, input_tensor, output_tensors

if __name__ == "__main__":
    args = utility.parse_args()
    print("image", args.image_dir)
    image_dir = 'D:\\abner\\project\\pyproject\\OCR\\bankcard-ocr\\src\\test_img'
    image_file_list = get_image_file_list(image_dir)

    text_detector = TextDetector()
    count = 0
    total_time = 0
    draw_img_save = "./inference_results"
    if not os.path.exists(draw_img_save):
        os.makedirs(draw_img_save)
    for image_file in image_file_list:
        img, flag = check_and_read_gif(image_file)
        if not flag:
            img = cv2.imread(image_file)
        if img is None:
            logger.info("error in loading image:{}".format(image_file))
            continue
        dt_boxes, elapse = text_detector(img)
        if count > 0:
            total_time += elapse
        count += 1
        print("Predict time of %s:" % image_file, elapse)
        src_im = utility.draw_text_det_res(dt_boxes, image_file)
        img_name_pure = image_file.split("\\")[-1]
        print("img name pure ",img_name_pure,os.path.join(draw_img_save, "det_res_%s" % img_name_pure))
        cv2.imwrite(
            os.path.join(draw_img_save, "det_res_%s" % img_name_pure), src_im)
    if count > 1:
        print("Avg Time:", total_time / (count - 1))
