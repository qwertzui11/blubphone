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

import socket
import threading
import json
import time

from gi.repository import GLib, Notify

import Contact
import Message



class BroadCastReceiver:
	def __init__ (self, listenerDevice):
		self.listenerDevice = listenerDevice

		self.receiver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.receiver.bind(("0.0.0.0", 7897))

		self.thread = threading.Thread(None, self.readFromSocket);

		self.thread.start()

	def readFromSocket(self):
        try:
		    while 1:
			    data,addr = self.receiver.recvfrom(1024)
                
                ''' some debug output '''
			    # print data
			    # print addr
                if data == "":
                    break;
                
                try:
                    message = json.loads(data)

                    msg_type = message["type"]
                    if msg_type == "device":
                        name = message["model"]

                        GLib.idle_add(self.listenerDevice, addr[0], name)
                        
                except KeyError:
                    print "Invalid json message received"
        except IOError, socket.error:
            print "broadcast listener thread going down"

        print "done at readFromSocket at broadcastreceiver"

    def shutdown(self):
        try:
            self.receiver.shutdown(socket.SHUT_RDWR)
        except socket.error:
            pass


class TcpClient:

	def __init__ (self, listenerConnected, listenerContact, listenerSms, listenerError):
		self.connectedListener = listenerConnected
		self.listenerContact = listenerContact
		self.listenerSms = listenerSms
		self.listenerError = listenerError
		self.port = 7897


	def connect (self, address, password):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try: 
		    self.client.connect((address, self.port))
        except socket.error:
            GLib.idle_add(self.listenerError, "Could not connect")
            GLib.idle_add(self.connectedListener, False)
            return
            
		GLib.idle_add(self.connectedListener, True)
		self.sendPassword(password)

        self.thread = threading.Thread(None, self.readFromSocket);
		self.thread.start()

	def readLine(self, sock):
		ret = ''
		while True:
			ch = sock.recv(1)
			if ch == '\n' or ch == '':
			    break
			else:
			    ret += ch
		return ret
	
	def readFromSocket(self):
		try:
		    while 1:
			    line = self.readLine(self.client)
			    # print line
			    if line == '':
				    break
                try:
                    message = json.loads(line)

                    msg_type = message["type"]
                    # print msg_type
                    
                    if msg_type == "error":
                        GLib.idle_add(self.listenerError, message["text"])

                    if msg_type == "contact":
                        GLib.idle_add(self.listenerContact, Contact.Contact(message["id"], message["name"], message["phoneNumber"]))

                    if msg_type == "sms":
                        GLib.idle_add(self.listenerSms, Message.Message(
                            message["id"], 
                            message["threadId"], 
                            message["address"], 
                            message["person"], 
                            message["timestamp"], 
                            message["sms_type"], 
                            message["body"], 
                            message["read"]))
                     
                except KeyError:
                    print "Invalid json message received"
        except IOError, socket.error:
            pass
        GLib.idle_add(self.connectedListener, False)

	def sendData(self, data):
		self.client.sendall(data)
		self.client.sendall("\n")

	def sendSms(self, phone_number, message):
		self.sendData(json.dumps({"type":"send_sms", "receiver": phone_number, "message": message}))

	def sendPassword(self, password):
		self.sendData(json.dumps({"type":"validate", "version": "1.1", "password": password}))

    def shutdown(self):
        try:
            self.client.shutdown(socket.SHUT_RDWR)
        except socket.error:
            pass

'''
def connected():
	print "connected"

def contact():
	print "contact"

def sms():
	print "sms"

def error():
	print "error"

def device():
	print "error"

BroadCastReceiver(device)

time.sleep(10)

print "connecting"

client = TcpClient(connected, contact, sms, error)
client.connect("192.168.4.31", "10688");

time.sleep(1)
client.sendSms("+4369919478701", "liebe\"K\nlima")

client.thread.join()

#client.sendData('{"4": 5,\n "6') 
#client.sendData('": 7}\n')
'''

