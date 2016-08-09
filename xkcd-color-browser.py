#!/usr/bin/env python3
#  Shaji Khan  [djshaji@gmail.com]
#  2016-08-09
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


from gi.repository import Gtk, Gdk, GdkPixbuf, GObject, GLib, Pango
import json, sys

class XKCDBrowser (Gtk.Window):
    icon_theme = Gtk.IconTheme.get_default ()

    ICON_SIZE = 128
    
    shortcuts = {
        Gdk.KEY_F10: lambda self: self.unmaximize () if self.is_maximized () else self.maximize (),
        Gdk.KEY_F5: lambda self: self.reload (),
        Gdk.KEY_Delete: lambda self: self.delete (),
        Gdk.KEY_Escape: lambda self: self.destroy ()
    }

    def new_pixbuf (self, size):
        # real ugly way to get an empty pixbuf
        return self.icon_theme.load_icon (self.icon_theme.get_example_icon_name (), size, Gtk.IconLookupFlags.FORCE_SIZE)

    def generate_icon (self, color, size = -1):
        if size == -1:
            size = self.ICON_SIZE
        
        pixbuf = self.new_pixbuf (size)
        pixbuf.fill (int (color [1:] + 'ff', base = 16))
        return pixbuf.copy ()

    def fill_store_thread (self, mythread, thread_number):
        list_ = mythread.args ['list']
        len_ = len (list_)
        store = []
        
        for x in range (thread_number * int (len_ / mythread.threads),
                        (thread_number + 1) * int (len_ / mythread.threads)):
            store.append ([self.generate_icon (list_ [x][1]).copy (), list_ [x][0]])

        mythread.queues [thread_number].put (store)

    def item_activated (ui, self, path):
        it = self.ui.store.get_iter (path)
        name = self.ui.store.get (it, 1) [0]

        p = Gtk.Popover.new (ui.toolbar)
        image = Gtk.Image ()
        image.set_from_pixbuf (ui.generate_icon (ui.xkcd_names [name], size = 400))
        box = Gtk.VBox ()
        box.pack_start (image, 1, 1, 0)
        label = Gtk.Label (name + '\n' + ui.xkcd_names [name])
        label.set_justify (2)
        box.pack_start (label, 0, 0, 0)
        p.add (box)
        p.show_all ()


    def fill_store (self):
        for name in self.xkcd_names:
            pixbuf = self.generate_icon (self.xkcd_names [name])
            self.store.append ([pixbuf, name])
    
    def hotkeys (self, window, event):
        if event.keyval in self.shortcuts:
            self.shortcuts [event.keyval] (self)
            return True

        
    def build_ui (self):
        #self.header = Gtk.HeaderBar ()
        self.set_title ('XKCD Color Survey Browser')
        #self.header.set_subtitle ('xkcd.com/color/rgb')
        #self.header.set_show_close_button (True)
        #self.set_titlebar (self.header)
        #self.set_decorated (False)
        self.iconview = Gtk.IconView ()
        self.iconview.ui = self
        self.iconview.sw = Gtk.ScrolledWindow ()
        self.iconview.sw.add (self.iconview)
        
        self.master = Gtk.HBox ()
        self.add (self.master)
        
        self.toolbar = Gtk.Toolbar ()
        self.box = Gtk.VBox ()
        
        self.master.pack_start (self.box, 1, 1, 0)
        #self.box.pack_start (self.header, 0, 0, 0)
        self.box.pack_start (self.iconview.sw, 1, 1, 0)
        self.box.pack_end (self.toolbar, 0, 1, 0)
              
        self.store = Gtk.ListStore (GdkPixbuf.Pixbuf, str)
        self.store.set_sort_column_id (1, 0)
        self.fill_store ()
        
        self.iconview.connect ('item-activated', self.item_activated)
        
        self.iconview.set_model (self.store)
        self.iconview.set_item_width (96)
        
        self.iconview.set_pixbuf_column (0)
        self.iconview.set_text_column (1)
        
        self.connect ('key-press-event', self.hotkeys)
        self.connect ('destroy', self.main_quit)
        
        self.iconview.grab_focus ()
        
        pango_font = Pango.FontDescription.from_string ("Ubuntu 27")
        self.modify_font (pango_font)
        
        self.set_size_request (800, 500)
        self.show_all ()
    
    def main (self):
        try:
            self.mainloop.run ()
        except KeyboardInterrupt:
            print ("Keyboard Interrupt")
            self.main_quit ()
    
    def __init__ (self, filename = None):
        try:
            if filename is None:
                self.xkcd_names = json.loads (open ('xkcd-colors.json').read ())
            else:
                self.xkcd_names = json.loads (open (filename).read ())
        except FileNotFoundError:
            message = 'Download xkcd colors json file from <b>here</b>:\n\nhttp://<b>github.com/charlesreid1/xkcd-colors</b>/\nblob/master/xkcd-colors.json\n\nor http://<b><span size=\'x-large\'>xkcd.com</span></b>/color/rgb for more info\n\nusage:\n<b>{}</b> <i>xkcd_colors_json_file</i>'.format (sys.argv [0])
            #print (message)
            dialog = Gtk.MessageDialog (buttons = Gtk.ButtonsType.OK, message_format = message)
            dialog.set_markup (message)
            dialog.run ()
            dialog.destroy ()
            sys.exit ()
            
        Gtk.Window.__init__ (self)
        self.mainloop = GLib.MainLoop()
        self.build_ui ()
    
    def main_quit (self, *args):
        self.mainloop.quit ()

def xkcd_browser (filename = None):
    b = XKCDBrowser (filename)
    b.main ()

if __name__ == '__main__':
    if len (sys.argv) > 1:
        xkcd_browser (sys.argv [1])
    else:
        xkcd_browser ()
