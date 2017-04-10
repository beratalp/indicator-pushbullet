#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
#
# Copyright (C) 2010 Lorenzo Carbonell
# lorenzo.carbonell.cerezo@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be Public,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
#

from gi.repository import Gtk, Gdk
import dbus
import dbus.service
import time
from dbus.mainloop.glib import DBusGMainLoop
import youtube_dl
			
class YouTubeDBUSService(dbus.service.Object):
	def __init__(self):
		bus_name = dbus.service.BusName('es.atareao.youtube', bus=dbus.SessionBus())
		dbus.service.Object.__init__(self, bus_name, '/es/atareao/youtube')
		clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
		clipboard.connect('owner-change',self.capture_clipboard)
		self.monitor_clipboard = True
		self.last_capture_url = None
		self.last_capture_time = int(time.time()*100)

	def capture_clipboard(self,data1,data2):
		if self.monitor_clipboard:
			clipboard = data1
			text = clipboard.wait_for_text()
			if text is not None:
				ydl = youtube_dl.YoutubeDL({'outtmpl': '%(id)s%(ext)s'})
				ydl.add_default_info_extractors()
				print(ydl.extract_info(text,download=False))
				if text.startswith('https://www.youtube.com/watch?v='):
					#url = text[32:]
					url = text
					newtime = int(time.time()*100)
					if self.last_capture_url != url or self.last_capture_time != newtime:
						self.last_capture_url = url
						self.last_capture_time = newtime
						self.captured_youtube_url(url)
				
	
	@dbus.service.method('es.atareao.youtube')
	def set_monitor_clipboard(self, monitor_clipboard):
		self.monitor_clipboard = monitor_clipboard
		print('---/ %s /---'%self.monitor_clipboard)

	@dbus.service.method('es.atareao.youtube')
	def set_captured_youtube_url(self, url):
		self.captured_youtube_url(url)

	@dbus.service.signal('es.atareao.youtube')
	def captured_youtube_url(self, url):
		pass

	@dbus.service.method('es.atareao.youtube')
	def test(self,a):
		return "Hello,World! " + a

if __name__ == '__main__':
	DBusGMainLoop(set_as_default=True)
	mYouTubeDBUSService = YouTubeDBUSService()
	Gtk.main() 
