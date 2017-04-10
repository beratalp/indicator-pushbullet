#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# preferences_dialog.py
#
# This file is part of PushBullet-Indicator
#
# Copyright (C) 2014
# Lorenzo Carbonell Cerezo <lorenzo.carbonell.cerezo@gmail.com>
# Copyright (C) 2017 Alp Erbil
# beratalp@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GdkPixbuf
import comun
from comun import _

class AnswerDialog(Gtk.Dialog):
	def __init__(self, package_name=None,icon=None, title='', message = ''):
		#
		Gtk.Dialog.__init__(self, 'PushBullet Indicator | '+ title, None,Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,(Gtk.STOCK_CANCEL, Gtk.ResponseType.REJECT,Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT))
		self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
		self.connect('close', self.close_application)		
		self.set_icon_from_file(comun.ICON)
		#
		vbox0 = Gtk.VBox(spacing = 5)
		vbox0.set_border_width(5)
		self.get_content_area().add(vbox0)
		frame1 = Gtk.Frame()
		frame1.set_size_request(500,300)
		vbox0.pack_start(frame1,False,False,1)
		table1 = Gtk.Table(3, 2, False)
		frame1.add(table1)
		#
		image0 = Gtk.Image()
		if package_name is None or package_name == 'com.pushbullet.android':
			pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(comun.MESSENGER_ICON,48,48)
		elif package_name == 'org.telegram.messenger':
			pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(comun.TELEGRAM_ICON,48,48)
		elif package_name == 'com.whatsapp':
			pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(comun.WHATSAPP_ICON,48,48)
		elif package_name == 'com.google.android.talk':
			pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(comun.HANGOUT_ICON,48,48)
		elif package_name == 'com.facebook.orca':
			pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(comun.FACEBOOK_ICON,48,48)
		elif package_name == 'jp.naver.line.android':
			pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(comun.LINE_ICON,48,48)
		image0.set_from_pixbuf(pixbuf)
		table1.attach(image0,0,2,0,1, xoptions=Gtk.AttachOptions.SHRINK, xpadding=5, ypadding=5)
		#
		image1 = Gtk.Image()
		if icon is None:
			pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(comun.ICON,48,48)
		else:
			pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(icon,48,48)
		image1.set_from_pixbuf(pixbuf)
		table1.attach(image1,0,1,1,2, xoptions=Gtk.AttachOptions.SHRINK, xpadding=5, ypadding=5)
		#
		scrolledwindow1 = Gtk.ScrolledWindow()
		scrolledwindow1.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
		table1.attach(scrolledwindow1,1,2,1,2, xpadding=5, ypadding=5)
		label1 = Gtk.TextView()
		label1.set_wrap_mode(wrap_mode=Gtk.WrapMode.WORD)
		label1.set_editable(False)
		label1.get_buffer().set_text(message)
		scrolledwindow1.add(label1)
		#
		label2 = Gtk.Label(_('Answer')+':')
		label2.set_alignment(0, 0.5)
		table1.attach(label2,0,1,2,3, xoptions=Gtk.AttachOptions.SHRINK, xpadding=5, ypadding=5)
		#
		scrolledwindow2 = Gtk.ScrolledWindow()
		scrolledwindow2.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
		table1.attach(scrolledwindow2,1,2,2,3, xpadding=5, ypadding=5)
		self.entry1 = Gtk.TextView()
		self.entry1 .set_wrap_mode(wrap_mode=Gtk.WrapMode.WORD)
		self.entry1.connect('key-release-event', self.on_key_released_event)
		scrolledwindow2.add(self.entry1)
		#
		self.set_focus(self.entry1)
		self.show_all()
		
		
	def on_key_released_event(self, widget, event):
		if event.keyval == 65421 or event.keyval == 65293:
			self.response(Gtk.ResponseType.ACCEPT)

	def close_application(self, event):
		self.hide()
	
	def get_answer(self):
		start_iter,end_iter = self.entry1.get_buffer().get_bounds()
		text = self.entry1.get_buffer().get_text(
				start_iter,
				end_iter, True)		
		return text
		

if __name__ == "__main__":
	cm = AnswerDialog()
	if 	cm.run() == Gtk.ResponseType.ACCEPT:
		cm.hide()
		print(cm.get_answer())	
	cm.destroy()
	exit(0)
