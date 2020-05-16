#!/usr/bin/env python3

from kivy.metrics import pt
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.codeinput import CodeInput
from kivy.uix.popup import Popup


class BugReportPopup(Popup):
	def __init__(self, title, text, posturl=None, **kwargs):
		super().__init__(title=title, **kwargs)
		self.text = text
		self.posturl = posturl
		layout = BoxLayout(orientation="vertical")
		btns = BoxLayout(size_hint_y=None, height=pt(20))
		ci = CodeInput(text=text, disabled=True)
		btnReport = Button(text="Send Report")
		btnCancel = Button(text="Cancel")
		btnReport.bind(on_release=self.on_report)
		btnCancel.bind(on_release=self.on_cancel)
		btnReport.disabled = False if self.posturl else True
		btns.add_widget(btnReport)
		btns.add_widget(btnCancel)
		layout.add_widget(ci)
		layout.add_widget(btns)
		self.content = layout

	def on_cancel(self, instance):
		self.dismiss()
		# TODO: test running us ways other than runTouchApp()
		self.parent.close()

	def on_report(self, instance):
		if not self.posturl:
			return
		n = len(self.text)
		print(f"{self.__class__}: sending report ({n} bytes) to: {self.posturl}")
		# TODO: send it somehwere...


if __name__ == "__main__":
	from kivy.base import runTouchApp
	app = BugReportPopup(title="TEST", text="everything is working...", posturl="http://localhost/bugreport")
	runTouchApp(app)
