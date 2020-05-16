#!/usr/bin/env python3

import sqlite3
import ephem
from datetime import datetime, timedelta
import math

from kivy.properties import ListProperty
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import NoTransition
from kivy.properties import ObjectProperty


from kivymd.app import MDApp
from kivymd.uix.picker import MDDatePicker
from kivymd.uix.picker import MDTimePicker

from table import TableView, TableColumn


class RV(BoxLayout):
    data_items = ListProperty([])

    def __init__(self, **kwargs):
        super(RV, self).__init__(**kwargs)
        self.fill_table()

    def fill_table(self):
        connection = sqlite3.connect("log.db")
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM log ORDER BY ID DESC")
        rows = cursor.fetchall()

        # create data_items
        for row in rows:
            print(row)
            for col in (*row, ''):
                self.data_items.append(col)
        cursor.close()
        if connection:
            connection.close()

class TV(TableView):
    def __init__(self, **kwargs):
        super(TV, self).__init__(**kwargs)

    def populate(self, filename):
        connection = sqlite3.connect(filename)
        cursor = connection.cursor()

        # columns
        cursor.execute("PRAGMA table_info('log')")
        cols = cursor.fetchall()
        headers = [str(v[1]) for v in cols]
        #print(headers)
        size_hints = {
            0: (3, None),
            1: (7, None),
            2: (7, None),
            3: (6, None),
            4: (6, None),
            5: (6, None),
            6: (4, None),
            7: (4, None),
            8: (4, None),
            9: (4, None),
            10: (4, None),
            11: (4, None),
            12: (4, None),
        }
        for i, col in enumerate(headers):
            sh = (1, 1)
            if i in size_hints:
                sh = size_hints[i]
            self.add_column(TableColumn(str(i), key=str(col), hint_text=str(i)), size_hint=sh)
        limit = 50
        cursor.execute("SELECT * FROM log ORDER BY ID DESC LIMIT %d" % limit)
        rows = cursor.fetchall()
        for row in rows:
            row_dict = dict(zip(headers, row))
            #print(row_dict)
            self.add_row(row_dict)
        cursor.close()
        if connection:
            connection.close()
        return self


class YalbApp(MDApp):
    title = "Yet Another LogBook"
