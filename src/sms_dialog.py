#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# preferences_dialog.py
#
# This file is part of PushBullet-Indicator
#
# Copyright (C) 2014
# Lorenzo Carbonell Cerezo <lorenzo.carbonell.cerezo@gmail.com>
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
import os
import sys
import comun
from comun import _
sys.path.insert(1,'/opt/extras.ubuntu.com/pushbullet-commons/share/pushbullet-commons')
import commons_comun
	
class SendSMSDialog(Gtk.Dialog):
	def __init__(self,devices = []):
		#
		Gtk.Dialog.__init__(self, _('Send a SMS'),None,Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,(Gtk.STOCK_CANCEL, Gtk.ResponseType.REJECT,Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT))
		self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
		self.connect('close', self.close_application)
		self.set_icon_from_file(commons_comun.ICON)
		#
		vbox0 = Gtk.VBox(spacing = 5)
		vbox0.set_border_width(5)
		#vbox0.set_size_request(400, 80)
		self.get_content_area().add(vbox0)
		#***************************************************************
		table_to = Gtk.Table(4, 2, False)
		vbox0.pack_start(table_to,False,False,0)
		#
		label_from = Gtk.Label(_('Select mobile')+':')
		label_from.set_alignment(0, 0.5)
		table_to.attach(label_from,0,1,0,1, xpadding=5, ypadding=5)			
		name_store = Gtk.ListStore(str,str)
		for adevice in devices:			
			name_store.append([adevice['label'],adevice['device_iden']])
		self.smsFrom = Gtk.ComboBox.new_with_model(name_store)		
		renderertext = Gtk.CellRendererText()
		renderertext.props.mode = Gtk.CellRendererMode.ACTIVATABLE
		self.smsFrom.pack_start(renderertext, False)
		self.smsFrom.add_attribute(renderertext, "text", 0)				
		self.smsFrom.set_active(0)
		table_to.attach(self.smsFrom,1,2,0,1, xpadding=5, ypadding=5)
		#
		label_to = Gtk.Label(_('Send a SMS to')+':')
		label_to.set_alignment(0, 0.5)
		table_to.attach(label_to,0,1,1,2, xpadding=5, ypadding=5)			
		self.smsTo = Gtk.Entry()
		table_to.attach(self.smsTo,1,2,1,2, xpadding=5, ypadding=5)
		#
		label_message = Gtk.Label(_('Message')+':')
		label_message.set_alignment(0, 0.5)
		table_to.attach(label_message,0,1,2,3, xpadding=5, ypadding=5)			
		
		# Scrolled Window 1 (for markdown)
		scrolledwindow1 = Gtk.ScrolledWindow()
		scrolledwindow1.set_hexpand(False)
		scrolledwindow1.set_vexpand(True)
		scrolledwindow1.set_size_request(400, 80)
		scrolledwindow1.set_property("shadow-type", Gtk.ShadowType.IN)
		table_to.attach(scrolledwindow1,0,2,3,4, xpadding=5, ypadding=5)
		
		# Markdown Editor
		self.writer = Gtk.TextView.new()
		self.writer.set_left_margin(5)
		self.writer.set_right_margin(5)
		self.writer.set_wrap_mode(Gtk.WrapMode.WORD)
		scrolledwindow1.add(self.writer)
		self.show_all()

	def get_buffer_text(self):
		try:
			start_iter,end_iter = self.writer.get_buffer().get_bounds()
			text = self.writer.get_buffer().get_text(
				start_iter,
				end_iter, True)
			return text
		except Exception:
			print('--------------------------')
			print('Errrorrrr')
			print('--------------------------')
			pass
		return None		

	def get_selected_in_combo(self):
		tree_iter = self.smsFrom.get_active_iter()
		if tree_iter != None:
			model = self.smsFrom.get_model()
			label, iden = model[tree_iter]
			return iden	
		return None
	
	def get_response(self):
		number = self.smsTo.get_text()
		if len(number) == 0:
			number = None
			message = None
			device_iden = None
		else:
			message = self.get_buffer_text()
			if message is None or len(message) == 0:
				number = None
				message = None
				device_iden = None
			else:
				device_iden = self.get_selected_in_combo()
				if device_iden is None:
					number = None
					message = None					
		return {'device_iden': device_iden, 'number':number,'message':message}
		
	def close_application(self, widget):
		self.hide()
if __name__ == "__main__":
	cm = SendSMSDialog()
	if 	cm.run() == Gtk.ResponseType.ACCEPT:
			cm.hide()
			print(cm.get_response())
	cm.destroy()
	exit(0)
