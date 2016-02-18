#!/bin/python

import cv2, numpy as np
import copy
import sys

def fill_contour_shape (image, cn):
    w = []
    h = []
    area = []
    for i in cn [0]:
        w.append (i [0][0])
        h.append (i [0][1])
        area . append ([i [0][0], i [0][1]])
    
    a = np.array (area)
    ww = np.array (w)
    hh = np.array (h)
    minw = min (w)
    maxw = max (w)
    minh = min (h)
    maxh = max (h)
    
    mat = np.ndarray ([maxh - minh, maxw - minw, 3], np.uint8)
    mat.fill (0)
    for x in range (minw, maxw):
        for y in range (minh, maxh):
            ys = np.where (hh == y)
            xs = np.where (ww == x)
            mya = []

            for g in xs [0]:
                mya.append (a [g])

            for h in ys [0]:
                mya.append (a [h])

            condition_1 = False
            condition_2 = False
            condition_3 = False
            condition_4 = False
            for l in mya:
                if l [0] == x:
                    if l [1] < y:
                        condition_1 = True
                    elif l [1] > y:
                        condition_2 = True
                    else:
                        break
                elif l [1] == y:
                    if l [0] < x:
                        condition_3 = True
                    elif l [0] > x:
                        condition_4 = True
                    else:
                        break
            if condition_1 and condition_2 and condition_3 and condition_4:
                mat [y - minh][x - minw] = (255,255,255)
                continue

    cv2.polylines (mat, [cn[0]], 1, (0,0,255))
    return mat

def copy_contour_shape (image, cn):
    if type (cn) is list:
        n = cn [0]

        for x in xrange (1, len (cn)):
            n = np.append (n, cn [x], axis = 0)
        
        cn = n

    w = []
    h = []
    area = []
    print cn

    for i in cn:
        w.append (i [0][0])
        h.append (i [0][1])
        area . append ([i [0][0], i [0][1]])
    
    a = np.array (area)
    ww = np.array (w)
    hh = np.array (h)
    minw = min (w)
    maxw = max (w)
    minh = min (h)
    maxh = max (h)
    
    mat = np.ndarray ([maxh - minh, maxw - minw, 3], np.uint8)
    mat.fill (0)
    print "Going for {} x {} iterations...".format (maxw - minw, maxh - minh)
    cx = 0
    cy = 0
    for x in range (minw, maxw):
        for y in range (minh, maxh):
            cx += 1
            cy += 1
            if cx > 5000 and cy > 5000:
                print x, y
                cx = cy = 0
            ys = np.where (hh == y)
            xs = np.where (ww == x)

            condition_1 = False
            condition_2 = False
            condition_3 = False
            condition_4 = False
            for l in xs [0]:
                if a [l] [1] < y:
                    condition_1 = True
                elif a[l] [1] > y:
                    condition_2 = True
                else:
                    break
                for l in ys [0]:
                    if a [l] [0] < x:
                        condition_3 = True
                    elif a [l] [0] > x:
                        condition_4 = True
                    else:
                        break
            if condition_1 and condition_2 and condition_3 and condition_4:
                mat [y - minh][x - minw] = image [y][x]
                continue

    
    return mat

def main ():
    image = cv2.imread (sys.argv [1])
    blur = cv2.medianBlur(image,7) # make this adjustable
    canny = cv2.Canny (blur,100,200) # make this adjustable too
    cn, hr = cv2.findContours (canny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    mat = copy_contour_shape (image, cn)
    cv2.namedWindow('test')
    cv2.imshow ('test', mat)
    cv2.waitKey ()
    

if __name__ == '__main__':
    main ()
