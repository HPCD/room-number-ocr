#!/usr/bin/env python
#-*- coding:utf-8 -*-
"""
@author:abner
@file:process_result.py
@ datetime:2021/1/8 15:19
@software: PyCharm

"""
import re
import logging

def removePunctuation(text):
    """
    去除标点符号
    """
    punctuation = '!,;:?"\'、，；'
    text = re.sub(r'[{}]+'.format(punctuation),' ',text)
    return text.strip()

def is_contains_chinese(strs):
    """
    判断是否包含中文
    """
    for _char in strs:
        if '\u4e00' <= _char <= '\u9fa5':
            return True
    return False

def find_same_line_index(dt_boxes):
    """
    字符1比字符2要低，字符1比字符2高，字符1和字符2相交
    两个字符区域是否同一行，从版面规律中总结出几个规律：
    a.两个字符在同一行其区域坐标有可能相交，但y1max和y2min不能超过一定阈值(abs(y2min-y1max)< threshold)，y1min和y2max 也不能超过一定阈值（abs(y1min-y2max)< threshold）
    a.其水平x距离不能相等，或不能超过一定阈值，如x1min 为5 ，x2min为5 那么这两个极有可能是同一列的，上下的关系而不是同一行
    c.作为同一行的字符其字符高度应该是一致的，即h1 约等于 h2
    dt_boxes 是已经按照纵轴y排好序
    需要比较x轴，是否在同一水平
    :param dt_boxes: 字符坐标
    :type dt_boxes:
    :return: 在同一行的字典索引号 如 字符1 和字符2在同一行 那么 {0：[1,2]}
    :rtype:
    """
    logging.info("find same line")
    boxes_length = len(dt_boxes)
    result_dict = {}
    num = 0
    # 遍历所有字符区域坐标
    for index in range(0,boxes_length):
        group = []
        #前一个和后一个比较，如果后一个坐标和前一个在同水平坐标上，当做同一组
        boxes = dt_boxes[index]
        #取得当前字符坐标
        xmin = int(boxes[0][0])
        ymin = int(boxes[0][1])
        xmax = int(boxes[1][0])
        ymax = int(boxes[2][1])
        group.append(index)
        #h为字符的高度
        h = ymax - ymin
        w = xmax - xmin
        #下一个字符比较
        for next_index in range(index+1,boxes_length):

            #比较区域坐标
            next_boxes = dt_boxes[next_index]
            next_xmin = int(next_boxes[0][0])
            next_ymin = int(next_boxes[0][1])
            next_xmax = int(next_boxes[1][0])
            next_ymax = int(next_boxes[2][1])

            next_h = next_ymax - next_ymin
            # 判断是否同一水平高度需要满足以下条件：1.当前字符的最小高度位置和比较字符的最小位置之差绝对值小于当前字符的字符高度，并且其中一个字符的最小值要大于另一个的最大值（说明相交）
            # 2.当前字符最大高度和比较字符最小高度的高度差小于当前字符高度的一半
            if ymin < next_ymax and ymax > next_ymin:
                # 两个条件满足说明高度方向相交
                if xmin < next_xmin and next_h > 0.8*h:
                    group.append(next_index)
        num += 1
        result_dict[num] = group
    logging.info("resuclt index %s",result_dict)
    return result_dict

def normal_str(text):
    # 去掉空格
    str_card = text.replace(" ", "")
    #去掉字符“-”
    str_card = str_card.replace("-", "")

    if 'b' in str_card:
        str_card = str_card.replace("b", '6')
    #全部为数字直接返回
    if str_card.isdigit():
        return str_card
    # 去掉英文
    #直接把英文字符替换成8
    str_card = re.sub('[a-zA-Z]','8',str_card)
    return  str_card

def filter_bank_word(text):
    """
    去掉一些不符合规则的词
    """
    #一般中国前面不再包含别的词了
    text_list = text.split("中国")
    if len(text_list) == 2:
        text = "中国"+text_list[-1]
    return text

def normal_bank_str(text):
    """
    对识别的银行名称信息进行规范化，去掉一些错误字符
    """

    #去掉括号
    text = text.replace("）","")
    text = re.sub(r'[{}]+'.format('0-9'), '', text)
    # 去掉英文
    pattern = re.compile(r'[\u4e00-\u9fa5]')
    english = re.sub(pattern, '', text)

    text = text.replace(english, "")

    text = filter_bank_word(text)

    return text

def process_predict_result(dt_boxes,rec_res):

    """
    根据传入的字符坐标和字符信息进行处理，从中提取出银行名称和银行卡号
    return : {"bank":“aaa”,'number':1234}
    """
    logging.info("process predict result")
    #存放银行卡结果信息
    card_content = {}
    if len(rec_res) == 0 :
        return card_content

    #按纵坐标进行分组
    result_dict = find_same_line_index(dt_boxes)
    #根据连接对结果进行处理
    for k,v in result_dict.items():
        s = ""
        #根据索引组成字符串
        for index in v:
            temp = str(rec_res[int(index)][0])
            if temp is not "":
                s += temp
                rec_res[int(index)][0] = ""

        if s is not "":
            #去除标点符号
            s = removePunctuation(s)
            #去掉空格
            s = s.replace(" ","")
            s = s.strip()
            # 银行卡号，招行16，交行17，其他19
            if  16==len(s) or len(s)== 19 or len(s)==17:
                #卡号应该是阿拉伯数字,包含中文和纯英文的都应该去掉
                if not is_contains_chinese(s) and not s.encode('UTF-8').isalpha():
                    #有些字符6会识别成b,而卡号不存在b
                    if 'b' in s:
                        s = s.replace("b",'6')
                    card_content["number"]=s
            #银行卡出现银字的信息不多，一般是银行或者银联，识别到银行就用银行切分，只识别到’银‘字且不属于’银联‘ 认为是银行的
            if "银行" in s :
                #把银行后面的数字去掉
                s = s.split("银行")[0]+"银行"
                s = normal_bank_str(s)
                #银行一般在第一行，所以只取第一个
                if 'bank' in card_content.keys():
                    continue
                card_content["bank"]=s
            elif ("银" in s and "银联" not in s):
                # 把银行后面的数字去掉
                s = s.split("银")[0] + "银行"
                s = normal_bank_str(s)
                if 'bank' in card_content.keys():
                    continue
                card_content["bank"] = s
    logging.info("return process predict result %s",card_content)
    return card_content

def precess_region_predict_result(dt_boxes,rec_res):
    """
    处理经过限定的字符区域预测结果，一般该区域只包含有银行卡号
    return: 只包含卡号信息
    """

    #号码结果
    card_num_content = {}
    length = len(dt_boxes)

    if length == 0:
        return card_num_content

    str_card = ""
    for index in range(0,length):
        #lower转小写
        seg = rec_res[index][0].lower()
        str_card += seg
    # 去掉错误字符
    str_card = normal_str(str_card)

    if  16==len(str_card) or len(str_card)== 19 or len(str_card)==17:
        card_num_content['card'] = str_card
    else:
        return card_num_content
    return card_num_content
