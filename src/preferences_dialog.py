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
import comun
import dbus
from dbus.mainloop.glib import DBusGMainLoop
import os
import sys
import shutil
import webbrowser
from comun import _

sys.path.insert(1,'/opt/extras.ubuntu.com/pushbullet-commons/share/pushbullet-commons')

from logindialog import LoginDialog
from configurator import Configuration
from commons_configurator import Configuration as TokenConfiguration

dbus_loop = DBusGMainLoop(set_as_default=True)
bus = dbus.SessionBus(mainloop=dbus_loop)

def create_or_remove_autostart(create):
	if not os.path.exists(comun.AUTOSTART_DIR):
		os.makedirs(comun.AUTOSTART_DIR)
	if create == True:
		if not os.path.exists(comun.FILE_AUTO_START):
			shutil.copyfile(comun.FILE_AUTO_START_ORIG,comun.FILE_AUTO_START)
	else:
		if os.path.exists(comun.FILE_AUTO_START):
			os.remove(comun.FILE_AUTO_START)


class PreferencesDialog(Gtk.Dialog):
	def __init__(self):
		#
		Gtk.Dialog.__init__(self, 'PushBullet Indicator | '+_('Preferences'),None,Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,(Gtk.STOCK_CANCEL, Gtk.ResponseType.REJECT,Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT))
		self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
		#self.set_size_request(400, 230)
		self.connect('close', self.close_application)
		self.set_icon_from_file(comun.ICON)
		#
		vbox0 = Gtk.VBox(spacing = 5)
		vbox0.set_border_width(5)
		self.get_content_area().add(vbox0)
		#***************************************************************
		self.notebook = Gtk.Notebook.new()
		vbox0.add(self.notebook)
		#***************************************************************
		vbox1 = Gtk.VBox(spacing = 5)
		vbox1.set_border_width(5)
		self.notebook.append_page(vbox1,Gtk.Label.new(_('Main')))
		frame1 = Gtk.Frame()
		vbox1.pack_start(frame1,False,True,1)
		table1 = Gtk.Table(4, 2, False)
		frame1.add(table1)
		#***************************************************************
		label1 = Gtk.Label(_('Allow access to PushBullet'))
		label1.set_alignment(0, 0.5)
		table1.attach(label1,0,1,0,1, xpadding=5, ypadding=5)
		self.switch1 = Gtk.Switch()
		self.switch1.connect('button-release-event',self.on_switch1_changed)
		table1.attach(self.switch1,1,2,0,1, xpadding=5, ypadding=5)
		label2 = Gtk.Label(_('Universal copy & paste'))
		label2.set_alignment(0, 0.5)
		table1.attach(label2,0,1,1,2, xpadding=5, ypadding=5)
		self.switch2 = Gtk.Switch()
		table1.attach(self.switch2,1,2,1,2, xpadding=5, ypadding=5, xoptions = Gtk.AttachOptions.SHRINK)

		label3 = Gtk.Label(_('Autostart'))
		label3.set_alignment(0, 0.5)
		table1.attach(label3,0,1,2,3, xpadding=5, ypadding=5)
		self.switch3 = Gtk.Switch()
		table1.attach(self.switch3,1,2,2,3, xpadding=5, ypadding=5, xoptions = Gtk.AttachOptions.SHRINK)

		label4 = Gtk.Label(_('Icon light'))
		label4.set_alignment(0, 0.5)
		table1.attach(label4,0,1,3,4, xpadding=5, ypadding=5)
		self.switch4 = Gtk.Switch()
		table1.attach(self.switch4,1,2,3,4, xpadding=5, ypadding=5, xoptions = Gtk.AttachOptions.SHRINK)
		#
		#***************************************************************
		vbox3 = Gtk.VBox(spacing = 5)
		vbox3.set_border_width(5)
		self.notebook.append_page(vbox3,Gtk.Label.new(_('Reply')))
		frame3 = Gtk.Frame()
		vbox3.pack_start(frame3,False,True,1)
		table3 = Gtk.Table(3, 2, False)
		frame3.add(table3)
		#***************************************************************
		label31 = Gtk.Label(_('Reply messages')+':')
		label31.set_alignment(0, 0.5)
		table3.attach(label31,0,1,0,1, xpadding=5, ypadding=5)
		#
		self.switch31 = Gtk.Switch()
		table3.attach(self.switch31,1,2,0,1, xpadding=5, ypadding=5)
		#
		label32 = Gtk.Label(_('Reply Whatsapp')+':')
		label32.set_alignment(0, 0.5)
		table3.attach(label32,0,1,1,2, xpadding=5, ypadding=5)
		#
		self.switch32 = Gtk.Switch()
		table3.attach(self.switch32,1,2,1,2, xpadding=5, ypadding=5)
		#
		label33 = Gtk.Label(_('Reply Telegram')+':')
		label33.set_alignment(0, 0.5)
		table3.attach(label33,0,1,2,3, xpadding=5, ypadding=5)
		#
		self.switch33 = Gtk.Switch()
		table3.attach(self.switch33,1,2,2,3, xpadding=5, ypadding=5)
		#
		label34 = Gtk.Label(_('Reply Hangout')+':')
		label34.set_alignment(0, 0.5)
		table3.attach(label34,0,1,3,4, xpadding=5, ypadding=5)
		#
		self.switch34 = Gtk.Switch()
		table3.attach(self.switch34,1,2,3,4, xpadding=5, ypadding=5)
		#
		label35 = Gtk.Label(_('Reply Facebook')+':')
		label35.set_alignment(0, 0.5)
		table3.attach(label35,0,1,4,5, xpadding=5, ypadding=5)
		#
		self.switch35 = Gtk.Switch()
		table3.attach(self.switch35,1,2,4,5, xpadding=5, ypadding=5)
		#
		label36 = Gtk.Label(_('Reply Line')+':')
		label36.set_alignment(0, 0.5)
		table3.attach(label36,0,1,5,6, xpadding=5, ypadding=5)
		#
		self.switch36 = Gtk.Switch()
		table3.attach(self.switch36,1,2,5,6, xpadding=5, ypadding=5)
		#
		self.load_preferences()
		#
		self.show_all()
		
	def on_switch1_changed(self,widget,event):
		print(event,type(event))
		if not widget.get_active():
			ld = LoginDialog()
			ld.run()
			self.oauth_access_token = ld.code
			ld.destroy()
			if self.oauth_access_token is None or len(self.oauth_access_token)<=0:
				self.oauth_access_token = None
		else:
			self.oauth_access_token = None
		try:
			print('****************************************************')
			print('register pushbullet service')
			self.pushBulletService = bus.get_object('es.atareao.pushbullet','/es/atareao/pushbullet')
			print('****************************************************')
			tokenConfiguration = TokenConfiguration()
			tokenConfiguration.set('oauth_access_token',self.oauth_access_token)
			tokenConfiguration.save()
			print(1)
			self.pushBulletService.restart()
			print(2)
			if self.oauth_access_token is None:
				#self.switch1.set_active(False)
				pass
			else:
				self.switch1.set_active(True)
		except dbus.DBusException as e:
			print(e)

		

	def close_application(self, event):
		self.hide()
	
	def messagedialog(self,title,message):
		dialog = Gtk.MessageDialog(None,Gtk.DialogFlags.MODAL,Gtk.MessageType.INFO,buttons=Gtk.ButtonsType.OK)
		dialog.set_markup("<b>%s</b>" % title)
		dialog.format_secondary_markup(message)
		dialog.run()
		dialog.destroy()
		
	def close_ok(self):
		self.save_preferences()

	def load_preferences(self):
		configuration = Configuration()
		tokenConfiguration = TokenConfiguration()
		first_time = configuration.get('first-time')
		version = configuration.get('version')
		if first_time:# or version != comun.VERSION:
			configuration.set_defaults()
			configuration.read()
		self.oauth_access_token = tokenConfiguration.get('oauth_access_token')
		if self.oauth_access_token is None or len(self.oauth_access_token) == 0:
			self.switch1.set_active(False)
		else:
			self.switch1.set_active(True)
		self.switch2.set_active(configuration.get('copy_paste'))
		self.switch3.set_active(os.path.exists(comun.FILE_AUTO_START))
		self.switch4.set_active(configuration.get('theme') == 'light')
		self.switch31.set_active(configuration.get('reply_sms'))
		self.switch32.set_active(configuration.get('reply_whatsapp'))
		self.switch33.set_active(configuration.get('reply_telegram'))
		self.switch34.set_active(configuration.get('reply_hangout'))
		self.switch35.set_active(configuration.get('reply_facebook'))
		self.switch36.set_active(configuration.get('reply_line'))
		

	def save_preferences(self):
		'''
		tokenConfiguration = TokenConfiguration()
		tokenConfiguration.set('oauth_access_token',self.oauth_access_token)
		tokenConfiguration.save()
		'''
		configuration = Configuration()		
		configuration.set('first-time',False)
		configuration.set('version',comun.VERSION)
		configuration.set('copy_paste',self.switch2.get_active())
		create_or_remove_autostart(self.switch3.get_active())
		if self.switch4.get_active() == True:
			configuration.set('theme','light')
		else:
			configuration.set('theme','dark')
		configuration.set('reply_sms',self.switch31.get_active())
		configuration.set('reply_whatsapp',self.switch32.get_active())
		configuration.set('reply_telegram',self.switch33.get_active())
		configuration.set('reply_hangout',self.switch34.get_active())
		configuration.set('reply_facebook',self.switch35.get_active())
		configuration.set('reply_line',self.switch36.get_active())
		configuration.save()
		

if __name__ == "__main__":
	cm = PreferencesDialog()
	if 	cm.run() == Gtk.ResponseType.ACCEPT:
			print(1)
			cm.close_ok()
	cm.hide()
	cm.destroy()
	exit(0)
