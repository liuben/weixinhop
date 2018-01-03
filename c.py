#! /usr/bin/python
# coding: utf-8

from PIL import Image
import sys
import math
import os
import time

STANDARD_DISTANCE=522.8
STANDARD_DURATION = 723.0
imgPath = '/Users/liuben/Desktop/test1234/'
phonePath = '/sdcard/test1234/'

# False 表示距离很远，True 表示距离很近
def colorDistance(start, cur, delta=20):
    r = start[0]-cur[0]
    g = start[1]-cur[1]
    b = start[2]-cur[2]
    distance = abs(r) + abs(g) + abs(b)
    if distance < delta:
        return True
    return False

def imageDistance(big,small,x,y,small_width,small_height):
    s=small[0,0]
    bi=big[x,y]
    if colorDistance(s,bi)==False:
        return 1000000000000.0
    distance = 0
    for row in range(0,small_height):
        for column in range(0,small_width):
            s=small[column,row]
            bi=big[x+column,y+row]

            r = s[0]-bi[0]
            g = s[1]-bi[1]
            b = s[2]-bi[2]
            distance += abs(r) + abs(g) + abs(b)
    return distance

if len(sys.argv) > 3:
    print 'failed! usage: c.py [-d|-l] or c.py -t filepath'
    exit()

debug_flag = False
log_flag = False
test_flag = False

if len(sys.argv)==2 :
    if sys.argv[1]=="-d":
        debug_flag = True
    elif sys.argv[1]=="-l":
        log_flag = True
    else:
        print 'option failed'
        exit()
elif len(sys.argv) ==3 :
    if sys.argv[1]=="-t":
        test_flag = True
    else:
        print 'option failed'
        exit()

# return 目标点坐标
def calc_dst(src_img,src_pixels):
    # 开始扫描位置
    x = src_img.width-1
    y = int(src_img.height*(340.0/1920.0))

    # 检索顶端特征点
    filter_points = [-1,-1]
    topx,topy = x,y
    find = False
    for row in range(topy,src_img.height/2,1):
        sp_row_color = src_pixels[topx,row]
        for column in range(topx,0,-1):
            if column>=filter_points[0] and column<=filter_points[1]:
                continue
            p_color = src_pixels[column, row]
            if colorDistance(sp_row_color, p_color) == False:
                # 判断是不是进入了棋子头部
                wrong = False
                for x in range(column,column-10,-1):
                    c = src_pixels[x,row]
                    if colorDistance(c, (53,54,61), 30):
                        if debug_flag:
                            print "进入棋子头部：%d,%d" % (x,row)
                        if x > src_img.width/2:
                            filter_points = [src_img.width/2, src_img.width]
                        else:
                            filter_points = [0,src_img.width/2]
                        wrong = True
                        break
                if wrong:
                    continue

                topx, topy = column, row
                find = True
                break
        if find:
            break

    # 计算顶端中点的坐标
    top_points_x = [topx]
    for column in range(topx-1, 0 ,-1):
        p_color = src_pixels[column, row]
        if colorDistance(sp_row_color, p_color) == False :
            top_points_x.append(column)
        else:
            break

    index = int(len(top_points_x)/2)
    topx = top_points_x[index]

    # 计算最右侧点
    right_x,right_y = top_points_x[0], topy
    find = False
    ver_count = 0
    for row in range(right_y+1,src_img.height):
        sp_row_color = src_pixels[src_img.width-1,row]
        for column in range(right_x,src_img.width):
            p_color = src_pixels[column,row]
            if colorDistance(sp_row_color, p_color) == True:
                if column == right_x:
                    # 找到了最右侧点
                    find = True
                elif column == right_x+1:
                    ver_count += 1
                    if ver_count > 5:
                        # 找到了最右侧点
                        find = True
                else:
                    ver_count = 0
                    right_x = column-1
                    right_y = row
                break
        if find :
            break

    # 计算目标点坐标
    dst_x,dst_y = topx,right_y
    if debug_flag:
        print "目标：%d,%d" % (dst_x,dst_y)

    return (dst_x,dst_y)

def calc_distance(filename):
    src_img = Image.open(imgPath + filename)
    src_pixels= src_img.load()

    # 计算目标点
    dst_x,dst_y = calc_dst(src_img,src_pixels)

    # 读取特征图
    ball = Image.open("ball.png")
    ball_pixels = ball.load()

    # 搜索特征
    startx,starty,endx,endy=0,0,0,0
    if dst_x > src_img.width / 2:
        startx = 0
        starty = dst_y+1
        endx = src_img.width / 2 - ball.width
        endy = src_img.height - ball.height
    else:
        startx = src_img.width /2
        endx = src_img.width - ball.width
        starty = dst_y+1
        endy = src_img.height - ball.height

    find = False
    ballx,bally=0,0

    min_distance = 1000000000000000000
    for row in range(starty,endy):
        for column in range(startx,endx):
            dis = imageDistance(src_pixels,ball_pixels,column, row, ball.width, ball.height)
            if dis<min_distance:
                min_distance = dis
                ballx = column + ball.width/2
                bally = row + ball.height/2


    if debug_flag:
        print "起点：%d,%d" % (ballx,bally)

    # 计算距离
    dx = float(ballx-dst_x)
    dy = float(bally-dst_y)
    distance = math.sqrt(dx*dx+dy*dy)
    if debug_flag:
        print "距离：%f" % distance

    return distance

def jump_one_step(filename):
    os.system("adb shell screencap " + phonePath + filename)
    os.system("adb pull " + phonePath + filename + " " + imgPath + filename)
    os.system("adb shell rm " + phonePath + filename)

    distance = calc_distance(filename)

    duration = distance/STANDARD_DISTANCE * STANDARD_DURATION
    duration = int(round(duration))

    print "duration: %d" % duration

    os.system("adb shell input swipe 100 100 100 100 " + str(duration))

if debug_flag:
    while True:
        cmd = raw_input("next: ")
        if cmd == "exit":
            break
        elif cmd =="":
            jump_one_step("a.png")

        elif cmd[0:4] == "jump":
            os.system("adb shell input swipe 100 100 100 100 " + cmd[5:])

        elif cmd == "shot":
            os.system("adb shell screencap " + phonePath + "a.png")
            os.system("adb pull " + phonePath + "a.png " + imgPath + "a.png")
            os.system("adb shell rm " + phonePath + "a.png")

        elif cmd == "debug":
            calc_distance("a.png")
elif test_flag:
    # 读取测试文件
    filename = sys.argv[2]
    f = open(filename,'r')
    for line in f:
        line = line.strip()
        if len(line)==0:
            continue
        fn,dst = line.split(' ')
        x,y = dst.split(',')
        x,y = int(x),int(y)

        src_img = Image.open(fn)
        src_pixels= src_img.load()

        # 计算目标点
        dst_x,dst_y = calc_dst(src_img,src_pixels)

        if abs(dst_x-x)<5 and abs(dst_y-y)<5:
            print fn + " is ok"
        else:
            print '%s is failed. expect (%d,%d), get (%d,%d)' % (fn,x,y,dst_x,dst_y)


    f.close()
    
else:
    counter = 1
    while True:
        jump_one_step(str(counter)+".png")
        if log_flag:
            counter+=1
        time.sleep(2)

