#!/usr/bin/env python
#-*- coding:utf-8 -*-
"""
@author:abner
@file:select_car_color.py
@ datetime:2020/8/20 11:07
@software: PyCharm

"""
import cv2

import numpy as np
from PIL import Image
import matplotlib.pyplot as plt

img_fname = 'd3.jpg'


def select_color():
    img = cv2.imread(img_fname)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    cv2.imshow("d",img)
    h, w, _ = img.shape
    jihe = []
    num = 0
    for a in range(h):
        for b in range(w):
            # print(img[a, b])
            jihe.append(list(img[a, b]))
            num += 1
    sumx = sumy = sumz = 0
    for i in range(num):
        [x, y, z] = jihe[i]
        sumx = sumx + x
        sumy = sumy + y
        sumz = sumz + z

    r = int(sumx / num)
    g = int(sumy / num)
    b = int(sumz / num)
    print("df",r, g, b)
    # print(num)
    # print(jihe)
    # print('集合长度%d' % (len(jihe)))

    colors_change = np.uint8([[[b, g, r]]])
    hsv_change = cv2.cvtColor(colors_change, cv2.COLOR_BGR2HSV)
    print(hsv_change)

    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    cv2.imshow("gray",gray)
    cv2.waitKey(0)

    cv2.destroyWindow('gary')

def extract_main_color1():
    import cv2
    import numpy as np
    from PIL import Image

    img_path = 'd4.jpg'
    image = Image.open(img_path)

    # 要提取的主要颜色数量
    num_colors = 256

    small_image = image.resize((80, 80))
    result = small_image.convert('P', palette=Image.ADAPTIVE, colors=num_colors)  # image with 5 dominating colors

    result = result.convert('RGB')
    # result.show() # 显示图像
    main_colors = result.getcolors(80 * 80)
    # print(main_colors)

    # 显示提取的主要颜色
    for count, col in main_colors:
        if count < 40:
            continue
        print(col)
        a = np.zeros((224, 224, 3))
        a = a + np.array(col)
        # print(a)
        cv2.imshow('a', a.astype(np.uint8)[:, :, ::-1])
        cv2.waitKey(1000)
def extract_main_color2():
    from scipy import stats

    from PIL import Image

    img = np.array(Image.open('d4.jpg'))  # 读取图片

    duo = []

    for img1 in img:  # 按行查看，每行中颜色最多的添加到 duo 中
        u = list(stats.mode(img1)[0][0])
        duo.append(u)

    c = stats.mode(duo)[0][0]  # 查看duo 中最多的颜色
    print("2",c)
    a = np.zeros((224, 224, 3))
    a = a + np.array(c)
    # print(a)
    cv2.imshow('a', a.astype(np.uint8)[:, :, ::-1])
    cv2.waitKey(10000)
    cv2.destroyWindow("a")
def extract_main_color3():


    img_path = 'd4.jpg'
    image = Image.open(img_path)
    print("dg")
    # 要提取的主要颜色数量
    num_colors = 3
    small_image = image.resize((80, 80))
    result = small_image.convert('P', palette=Image.ADAPTIVE, colors=num_colors)
    result = result.convert('RGB')
    main_colors = result.getcolors()

    col_extract = []
    # 显示提取的主要颜色
    for count, col in main_colors:
        print(col)#RGB转RGBA，可输出RGBA色号
        col_extract.append([col[i] / 255 for i in range(3)])

    # 使用提取的颜色绘制条形图
    plt.figure(dpi=150)
    plt.bar(range(len(col_extract)), np.ones(len(col_extract)), color=(col_extract))
    plt.xticks(range(len(col_extract)), (range(len(col_extract))))
    plt.show()

def extract_main_color4():
    import binascii
    import struct
    from PIL import Image
    import numpy as np
    import scipy
    import scipy.misc
    import scipy.cluster

    NUM_CLUSTERS = 5

    print('reading image')
    im = Image.open('d3.jpg')
    im = im.resize((150, 150))  # optional, to reduce time
    ar = np.asarray(im)
    shape = ar.shape
    ar = ar.reshape(scipy.product(shape[:2]), shape[2]).astype(float)

    print('finding clusters')
    codes, dist = scipy.cluster.vq.kmeans(ar, NUM_CLUSTERS)
    print('cluster centres:\n', codes)

    vecs, dist = scipy.cluster.vq.vq(ar, codes)  # assign codes
    counts, bins = scipy.histogram(vecs, len(codes))  # count occurrences

    index_max = scipy.argmax(counts)  # find most frequent
    peak = codes[index_max]
    colour = binascii.hexlify(bytearray(int(c) for c in peak)).decode('ascii')
    print('most frequent is %s (#%s)' % (peak, colour))
    import imageio
    c = ar.copy()
    for i, code in enumerate(codes):
        c[scipy.r_[scipy.where(vecs == i)], :] = code
    imageio.imwrite('clusters.png', c.reshape(*shape).astype(np.uint8))
    print('saved clustered image')


def extract_domain_color(img_name):
    # 本地导入
    from src.colorthief import ColorThief
    # from colorthief import ColorThief
    color_thief = ColorThief(img_name)
    # get the dominant color
    domain_color = color_thief.get_color(quality=1)
    print("dominant ", len(domain_color))
    color_list = []
    if len(domain_color)< 0:
        return []

    #(150, 151, 154, 29688, 125840, 23) 23为色彩的比例
    # print(color_thief.get_palette(quality=1))
    dominant_color_list = domain_color[0]
    return [domain_color[0],domain_color[1],domain_color[2]]



# select_color()
# extract_main_color4()
# resutl = extract_domain_color('D:/abner\project\pyproject\canvas\src\cut_img/ab05fa1c-e779-11ea-b862-f875a4fc33a4.jpg')
# print(resutl)