#!/bin/python

import cv2, numpy as np
import copy
import sys

class ColorCluster:
    colormaps = None
    mean = None # So we'll have a single mean color for a color cluster

    def generate_mat (self):
        w = []
        h = []
        
        cw = [] # contour widths
        ch = []
        
        for i in self.colormaps:
            #print np.amax (i.contour, axis =0) [0]
            #cw.append (np.amax (i.contour, axis =0) [0][0])
            #ch.append (np.amax (i.contour, axis =0) [0][1])
            #cw.append (np.amin (i.contour, axis =0) [0][0])
            #ch.append (np.amin (i.contour, axis =0) [0][1])
            #for j in i.area:
                #w.append (j [0])
                #h.append (j [1])
            for c in i.contour:
                cw.append (c [0][0])
                ch.append (c [0][1])
        
        maxw = max (cw)
        minw = min (cw)
        maxh = max (ch)
        minh = min (ch)
        #print maxw - minw +1, maxh - minh +1
        #print minw
        new_mat = np.ndarray ([maxh + 1, maxw + 1, 3], np.uint8)
        new_mat.fill (0)
        
        for j in self.colormaps:
            for k in j.area:
                min1 = np.amin (j.contour, axis =0) [0][0]
                min2 = np.amin (j.contour, axis =0) [0][1]
                #print  k[0] + min2, k [1] + min1, new_mat.shape
                #if k[0] + min2 > new_mat . shape [0] or k[1] + min1 > new_mat.shape [1]:
                    #print "aaa"
                    #sys.exit ()
                new_mat [k[0] + min2, k[1] + min1] = j.mat [k[0], k[1]]
        
        return new_mat

    def add_mat (self, mat, addendum):
        h = mat.shape [1] + addendum.shape [1] + 1
        w = mat.shape [0] + addendum.shape [0] + 1
        new_mat = np.ndarray ([w,h,3], np.uint8)
        #print mat.shape, addendum.shape, new_mat.shape
        
        for i in xrange (mat.shape [0]):
            for j in xrange (mat.shape [1]):
                new_mat [i,j] = mat[i,j]
        
        for k in xrange (addendum.shape [0]):
            for l in xrange (addendum.shape [1]):
                #print j, 
                new_mat [mat.shape [0] + k][mat.shape [1] +l] = addendum [k,l]
        return addendum

    def get_mat (self):
        return self.generate_mat ()

    def get_mat2 (self):
        #print 'len',len (self.colormaps)
        #mat = self.colormaps [0].mat
        mat = np.ndarray ([0,0,3], np.uint8)
        for x in xrange (0, len (self.colormaps)):
            #print "colormap" , self.colormaps [x].mat.shape
            mat = self.add_mat (mat, self.colormaps [x].mat)
        
        return mat

    def get_mat1 (self):
        mat = self.colormaps [0].mat
        for x in xrange (1, len (self.colormaps)):
            print self.colormaps [x].mat.shape, mat.shape
            mat = np.append (mat, self.colormaps [x].mat, axis = 0)

        return mat

    def populate (self, colormap):
        self.colormaps = []
        self.colormaps.append (colormap)
        self.mean = self.colormaps [0].mean

    def calculate_color_mean (self):
        means = []
        for i in self.colormaps:
            means.append (i.mean)
        
        self.mean = (max (means) + np.uint16 (min (means))) / 2

    def append (self, colormap):
        self.colormaps.append (colormap)
        self.calculate_color_mean ()
    
    def match_color (self, color):
        for i in self.colormaps:
            if i.match_color (color):
                return True
            else:
                return False

    def match_geometry (self, contour):
        for i in self.colormaps:
            if i.match_geometry (contour):
                return True
            else:
                return False
        