#    theme_cls = ThemeManager()
    previous_date = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.time_dialog = MDTimePicker()
        self.previous_time = datetime.utcnow()

    def build(self):
        table = TV(
            size=(Window.size[0], Window.size[1]),
            pos_hint={'x': 0.0, 'y': 0.0},
            do_scroll_x=True,
        )
        table.populate("log.db")
        #print(str(table))
        self.root.ids.sm.transition = NoTransition()
        self.root.ids.scr_second_box.add_widget(table)

        def _on_rotate(obj, *args):
            #print(*args)
            self.on_rotate(*args)
        Window.bind(on_rotate=_on_rotate)
        Window.bind(on_resize=_on_rotate)


        #scr2.add_widget(RV())
        print("Vsykuyu hernyu delat tut")

    def calculate_night_time(self, coords_departure, coords_arrival, takeoff, landing):
        if landing < takeoff:
            landing += timedelta(days=1)

        departure_ap = ephem.Observer()
        departure_ap.lat = math.radians(coords_departure[0])
        departure_ap.lon = math.radians(coords_departure[1])
        arrival_ap = ephem.Observer()
        arrival_ap.lat = math.radians(coords_arrival[0])
        arrival_ap.lon = math.radians(coords_arrival[1])
        departure_ap.date = takeoff
        arrival_ap.date = takeoff + timedelta(days=(departure_ap.lon - arrival_ap.lon) / math.pi / 12.0)

        s = ephem.Sun()
        plane = ephem.Observer()
        plane.date = takeoff
        flight_time_minutes = int((landing - takeoff).total_seconds() // 60)
        print("ldgt-to in minutes:", flight_time_minutes, "HH:MM :", timedelta(hours=flight_time_minutes / 60.0))
        dlat = (arrival_ap.lat - departure_ap.lat) / flight_time_minutes
        dlon = (arrival_ap.lon - departure_ap.lon) / flight_time_minutes
        dt = timedelta(seconds=60)
        nt = 0
        for i in range(flight_time_minutes):
            plane.date = takeoff + dt * float(i + 0.5)
            plane.lat = departure_ap.lat + dlat * float(i)
            plane.lon = departure_ap.lon + dlon * float(i)
            try:
                if plane.next_rising(s) < plane.next_setting(s):
                    nt += 1
            except ephem.NeverUpError:
                nt += 1
            except ephem.AlwaysUpError:
                pass
        nt = timedelta(hours=nt / 60.0)
        return nt

    def new_leg(self):
        date = self.root.ids.date_picker_input.text
        flightno = self.root.ids.flight_no_item_input.text
        acno = self.root.ids.aircraft_id_item_input.text
        fromap = self.root.ids.from_item_input.text
        toap = self.root.ids.to_item_input.text
        ofbt = self.root.ids.offblock_item_input.text
        tot = self.root.ids.takeoff_item_input.text
        lt = self.root.ids.landing_item_input.text
        onbt = self.root.ids.onblock_item_input.text

        offblocktime = datetime.strptime(date + " " + ofbt, "%Y-%m-%d %H:%M")
        onblocktime = datetime.strptime(date + " " + onbt, "%Y-%m-%d %H:%M")
        takeofftime = datetime.strptime(date + " " + tot, "%Y-%m-%d %H:%M")
        landingtime = datetime.strptime(date + " " + lt, "%Y-%m-%d %H:%M")

        if offblocktime > onblocktime:  # Check next day
            onblocktime += timedelta(days=1)
        blktime = onblocktime - offblocktime

        if landingtime < takeofftime:  # Check next day
            landingtime += timedelta(days=1)
        flttime = landingtime - takeofftime

        #coords_departure = self.get_ap_coords(fromap)
        coords_departure = (51.8779638888889, -176.646030555556)
        #coords_arrival = self.get_ap_coords(toap)
        coords_arrival = (44.814998626709, 136.292007446289)
        takeoff = takeofftime
        landing = landingtime
        night_time = self.calculate_night_time(coords_departure, coords_arrival, takeoff, landing)

        connection = sqlite3.connect("log.db")
        cursor = connection.cursor()
        sql = "INSERT INTO log ('Date', 'FlightNumber', 'Aircraft', 'AirportDeparture', 'AirportArrival', 'OffBlock', 'TakeOff', 'Landing', 'OnBlock', 'FlightTime', 'BlockTime', 'NightTime')" \
              " VALUES (?,?,?,?,?,?,?,?,?,?,?,?)"
        data = (date, flightno, acno, fromap, toap, ofbt, tot, lt, onbt, str(flttime)[:-3], str(blktime)[:-3], str(night_time)[:-3])
        cursor.execute(sql, data)
        connection.commit()
        cursor.close()
        if connection:
            connection.close()

        print(blktime, flttime, night_time)
        print(date, flightno, acno, fromap, toap, ofbt, tot, lt, onbt)

    def get_id(self, instance):
        for id, widget in self.root.ids.items():
            if widget.__self__ == instance:
                return id

    def on_rotate(self, angle, *args):
        table = self.root.ids.scr_second.children[0].children[0]
        table.layout.width = max(Window.size[0], Window.size[1])

    def on_refresh(self):
        self.on_rotate(0)

    def get_time_picker_data(self, instance, time):
        name = self.get_id(instance)
        if not name:
            return
        self.root.ids[name + "_item_input"].text = str(time)[:-3]
        self.previous_time = time

    def show_time_picker(self, instance):
        self.time_dialog = MDTimePicker()
        self.time_dialog.bind(time=lambda x, time: self.get_time_picker_data(instance, time))
        try:
            self.time_dialog.set_time(self.previous_time)
        except AttributeError:
            pass
        self.time_dialog.open()

    def set_previous_date(self, date_obj):
        self.previous_date = date_obj
        self.root.ids.date_picker_input.text = str(date_obj)

    def show_date_picker(self):
        pd = self.previous_date
        try:
            MDDatePicker(self.set_previous_date,
                         pd.year, pd.month, pd.day).open()
        except AttributeError:
            MDDatePicker(self.set_previous_date).open()

    def screen_main(self):
        sm = self.root.ids.sm
        sm.switch_to(self.root.ids.scr_main)

    def scr_edit(self):
        sm = self.root.ids.sm
        sm.switch_to(self.root.ids.scr_edit)

    def screen_second(self):
        sm = self.root.ids.sm
        sm.switch_to(self.root.ids.scr_second)
        self.root.ids.ap.title = sm.current_screen.name

    def screen_debug(self):
        sm = self.root.ids.sm
        sm.switch_to(self.root.ids.scr_debug)
        self.root.ids.ap.title = sm.current_screen.name


if __name__ == "__main__":
    trace = None
    try:
        YalbApp().run()
    except:
        import sys, traceback
        trace = "".join(traceback.format_exception(*sys.exc_info()))
        print(trace)
