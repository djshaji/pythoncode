# pythoncode
My python code (currently mostly gtk3 / opencv)

---------------------------------
XKCD Color Browser
---------------------------------
Color Browser for xkcd color survey. You can see
a sample of ~200 named colors from the survey 
conducted by Randall.

See xkcd.com/color/rgb for details.

You need a json file with the color descriptions.
Get it from here:
https://github.com/charlesreid1/xkcd-colors/blob/master/xkcd-colors.json

---------------------------------
* opencv-blur-canny-console.py *
---------------------------------

What is it?
A simple frontend for opencv blur and canny edge detection. It can open images from the command line, through a file browser, and can even take snapshots from a webcam (!)

Requirements:
 - python 2.7
 - opencv 2.4 python bindings
 - gtk3 python bindings
 - Mountain Dew™

* Important Note: Mountain Dew is for drinking purposes only. Do not use on electronic equipment!

* Important Note 2: If you break something, don't sue me! See License!
This is my first major contribution to the Open CV project. Actually it's not really a contribution yet, although I will try my best to get this concept and code incorporated into the project. It would be a big achievement (!) for me. Still, the code is open source (GPL 3 or later) and everyone is free to use it.

-------------
* Colormaps *
-------------

To begin with, the purpose here is to extract shape and object information from an image. A colormap essentially falls somewhere between a contour and a "shape." The hierarchy is built like this:

-----------        ------------         -----------------
| Contour |   ->   | Colormap |   ->    | Color Cluster |
-----------        ------------         -----------------

A colormap consists of a single (semi) closed regin, along with its contour and color information (mean) (b,g,r).  A Color Cluster contains many colormaps, which are grouped together by proximity and similarity of color information.

The public (!) API is simple to use. a high level function is provided, which takes an image and contours as argument, and returns a list of color clusters. For each colormap in the cluster, the get_mat () method builds an intelligent reproduction of the original shape.

Basic classes:

class ColorCluster:
    colormaps = [list of colormaps]
    mean = (b ,g ,r)
    
    def generate_mat ()
    
    def populate (self, colormap)
    # you have to call this function after first creating a color cluster object with a valid colormap.
    
    def append (self, colormap)
    # adding a colormap to the cluster
    
    def match_color (self, color)
    # matching color
    
    def match_geometry (self, contour)
    # yep


class ColorMap:
    area = [[x,y]] # list of coordinates inside contour
    contour = contour passed during intialization
    mean = (b, g, r)
    mat = passed during intialization

    color_range = 50 # 0 ~ 255
    proximity_range = 50 # pixels

    def populate (self, area = None, contour = None, mean = None, mat = None)
    # to be called after object creation with relevant arguments
    
    def match_color (self, color)
    def match_geometry (self, contour)

In most cases, the high level function contour_to_color_cluster () will be convenient.
