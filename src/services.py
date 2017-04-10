#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
#
# services.py
#
# Copyright (C) 2012 Lorenzo Carbonell
# lorenzo.carbonell.cerezo@gmail.com
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
#
#
#

import requests
import json
import os
from urllib.parse import urlencode
import random
import time
from logindialog import LoginDialog
import mimetypes
import io

CLIENT_ID = 'RpkMU0UUoiDMNZnY1ZLJXWLw7QYm4QRY'
CLIENT_SECRET = 'D80i4GrB8f0KoJsjph0Zl9bTQaHWn3p0'
class PushbulletService(object):
	def __init__(self,client_id,client_secret,token_file):
		self.session = requests.session()
		self.request_token_url = 'https://api.pushbullet.com/oauth2'
		self.authorize_url = 'https://www.dropbox.com/1/oauth/authorize'
		self.access_token_url = 'https://api.pushbullet.com/oauth2/token'
		self.client_id = client_id
		self.client_secret = client_secret
		self.token_file = token_file
		self.access_token = None
		self.refresh_token = None
		if os.path.exists(token_file):
			f = open(token_file,'r')
			text = f.read()
			f.close()
			try:			
				data = json.loads(text)
				self.oauth_token = data['oauth_token']
				self.oauth_token_secret = data['oauth_token_secret']
			except Exception as e:
				print('Error')
				print(e)

	def get_access_token(self,code):
		params = {}
		params['grant_type'] = 'authorization_code'
		params['client_id'] = self.client_id
		params['client_secret'] = self.client_secret
		params['code'] = code
		print(params)
		response = self.session.request('POST',self.access_token_url,params=params)
		print(response,response.status_code,response.text)
		if response.status_code == 200:
			oauth_token_secret, oauth_token,uid = response.text.split('&')
			oauth_token_secret = oauth_token_secret.split('=')[1]
			oauth_token = oauth_token.split('=')[1]
			uid = uid.split('=')[1]
			self.oauth_token = oauth_token
			self.oauth_token_secret = oauth_token_secret
			f = open(self.token_file,'w')
			f.write(json.dumps({'oauth_token':oauth_token,'oauth_token_secret':oauth_token_secret}))
			f.close()
			
			return uid, oauth_token, oauth_token_secret
		return None		
		

	def get_request_token(self):
		params = {}
		params['client_id'] = self.client_id
		params['redirect_uri'] = 'http://www.atareao.es/tag/pushbullet-indicator/'
		params['response_type'] = 'token'
		#params['oauth_timestamp'] = int(time.time())
		#params['oauth_nonce'] = ''.join([str(random.randint(0, 9)) for i in range(8)])
		#params['oauth_version'] = '1.0'
		#params['oauth_signature_method'] = 'PLAINTEXT'
		#params['oauth_signature'] = '%s&'%SECRET
		response = self.session.request('POST',self.request_token_url,params=params)
		print(response,response.text)
		if response.status_code == 200:
			oauth_token_secret, oauth_token = response.text.split('&')
			oauth_token_secret = oauth_token_secret.split('=')[1]
			self.ts = oauth_token_secret
			oauth_token = oauth_token.split('=')[1]
			return oauth_token, oauth_token_secret
		return None	

if __name__ == '__main__':
	pbservice = PushbulletService(CLIENT_ID,CLIENT_SECRET,'/home/atareao/token')
	ld = LoginDialog('https://www.pushbullet.com/authorize?client_id=RpkMU0UUoiDMNZnY1ZLJXWLw7QYm4QRY&redirect_uri=http%3A%2F%2Fwww.atareao.es%2Ftag%2Fpushbullet-indicator&response_type=code&scope=everything')
	ld.run()
	code = ld.code
	print('---------------------------------')
	print(code)
	print('---------------------------------')
	pbservice.get_access_token(code)
	

	#oauth_token,oauth_token_secret = us.get_request_token()
	
	
	#ds = DropboxService('','','token')
	'''
	oauth_token,oauth_token_secret = ds.get_request_token()
	authorize_url = ds.get_authorize_url(oauth_token,oauth_token_secret)
	ld = LoginDialog(1024,600,authorize_url,'http://localhost/?uid=','not_approved=true')
	ld.run()
	ans = ld.code
	ld.destroy()
	if ans is not None:
		print(ans)
		uid,oauth_token = ans.split('&')
		uid = uid.split('=')[1]
		oauth_token = oauth_token.split('=')[1]
		print(uid,oauth_token)
		ans = ds.get_access_token(oauth_token,oauth_token_secret)
		print(ans)
		print(ds.get_account_info())
	'''
	'''
	print(ds.get_account_info())
	print(ds.get_file('data'))
	print(ds.put_file('/home/atareao/Escritorio/data'))
	'''
	exit(0)
	
