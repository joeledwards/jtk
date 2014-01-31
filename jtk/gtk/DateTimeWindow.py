import time

import pygtk
pygtk.require('2.0')
import gtk
import gobject

class DateTimeWindow:
    def __init__(self):
        self.completion_callback = None
        self.completion_data = None
        self.cancel_callback = None
        self.cancel_data = None
        self.time_high = True
        self.granularity = "day"
        self.granules  = { 'day'    : 4 ,
                           'hour'   : 3 ,
                           'minute' : 2 ,
                           'second' : 1 } 
        times = time.gmtime()
        self.timestamp = { 'year'   : times[0] ,
                           'month'  : times[1] ,
                           'day'    : times[2] ,
                           'hour'   : times[3] ,
                           'minute' : times[4] ,
                           'second' : times[5] }
        self.pushing = False
        self.running = False

    def create_window(self):
        if self.running:
            return
        self.running = True
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.vbox_date_time = gtk.VBox()
        self.hbox_time = gtk.HBox()
        self.vbox_hour = gtk.VBox()
        self.vbox_minute = gtk.VBox()
        self.vbox_second = gtk.VBox()
        self.hbox_control = gtk.HBox()

        self.label_hour   = gtk.Label("Hour")
        self.label_minute = gtk.Label("Minute")
        self.label_second = gtk.Label("Second")
        self.spinbutton_hour   = gtk.SpinButton()
        self.spinbutton_minute = gtk.SpinButton()
        self.spinbutton_second = gtk.SpinButton()
        self.button_today  = gtk.Button(label="Today",  stock=None, use_underline=True)
        self.button_ok     = gtk.Button(label="OK",     stock=None, use_underline=True)
        self.button_cancel = gtk.Button(label="Cancel", stock=None, use_underline=True)

        self.calendar = gtk.Calendar()

        self.window.add( self.vbox_date_time )
        self.vbox_date_time.add( self.calendar )
        self.vbox_date_time.add( self.hbox_time )
        self.vbox_date_time.add( self.hbox_control )
        self.hbox_time.add( self.vbox_hour )
        self.hbox_time.add( self.vbox_minute )
        self.hbox_time.add( self.vbox_second )

        self.vbox_hour.add( self.label_hour )
        self.vbox_hour.add( self.spinbutton_hour )
        self.vbox_minute.add( self.label_minute )
        self.vbox_minute.add( self.spinbutton_minute )
        self.vbox_second.add( self.label_second )
        self.vbox_second.add( self.spinbutton_second )
        self.hbox_control.pack_start( self.button_today,  True, True, 0 )
        self.hbox_control.pack_start( self.button_ok,     True, True, 0 )
        self.hbox_control.pack_end(   self.button_cancel, True, True, 0 )

        self.spinbutton_hour.set_range(0,23)
        self.spinbutton_minute.set_range(0,59)
        self.spinbutton_second.set_range(0,59)

        self.spinbutton_hour.set_increments(1,5)
        self.spinbutton_minute.set_increments(1,5)
        self.spinbutton_second.set_increments(1,5)

        # Setup our signals
        self.window.connect( "destroy_event", self.callback_complete, None )
        self.window.connect( "delete_event", self.callback_complete, None )

        self.calendar.connect( "day-selected", self.callback_update_time, None )
        self.calendar.connect( "day-selected-double-click", self.callback_update_time, None )
        self.calendar.connect( "month-changed", self.callback_update_time, None )
        self.calendar.connect( "next-month", self.callback_update_time, None )
        self.calendar.connect( "prev-month", self.callback_update_time, None )
        self.calendar.connect( "next-year", self.callback_update_time, None )
        self.calendar.connect( "prev-year", self.callback_update_time, None )
        self.spinbutton_hour.connect( "value-changed", self.callback_update_time, None )
        self.spinbutton_minute.connect( "value-changed", self.callback_update_time, None )
        self.spinbutton_second.connect( "value-changed", self.callback_update_time, None )
        self.button_today.connect(  "clicked", self.callback_today,    None )
        self.button_ok.connect(     "clicked", self.callback_complete, None )
        self.button_cancel.connect( "clicked", self.callback_cancel,   None )

        # Show our contents
        self.window.show_all()
        self.push_time()

    def set_granularity(self, granule):
        if self.granules.has_key(granule):
            self.granularity = granule

    def get_granularity(self):
        return self.granularity

    def get_granule(self, granule):
        if self.granules.has_key(granule):
            return self.granules[granule]
        return 0

    def current_granule(self):
        if self.granules.has_key(self.granularity):
            return self.granules[self.granularity]
        return 0

    def set_default_high(self, high=True):
        self.time_high = high

    def get_default_high(self):
        return self.time_high
        
    def delete_window(self):
        if not self.running:
            return
        self.window.hide_all()
        del self.window
        self.window = None
        self.running = False

    def callback_update_time(self, widget, event, data=None):
        if not self.calendar or self.pushing:
            return
        (year, month, day) = self.calendar.get_date()
        self.timestamp['year']   = year
        self.timestamp['month']  = month + 1
        self.timestamp['day']    = day
        if self.current_granule() <= self.get_granule('hour'):
            self.timestamp['hour'] = int(self.spinbutton_hour.get_value())
        elif self.time_high:
            self.timestamp['hour'] = 23
        else:
            self.timestamp['hour'] = 0

        if self.current_granule() <= self.get_granule('minute'):
            self.timestamp['minute'] = int(self.spinbutton_minute.get_value())
        elif self.time_high:
            self.timestamp['minute'] = 59
        else:
            self.timestamp['minute'] = 0

        if self.current_granule() <= self.get_granule('second'):
            self.timestamp['second'] = int(self.spinbutton_second.get_value())
        elif self.time_high:
            self.timestamp['second'] = 59
        else:
            self.timestamp['second'] = 0

    def callback_today(self, widget=None, event=None, data=None):
        times = time.gmtime()
        self.timestamp = { 'year'   : times[0] ,
                           'month'  : times[1] ,
                           'day'    : times[2] ,
                           'hour'   : times[3] ,
                           'minute' : times[4] ,
                           'second' : times[5] }
        self.push_time()

    def callback_complete(self, widget=None, event=None, data=None):
        if self.completion_data is None:
            self.completion_callback()
        else:
            self.completion_callback( self.completion_data )
        self.delete_window()

    def set_callback_complete(self, callback, data=None):
        self.completion_callback = callback
        self.completion_data = data

    def callback_cancel(self, widget=None, event=None, data=None):
        if self.cancel_data is None:
            self.cancel_callback()
        else:
            self.cancel_callback( self.completion_data )
        self.delete_window()

    def set_callback_cancel(self, callback, data=None):
        self.cancel_callback = callback
        self.cancel_data = data

    def push_time(self):
        self.pushing = True
        self.calendar.select_month(self.timestamp['month'] - 1, self.timestamp['year'])
        self.calendar.select_day(self.timestamp['day'])
        if self.current_granule() <= self.get_granule('hour'):
            self.spinbutton_hour.set_value(self.timestamp['hour'])
        if self.current_granule() <= self.get_granule('minute'):
            self.spinbutton_minute.set_value(self.timestamp['minute'])
        if self.current_granule() <= self.get_granule('second'):
            self.spinbutton_second.set_value(self.timestamp['second'])
        self.pushing = False

    def prompt(self):
        self.create_window()

    def get_date(self):
        date_str = "%(year)04d/%(month)02d/%(day)02d %(hour)02d:%(minute)02d:%(second)02d UTC" % self.timestamp
        date = time.strptime(date_str,"%Y/%m/%d %H:%M:%S %Z")
        return date

    def set_date(self, date):
        self.timestamp['year']   = date[0]
        self.timestamp['month']  = date[1]
        self.timestamp['day']    = date[2]
        if self.current_granule() <= self.get_granule('hour'):
            self.timestamp['hour']   = date[3]
        elif self.time_high:
            self.timestamp['hour'] = 23
        else:
            self.timestamp['hour'] = 0

        if self.current_granule() <= self.get_granule('minute'):
            self.timestamp['minute'] = date[4]
        elif self.time_high:
            self.timestamp['minute'] = 59
        else:
            self.timestamp['minute'] = 0

        if self.current_granule() <= self.get_granule('second'):
            self.timestamp['second'] = date[5]
        elif self.time_high:
            self.timestamp['second'] = 59
        else:
            self.timestamp['second'] = 0

