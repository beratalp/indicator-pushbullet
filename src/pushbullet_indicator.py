#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# pushbullet-indicator.py
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
from gi.repository import GLib
from gi.repository import GdkPixbuf
from gi.repository import AppIndicator3 as appindicator
from gi.repository import Notify
from gi.repository import GObject

import os
import sys
import glob
import json
import webbrowser
import subprocess
import dbus
import platform
import base64
import io
import time
import requests
import PIL.Image
import tempfile
from threading import Thread

from configurator import Configuration
from preferences_dialog import PreferencesDialog
from answer_dialog import AnswerDialog
from sms_dialog import SendSMSDialog
from comun import _
import comun
from dbus.mainloop.glib import DBusGMainLoop


sys.path.insert(1,'/opt/extras.ubuntu.com/pushbullet-commons/share/pushbullet-commons')
import commons_comun
from commons_configurator import Configuration as TokenConfiguration
from pushbullet_dialogs import ActionDialog
from logindialog import LoginDialog
from commons_comun import internet_on

# Callbacks for asynchronous calls

failed = False
pushbullet_replied = False
raise_replied = False

def handle_pushbullet_reply():
    global pushbullet_replied
    pushbullet_replied = True
    if pushbullet_replied and raise_replied:
        loop.quit()

def handle_pushbullet_error(e):
    global failed
    global pushbullet_replied
    pushbullet_replied = True
    failed = True
    print("HelloWorld raised an exception! That's not meant to happen...")
    print("\t", str(e))
    if pushbullet_replied and raise_replied:
        loop.quit()

def handle_raise_reply():
    global failed
    global raise_replied
    raise_replied = True
    failed = True
    print("RaiseException returned normally! That's not meant to happen...")
    if pushbullet_replied and raise_replied:
        loop.quit()

def handle_raise_error(e):
    global raise_replied
    raise_replied = True
    print("RaiseException raised an exception as expected:")
    print("\t", str(e))

def add2menu(menu, text = None, icon = None, conector_event = None, conector_action = None):
	if text != None:
		menu_item = Gtk.ImageMenuItem.new_with_label(text)
		if icon:
			image = Gtk.Image.new_from_file(icon)
			menu_item.set_image(image)
			menu_item.set_always_show_image(True)
	else:
		if icon == None:
			menu_item = Gtk.SeparatorMenuItem()
		else:
			menu_item = Gtk.ImageMenuItem.new_from_file(icon)
			menu_item.set_always_show_image(True)
	if conector_event != None and conector_action != None:				
		menu_item.connect(conector_event,conector_action)
	menu_item.show()
	menu.append(menu_item)
	return menu_item

