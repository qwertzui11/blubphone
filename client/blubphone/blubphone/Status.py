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


from gi.repository import Gtk, Gdk, GLib

import Network
import threading
import os
import sys

PROJECT_ROOT_DIRECTORY = os.path.abspath(
        os.path.dirname(os.path.dirname(os.path.realpath(sys.argv[0])))) + "/data/"

class Status:
	opened = False
    devices = dict()
    connected = False
	
	def __init__(self, notebook, main_window):

        print "init Status"

		self.notebook = notebook
		self.main_window = main_window

        self.dialog = Gtk.MessageDialog(main_window, 0, Gtk.MessageType.WARNING, Gtk.ButtonsType.CLOSE, "Network error")
        self.dialog.set_title("Network error")

        print PROJECT_ROOT_DIRECTORY
		
		status_builder = Gtk.Builder()
		status_builder.add_from_file(PROJECT_ROOT_DIRECTORY + "ui/Status.ui")
		
		self.status = status_builder.get_object("box1")
		self.status.unparent()    

		status_builder.add_from_file(PROJECT_ROOT_DIRECTORY + "ui/Close.ui")
		
		self.close = status_builder.get_object("box4")
		self.close.unparent()
		
		self.drop_conn_btn = status_builder.get_object("Drop_Connection")
		self.conn_btn = status_builder.get_object("Establish_Connection")
        self.device_list = status_builder.get_object("device_list")
        self.ip_entry = status_builder.get_object("ip")       
        
        self.name_store = Gtk.ListStore(str)
        self.device_list.set_model(self.name_store)
        renderer_text = Gtk.CellRendererText()
        self.device_list.pack_start(renderer_text, True)
        self.device_list.add_attribute(renderer_text, "text", 0)
        self.device_list.set_entry_text_column(0)
        self.device_list.connect("changed", self.on_device_list_changed)
		
		self.entry_field = status_builder.get_object("entry1")
		self.entry_field.connect("activate", self.on_PwEntry_clicked)
		
		self.conn_btn.connect("clicked", self.on_connect_clicked)
		self.drop_conn_btn.connect("clicked", self.on_disconnect_clicked)
		self.drop_conn_btn.hide()

        self.notebook.append_page(self.status, self.close)
		
        ''' install broadcast receiver '''
        self.broadcast = Network.BroadCastReceiver(self.new_devive_received)

        GLib.timeout_add_seconds(5, self.check_device_timeout)

        # init tcpClient
        self.client = Network.TcpClient(self.listenerConnected, self.main_window.listenerContact, self.main_window.listenerSms, self.listenerError)

    def set_opened(self):
        self.notebook.set_current_page(0)
        
    def on_PwEntry_clicked(self, widget):
		#read pw from entry
		password = self.entry_field.get_text()
        address = self.ip_entry.get_text()
        self.client.connect(address, password)		

    def on_device_list_changed(self, combo):
        tree_iter = combo.get_active_iter()
        if tree_iter != None:
            model = combo.get_model()
            name = model[tree_iter][0]
            if name in self.devices:
                self.ip_entry.set_text(self.devices[name][1])
            else:
                print "failed to set ip from device_list"

    def check_device_timeout(self):
        for key in self.devices.iterkeys():
            if self.devices[key][0] - GLib.get_current_time() < -11:
                print "device times out --> removing"
                self.update_device_list(key, False)
                del self.devices[key]
                break
            
        return True

    def update_device_list(self, item, add):
        if add:
            self.name_store.append([item])
        else:
            myIter = self.name_store.get_iter_first()
            while myIter != None:
                if self.name_store[myIter][0] == item:
                    self.name_store.remove(myIter)
                    break
                myIter = self.name_store.iter_next(myIter)
		
    def new_devive_received(self, ip, name):
        # print ip
        # print name

        print_name = name + " <" + ip + ">"
        toUpdate = print_name not in self.devices
        self.devices[print_name] = [GLib.get_current_time(), ip]

        if toUpdate:
            self.update_device_list(print_name, True)


		
	def on_connect_clicked(self, widget):
		#read pw from entry
		password = self.entry_field.get_text()
        address = self.ip_entry.get_text()
        self.client.connect(address, password)		
			
			
	def on_disconnect_clicked(self, widget):
		self.client.shutdown()
		self.main_window.disable_writebutton()
		self.entry_field.set_sensitive(True)
		self.ip_entry.set_sensitive(True)
		
	
	def get_ipfield():
		return self.ip_entry
		
		
	def get_pw_field():
		return self.entry_field			
			
	def set_builder(self, builder):
		self.builder = builder

    
    def on_destroy_(self, widget):
        pass


    def listenerConnected(self, connected):
        self.connected = connected
        if connected:
            print "successfully connected"
        else:
            print "disconnected"

        if connected:
            self.conn_btn.hide()
		    self.drop_conn_btn.show()
        else:
            self.conn_btn.show()
		    self.drop_conn_btn.hide()

        self.main_window.listenerConnected(connected)

    
    def listenerError(self, error):
        print "before error"
        self.dialog.set_markup(error)
        self.dialog.run()
        self.dialog.hide()
        print error

    def shutdown_network(self):
        self.broadcast.shutdown()
        self.client.shutdown()

    def sendSms(self, phone_number, message):
        if self.connected == True:
            self.client.sendSms(phone_number, message)
        else:
            self.dialog.set_markup("Cannot send Sms, because not connected.")
            self.dialog.run()
            self.dialog.hide()
            return False
        return True
