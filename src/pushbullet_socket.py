#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# pushbullet_socket.py
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

from ws4py.client.threadedclient import WebSocketClient
import json
import dbus
from datetime import datetime
import logging
import sys
sys.path.insert(1,'/opt/extras.ubuntu.com/pushbullet-commons/share/pushbullet-commons')
import commons_comun
from commons_configurator import Configuration as TokenConfiguration

class PushBulletSocketClient(WebSocketClient):
	
	def __init__(self,oauth_access_token):
		WebSocketClient.__init__(self,'wss://stream.pushbullet.com/websocket/' + oauth_access_token,protocols=['http-only', 'chat'])
		bus = dbus.SessionBus()
		self.modified_after = 0
		self.read_preferences()
		self.logger = logging.getLogger('PushBulletSocketClient')
		hdlr = logging.FileHandler('/tmp/pushbulletsocketclient_temporal_logging.log')
		formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
		hdlr.setFormatter(formatter)
		self.logger.addHandler(hdlr) 
		self.logger.setLevel(logging.INFO)		
		self.daemon = True
		try:
			self.pushBulletService = bus.get_object('es.atareao.pushbullet','/es/atareao/pushbullet')
		except dbus.DBusException as e:
			exit(1)		

	def received_message(self, message):
		try:
			data = json.loads(message.data.decode())
			self.logger.info(str(data))
			print('WebSocketClient',datetime.now().strftime('%Y-%m-%d %H:%M:%S'),str(data))
			if data['type'] == 'tickle' and data['subtype'] == 'push':
				self.pushBulletService.set_pushing(False,'tickle','{}')
			elif data['type'] == 'push': 
				self.pushBulletService.set_pushing(False,'push',json.dumps(data['push']))
		except Exception as e:
			self.logger.error('Error in WebSocketClient %s'%(str(e)))
			print('Error in WebSocketClient',e)

	def read_preferences(self):
		tokenConfiguration = TokenConfiguration()
		self.iden = tokenConfiguration.get('source_user_iden')			

if __name__ == '__main__':
	while(True):
		configuration = TokenConfiguration()
		oauth_access_token = configuration.get('oauth_access_token')
		if oauth_access_token is not None and len(oauth_access_token)>0:
			try:
				ws = PushBulletSocketClient(oauth_access_token)
				ws.connect()
				ws.run_forever()
				print(1)
			except Exception as e:
				ws.logger.error('Error in WebSocketClient %s'%(str(e)))
				ws.close()
	exit(0)
