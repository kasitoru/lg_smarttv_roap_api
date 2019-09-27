# LG SmartTV ROAP API
# Author: Sergey Avdeev
# E-Mail: avdeevsv91@gmail.com
# URL: https://github.com/avdeevsv91/lg_smarttv_roap_api

import socket, re, http.client
import xml.etree.ElementTree as etree

class SmartTV:
	TV_CMD_POWER = 1
	TV_CMD_NUMBER_0 = 2
	TV_CMD_NUMBER_1 = 3
	TV_CMD_NUMBER_2 = 4
	TV_CMD_NUMBER_3 = 5
	TV_CMD_NUMBER_4 = 6
	TV_CMD_NUMBER_5 = 7
	TV_CMD_NUMBER_6 = 8
	TV_CMD_NUMBER_7 = 9
	TV_CMD_NUMBER_8 = 10
	TV_CMD_NUMBER_9 = 11
	TV_CMD_UP = 12
	TV_CMD_DOWN = 13
	TV_CMD_LEFT = 14
	TV_CMD_RIGHT = 15
	TV_CMD_OK = 20
	TV_CMD_HOME_MENU = 21
	TV_CMD_BACK = 23
	TV_CMD_VOLUME_UP = 24
	TV_CMD_VOLUME_DOWN = 25
	TV_CMD_MUTE_TOGGLE = 26
	TV_CMD_CHANNEL_UP = 27
	TV_CMD_CHANNEL_DOWN = 28
	TV_CMD_BLUE = 29
	TV_CMD_GREEN = 30
	TV_CMD_RED = 31
	TV_CMD_YELLOW = 32
	TV_CMD_PLAY = 33
	TV_CMD_PAUSE = 34
	TV_CMD_STOP = 35
	TV_CMD_FAST_FORWARD = 36
	TV_CMD_REWIND = 37
	TV_CMD_SKIP_FORWARD = 38
	TV_CMD_SKIP_BACKWARD = 39
	TV_CMD_RECORD = 40
	TV_CMD_RECORDING_LIST = 41
	TV_CMD_REPEAT = 42
	TV_CMD_LIVE_TV = 43
	TV_CMD_EPG = 44
	TV_CMD_PROGRAM_INFORMATION = 45
	TV_CMD_ASPECT_RATIO = 46
	TV_CMD_EXTERNAL_INPUT = 47
	TV_CMD_PIP_SECONDARY_VIDEO = 48
	TV_CMD_SHOW_SUBTITLE = 49
	TV_CMD_PROGRAM_LIST = 50
	TV_CMD_TELE_TEXT = 51
	TV_CMD_MARK = 52
	TV_CMD_3D_VIDEO = 400
	TV_CMD_3D_LR = 401
	TV_CMD_DASH = 402
	TV_CMD_PREVIOUS_CHANNEL = 403
	TV_CMD_FAVORITE_CHANNEL = 404
	TV_CMD_QUICK_MENU = 405
	TV_CMD_TEXT_OPTION = 406
	TV_CMD_AUDIO_DESCRIPTION = 407
	TV_CMD_ENERGY_SAVING = 409
	TV_CMD_AV_MODE = 410
	TV_CMD_SIMPLINK = 411
	TV_CMD_EXIT = 412
	TV_CMD_RESERVATION_PROGRAM_LIST = 413
	TV_CMD_PIP_CHANNEL_UP = 414
	TV_CMD_PIP_CHANNEL_DOWN = 415
	TV_CMD_SWITCH_VIDEO = 416
	TV_CMD_APPS = 417
	TV_CMD_MOUSE_MOVE = 'HandleTouchMove'
	TV_CMD_MOUSE_CLICK = 'HandleTouchClick'
	TV_CMD_TOUCH_WHEEL = 'HandleTouchWheel'
	TV_CMD_CHANGE_CHANNEL = 'HandleChannelChange'
	TV_CMD_SCROLL_UP = 'up'
	TV_CMD_SCROLL_DOWN = 'down'
	TV_INFO_CURRENT_CHANNEL = 'cur_channel'
	TV_INFO_CHANNEL_LIST = 'channel_list'
	TV_INFO_CONTEXT_UI = 'context_ui'
	TV_INFO_VOLUME = 'volume_info'
	TV_INFO_SCREEN = 'screen_image'
	TV_INFO_3D = 'is_3d'
	TV_LAUNCH_APP = 'AppExecute'

	def __init__(self, ipaddress, port = 8080):
		self.ip = ipaddress
		self.port = port
		self.session = None

	def __encodeData(data, type):
		params = ''
		for name, value in data.items():
			params += '<{0}>{1}</{0}>'.format(name, value)
		return '<?xml version="1.0" encoding="utf-8"?>' + '\r\n' + \
			   '<{0}>{1}</{0}>'.format(type, params)

	def __execRequest(self, url, data = {}):
		conn = http.client.HTTPConnection(self.ip, self.port)
		if data:
			method = 'POST'
			if self.session:
				data['session'] = self.session
			enc = SmartTV.__encodeData(data, url.split('/')[-1])
		else:
			method = 'GET'
			enc = None
		conn.request(method, url, enc, {'Content-Type': 'application/atom+xml'})
		httpResponse = conn.getresponse()
		resp = httpResponse.read()
		try:
			xml = etree.fromstring(resp)
		except:
			return resp
		if xml.find('ROAPError').text != '200':
			raise Exception('Error ({0}): {1}'.format(xml.find('ROAPError').text, xml.find('ROAPErrorDetail').text))
		return xml

	def findTV():
		strngtoXmit = 'M-SEARCH * HTTP/1.1' + '\r\n' + \
			'HOST: 239.255.255.250:1900' + '\r\n' + \
			'MAN: "ssdp:discover"' + '\r\n' + \
			'MX: 3' + '\r\n' + \
			'ST: roap:rootservice' + '\r\n' + '\r\n'
		bytestoXmit = strngtoXmit.encode()
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		sock.settimeout(3)
		gotstr = 'notyet'
		ipaddress = None
		i = 0
		sock.sendto(bytestoXmit, ('239.255.255.250', 1900))
		while ipaddress is None and i <= 5 and gotstr == 'notyet':
			try:
				gotbytes, addressport = sock.recvfrom(512)
				gotstr = gotbytes.decode()
			except:
				i += 1
				sock.sendto(bytestoXmit, ('239.255.255.250', 1900))
			if re.search('LOCATION', gotstr):
				#ipaddress, _ = addressport
				ipaddress = re.search(r'[0-9]+(?:\.[0-9]+){3}', gotstr).group()
			else:
				gotstr = 'notyet'
			i += 1
		sock.close()
		return ipaddress

	def displayKey(self):
		return self.__execRequest('/roap/api/auth', {'type': 'AuthKeyReq'})

	def sendKey(self, key):
		resp = self.__execRequest('/roap/api/auth', {'type': 'AuthReq', 'value': key})
		self.session = resp.find("session").text
		return resp

	def sendCommand(self, cmd, params = {}):
		if isinstance(cmd, int) and not params:
			params['value'] = cmd
			cmd = 'HandleKeyInput'
		params['name'] = cmd
		return self.__execRequest('/roap/api/command', params)

	def getData(self, target):
		return self.__execRequest('/roap/api/data?target=' + target)
