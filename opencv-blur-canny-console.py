#!/usr/bin/python
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#
# Version 13.02.2016
#

from __future__ import division

import sys, glob, os
from gi.repository import Gtk, Gdk, GdkPixbuf, GObject, GLib
import cv2, numpy as np
from time import sleep, clock
import cv2, numpy as np
from colour import Color
import copy

#loader = GdkPixbuf.PixbufLoader.new_with_type ("jpeg")

def capture_from_camera ():
    camera = cv2.VideoCapture (0)
    for x in xrange (0, 10):
        retval, image = camera.read ()
        sleep (.1)
    
    retval, image = camera.read ()
    camera.release ()
    return image

def save_file (image):
    dialog = Gtk.FileChooserDialog (title = "Save Image",
                                    action = Gtk.FileChooserAction.SAVE)
    dialog.run ()
    filename = dialog.get_filename ()
    dialog.destroy ()
    
    if ".jpg" not in filename:
        filename = filename + ".jpg"
    
    return cv2.imwrite (filename, image)
                     

def message_box (title, message, message_type):
    mb = Gtk.MessageDialog (None, 0, message_type, Gtk.ButtonsType.OK, title)
    mb.format_secondary_text (message)
    mb.run ()
    mb.destroy ()

def reduce_colors (image, k = 8, repeat = 1):
    z = np.float32 (image.reshape((-1,3)))
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    #k = 8
    ret,label,center=cv2.kmeans(z,k, criteria, repeat, cv2.KMEANS_RANDOM_CENTERS)
    center = np.uint8(center)
    res = center[label.flatten()]
    res2 = res.reshape((image.shape))
    return res2

# the money shot right here
def cv2_image_to_gdk_pixbuf (image):
    retval, jpg = cv2.imencode (".jpg", image)
    loader = GdkPixbuf.PixbufLoader.new_with_type ("jpeg")
    loader.write (jpg)
    loader.close ()
    pixbuf = loader.get_pixbuf ()
    #GObject.Object.unref (loader)
    return pixbuf

class Timer:
    epoch = clock ()
    
    def get_time (self):
        return clock () - self.epoch

