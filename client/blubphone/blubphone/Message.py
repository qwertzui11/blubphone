# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
### BEGIN LICENSE
# Copyright (C) 2012 Markus Lanner markus@mlanner.com
# Copyright (C) 2012 Manuela Weilharter caitilyn@gmail.com
# 
# This program is free software: you can redistribute it and/or modify it 
# under the terms of the GNU General Public License version 3, as published 
# by the Free Software Foundation.
# 
# This program is distributed in the hope that it will be useful, but 
# WITHOUT ANY WARRANTY; without even the implied warranties of 
# MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR 
# PURPOSE.  See the GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along 
# with this program.  If not, see <http://www.gnu.org/licenses/>.
### END LICENSE

from datetime import datetime

class Message:
	
	"""
	id: 
	threadid:
	tel nr:
	person id:
	timestamp
	type: 1-4
	body: text
	
	"""
	
	def __init__(self, msg_id, thread_id, person_telnr, person_id, msg_timestamp, msg_type, msg_text, msg_read): 
        self.msg_id = msg_id 
        self.thread_id = thread_id 
        self.person_telnr = person_telnr.replace(" ", "") 
        self.person_id = person_id
        self.msg_timestamp = msg_timestamp 
        self.msg_type = msg_type
        self.msg_text = msg_text	
        self.msg_read = msg_read
		
		
	def get_person(self):
		return self.person_id
		
		
	def get_text(self):
		return self.msg_text
		
	def get_read(self):
        return self.msg_read
		
	def get_type(self):
		return self.msg_type
		
	def get_time(self):
		return self.msg_timestamp

    def get_time_string(self):
        converted = datetime.fromtimestamp(self.msg_timestamp/1000.0);
        return converted.strftime("%d. %B %Y %I:%M%p")

    def get_telnr(self):
		return self.person_telnr