class ColorMap:
    area = None
    contour = None
    mean = None
    mat = None
    
    color_range = 50 # 0 ~ 255
    proximity_range = 50 # pixels

    def __init__ (self):
        self.__add__ = self.append
    
    def populate (self, area = None, contour = None, mean = None, mat = None):
        if area is not None:
            self.area = area
        if mat is not None:
            self.mat = mat
        if contour is not None:
            self.contour = contour
        if mean is not None:
            self.mean = mean
        
    def append (self, colormap):
        for i in colormap.area:
            self.area.append (i)
        self.contour = np.append (self.contour, colormap.contour, axis = 0)
        self.mean = (self.mean + colormap.mean) / 2

    def match_color_individually (self, color1, color2):
        retval = False
        if color1 == color2:
            retval = True
        elif color1 > color2 and color1 < color2 + self.color_range:
            retval = True
        elif color1 < color2 and color1 > color2 - self.color_range:
            retval = True
        return retval
    
    def match_color (self, color):
        condition_1 = False
        condition_2 = False
        condition_3 = False
        
        #if color [0] < self.mean [0] + self.color_range or color[0] > self.mean [0]+ self.color_range:
            #condition_1 = True
        #if color [1] < self.mean [1] + self.color_range or color[1] > self.mean [1]+ self.color_range:
            #condition_2 = True
        #if color [2] < self.mean [2] + self.color_range or color[2] > self.mean [2] + self.color_range:
            #condition_3 = True

        # isn't this some of the most beautiful code you've ever seen?
        # I've got goosebumps
        
        condition_1 = self.match_color_individually (color [0], self.mean [0])
        condition_2 = self.match_color_individually (color [1], self.mean [1])
        condition_3 = self.match_color_individually (color [2], self.mean [2])
        #print "----------------\nmatching"
        #print color [0],color [1],color [2]
        #print self.mean [0],self.mean [1],self.mean [2]
        #print "gave the answer ",condition_1 and condition_2 and condition_3
        #print "------------------"
        return condition_1 and condition_2 and condition_3

    def match_geometry (self, contour):
        #print np.amin (contour, axis =0) [0] [0]
        minw_incoming = np.amin (contour, axis =0) [0][0]
        minh_incoming = np.amin (contour, axis =0) [0][1]
        minw = np.amin (self.contour, axis =0) [0][0]
        minh = np.amin (self.contour, axis =0) [0][1]
        maxw_incoming = np.amax (contour, axis =0) [0][0]
        maxh_incoming = np.amax (contour, axis =0) [0][1]
        maxw = np.amax (self.contour, axis =0) [0][0]
        maxh = np.amax (self.contour, axis =0) [0][1]
        
        # this is some nice logic I've stumbled across
        condition_1 = False
        condition_2 = False
        condition_3 = False
        condition_4 = False
        condition_5 = False
        condition_6 = False
        condition_7 = False
        condition_8 = False
        
        if minw_incoming > maxw and minw_incoming < maxw + self.proximity_range:
            condition_1 = True
        if minh_incoming > maxh and minh_incoming < maxh + self.proximity_range:
            condition_2 = True
        if minh_incoming < minh and minh_incoming > minh - self.proximity_range:
            condition_3 = True
        if minw_incoming < minw and minw_incoming > minw - self.proximity_range:
            condition_4 = True
        if maxw_incoming > minw and maxw_incoming < minw + self.proximity_range:
            condition_5 = True
        if maxh_incoming > minh and maxh_incoming < minh + self.proximity_range:
            condition_6 = True
        if maxh_incoming < maxh and maxh_incoming > maxh - self.proximity_range:
            condition_7 = True
        if maxw_incoming < maxw and maxw_incoming > maxw - self.proximity_range:
            condition_8 = True
            
        #return condition_1 and condition_2 and condition_3 and condition_4
        if condition_1 and condition_2:
            return True
        if condition_3 and condition_4:
            return True
        if condition_5 and condition_6:
            return True
        if condition_7 and condition_8:
            return True
        return False

def copy_contour_shape (image, cn):
    if type (cn) is list:
        n = cn [0]

        for x in xrange (1, len (cn)):
            n = np.append (n, cn [x], axis = 0)
        
        cn = n

    w = []
    h = []
    area = []

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
    area2 = []
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
                area2.append ([y - minh,x - minw])
                continue
            #else:
                #mat [y - minh][x - minw] = (10,10,10)
                #mat.delete ([y - minh][x - minw])
    #print area2
    return mat, area2

def get_mean_color (mat, area):
    if len (area) is 0:
        #print "Warning: area is 0!", mat
        return (0,0,0)
    
    b = []
    g = []
    r = []

    for i in area:
        #print mat [i[0],i[1]]
        b .append  (mat [i[0], i[1]][0])
        g .append  (mat [i[0], i[1]][1])
        r .append  (mat [i[0], i[1]][2])
        #g .append  (mat [i][1])
        #r .append  (mat [i][2])
    
    maxb = max (b) + np.uint16 (min (b))
    maxg = max (g) + np.uint16 (min (g))
    maxr = max (r) + np.uint16 (min (r))
    
    #print maxb / 2.0, maxg / 2.0, maxr / 2.0
    return maxb / 2.0, maxg / 2.0, maxr / 2.0

def contour_to_color_cluster (image, cn):
    cluster_list = []
    length = len (cn)
    for counter in xrange (length):
        print "Generating shape {} of {}".format (counter, length)
        c = cn [counter]
        mat, area = copy_contour_shape (image, c)
        mean = get_mean_color (mat, area)
        #print mean
        colormap = ColorMap ()
        colormap.populate (area = area, contour = c, mean = mean, mat = mat)
        found_a_match = False
        for cl in cluster_list:
            if cl.match_color (colormap.mean) and cl.match_geometry (colormap.contour):
                cl.append (colormap)
                found_a_match = True
                break
        
        if not found_a_match:
            cluster = ColorCluster ()
            cluster.populate (colormap)
            cluster_list.append (cluster)
            
    return cluster_list
    

def main ():
    image = cv2.imread (sys.argv [1])
    blur = cv2.medianBlur(image,7) # make this adjustable
    canny = cv2.Canny (blur,100,100) # make this adjustable too
    cn, hr = cv2.findContours (canny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    #mat, area = copy_contour_shape (image, cn)
    
    
    cluster_list = contour_to_color_cluster (image, cn)
    print len (cluster_list), len (cn)
    
    #print get_mean_color (mat, area)
    cv2.namedWindow('test')
    cv2.imshow ('test', cluster_list [0].get_mat ())
    #print cluster_list [71].mean 
    cv2.waitKey ()
    

if __name__ == '__main__':
    main ()
