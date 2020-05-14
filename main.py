#!/usr/bin/env python3

import sqlite3
import datetime

from kivy.properties import ListProperty
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition, FadeTransition
from kivy.properties import ObjectProperty
from kivy.uix.splitter import Splitter

from kivymd.app import MDApp
#from kivymd.theming import ThemeManager
from kivymd.uix.picker import MDDatePicker
from kivymd.uix.picker import MDTimePicker
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.selectioncontrol import MDCheckbox

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
        return self


class YalbApp(MDApp):
    title = "Yet Another LogBook"
#    theme_cls = ThemeManager()
    previous_date = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.previous_time = datetime.datetime.utcnow()

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
        self.root.ids[name + "_item_input"].text = str(time)
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
    YalbApp().run()
