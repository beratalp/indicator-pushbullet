#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# comun.py
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

import urllib.request

__author__ = 'Lorenzo Carbonell <lorenzo.carbonell.cerezo@gmail.com>'
__copyright__ = 'Copyright (c) 2012-2014 Lorenzo Carbonell'
__license__ = 'GPLV3'
__url__ = 'http://www.atareao.es'

import os
import locale
import gettext

######################################

def is_package():
	return not os.path.dirname(os.path.abspath(__file__)).endswith('src')

######################################

PARAMS = {
			'first-time':True,
			'version':'',
			'theme':'light',
			'name':None,
			'modified_after':0,
			'copy_paste':True,
			'reply_sms':False,
			'reply_whatsapp':False,
			'reply_telegram':False,
			'reply_hangout':False,
			'reply_facebook':False,
			'reply_line':False,
			'last_push':{}			
			}


APP = 'pushbullet-indicator'
APPCONF = APP + '.conf'
APPDATA = APP + '.data'
APPNAME = 'PushBullet-Indicator'
CONFIG_DIR = os.path.join(os.path.expanduser('~'),'.config')
CONFIG_APP_DIR = os.path.join(CONFIG_DIR, APP)
CONFIG_FILE = os.path.join(CONFIG_APP_DIR, APPCONF)
DATA_FILE = os.path.join(CONFIG_APP_DIR, APPDATA)
BACKUP_FILE = os.path.join(CONFIG_APP_DIR, 'backup')
TOKEN_FILE = os.path.join(CONFIG_APP_DIR, 'token')
AUTOSTART_DIR = os.path.join(CONFIG_DIR,'autostart')
FILE_AUTO_START = os.path.join(AUTOSTART_DIR,'pushbullet-indicator-autostart.desktop')
if not os.path.exists(CONFIG_APP_DIR):
	os.makedirs(CONFIG_APP_DIR)

print(os.path.dirname(os.path.abspath(__file__)))

if is_package():
	ROOTDIR = '/opt/extras.ubuntu.com/pushbullet-indicator/share/'
	LANGDIR = os.path.join(ROOTDIR, 'locale-langpack')
	APPDIR = os.path.join(ROOTDIR, APP)
	ICONDIR = os.path.join(APPDIR, 'icons')
	SOCIALDIR = os.path.join(APPDIR, 'social')
	CHANGELOG = os.path.join(APPDIR,'changelog')
	FILE_AUTO_START_ORIG = os.path.join(APPDIR,'pushbullet-indicator-autostart.desktop')
	WATCHDOG = os.path.join(APPDIR,'pushbullet_socket.py')
else:
	ROOTDIR = os.path.dirname(__file__)
	LANGDIR = os.path.join(ROOTDIR, 'template1')
	APPDIR = os.path.join(ROOTDIR, APP)
	ICONDIR =  os.path.normpath(os.path.join(ROOTDIR, '../data/icons'))
	SOCIALDIR =  os.path.normpath(os.path.join(ROOTDIR, '../data/social'))
	DEBIANDIR = os.path.normpath(os.path.join(ROOTDIR, '../debian'))
	CHANGELOG = os.path.join(DEBIANDIR,'changelog')
	FILE_AUTO_START_ORIG = os.path.join(os.path.normpath(os.path.join(ROOTDIR, '../data')),'pushbullet-indicator-autostart.desktop')
	WATCHDOG = os.path.join(ROOTDIR,'pushbullet_socket.py')
ICON = os.path.join(ICONDIR,'pushbullet-indicator.svg')
STATUS_ICON = {}
STATUS_ICON['light'] = (os.path.join(ICONDIR,'pushbullet-indicator-light.svg'),os.path.join(ICONDIR,'pushbullet-indicator-sync-light.svg'))
STATUS_ICON['dark'] = (os.path.join(ICONDIR,'pushbullet-indicator-dark.svg'),os.path.join(ICONDIR,'pushbullet-indicator-sync-dark.svg'))

ADDRESS_ICON = os.path.join(ICONDIR,'address.svg')
FILE_ICON = os.path.join(ICONDIR,'file.svg')
LINK_ICON = os.path.join(ICONDIR,'link.svg')
LIST_ICON = os.path.join(ICONDIR,'list.svg')
NOTE_ICON = os.path.join(ICONDIR,'note.svg')
IMAGE_ICON = os.path.join(ICONDIR,'image.svg')
FACEBOOK_ICON = os.path.join(ICONDIR,'facebook.svg')
HANGOUT_ICON = os.path.join(ICONDIR,'hangout.svg')
LINE_ICON = os.path.join(ICONDIR,'line.svg')
MESSENGER_ICON = os.path.join(ICONDIR,'messenger.svg')
TELEGRAM_ICON = os.path.join(ICONDIR,'telegram.svg')
WHATSAPP_ICON = os.path.join(ICONDIR,'whatsapp')

f = open(CHANGELOG,'r')
line = f.readline()
f.close()
pos=line.find('(')
posf=line.find(')',pos)
VERSION = line[pos+1:posf].strip()
if not is_package():
	VERSION = VERSION + '-src'
try:
	current_locale, encoding = locale.getdefaultlocale()
	language = gettext.translation(APP, LANGDIR, [current_locale])
	language.install()
	_ = language.gettext
except Exception as e:
	_ = str
	
def read_from_url(url):
	try:
		url = url.replace(' ','%20')
		request = urllib.request.Request(url, headers={'User-Agent' : 'Magic Browser'})
		f = urllib.request.urlopen(request)
		json_string = f.read()
		f.close()
		return json_string
	except:
		return None

def internet_on():
	try:
		response=urllib.request.urlopen('http://google.com',timeout=1)
		return True
	except:
		pass
	return False

	
