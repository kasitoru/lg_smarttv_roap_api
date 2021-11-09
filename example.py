# LG SmartTV ROAP API
# Author: Sergey Avdeev
# E-Mail: avdeevsv91@gmail.com
# URL: https://github.com/kasitoru/lg_smarttv_roap_api

import cv2, numpy
from LG import SmartTV

IP_ADDRESS = '192.168.0.198'
TV_KEY = ''

# Find TV
while(not IP_ADDRESS):
	print('Searching TV...')
	IP_ADDRESS = SmartTV.findTV()
print('TV IP: ' + IP_ADDRESS)
TV = SmartTV(IP_ADDRESS)

# Authorization
auth = False
print('Authorization...')
while(not auth):
	if TV_KEY:
		try:
			TV.sendKey(TV_KEY)
			auth = True
		except:
			print('Wrong key! Try again...')
			TV_KEY = ''
	else:
		try:
			TV.displayKey()
			TV_KEY = input('Enter key: ')
		except:
			print('TV is offline!')

# Send simple command
TV.sendCommand(SmartTV.TV_CMD_CHANNEL_UP)

# Screen capture
print('Start capturing...')
while(True):
	image = TV.getData(SmartTV.TV_INFO_SCREEN)
	npimg = numpy.frombuffer(image, numpy.uint8)
	frame = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
	cv2.imshow('TV ({0}) [Press ESC to exit]'.format(IP_ADDRESS), frame)
	if cv2.waitKey(1) == 27:
		break