class PushBullet_Indicator(object):

	def __init__(self,dbus_loop):
		self.icon = comun.ICON
		self.active_icon = None
		self.attention_icon = None		
		self.about_dialog = None
		self.active = False
		self.animate = False
		self.the_watchdog = None
		self.frame = 0
		#
		clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
		clipboard.connect('owner-change',self.capture_clipboard)
		self.monitor_clipboard = True
		self.last_capture_text = None
		self.last_capture_time = int(time.time()*100)		
		#
		self.clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
		bus = dbus.SessionBus(mainloop=dbus_loop)
		try:
			self.pushBulletService = bus.get_object('es.atareao.pushbullet','/es/atareao/pushbullet')
			bus.add_signal_receiver(self.pushing_signal_handler, dbus_interface = 'es.atareao.pushbullet', signal_name = 'pushing')
		except dbus.DBusException as e:
			exit(1)
		self.notification = Notify.Notification.new('','', None)
		self.read_preferences()
		#
		self.indicator = appindicator.Indicator.new ('PushBullet-Indicator',\
			self.active_icon, appindicator.IndicatorCategory.HARDWARE)
		self.indicator.set_attention_icon(self.attention_icon)
		self.indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
		#
		menu = self.get_menu()
		self.indicator.set_menu(menu)
		
	def capture_clipboard(self,data1,data2):
		if self.monitor_clipboard and self.copy_paste:
			clipboard = data1
			text = clipboard.wait_for_text()
			if text is not None:
				url = text
				newtime = int(time.time()*100)
				if self.last_capture_text != text or self.last_capture_time != newtime:					
					self.last_capture_text = text
					self.last_capture_time = newtime
					print('Captured!!!!!. Text: %s'%text)
					#send_copy(self,source_user_iden,source_device_iden, body):	
					print(self.user['iden'],self.pushBulletService.get_source_user_iden(),text)				
					self.pushBulletService.send_copy(text,
						dbus_interface='es.atareao.pushbullet',
						reply_handler=handle_pushbullet_reply,
						error_handler=handle_pushbullet_error)					
					print('Captured!!!!!. Text: %s'%text)
	
	def pushing_signal_handler(self,is_pushing,kind,push=None):
		if is_pushing == True:
			self.active = True
			print('Start to pushing: '+ kind)
			GObject.timeout_add(500, self.animate_icon)
		else:
			if kind == 'tickle':
				sent_to = None
				try:
					ans = self.pushBulletService.getPushHistory(self.modified_after)				
					if ans is not None:
						ans = json.loads(ans)
						if len(ans)>0:					
							self.last_push = ans[0]
							configuration = Configuration()
							configuration.set('last_push', self.last_push)
							if 'modified' in self.last_push.keys():
								self.modified_after = self.last_push['modified']								
								configuration.set('modified_after',self.modified_after)
							configuration.save()
							print('-------------------------------------------')
							print('-------------------------------------------')
							print('-------------------!!----------------------')
							print(ans[0])
							print('-------------------!!----------------------')
							if self.pushBulletService.get_source_user_iden() != ans[0]['source_device_iden']:
								kind = self.last_push['type']
								if kind == 'file':
									self.notification.update('PushBullet-Indicator',
												_('File recieved'), self.active_icon)
									self.notification.show()
								elif kind == 'link':
									self.notification.update('PushBullet-Indicator',
												_('Link recieved'), self.active_icon)
									self.notification.show()
								elif kind == 'note':
									self.notification.update('PushBullet-Indicator',
												_('Note recieved'), self.active_icon)													
									self.notification.show()
							print('-------------------------------------------')
							print('-------------------------------------------')
							print('-------------------------------------------')
				except Exception as e:
					print(e)
			elif kind == 'push' and push and push is not None:
				push = json.loads(push)
				print('-------------------------------------------')
				print('-------------------------------------------')
				print('-------------------------------------------')
				print(push)
				istemporaryfile = False
				if 'type' in push.keys():
					if push['type'] == 'mirror':					
						try:
							title = 'PushBullet-Indicator'
							body = _('A push mirrored')
							icon = self.active_icon
							if 'title' in push.keys():
								title += ': '+push['title']
							if 'body' in push.keys():
								body = push['body']
							if 'icon' in push.keys():
								temporaryfilename = tempfile.mkstemp(suffix='.png', prefix='pushbullet_indicator_temp_', dir=None, text=False)[1]
								img = PIL.Image.open(io.BytesIO(base64.b64decode(push['icon'])))
								img.save(temporaryfilename)
								icon = temporaryfilename
								istemporaryfile = True					
							print('-------------------------------------------')
							print('title: '+title)
							print('body: '+body)
							print('icon: '+icon)
							print('-------------------------------------------')							
							if (push['package_name'] == 'com.pushbullet.android' and self.reply_sms) or \
								(push['package_name'] == 'org.telegram.messenger' and self.reply_telegram) or \
								(push['package_name'] == 'com.whatsapp' and self.reply_whatsapp) or \
								(push['package_name'] == 'com.google.android.talk' and self.reply_hangout) or \
								(push['package_name'] == 'com.facebook.orca' and self.reply_facebook) or \
								(push['package_name'] == 'jp.naver.line.android' and self.reply_line):
								print('/*****************************************/')
								print('Message')
								print(push)
								#package_name, source_user_iden, target_device_iden, conversation_iden, message):
								answerDialog = AnswerDialog(icon,title,body)								
								if 	answerDialog.run() == Gtk.ResponseType.ACCEPT:
									answerDialog.hide()									
									package_name = push['package_name']
									source_user_iden = push['source_user_iden']								
									target_device_iden = push['source_device_iden']
									conversation_iden = push['conversation_iden']
									message = answerDialog.get_answer()
									self.pushBulletService.send_reply(package_name,
										source_user_iden,
										target_device_iden,
										conversation_iden,
										message,
										dbus_interface='es.atareao.pushbullet',
										reply_handler=handle_pushbullet_reply,
										error_handler=handle_pushbullet_error)
								answerDialog.destroy()								
								print('/*****************************************/')
							else:
								self.notification.update(title,
														body,icon)
								self.notification.show()
							if istemporaryfile:
								if os.path.exists(temporaryfilename):
									os.remove(temporaryfilename)								
						except Exception as e:
							print('An error in mirroring push')
							print(e)
					elif push['type'] == 'clip' and self.copy_paste:
						try:
							if push['source_device_iden'] != self.pushBulletService.get_source_device_iden():
								title = 'PushBullet-Indicator'
								body = _('A push copied')
								icon = self.active_icon
								temporaryfilename = tempfile.mkstemp(suffix='.png', prefix='pushbullet_indicator_temp_', dir=None, text=False)[1]
								if 'title' in push.keys():
									title += ': '+push['title']
								if 'body' in push.keys():								
									body = push['body']								
									if body.startswith('http'):
										response = requests.get(body)									
										img = PIL.Image.open(io.BytesIO(response.content))
										img.save(temporaryfilename)
										icon = temporaryfilename
										image = Gtk.Image()
										image.set_from_pixbuf(GdkPixbuf.Pixbuf.new_from_file(temporaryfilename))
										self.clipboard.set_image(image.get_pixbuf())
										body = _('Image copied')
									elif body.startswith('data:image'):
										oncoma = body.find(',')
										if oncoma>-1:
											oncoma += 1										
											img = PIL.Image.open(io.BytesIO(base64.b64decode(body[oncoma:])))
											img.save(temporaryfilename)
											icon = temporaryfilename
											image = Gtk.Image()
											image.set_from_pixbuf(GdkPixbuf.Pixbuf.new_from_file(temporaryfilename))
											self.clipboard.set_image(image.get_pixbuf())
											body = _('Image copied')
									else:
										self.clipboard.set_text(body, -1)
										body = _('Text copied')+':\n\n'+body									
								print('-------------------------------------------')
								print('title: '+title)
								print('body: '+body)
								print('icon: '+icon)
								print('-------------------------------------------')							
								if len(body)>255:
									body = body[:252]+'...'
								self.notification.update(title,
														body,icon)
								self.notification.show()
								if os.path.exists(temporaryfilename):
									os.remove(temporaryfilename)
						except Exception as e:
							print('An error in mirroring push')
							print(e)						
				print('-------------------------------------------')
				print('-------------------------------------------')
				print('-------------------------------------------')							
			self.active = False
			print('End to pushing: '+ kind)

	############ preferences related methods #################
	def theme_change(self, theme):
		"""Change the icon theme of the indicator.
			If the theme selected is invalid set the "normal" theme.
			:param theme: the index of the selected theme."""
		self.active_icon = comun.STATUS_ICON[theme][0]
		self.attention_icon = comun.STATUS_ICON[theme][1]
		self.indicator.set_icon(self.active_icon)
		self.indicator.set_attention_icon(self.attention_icon)

	################## main functions ####################

	def read_preferences(self):
		configuration = Configuration()
		tokenConfiguration = TokenConfiguration()
		self.first_time = configuration.get('first-time')
		self.version = configuration.get('version')
		self.theme = configuration.get('theme')
		self.modified_after = configuration.get('modified_after')
		self.last_push = configuration.get('last_push')
		self.ICON = comun.ICON
		self.active_icon = comun.STATUS_ICON[configuration.get('theme')][0]
		self.attention_icon = comun.STATUS_ICON[configuration.get('theme')][1]
		self.copy_paste = configuration.get('copy_paste')
		self.reply_sms = configuration.get('reply_sms')
		self.reply_whatsapp = configuration.get('reply_whatsapp')
		self.reply_telegram = configuration.get('reply_telegram')
		self.reply_hangout = configuration.get('reply_hangout')
		self.reply_facebook = configuration.get('reply_facebook')
		self.reply_line = configuration.get('reply_line')
		while(self.pushBulletService.is_login() == False and internet_on()):
			ld = LoginDialog()
			ld.run()
			oauth_access_token = ld.code
			tokenConfiguration = TokenConfiguration()
			tokenConfiguration.set('oauth_access_token',oauth_access_token)
			tokenConfiguration.save()
			self.pushBulletService.restart()

		'''
		all_ok = True
		if self.oauth_access_token is None or len(self.oauth_access_token)==0 or self.name is None or len(self.name) == 0:
			all_ok = False
		else:
			all_ok = self.pushBulletService.set_oauth_access_token(self.oauth_access_token)
		preferencesDialog = PreferencesDialog()
		while(all_ok == False):			
			if 	preferencesDialog.run() == Gtk.ResponseType.ACCEPT:
				preferencesDialog.close_ok()	
				configuration = Configuration()
				self.oauth_access_token = configuration.get('oauth_access_token')
				self.theme = configuration.get('theme')
				self.active_icon = comun.STATUS_ICON[configuration.get('theme')][0]
				self.attention_icon = comun.STATUS_ICON[configuration.get('theme')][1]			
				self.name = configuration.get('name')
				if self.oauth_access_token is None or len(self.oauth_access_token)==0 or self.name is None or len(self.name) == 0:
					all_ok = False
					if self.name is None or len(self.name) == 0:
						md = Gtk.MessageDialog(	parent = None,
											flags = Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
											type = Gtk.MessageType.ERROR,
											buttons = Gtk.ButtonsType.OK_CANCEL,
											message_format = _('You must set a name for your device'))
						md.run()
						md.destroy()
						preferencesDialog.notebook.set_current_page(1)
				else:				
					all_ok = self.pushBulletService.set_oauth_access_token(self.oauth_access_token)
			else:
				exit(0)
		preferencesDialog.destroy()
		'''
		#
		#
		self.launch_watchdog()
		print('--------------------------')
		self.devices = json.loads(self.pushBulletService.getDevices())
		self.contacts = json.loads(self.pushBulletService.getContacts())
		self.user = json.loads(self.pushBulletService.getUser())
		print('Getting last push')
		ans = self.pushBulletService.getPushHistory(self.modified_after)				
		if ans is not None and len(ans)>0:
			ans = json.loads(ans)
			print(ans)
			if ans is not None and len(ans)>0 and 'modified' in ans[0].keys():
				self.modified_after = ans[0]['modified']
				self.last_push = ans[0]
				configuration = Configuration()
				configuration.set('modified_after',self.modified_after)
				configuration.set('last_push',self.last_push)
				configuration.save()
		print('--------------------------')
			

	################### menu creation ######################

	def get_help_menu(self):
		help_menu =Gtk.Menu()
		#
		add2menu(help_menu,text = _('Homepage...'),conector_event = 'activate',conector_action = lambda x: webbrowser.open('https://launchpad.net/pushbullet-indicator'))
		add2menu(help_menu,text = _('Get help online...'),conector_event = 'activate',conector_action = lambda x: webbrowser.open('https://answers.launchpad.net/pushbullet-indicator'))
		add2menu(help_menu,text = _('Translate this application...'),conector_event = 'activate',conector_action = lambda x: webbrowser.open('https://translations.launchpad.net/pushbullet-indicator'))
		add2menu(help_menu,text = _('Report a bug...'),conector_event = 'activate',conector_action = lambda x: webbrowser.open('https://bugs.launchpad.net/pushbullet-indicator'))
		add2menu(help_menu)
		web = add2menu(help_menu,text = _('Homepage'),conector_event = 'activate',conector_action = lambda x: webbrowser.open('http://www.atareao.es/tag/pushbullet-indicator'))
		twitter = add2menu(help_menu,text = _('Follow us in Twitter'),conector_event = 'activate',conector_action = lambda x: webbrowser.open('https://twitter.com/atareao'))
		googleplus = add2menu(help_menu,text = _('Follow us in Google+'),conector_event = 'activate',conector_action = lambda x: webbrowser.open('https://plus.google.com/118214486317320563625/posts'))
		facebook = add2menu(help_menu,text = _('Follow us in Facebook'),conector_event = 'activate',conector_action = lambda x: webbrowser.open('http://www.facebook.com/elatareao'))
		add2menu(help_menu)
		#		
		web.set_image(Gtk.Image.new_from_file(os.path.join(comun.SOCIALDIR,'web.svg')))
		web.set_always_show_image(True)
		twitter.set_image(Gtk.Image.new_from_file(os.path.join(comun.SOCIALDIR,'twitter.svg')))
		twitter.set_always_show_image(True)
		googleplus.set_image(Gtk.Image.new_from_file(os.path.join(comun.SOCIALDIR,'googleplus.svg')))
		googleplus.set_always_show_image(True)
		facebook.set_image(Gtk.Image.new_from_file(os.path.join(comun.SOCIALDIR,'facebook.svg')))
		facebook.set_always_show_image(True)
		
		add2menu(help_menu)
		add2menu(help_menu,text = _('About'),conector_event = 'activate',conector_action = self.on_about_item)
		#
		help_menu.show()
		return(help_menu)

	def get_contact_name_by_email(self,email):
		for key in self.contacts.keys():
			if 'email' in self.contacts[key].keys() and self.contacts[key]['email'] == email:
				return self.contacts[key]['name']
		return ''
	def get_device_identification(self,device_iden):
		if device_iden in self.devices.keys():
			if 'nickname' in self.devices[device_iden].keys() and len(self.devices[device_iden]['nickname'])>0:
				return self.devices[device_iden]['nickname']
			elif 'model' in self.devices[device_iden].keys() and len(self.devices[device_iden]['model'])>0:
				return self.devices[device_iden]['model']
		return ''		

	def on_drag_data_received(self, widget, drag_context, x,y, selection_data,info, time):
		print(e)
	def get_menu(self):
		"""Create and populate the menu."""
		menu = Gtk.Menu()

		send_push = Gtk.MenuItem.new_with_label(_('Send push'))
		send_push.connect('activate',self.on_send_push_clicked)
		send_push.show()
		menu.append(send_push)		

		send_sms = Gtk.MenuItem.new_with_label(_('Send sms'))
		send_sms.connect('activate',self.on_send_sms_clicked)
		send_sms.show()
		menu.append(send_sms)		


		separator0 = Gtk.SeparatorMenuItem()
		separator0.show()
		menu.append(separator0)

		show_last_push = Gtk.MenuItem.new_with_label(_('Show last push'))
		show_last_push.connect('activate',self.on_show_last_push_clicked)
		show_last_push.show()
		menu.append(show_last_push)		

		separator1 = Gtk.SeparatorMenuItem()
		separator1.show()
		menu.append(separator1)
		#
		menu_preferences = Gtk.MenuItem.new_with_label(_('Preferences'))		
		menu_preferences.connect('activate',self.on_preferences_item)
		menu_preferences.show()
		menu.append(menu_preferences)
		
		menu_help = Gtk.MenuItem.new_with_label(_('Help'))		
		menu_help.set_submenu(self.get_help_menu())
		menu_help.show()
		menu.append(menu_help)
		#
		separator2 = Gtk.SeparatorMenuItem()
		separator2.show()
		menu.append(separator2)		
		#
		menu_exit = Gtk.MenuItem.new_with_label(_('Exit'))
		menu_exit.connect('activate',self.on_quit_item)
		menu_exit.show()
		menu.append(menu_exit)
		#
		menu.show()
		return(menu)
	def on_send_sms_clicked(self,widget):
		tdevices = []
		for device in self.devices:
			print(self.devices[device])
			if 'nickname' in self.devices[device].keys() and len(self.devices[device]['nickname'])>0:
				label = self.devices[device]['nickname']
				if self.devices[device]['active'] and 'has_sms' in self.devices[device].keys() and self.devices[device]['has_sms']:
					tdevices.append({'device_iden':device,'label':label})
			elif 'model' in self.devices[device].keys() and len(self.devices[device]['model'])>0:
				label = self.devices[device]['model']
				if self.devices[device]['active'] and 'has_sms' in self.devices[device].keys() and self.devices[device]['has_sms']:
					tdevices.append({'device_iden':device,'label':label})			
		sdevices = sorted(tdevices, key=lambda k: k['label']) 
		cm = SendSMSDialog(sdevices)
		if 	cm.run() == Gtk.ResponseType.ACCEPT:
			cm.hide()
			answer = cm.get_response()
			if answer['number'] is not None and answer['message'] is not None and answer['device_iden'] is not None:
				self.pushBulletService.send_sms(answer['device_iden'], answer['number'], answer['message'],
								dbus_interface='es.atareao.pushbullet',
								reply_handler=handle_pushbullet_reply,
								error_handler=handle_pushbullet_error)
		cm.destroy()
	def on_send_push_clicked(self,widget):
		tdevices = []
		tcontacts = []
		for device in self.devices:
			if 'nickname' in self.devices[device].keys() and len(self.devices[device]['nickname'])>0:
				label = self.devices[device]['nickname']
				tdevices.append({'device_iden':device,'label':label})
			elif 'model' in self.devices[device].keys() and len(self.devices[device]['model'])>0:
				label = self.devices[device]['model']
				tdevices.append({'device_iden':device,'label':label})			
		sdevices = sorted(tdevices, key=lambda k: k['label']) 
		for contact in self.contacts:
			if self.contacts[contact]['active'] and 'name' in self.contacts[contact].keys() and 'email' in self.contacts[contact].keys():
				tcontacts.append({'contact_iden':contact,'name':self.contacts[contact]['name'],'email':self.contacts[contact]['email']})
		scontacts = sorted(tcontacts, key=lambda k: k['name']) 
		sdevices = sorted(tdevices, key=lambda k: k['label']) 				
		actionDialog = ActionDialog(None,sdevices,scontacts)
		if 	actionDialog.run() == Gtk.ResponseType.ACCEPT:
			response = actionDialog.get_response()
			actionDialog.hide()
			while Gtk.events_pending():
				Gtk.main_iteration()						
			if response is not None:
				self.send_bullet(response,device)		
		actionDialog.destroy()
		
	def on_show_last_push_clicked(self,widget):
		if self.last_push:
			actionDialog = ActionDialog(self.last_push,None,None)
			actionDialog.run()
			actionDialog.destroy()

		
	def send_bullet(self,response,identification):
		print(response,identification)
		iscontact = (response['to']['type'] == 'contact')
		if response['kind'] == 'file' or response['kind'] == 'image':
			self.pushBulletService.send_file(response['to']['iden'],response['file'], response['body'], iscontact,
						dbus_interface='es.atareao.pushbullet',
						reply_handler=handle_pushbullet_reply,
						error_handler=handle_pushbullet_error)
		elif response['kind'] == 'link':
			self.pushBulletService.send_link(response['to']['iden'],response['title'],response['body'],response['link'], iscontact,
							dbus_interface='es.atareao.pushbullet',
                            reply_handler=handle_pushbullet_reply,
                            error_handler=handle_pushbullet_error)
		elif response['kind'] == 'note':
			self.pushBulletService.send_note(response['to']['iden'],response['title'],response['body'], iscontact,
							dbus_interface='es.atareao.pushbullet',
                            reply_handler=handle_pushbullet_reply,
                            error_handler=handle_pushbullet_error)
	def launch_watchdog(self):
		"""Call the watchdog."""
		if self.the_watchdog is None:
			self.the_watchdog = subprocess.Popen(comun.WATCHDOG)

	def kill_watchdog(self):
		"""Kill the watchdog."""
		if self.the_watchdog is not None:
			self.the_watchdog.kill()
			self.the_watchdog = None
		
	def animate_icon(self):
		if not self.active:
			self.animate = False
			self.indicator.set_icon(self.active_icon)
			self.frame = 0
			return False
		else:
			self.animate = True
			afile = os.path.join(comun.ICONDIR,'pushbullet-indicator-sync{}-'.format(self.frame % 4)+self.theme+'.svg')
			self.indicator.set_icon(afile)
			self.frame += 1
			return True

	def get_about_dialog(self):
		"""Create and populate the about dialog."""
		about_dialog = Gtk.AboutDialog()
		about_dialog.set_name(comun.APPNAME)
		about_dialog.set_version(comun.VERSION)
		about_dialog.set_copyright('Copyrignt (c) 2014\nLorenzo Carbonell Cerezo')
		about_dialog.set_comments(_('An indicator for PushBullet'))
		about_dialog.set_license(''+
		'This program is free software: you can redistribute it and/or modify it\n'+
		'under the terms of the GNU General Public License as published by the\n'+
		'Free Software Foundation, either version 3 of the License, or (at your option)\n'+
		'any later version.\n\n'+
		'This program is distributed in the hope that it will be useful, but\n'+
		'WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY\n'+
		'or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for\n'+
		'more details.\n\n'+
		'You should have received a copy of the GNU General Public License along with\n'+
		'this program.  If not, see <http://www.gnu.org/licenses/>.')
		about_dialog.set_website('http://www.atareao.es')
		about_dialog.set_website_label('http://www.atareao.es')
		about_dialog.set_authors(['Lorenzo Carbonell <https://launchpad.net/~lorenzo-carbonell>'])
		about_dialog.set_documenters(['Lorenzo Carbonell <https://launchpad.net/~lorenzo-carbonell>'])
		about_dialog.set_translator_credits(''+
		'Lorenzo Carbonell <https://launchpad.net/~lorenzo-carbonell>\n')
		about_dialog.set_icon(GdkPixbuf.Pixbuf.new_from_file(comun.ICON))
		about_dialog.set_logo(GdkPixbuf.Pixbuf.new_from_file(comun.ICON))
		about_dialog.set_program_name(comun.APPNAME)
		return about_dialog

	###################### callbacks for the menu #######################
	def on_preferences_item(self, widget, data=None):
		widget.set_sensitive(False)
		preferences_dialog = PreferencesDialog()
		if 	preferences_dialog.run() == Gtk.ResponseType.ACCEPT:
			preferences_dialog.hide()
			preferences_dialog.close_ok()
			self.read_preferences()
		preferences_dialog.hide()
		preferences_dialog.destroy()
		# we need to change the status icons
		self.indicator.set_icon(self.active_icon)
		self.indicator.set_attention_icon(self.attention_icon)
		widget.set_sensitive(True)

	def on_quit_item(self, widget, data=None):
		self.__del__()
		exit(0)

	def __del__(self):
		'''On destroy kill the watchdog if any'''
		print('----------------------------------')
		print('----------------------------------')
		print('On destroy kill the watchdog if any')
		print('----------------------------------')
		print('----------------------------------')
		self.kill_watchdog()
		for afile in glob.glob('/tmp/pushbullet_indicator_temp_*.png'):
			if os.path.exists(afile):
				os.remove(afile)

	def on_about_item(self, widget, data=None):
		if self.about_dialog:
			self.about_dialog.present()
		else:
			self.about_dialog = self.get_about_dialog()
			self.about_dialog.run()
			self.about_dialog.destroy()
			self.about_dialog = None

#################################################################

def main():
	dbus_loop = DBusGMainLoop(set_as_default=True)
	if dbus.SessionBus(mainloop=dbus_loop).request_name('es.atareao.PushBulletIndicator') != dbus.bus.REQUEST_NAME_REPLY_PRIMARY_OWNER:
		print("application already running")
		exit(0)		
	Notify.init('pushbullet-indicator')
	pushbullet_indicator=PushBullet_Indicator(dbus_loop)
	Gtk.main()
	exit(0)
	
if __name__ == "__main__":
	main()
