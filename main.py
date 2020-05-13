#!/usr/bin/env python3

import sqlite3

from kivy.app import App
from kivy.properties import ListProperty
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition, FadeTransition
from kivymd.date_picker import MDDatePicker

from kivymd.theming import ThemeManager
from kivymd.label import MDLabel
from kivymd.button import MDRaisedButton
from kivymd.selectioncontrols import MDCheckbox
from kivymd.time_picker import MDTimePicker

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



class YalbApp(App):
    title = "Yet Another LogBook"
    theme_cls = ThemeManager()

    def build(self):
        table = TV(
            size=(Window.size[0], 1),
            pos_hint={'x': 0.0, 'y': 0.0},
        )
        table.populate("log.db")
        #print(str(table))
        self.root.ids.sm.transition = NoTransition()
        self.root.ids.scr_second.add_widget(table)



        def _on_rotate(obj, *args):
            #print(*args)
            self.on_rotate(*args)
        Window.bind(on_rotate=_on_rotate)
        Window.bind(on_resize=_on_rotate)


        #scr2.add_widget(RV())
        print("Vsykuyu hernyu delat tut")

    def on_rotate(self, angle, *args):
        table = self.root.ids.scr_second.children[0].children[0]
        table.layout.width = max(Window.size[0], Window.size[1])

    def on_refresh(self):
        self.on_rotate(0)

    def get_time_picker_data(self, instance, time):
        self.root.ids.time_picker_label.text = str(time)
        self.previous_time = time

    def show_example_time_picker(self):
        self.time_dialog = MDTimePicker()
        self.time_dialog.bind(time=self.get_time_picker_data)
        if self.root.ids.time_picker_use_previous_time.active:
            try:
                self.time_dialog.set_time(self.previous_time)
            except AttributeError:
                pass
        self.time_dialog.open()

    def set_previous_date(self, date_obj):
        self.previous_date = date_obj
        self.root.ids.date_picker_label.text = str(date_obj)

    def show_example_date_picker(self):
        if self.root.ids.date_picker_use_previous_date.active:
            pd = self.previous_date
            try:
                MDDatePicker(self.set_previous_date,
                             pd.year, pd.month, pd.day).open()
            except AttributeError:
                MDDatePicker(self.set_previous_date).open()
        else:
            MDDatePicker(self.set_previous_date).open()

    def scr_edit(self):
        sm = self.root.ids.sm
        sm.switch_to(self.root.ids.scr_edit)

    def screen_prev(self):
        sm = self.root.ids.sm
        sm.switch_to(self.root.ids.scr_main, direction="right")
        self.root.ids.ap.title = sm.current_screen.name

    def screen_next(self):
        sm = self.root.ids.sm
        sm.switch_to(self.root.ids.scr_second, direction="left")
        self.root.ids.ap.title = sm.current_screen.name


if __name__ == "__main__":
    YalbApp().run()
