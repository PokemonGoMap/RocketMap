#!/usr/bin/python
# -*- coding: utf-8 -*-

"""accept-tos.py: Example script to accept in-game Terms of Service"""

from pgoapi import PGoApi
from pgoapi.utilities import f2i
from pgoapi import utilities as util
from pgoapi.exceptions import AuthException
import pprint
import time
import threading

def accept_tos(username, password, auth):
	#print('Accepting Terms of Service for {}'.format(username))
	api = PGoApi()
	api.set_position(51.5030922, 7.466812, 0.0)
	api.login(auth, username, password)
	time.sleep(5)
	req = api.create_request()
	req.mark_tutorial_complete(tutorials_completed = 0, send_marketing_emails = False, send_push_notifications = False)
	response = req.call()
	#print('Accepted Terms of Service for {}'.format(username))
	print('%s	%s	%s' % (username, password, response['status_code']))
	#print('Response dictionary: \r\n{}'.format(pprint.PrettyPrinter(indent=4).pformat(response)))

accept_tos('NAME', 'PASSWORD', 'ptc')