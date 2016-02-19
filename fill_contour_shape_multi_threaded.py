#!/usr/bin/python

from multiprocessing import Process, Queue
import time
import sys
import numpy as np
import cv2

class MyThread:
    queues = None # []
    processes = None # []
    threads = 4 # default
    target = None # ()
    args = None
    return_data = None # []
    
    def __init__ (self, threads, target, args):
        self.queues = []
        self.processes = []
        self.threads = threads
        self.target = target
        self.args = args
        self.return_data = []
        self.initialize ()

    def initialize (self):
        for x in xrange (self.threads):
            p = Process (target = self.target, args = (self, x))
            q = Queue ()
            self.processes .append (p)
            self.queues.append (q)
            
    def start (self):
        for t in xrange (self.threads):
            self.processes [t].start ()

    def join (self):
        for t in xrange (self.threads):
            #print len (self.queues), t
            self.return_data.append (self.queues [t].get ())
            self.processes [t].join ()
    
    def get_data (self):
        if self.return_data is None:
            self.join ()
            
        return self.return_data

def copy_contour_shape_multiprocessing (image, cn):
    if type (cn) is list:
        n = cn [0]

        for x in xrange (1, len (cn)):
            n = np.append (n, cn [x], axis = 0)
        
        cn = n

    w = []
    h = []
    area = []
    #print cn

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
    
    print "Going for {} x {} iterations...".format (maxw - minw, maxh - minh)
    cx = 0
    cy = 0

    args = dict ()
    args ["image"] = image
    args ["minh"] = minh
    args ["maxh"] = maxh
    args ["minw"] = minw
    args ["maxw"] = maxw
    args ["hh"] = hh
    args ["ww"] = ww
    args ["a"] = a
    
    mythread = MyThread (4, copy_contour_shape_multiprocessing_run_thread, args)
    mythread.start ()
    mats = mythread.get_data ()
    mythread.join ()

    mat = np.ndarray ([0, maxw - minw, 3], np.uint8)
    mat.fill (0)
    for x in mats:
        mat = np.append (mat, x, axis = 0)
                
    return mat


def copy_contour_shape_multiprocessing_run_thread (mythread, thread_number):
    image = mythread.args ["image"]
    minh = mythread.args ["minh"]
    maxh = mythread.args ["maxh"]
    minw = mythread.args ["minw"]
    maxw = mythread.args ["maxw"]
    hh = mythread.args ["hh"]
    ww = mythread.args ["ww"]
    a = mythread.args ["a"]
    
    iteration = (maxh - minh) / float (mythread.threads)
    maxh = minh + (iteration * (thread_number + 1))
    minh = minh + (iteration * (thread_number))
    mat = np.ndarray ([maxh - minh, maxw - minw, 3], np.uint8)
    mat.fill (0)
    for x in range (int (minw), int (maxw)):
        for y in range (int (minh), int (maxh)):
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
                #print x, y
                continue
    #print "q",mythread.queues [thread_number]
    mythread.queues [thread_number].put (mat)


class Timer:
    epoch = time.clock ()
    
    def time (self):
        return time.clock () - self.epoch

def copy_contour_shape_multi_calculation (image, minh, maxh, minw, maxw, hh, ww, a, q):
    mat = np.ndarray ([maxh - minh, maxw - minw, 3], np.uint8)
    mat.fill (0)
    for x in range (int (minw), int (maxw)):
        for y in range (int (minh), int (maxh)):
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
                #print x, y
                continue
    q.put (mat)

def copy_contour_shape_multi (image, cn):
    if type (cn) is list:
        n = cn [0]

        for x in xrange (1, len (cn)):
            n = np.append (n, cn [x], axis = 0)
        
        cn = n

    w = []
    h = []
    area = []
    #print cn

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
    
    print "Going for {} x {} iterations...".format (maxw - minw, maxh - minh)
    cx = 0
    cy = 0

    iteration = (maxh - minh) / 4.0
    q1 = Queue ()
    q2 = Queue ()
    q3 = Queue ()
    q4 = Queue ()
    p1 = Process (target = copy_contour_shape_multi_calculation, args = (image, minh, minh + iteration, minw, maxw, hh, ww, a, q1))
    p2 = Process (target = copy_contour_shape_multi_calculation, args = (image, minh + iteration, minh + (2* iteration), minw, maxw, hh, ww, a, q2))
    p3 = Process (target = copy_contour_shape_multi_calculation, args = (image, minh + (2* iteration), minh + (3* iteration), minw, maxw, hh, ww, a, q3))
    p4 = Process (target = copy_contour_shape_multi_calculation, args = (image, minh + (3* iteration), maxh, minw, maxw, hh, ww, a, q4))
    
    #copy_contour_shape_multi_calculation (image, mat, minh, maxh, minw, maxw, hh, ww, a)
    p1.start ()
    p2.start ()
    p3.start ()
    p4.start ()
    print "a"
    mat1 = q1.get ()
    mat2 = q2.get ()
    mat3 = q3.get ()
    mat4 = q4.get ()
    print "b"
    p1.join ()
    p2.join ()
    p3.join ()
    p4.join ()
    mat = np.ndarray ([0, maxw - minw, 3], np.uint8)
    mat.fill (0)
    for x in mat1, mat2, mat3, mat4:
        mat = np.append (mat, x, axis = 0)
                
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
    t = Timer ()
    t1 = t.time ()
    mat = copy_contour_shape (image, cn)
    cv2.namedWindow('test')
    cv2.imshow ('test', mat)
    print t.time () - t1
    sys.stdout.flush ()
    cv2.waitKey ()
    #cv2.destroyAllWindows ()
    t1 = t.time ()
    mat = copy_contour_shape_multiprocessing (image, cn)
    print t.time () - t1
    #cv2.namedWindow('test')
    cv2.imshow ('test', mat)
    cv2.waitKey ()
    

if __name__ == '__main__':
    main ()