class Canny (Gtk.Grid):
    on = Gtk.Switch.new ()
    threshold1 = Gtk.SpinButton.new_with_range (1.0, 1000, 1)
    threshold2 = Gtk.SpinButton.new_with_range (1.0, 1000, 1)
    aperture = Gtk.SpinButton.new_with_range (3.0, 20, 1)
    l2_gradient = Gtk.CheckButton.new_with_label ("More Accurate\nL2")
    only_contours = Gtk.CheckButton.new_with_label ("Draw Only\nContours")
    contour_thickness = Gtk.SpinButton.new_with_range (1.0, 20.0, 1.0)
    color_button = Gtk.ColorButton.new_with_color (Gdk.Color.from_floats (0, 1, 0))
    color_button.set_use_alpha (False)
    show_contours = Gtk.Entry.new ()
    show_contours_all = Gtk.CheckButton.new_with_label ("All")
    show_contours_all.set_active (1)
    # this is just brilliant! python is simply amazing :)
    for c in l2_gradient.get_children (), only_contours.get_children ():
        for i in c:
            if type (i) is Gtk.Label:
                i.set_justify (2)
    
    
    def __init__ (self):
        Gtk.Grid.__init__ (self)
        self.attach (Gtk.Label.new (" "), 0, 0, 1, 1)
        self.attach (Gtk.Label.new (" "), 4, 0, 1, 1)
        self.attach (self.on, 1, 1, 1, 1)
        self.attach (Gtk.Label.new ("Threshold 1"), 1, 2, 1, 1)
        self.attach (self.threshold1, 1, 3, 1, 1)
        self.attach (Gtk.Label.new ("Threshold 2"), 1, 4, 1, 1)
        self.attach (self.threshold2, 1, 5, 1, 1)        
        l = Gtk.Label ("Show Contours")
        l.set_justify (2)
        self.attach (l, 1, 6, 1, 1)
        #self.attach (Gtk.Label.new ("All"), 1, 7, 1, 1)
        self.attach (self.show_contours_all, 1, 8, 1, 1)
        self.attach (self.show_contours, 1, 7, 1, 1)        
        self.attach (Gtk.Label.new ("Aperture"), 3, 1, 1, 1)
        self.attach (self.aperture, 3, 2, 1, 1)
        self.attach (self.l2_gradient, 3, 3, 1, 1)
        self.attach (self.only_contours, 3, 4, 1, 1)
        l = Gtk.Label ("Contour\nThickness")
        l.set_justify (2)
        self.attach (l, 3, 5, 1, 1)
        self.attach (self.contour_thickness, 3, 6, 1, 1)
        self.attach (self.color_button, 3, 7, 1, 1)
        self.set_column_spacing (10)
        self.set_row_spacing (5)
    
    def do_canny (self, image):
        if not self.on.get_active ():
            return image

        canny = cv2.Canny (image, \
                self.threshold1.get_value_as_int (), \
                self.threshold2.get_value_as_int (), \
                None, \
                self.aperture.get_value_as_int (), \
                self.l2_gradient.get_active ())
        
        cn = self.show_contours.get_text ()
        begin = -1
        end = -1

        if len (cn) > 0:
            if ":" in cn:
                split = cn.split (":")
                begin = int (split [0])
                end = int (split [1])
            else:
                begin = int (cn)
        
        if not self.show_contours_all.get_active ():
            if begin >= 0 and end >= 0:
                canny = canny [begin:end]
            elif begin >= 0:
                canny = canny [begin]
        
        if not self.only_contours.get_active ():
            return canny
        else:
            color = self.color_button.get_color ().to_floats ()
            c = Color (rgb = color)
            new_color = tuple ([c.blue * 255, c.green * 255, c.red * 255])
            #print new_color
            cn, hr = cv2.findContours (canny, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
            cv2.drawContours (image, cn, -1, new_color, self.contour_thickness.get_value_as_int ())
            return image

class TreeBrowser (Gtk.TreeView):
    timer = Timer ()
    time = timer.get_time ()
    
    store = Gtk.ListStore (GdkPixbuf.Pixbuf, str, str)
    rp = Gtk.CellRendererPixbuf ()
    rd = Gtk.CellRendererText ()
    cp = Gtk.TreeViewColumn ("Thumb", rp, pixbuf = 0)
    cd = Gtk.TreeViewColumn ("Filename", rd, text = 1)
    
    def __init__(self):
        Gtk.TreeView.__init__(self)
        self.set_model (self.store)
        self.append_column (self.cp)
        self.append_column (self.cd)
        self.set_activate_on_single_click (1)
        self.get_selection ().set_mode (1)

    def propagate_dir (self, dirname):
        self.set_model (None)
        self.store.clear ()
        files = glob.glob (dirname + "/*jpg")
        #print files
        for i in files:
            #print "loading file {} of {}".format (files.index (i), len (files))
            #try:
                #pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale (i, 256, 256, 1)
            #except GLib.Error as e:
                #print e
            
            self.store.append ([None, os.path.basename (i), i])
    
        self.set_model (self.store)
        
    def load_thumbs_lazy (self, * args):
        #print self.timer.get_time () - self.time
        if self.timer.get_time () - self.time < .1:
            return
        start, end = self.get_visible_range ()
        #print start, end
        for x in xrange (int (start.to_string ()), int (end.to_string ())):
            path = Gtk.TreePath.new_from_string (str (x))
            i = self.store.get_iter (path)
            p = self.store.get (i, 0) [0]
            if p is not None:
                #print "already loaded"
                continue
            filename = self.store.get (i, 2) [0]
            p = GdkPixbuf.Pixbuf.new_from_file_at_scale (filename, 256, 200, 1)
            self.store.set_value (i, 0, p)
        
        self.time = self.timer.get_time ()
        
class FileBrowser (Gtk.IconView):
    store = Gtk.ListStore (GdkPixbuf.Pixbuf, str, str)
    current_dir = None
    
    def __init__(self):
        Gtk.IconView.__init__(self)
        self.set_model (self.store)
        self.set_pixbuf_column (0)
        self.set_text_column (1)
        self.set_item_orientation (1)
        #self.set_columns (1)
        
    def propagate_dir (self, dirname):
        files = glob.glob (dirname + "/*jpg")
        #print files
        for i in files:
            #print "loading file {} of {}".format (files.index (i), len (files))
            #try:
                #pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale (i, 256, 256, 1)
            #except GLib.Error as e:
                #print e
            
            self.store.append ([None, os.path.basename (i), i])

class Image:
    filename = None
    pixbuf = None
    #cache = [[]]
    old_size = [0, 0]
    ratio = 1.0
    width = 0
    height = 0
    camera_shot = None

class BlurConfig:
        def __init__ (self):
            self.box_filter = None
            self.box_filter_on = None
            self.box_filter_kernel_x = None
            self.box_filter_kernel_y = None
            #self.box_filter_sigma_x = None
            #self.box_filter_sigma_y = None
            self.box_filter_normalize = None
            
            self.normalized_box_filter = None
            self.normalized_box_filter_on = None
            self.normalized_box_filter_kernel_x = None
            self.normalized_box_filter_kernel_y = None

            self.convolution_2d = None
            self.convolution_2d_on = None
            self.convolution_2d_kernel_x = None
            self.convolution_2d_kernel_y = None
            
            self.gaussian_blur = None
            self.gaussian_blur_on = None
            self.gaussian_blur_kernel_x = None
            self.gaussian_blur_kernel_y = None
            self.gaussian_blur_sigma_x = None
            self.gaussian_blur_sigma_y = None
            
            self.median_blur = None
            self.median_blur_on = None
            self.median_blur_kernel = None

            self.bilateral_filter = None
            self.bilateral_filter_on = None
            self.bilateral_filter_diameter = None
            self.bilateral_filter_sigma_color = None
            self.bilateral_filter_sigma_space = None
            
            self.adaptive_bilateral_filter = None
            self.adaptive_bilateral_filter_on = None
            self.adaptive_bilateral_filter_kernel_x = None
            self.adaptive_bilateral_filter_kernel_y = None
            self.adaptive_bilateral_filter_sigma_space = None
            self.adaptive_bilateral_filter_max_sigma_color = None
            
            
class Blur:
    def simple_blur_do (self, image):
        blur = cv2.blur (image, (self.config.normalized_box_filter_kernel_x.get_value_as_int (), \
                                self.config.normalized_box_filter_kernel_y.get_value_as_int ()))
        return blur
        
    def box_filter_do (self, image):
        blur = cv2.boxFilter (image, -1, (self.config.box_filter_kernel_x.get_value_as_int (), self.config.box_filter_kernel_y.get_value_as_int ()), None, (-1,-1), self.config.box_filter_normalize.get_active ())
        return blur
    
    def convolution_2d_do (self, image):
        #print "hi", (self.config.convolution_2d_kernel_x.get_value (), self.config.convolution_2d_kernel_y.get_value ())
        blur = cv2.filter2D (image, cv2.CV_8U, (self.config.convolution_2d_kernel_x.get_value (), self.config.convolution_2d_kernel_y.get_value ()))
        return blur
    
    def gaussian_blur_do (self, image):
        blur = cv2.GaussianBlur (image, (self.config.gaussian_blur_kernel_x.get_value_as_int (), \
                                 self.config.gaussian_blur_kernel_y.get_value_as_int ()),
                                 self.config.gaussian_blur_sigma_x.get_value_as_int (),
                                 None,
                                 self.config.gaussian_blur_sigma_y.get_value_as_int ())
        
        return blur
    
    def median_blur_do (self, image):
        blur = cv2.medianBlur (image, self.config.median_blur_kernel.get_value_as_int ())
        return blur
    
    def bilateral_filter_do (self, image):
        return cv2.bilateralFilter (image, self.config.bilateral_filter_diameter.get_value_as_int (), \
                                    self.config.bilateral_filter_sigma_color.get_value_as_int (),
                                    self.config.bilateral_filter_sigma_space.get_value_as_int ())

    def adaptive_bilateral_filter_do (self, image):
        return cv2.adaptiveBilateralFilter (image, \
                (self.config.adaptive_bilateral_filter_kernel_x.get_value_as_int (), \
                self.config.adaptive_bilateral_filter_kernel_y.get_value_as_int ()), \
                self.config.adaptive_bilateral_filter_sigma_space.get_value_as_int (), \
                self.config.adaptive_bilateral_filter_max_sigma_color.get_value_as_int ())

    def do_blur (self, image):
        if self.config.normalized_box_filter_on.get_active ():
            image = self.simple_blur_do (image)
        
        if self.config.box_filter_on.get_active ():
            image = self.box_filter_do (image)
        
        if self.config.convolution_2d_on.get_active ():
            image = self.convolution_2d_do (image)
        
        if self.config.gaussian_blur_on.get_active ():
            image = self.gaussian_blur_do (image)
        
        if self.config.median_blur_on.get_active ():
            image = self.median_blur_do (image)
        
        if self.config.bilateral_filter_on.get_active ():
            image = self.bilateral_filter_do (image)

        if self.config.adaptive_bilateral_filter_on.get_active ():
            image = self.adaptive_bilateral_filter_do (image)
        
        return image
        
    def __init__ (self):
        self.config = BlurConfig ()
        notebook = Gtk.Notebook ()
        notebook.set_scrollable (1)
        notebook.popup_enable ()
        notebook.set_tab_pos (1)
        bx = Gtk.Label ("Box Filter")
        bx.set_justify (1)
        notebook.append_page (self.box_filter (), bx)
        nbx = Gtk.Label ("Normalized\nBox Filter")
        nbx.set_justify (2)
        notebook.append_page (self.simple_blur (), nbx)
        d2 = Gtk.Label ("2D\nConvolution")
        d2.set_justify (2)
        notebook.append_page (self.convolution_2d (), d2)
        gb = Gtk.Label ("Gaussian\nBlur")
        gb.set_justify (2)
        notebook.append_page (self.gaussian_blur (), gb)
        mb = Gtk.Label ("Median\nBlur")
        mb.set_justify (2)
        notebook.append_page (self.median_blur (), mb)
        blf = Gtk.Label ("Bilateral\nFilter")
        blf.set_justify (2)
        notebook.append_page (self.bilateral_filter (), blf)
        abf = Gtk.Label ("Adaptive\nBilateral\nFilter")
        abf.set_justify (2)
        notebook.append_page (self.adaptive_bilateral_filter (), abf)
        self.widget = notebook
        
    def simple_blur (self):
        simple = Gtk.VBox.new (False, 4)
        simple.set_homogeneous (0)
        self.sswitch = Gtk.Switch ()
        self.config.normalized_box_filter_on = self.sswitch
        #kernel = Gtk.ButtonBox (0, homogeneous = 0)
        self.sspin = Gtk.SpinButton.new_with_range (1.0, 20.0, 1.0)
        self.sspin2 = Gtk.SpinButton.new_with_range (1.0, 20.0, 1.0)
        self.config.normalized_box_filter_kernel_x = self.sspin
        self.config.normalized_box_filter_kernel_y = self.sspin2
        simple.pack_start (self.sswitch, 0, 0, 20)
        simple.pack_start (Gtk.Label ("Kernel"), 0, 0, 0)
        simple.pack_start (self.sspin, 0, 0, 0)
        simple.pack_start (self.sspin2, 0, 0, 0)
        
        #simple.pack_start (kernel, 0, 0, 0)
        
        self.swidget = simple
        pad = Gtk.HBox.new (1,4)
        pad.pack_start (simple, 1, 1, 20)
        self.config.normalized_box_filter = pad
        return pad
    
    def convolution_2d (self):
        conv2d = Gtk.VBox.new (False, 4)
        conv2d.set_homogeneous (0)
        self.cswitch = Gtk.Switch ()
        self.config.convolution_2d_on = self.cswitch
        #kernel = Gtk.ButtonBox (0, homogeneous = 0)
        self.cspin = Gtk.SpinButton.new_with_range (0.1, 20.0, .1)
        self.cspin2 = Gtk.SpinButton.new_with_range (0.1, 20.0, .1)
        self.config.convolution_2d_kernel_x = self.cspin
        self.config.convolution_2d_kernel_y = self.cspin2
        conv2d.pack_start (self.cswitch, 0, 0, 20)
        conv2d.pack_start (Gtk.Label ("Kernel"), 0, 0, 0)
        conv2d.pack_start (self.cspin, 0, 0, 0)
        conv2d.pack_start (self.cspin2, 0, 0, 0)
        
        #conv2d.pack_start (kernel, 0, 0, 0)
        
        self.cwidget = conv2d
        pad = Gtk.HBox.new (1,4)
        pad.pack_start (conv2d, 1, 1, 20)
        self.config.convolution_2d = pad
        return pad
    
    def bilateral_filter (self):
        bfil = Gtk.VBox.new (False, 4)
        self.bswitch = Gtk.Switch ()
        self.config.bilateral_filter_on = self.bswitch
        bfil.set_homogeneous (0)
        #kernel = Gtk.ButtonBox (0, homogeneous = 0)
        self.bspin = Gtk.SpinButton.new_with_range (1.0, 20.0, 1.0)
        self.bspin2 = Gtk.SpinButton.new_with_range (1.0, 1000.0, 1.0)
        self.bspin3 = Gtk.SpinButton.new_with_range (1.0, 1000.0, 1.0)
        self.config.bilateral_filter_diameter = self.bspin
        self.config.bilateral_filter_sigma_color = self.bspin2
        self.config.bilateral_filter_sigma_space = self.bspin3
        bfil.pack_start (self.bswitch, 0, 0, 20)
        bfil.pack_start (Gtk.Label ("Diameter"), 0, 0, 0)
        bfil.pack_start (self.bspin, 0, 0, 0)
        bfil.pack_start (Gtk.Label ("Sigma Color"), 0, 0, 0)
        bfil.pack_start (self.bspin2, 0, 0, 0)
        bfil.pack_start (Gtk.Label ("Sigma Space"), 0, 0, 0)
        bfil.pack_start (self.bspin3, 0, 0, 0)
        
        #bfil.pack_start (kernel, 0, 0, 0)
        
        self.bwidget = bfil
        pad = Gtk.HBox.new (1,4)
        pad.pack_start (bfil, 1, 1, 20)
        self.config.bilateral_filter = pad
        return pad

    def adaptive_bilateral_filter (self):
        abfil = Gtk.VBox.new (False, 4)
        abfil.set_homogeneous (0)
        self.abswitch = Gtk.Switch ()
        self.config.adaptive_bilateral_filter_on = self.abswitch
        #kernel = Gtk.ButtonBox (0, homogeneous = 0)
        #kernel.set_homogeneous (0)
        self.abspin = Gtk.SpinButton.new_with_range (1.0, 20.0, 1.0)
        self.abspin1 = Gtk.SpinButton.new_with_range (1.0, 20.0, 1.0)
        self.abspin2 = Gtk.SpinButton.new_with_range (1.0, 1000.0, 1.0)
        self.abspin3 = Gtk.SpinButton.new_with_range (1.0, 1000.0, 1.0)
        self.config.adaptive_bilateral_filter_kernel_x = self.abspin
        self.config.adaptive_bilateral_filter_kernel_y = self.abspin1
        self.config.adaptive_bilateral_filter_sigma_space = self.abspin2
        self.config.adaptive_bilateral_filter_max_sigma_color = self.abspin3
        abfil.pack_start (self.abswitch, 0, 0, 20)
        abfil.pack_start (Gtk.Label ("Kernel"), 0, 0, 0)
        abfil.pack_start (self.abspin, 0, 0, 0)
        abfil.pack_start (self.abspin1, 0, 0, 0)
        abfil.pack_start (Gtk.Label ("Sigma\nSpace"), 0, 0, 0)
        abfil.pack_start (self.abspin2, 0, 0, 0)
        abfil.pack_start (Gtk.Label ("Max Sigma\nColor"), 0, 0, 0)
        abfil.pack_start (self.abspin3, 0, 0, 0)
        
        #abfil.pack_start (kernel, 0, 0, 0)
        
        self.abwidget = abfil
        pad = Gtk.HBox.new (1,4)
        pad.pack_start (abfil, 1, 1, 20)
        self.config.adaptive_bilateral_filter = pad
        return pad

    def median_blur (self):
        median = Gtk.VBox.new (False, 4)
        self.mswitch = Gtk.Switch ()
        self.config.median_blur_on = self.mswitch
        median.set_homogeneous (0)
        #kernel = Gtk.ButtonBox (0, homogeneous = 0)
        self.mspin = Gtk.SpinButton.new_with_range (1.0, 20.0, 1.0)
        self.config.median_blur_kernel = self.mspin
        median.pack_start (self.mswitch, 0, 0, 20)
        median.pack_start (Gtk.Label ("Kernel size"), 0, 0, 0)
        median.pack_start (self.mspin, 0, 0, 0)
        
        #median.pack_start (kernel, 0, 0, 0)
        
        self.mwidget = median
        pad = Gtk.HBox.new (1,4)
        pad.pack_start (median, 1, 1, 20)
        self.config.median_blur = pad
        return pad

    def gaussian_blur (self):
        gauss = Gtk.VBox.new (False, 4)
        self.gswitch = Gtk.Switch ()
        self.config.gaussian_blur_on = self.gswitch
        gauss.set_homogeneous (0)
        #kernel = Gtk.ButtonBox (0, homogeneous = 0)
        gauss.set_homogeneous (False)
        #kernel.set_homogeneous (False)
        #sigma = Gtk.ButtonBox (0, homogeneous = 0)
        #sigma.set_homogeneous (False)
        self.gspin = Gtk.SpinButton.new_with_range (1.0, 20.0, 1.0)
        self.gspin2 = Gtk.SpinButton.new_with_range (1.0, 20.0, 1.0)
        self.gsigmax = Gtk.SpinButton.new_with_range (1.0, 20.0, 1.0)
        self.gsigmay = Gtk.SpinButton.new_with_range (1.0, 20.0, 1.0)
        gauss.pack_start (self.gswitch, 0, 0, 20)
        gauss.pack_start (Gtk.Label ("Kernel"), 0, 0, 0)
        gauss.pack_start (self.gspin, 0, 0, 0)
        gauss.pack_start (self.gspin2, 0, 0, 0)
        gauss.pack_start (Gtk.Label ("Sigma X"), 0, 0, 0)
        gauss.pack_start (self.gsigmax, 0, 0, 0)
        gauss.pack_start (Gtk.Label ("Sigma Y"), 0, 0, 0)
        gauss.pack_start (self.gsigmay, 0, 0, 0)
        self.config.gaussian_blur_kernel_x = self.gspin
        self.config.gaussian_blur_kernel_y = self.gspin2
        self.config.gaussian_blur_sigma_x = self.gsigmax
        self.config.gaussian_blur_sigma_y = self.gsigmay
        #gauss.pack_start (kernel, 0, 0, 0)
        #gauss.pack_start (sigma, 0, 0, 0)
        
        self.gwidget = gauss
        pad = Gtk.HBox.new (1,4)
        pad.pack_start (gauss, 1, 1, 20)
        self.config.gaussian_blur = pad
        return pad

    def box_filter (self):
        box_fil = Gtk.VBox.new (False, 4)
        box_fil.set_homogeneous (0)
        self.bfswitch = Gtk.Switch ()
        self.config.box_filter_on = self.bfswitch
        #kernel = Gtk.ButtonBox (0, homogeneous = 0)
        #sigma = Gtk.ButtonBox (0, homogeneous = 0)
        self.bfspin = Gtk.SpinButton.new_with_range (1.0, 20.0, 1.0)
        self.bfspin2 = Gtk.SpinButton.new_with_range (1.0, 20.0, 1.0)
        self.bfsigmax = Gtk.SpinButton.new_with_range (1.0, 20.0, 1.0)
        self.bfsigmay = Gtk.SpinButton.new_with_range (1.0, 20.0, 1.0)
        box_fil.pack_start (self.bfswitch, 0, 0, 20)
        box_fil.pack_start (Gtk.Label ("Kernel"), 0, 0, 0)
        box_fil.pack_start (self.bfspin, 0, 0, 0)
        box_fil.pack_start (self.bfspin2, 0, 0, 0)
        #box_fil.pack_start (Gtk.Label ("Sigma X"), 0, 0, 0)
        #box_fil.pack_start (self.bfsigmax, 0, 0, 0)
        #box_fil.pack_start (Gtk.Label ("Sigma Y"), 0, 0, 0)
        #box_fil.pack_start (self.bfsigmay, 0, 0, 0)
        self.config.box_filter_kernel_x = self.bfspin
        self.config.box_filter_kernel_y = self.bfspin2
        #self.config.box_filter_sigma_x = self.bfsigmax
        #self.config.box_filter_sigma_y = self.bfsigmay
        self.bf_normalize = Gtk.CheckButton (label = "Normalize")
        self.config.box_filter_normalize = self.bf_normalize
        #box_fil.pack_start (kernel, 0, 0, 0)
        #box_fil.pack_start (sigma, 0, 0, 0)
        box_fil.pack_start (self.bf_normalize, 0, 0, 0)
        
        self.gwidget = box_fil
        pad = Gtk.HBox.new (1,4)
        pad.pack_start (box_fil, 1, 1, 20)
        return pad

class ReduceColors:
    widget = None
    def __init__ (self):
        master = Gtk.VBox.new (False, 4)
        self.switch = Gtk.Switch ()
        master.pack_start (self.switch, 0, 0, 20)
        l = Gtk.Label ("Number of\nclusters")
        l.set_justify (2)
        master.pack_start (l, 0, 0, 0)
        self.k = Gtk.SpinButton.new_with_range (1, 256, 1)
        master.pack_start (self.k, 0, 0, 0)
        
        master.pack_start (Gtk.Label ("Attempts"), 0, 0, 0)
        self.repeat = Gtk.SpinButton.new_with_range (1, 20, 1)
        master.pack_start (self.repeat, 0, 0, 0)
        
        pad = Gtk.HBox.new (1,4)
        pad.pack_start (master, 0, 0, 20)
        self.widget = pad
                
    def reduce_colors (self, image):
        if not self.switch.get_active ():
            return image
        else:
            return reduce_colors (image, self.k.get_value_as_int (), self.repeat.get_value_as_int ())
        
class UI:
    timer = Timer ()
    
    window = Gtk.Window ()
    window_size = [0, 0]
    window_state = None

    img = Image ()
    image = Gtk.Image ()
    
    master = Gtk.VBox.new (False, 0)
    window.add (master)
    window.set_title ("Control Panel")
    window.set_icon_from_file ("/usr/local/share/icons/clover.png")
    
    # If you want a custom header bar
    #window.set_decorated (False)
    #header = Gtk.HeaderBar ()
    #header.set_title ("Control Panel")
    #header.set_subtitle ("Clover OpenCV Visual Cortex")
    #header.set_show_close_button (True)
    #master.pack_start (header, 0, 0, 0)
    
    paned = Gtk.Paned ()
    master.pack_start (paned, True, True, 0)
    
    sw1 = Gtk.ScrolledWindow.new ()
    paned.pack1 (sw1, resize = 1, shrink = 0)
    
    event_box = Gtk.EventBox.new ()
    event_box.add (image)
    sw1.add (event_box)
    sw1.set_policy (1, 1)
    #sw1.set_opacity (.75)
    
    window.set_size_request (800, 600)
    
    notebook = Gtk.Notebook ()
    notebook.set_scrollable (1)
    notebook.popup_enable ()
    sw2 = Gtk.ScrolledWindow ()
    sw2.set_policy (1, 1)
    
    sw2.add (notebook)
    paned.pack2 (sw2, resize = 0, shrink = 0)
    paned.set_position (500)
    paned.position = 500
    #sw2.set_size_request (300, 180)
    sw2.show_all ()
    
    blur = Blur ()
    notebook.append_page (blur.widget, Gtk.Label ("Blur"))
    
    color_red = ReduceColors ()
    notebook.append_page (color_red.widget, Gtk.Label ("Color Reduction"))
    
    canny = Canny ()
    notebook.append_page (canny, Gtk.Label ("Canny Edge\nDetection"))
    
    file_browser = TreeBrowser ()
    if len (sys.argv) > 1:
        file_browser.propagate_dir (os.path.dirname (sys.argv [1]))
    swfb = Gtk.ScrolledWindow.new ()
    swfb.add (file_browser)
    swfb.set_policy (1, 1)
    notebook.append_page (swfb, Gtk.Label ("File Browser"))
    
    zoom_box = Gtk.ActionBar.new ()
    icon_size = 2 # 3
    zoom_in = Gtk.Button.new_from_icon_name ("gtk-zoom-in", icon_size)
    zoom_out = Gtk.Button.new_from_icon_name ("gtk-zoom-out", icon_size)
    zoom_fit = Gtk.Button.new_from_icon_name ("gtk-zoom-fit", icon_size)
    zoom_100 = Gtk.Button.new_from_icon_name ("gtk-zoom-100", icon_size)
    
    zoom_in.set_tooltip_text ("Zoom in")
    zoom_out.set_tooltip_text ("Zoom out")
    zoom_fit.set_tooltip_text ("Zoom fit")
    zoom_100.set_tooltip_text ("Zoom to original size")
    
    zoom_box.pack_start (zoom_in)
    zoom_box.pack_start (zoom_out)
    zoom_box.pack_start (zoom_fit)
    zoom_box.pack_start (zoom_100)
    zoom_box.pack_start (Gtk.HSeparator.new ())

    camera_button = Gtk.Button.new_from_icon_name ("camera", icon_size)
    zoom_box.pack_start (camera_button)
    zoom_box.pack_start (Gtk.HSeparator.new ())
    
    open_button = Gtk.Button.new_from_icon_name ("gtk-open", icon_size)
    save_button = Gtk.Button.new_from_icon_name ("gtk-save", icon_size)
    zoom_box.pack_start (open_button)
    zoom_box.pack_start (save_button)
    zoom_step = 50
    open_button.set_tooltip_text ("Open file")
    save_button.set_tooltip_text ("Save file")
    camera_button.set_tooltip_text ("Take picture from camera")
    
    status = Gtk.Statusbar.new ()
    zoom_box.pack_start (status)
    
    master.pack_end (zoom_box, 0, 0, 0)
    window.show_all ()
    
    w = window.get_allocated_width () - notebook.get_allocated_width ()
    paned.set_position (w)
    
    scroll_event_time = 0
    
    while Gtk.events_pending ():
        Gtk.main_iteration_do (0)
    
    def set_status (self, message):
        self.status.push (self.status.get_context_id (message), message)
        self.update_ui ()
    
    def load_image (self, filename):
        self.load_image_at_size (filename, self.sw1.get_allocated_width () -5, self.sw1.get_allocated_height () - 5)
    
    def load_image_at_size (self, filename, width, height):
        #if self.img.old_size [0] == width and self.img.old_size [1] == height:
            #return

        #print "[{}] Loading {} at size {} x {}".format (self.timer.get_time (), filename, width, height)
        
        # we load the pixbuf from disk only once and then do stuff to it in memory
        if self.img.pixbuf == None:
            self.img.pixbuf = GdkPixbuf.Pixbuf.new_from_file (filename)
            self.img.width = self.img.pixbuf.get_width () * 1.0
            self.img.height = self.img.pixbuf.get_height () * 1.0
            self.img.filename = filename
            
            if self.img.width > self.img.height:
                self.img.ratio = self.img.width / self.img.height
            else:
                self.img.ratio = float (self.img.height / float (self.img.width))
        
        w = self.img.pixbuf.get_width ()
        h = self.img.pixbuf.get_height ()
        
        ratio = w  / float (h)
        if width > 0 and height > 0:
            if w > h:
                pixbuf = self.img.pixbuf.scale_simple (float (width), float (width / ratio), 0)
            else:
                pixbuf = self.img.pixbuf.scale_simple (height * ratio, height, 0)
        
        else:
            pixbuf = self.img.pixbuf.copy ()
        
        self.image.set_from_pixbuf (pixbuf)
        #pixbuf = GdkPixbuf.Pixbuf.new_from_file (filename)
        #self.img.cache.append ([filename, pixbuf])
        #self.image.set_from_pixbuf (pixbuf.scale_simple (width, height, 3))
        self.img.old_size [0] = width
        self.img.old_size [1] = height
    
    def image_zoom_100 (self, *args):
        self.load_image_at_size (self.img.filename, -1, -1)
    
    def image_zoom_in (self, *args):
        width = GdkPixbuf.Pixbuf.get_width (self.image.get_pixbuf ())
        height = GdkPixbuf.Pixbuf.get_height (self.image.get_pixbuf ())
        
        self.load_image_at_size (self.img.filename, width + self.zoom_step, height + self.zoom_step)
        
    def image_zoom_out (self, *args):
        width = GdkPixbuf.Pixbuf.get_width (self.image.get_pixbuf ())
        height = GdkPixbuf.Pixbuf.get_height (self.image.get_pixbuf ())
        
        self.load_image_at_size (self.img.filename, width - self.zoom_step, height - self.zoom_step)
    
    def image_get_current_zoom (self):
        p = self.image.get_pixbuf ()
        width = 640
        height = 480
        
        if p is not None:
            width = GdkPixbuf.Pixbuf.get_width (p)
            height = GdkPixbuf.Pixbuf.get_height (p)
        else:
            width = self.sw1.get_allocated_width () -5
            height = self.sw1.get_allocated_height () -5
        
        return width, height
    
    def refresh_image (self, **args):
        w, h = self.image_get_current_zoom ()
        self.load_image_at_size (None, w, h)
    
    def update_ui (self):
        while Gtk.events_pending ():
            Gtk.main_iteration_do (0)
    
    def image_zoom_2x (self):
        p = GdkPixbuf.Pixbuf.new_from_file (self.img.filename)
        self.load_image_at_size (self.img.filename, p.get_width () * 2, p.get_height () * 2)

    def image_zoom_4x (self):
        p = GdkPixbuf.Pixbuf.new_from_file (self.img.filename)
        self.load_image_at_size (self.img.filename, p.get_width () * 4, p.get_height () * 4)
    
    def image_zoom_3x (self):
        p = GdkPixbuf.Pixbuf.new_from_file (self.img.filename)
        self.load_image_at_size (self.img.filename, p.get_width () * 3, p.get_height () * 3)
    
    def handle_size_change (self, *args):
        self.update_ui ()
        w, h = self.window.get_size ()
        #print args [0], args [1].type, w, self.window_size [0]
        #if type (args [0]) == Gtk.ScrolledWindow:
            #if self.paned.position == self.paned.get_position ():
                #print "no1"
                #return
            #self.paned.position = self.paned.get_position ()
        #if len (args) > 1:
            #if type (args [1]) == Gdk.EventConfigure:
                #if args [1].type == Gdk.EventType.CONFIGURE:
                    #if self.window_size [0] == w and self.window_size [1] == h:
                        #print args [1].type
                        #return
            #elif type (args [1]) == Gdk.EventWindowState:
                #if args [1].new_window_state != Gdk.WindowState.FULLSCREEN and \
                    #args [1].new_window_state != Gdk.WindowState.MAXIMIZED and \
                    #args [1].new_window_state != Gdk.WindowState.FOCUSED:
                        #print args [1].new_window_state
                        #return
                    
                #if self.window_size [0] == w and self.window_size [1] == h:
                        #return
                
        self.update_ui ()
        self.window_size [0] = w
        self.window_size [1] = h
        self.load_image (self.img.filename)
        self.update_ui ()
        return True

    def scroll_callback_handler (self, widget, event):
        if event.time - self.scroll_event_time < 100:
            return
        self.scroll_event_time = event.time
        
        if event.state == Gdk.ModifierType.CONTROL_MASK:
            t = event.get_scroll_deltas ()
            x = t [0]
            y = t [1]
            w, h = self.image_get_current_zoom ()
            
            if y > 0:
                self.load_image_at_size (self.img.filename, w - self.zoom_step, h - self.zoom_step)
            else:
                self.load_image_at_size (self.img.filename, w + self.zoom_step, h + self.zoom_step)
        return False
    
    def change_image (self, *args):
        store, path = self.file_browser.get_selection ().get_selected_rows ()
        if len (path) is 0:
            return

        i = self.file_browser.store.get_iter (path)
        self.img.filename = self.file_browser.store.get (i, 2) [0]
        self.do_effects ()
        #self.img.pixbuf = GdkPixbuf.Pixbuf.new_from_file (self.img.filename)
        self.load_image (self.img.filename)
    
    def save_image (self, *args):
        dialog = Gtk.FileChooserDialog ("Save Image", self.window,
                                        Gtk.FileChooserAction.SAVE,
                                        (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_SAVE, Gtk.ResponseType.OK))
        response = dialog.run ()
        filename = dialog.get_filename ()
        dialog.destroy ()
        
        if response is Gtk.ResponseType.CANCEL or filename is None:
            return
        
        if ".jpg" not in filename:
            filename = filename + ".jpg"
        
        self.img.pixbuf.savev (filename, "jpeg", "", [])
        

    def open_image (self, *args):
        dialog = Gtk.FileChooserDialog ("OPen Image", self.window,
                                        Gtk.FileChooserAction.OPEN,
                                        (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_SAVE, Gtk.ResponseType.OK))
        response = dialog.run ()
        filename = dialog.get_filename ()
        dialog.destroy ()
        
        if response is Gtk.ResponseType.CANCEL or filename is None:
            return
        
        self.img.filename = filename
        self.do_effects (self)
        self.file_browser.propagate_dir (os.path.dirname (filename))
        #self.file_browser.load_thumbs_lazy ()
        #self.file_browser.get_hadjustment ().emit ("value-changed")

    def connect_signals (self):
        #self.window.connect ("configure-event", self.handle_size_change)
        self.window.connect ("key-press-event", self.hotkeys)
        #self.master.connect ("size-allocate", self.handle_size_change)
        #self.sw2.connect ("size-allocate", self.handle_size_change)
        #self.window.connect ("window-state-event", self.handle_size_change)
        self.sw1.connect ("scroll-event", self.scroll_callback_handler)
        self.window.connect ("delete-event", Gtk.main_quit)
        self.zoom_in.connect ("clicked", self.image_zoom_in)
        self.zoom_out.connect ("clicked", self.image_zoom_out)
        self.zoom_100.connect ("clicked", self.image_zoom_100)
        self.zoom_fit.connect ("clicked", self.handle_size_change)
        #self.file_browser.connect ("row-activated", self.change_image)
        self.file_browser.get_selection ().connect ("changed", self.change_image)
        self.file_browser.get_vadjustment ().connect ("value-changed", self.file_browser.load_thumbs_lazy)
        self.file_browser.get_hadjustment ().connect ("value-changed", self.file_browser.load_thumbs_lazy)
        self.file_browser.get_hadjustment ().emit ("value-changed")
        self.save_button.connect ("clicked", self.save_image)
        self.open_button.connect ("clicked", self.open_image)
        self.camera_button.connect ("clicked", self.do_capture_from_camera)
    
    def hotkeys (self, widget, event):        
        #print event.keyval, event.state
        if event.state > 5:
            if self.notebook.get_n_pages () >= event.keyval - 49:
                self.notebook.set_current_page (event.keyval - 49)
        elif event.state > 1 and event.state < 5:
            current = self.notebook.get_nth_page (self.notebook.get_current_page ())
            children = current.get_children ()
            children.insert (0, current)
            for child in children:
                if type (child) == Gtk.Notebook:
                    if child.get_n_pages () >= event.keyval - 49:
                        child.set_current_page (event.keyval - 49)
                        return 1
            
            if event.keyval in self.control_shortcuts:
                self.control_shortcuts [event.keyval] (self)
        elif event.keyval in self.shortcuts:
            self.shortcuts [event.keyval] (self)
            return 1
        else:
            return 0
    
    def __init__ (self):
        self.connect_signals ()
        self.connect_blur_signals ()
        self.connect_colors_red_signals ()
        self.connect_canny_signals ()
    
    def track_window_state (self, window, event):
        self.window_state = event.state
    
    def maximize_window (self):
        if self.window_state is Gdk.WindowState.MAXIMIZED:
            self.window.unmaximize ()
            self.window_state = Gdk.WindowState.FOCUSED
        else:
            self.window.maximize ()
            self.window_state = Gdk.WindowState.MAXIMIZED

    def fullscreen_window (self):
        if self.window_state is Gdk.WindowState.FULLSCREEN:
            self.window.unfullscreen ()
            self.window_state = Gdk.WindowState.FOCUSED
        else:
            self.window.fullscreen ()
            self.window_state = Gdk.WindowState.FULLSCREEN

    def do_capture_from_camera (self, *args):
        self.set_status ("Taking picture, please smile..")
        image = capture_from_camera ()
        self.img.camera_shot = image
        self.img.filename = "self://camerashot"
        self.do_effects ()
    
    shortcuts = {113: Gtk.main_quit,
                 65307: Gtk.main_quit,
                 122: image_zoom_out,
                 45: image_zoom_out,
                 91: image_zoom_out,
                 120: handle_size_change,
                 #92: handle_size_change,
                 96: handle_size_change,
                 99:  image_zoom_100,
                 118: image_zoom_in,
                 61: image_zoom_in,
                 33:  image_zoom_100,
                 93: image_zoom_in,
                 92:  image_zoom_100,
                 64:  image_zoom_2x,
                 35:  image_zoom_3x,
                 36:  image_zoom_4x,
                 109: maximize_window,
                 102: fullscreen_window,
                 112: do_capture_from_camera
                }

    control_shortcuts = {115: save_image,
                         111: open_image
                        }

                        
    def do_effects (self, *args):
        self.update_ui ()
        try:
            self.set_status ("Applying effects ...")
            self.update_ui ()
            time = self.timer.get_time ()
            if self.img.filename == "self://camerashot":
                image = copy.copy (self.img.camera_shot)
            else:
                image = cv2.imread (self.img.filename)
            image = self.blur.do_blur (image)
            image = self.color_red.reduce_colors (image)
            image = self.canny.do_canny (image)
            #self.image.set_from_pixbuf (pixbuf)
            self.img.pixbuf = cv2_image_to_gdk_pixbuf (image)
            self.refresh_image ()
            self.set_status ("Done! Operation took {} seconds".format (self.timer.get_time () - time))
        except cv2.error as e:
            #print e, "s"
            #message_box ("Error applying effects", "Please see console window for details", Gtk.MessageType.WARNING)
            self.set_status ("Error applying effects :(")
        #finally:
            #print "error"

    def connect_colors_red_signals (self):
        self.color_red.switch.connect ("state-set", self.do_effects)
        self.color_red.k.connect ("value-changed", self.do_effects)
        self.color_red.repeat.connect ("value-changed", self.do_effects)
        
    def connect_canny_signals (self):
        self.canny.on.connect ("state-set", self.do_effects)
        self.canny.l2_gradient.connect ("toggled", self.do_effects)
        self.canny.only_contours.connect ("toggled", self.do_effects)
        self.canny.threshold1.connect ("value-changed", self.do_effects)
        self.canny.threshold2.connect ("value-changed", self.do_effects)
        self.canny.aperture.connect ("value-changed", self.do_effects)
        self.canny.contour_thickness.connect ("value-changed", self.do_effects)
        self.canny.color_button.connect ("color-set", self.do_effects)
        self.canny.show_contours_all.connect ("toggled", self.do_effects)
        self.canny.show_contours.connect ("activate", self.do_effects)
    
    def connect_blur_signals (self):
        self.blur.config.box_filter_on.connect ("state-set", self.do_effects)
        self.blur.config.box_filter_kernel_x.connect ("value-changed", self.do_effects)
        self.blur.config.box_filter_kernel_y.connect ("value-changed", self.do_effects)
        #self.blur.config.box_filter_sigma_x 
        #self.blur.config.box_filter_sigma_y 
        self.blur.config.box_filter_normalize.connect ("toggled", self.do_effects)
        
        self.blur.config.normalized_box_filter_on.connect ("state-set", self.do_effects)
        self.blur.config.normalized_box_filter_kernel_x.connect ("value-changed", self.do_effects)
        self.blur.config.normalized_box_filter_kernel_y .connect ("value-changed", self.do_effects)

        self.blur.config.convolution_2d_on.connect ("state-set", self.do_effects)
        self.blur.config.convolution_2d_kernel_x .connect ("value-changed", self.do_effects)
        self.blur.config.convolution_2d_kernel_y .connect ("value-changed", self.do_effects)
        
        self.blur.config.gaussian_blur_on.connect ("state-set", self.do_effects)
        self.blur.config.gaussian_blur_kernel_x .connect ("value-changed", self.do_effects)
        self.blur.config.gaussian_blur_kernel_y .connect ("value-changed", self.do_effects)
        self.blur.config.gaussian_blur_sigma_x .connect ("value-changed", self.do_effects)
        self.blur.config.gaussian_blur_sigma_y .connect ("value-changed", self.do_effects)
        
        self.blur.config.median_blur_on.connect ("state-set", self.do_effects)
        self.blur.config.median_blur_kernel .connect ("value-changed", self.do_effects)

        self.blur.config.bilateral_filter_on.connect ("state-set", self.do_effects)
        self.blur.config.bilateral_filter_diameter .connect ("value-changed", self.do_effects)
        self.blur.config.bilateral_filter_sigma_color .connect ("value-changed", self.do_effects)
        self.blur.config.bilateral_filter_sigma_space .connect ("value-changed", self.do_effects)
        
        self.blur.config.adaptive_bilateral_filter_on.connect ("state-set", self.do_effects)
        self.blur.config.adaptive_bilateral_filter_kernel_x .connect ("value-changed", self.do_effects)
        self.blur.config.adaptive_bilateral_filter_kernel_y .connect ("value-changed", self.do_effects)
        self.blur.config.adaptive_bilateral_filter_sigma_space .connect ("value-changed", self.do_effects)
        self.blur.config.adaptive_bilateral_filter_max_sigma_color .connect ("value-changed", self.do_effects)

def main (args):
    print "Welcome! Using opencv ", cv2.__version__
    ui = UI ()
    if len (args) > 1:
        ui.load_image (args [1])
    
    ui.set_status ("Welcome! Loaded program in {} seconds!".format (ui.timer.get_time () - ui.timer.epoch))
    Gtk.main ()

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
