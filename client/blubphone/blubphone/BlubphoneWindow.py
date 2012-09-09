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

import gettext
import Contact
import Network
import Search
import SmsThread
import Status
import Write
import os
import sys

from gettext import gettext as _
gettext.textdomain('blubphone')

from gi.repository import Gtk, Gdk, Notify
import logging
logger = logging.getLogger('blubphone')

from blubphone_lib import Window
from blubphone.AboutBlubphoneDialog import AboutBlubphoneDialog
from blubphone.PreferencesBlubphoneDialog import PreferencesBlubphoneDialog

PROJECT_ROOT_DIRECTORY = os.path.abspath(
        os.path.dirname(os.path.dirname(os.path.realpath(sys.argv[0])))) + "/data/"

# See blubphone_lib.Window.py for more details about how this class works
class BlubphoneWindow(Window):
    __gtype_name__ = "BlubphoneWindow"   

    all_contacts = dict()
    all_contacts_list = []
    all_sms = dict()
    all_sms_threads = dict()
    #all_write_tabs = []
    
    def finish_initializing(self, builder): # pylint: disable=E1002
        """Set up the main window"""
        super(BlubphoneWindow, self).finish_initializing(builder)

        self.AboutDialog = AboutBlubphoneDialog
        self.set_default_size(800, 600)
        self.move(300, 100)
		
        self.PreferencesDialog = PreferencesBlubphoneDialog    

        self.notebook = builder.get_object("TabPanel")
        
        self.status = Status.Status(self.notebook, self)
  
		#self.status.set_opened()

        #self.disconnect_btn = self.builder.get_object("Disconnect")
		#self.connect_btn = self.builder.get_object("Connect")
	
		connect_menu = builder.get_object("mnu_new")
		self.newsms_menu = builder.get_object("mnu_open")
		self.newsms_btn = builder.get_object("Write")
		self.newsms_btn.set_sensitive(False)
		connect_menu.connect("activate", self.on_Status_clicked)
     
        ''' set up tcp Connection to android '''
        # client = Network.tcpClient()

        # Notification
		Notify.init("blubPhone")


    # open Status-Tab
    def on_Status_clicked(self, widget):
		self.status.set_opened()

    def on_Disconnect_clicked(self, widget):
        self.status.set_opened()
        
    # open WriteSMS-Tab
    def on_Write_clicked(self, widget):    		
        if self.status.connected == False:
            self.status.listenerError("Please connect first")
            return
        Write.Write(self.notebook, self)
		

    def listenerContact(self, contact):
        self.all_contacts[contact.get_telnr()] = contact
        self.all_contacts_list.append(contact)

    def listenerSms(self, sms):
        # print "listenerSms"
        person = sms.get_telnr()
        if person in self.all_sms:
            self.all_sms[person].append(sms)
        else:
            self.all_sms[person] = [sms]
        if person in self.all_sms_threads:
            self.all_sms_threads[person].append_sms(sms)
        if sms.get_read() == False:
            telnr = sms.get_telnr()
            if telnr in self.all_sms_threads:
                self.all_sms_threads[telnr].set_focus()
            else:
                if telnr in self.all_contacts:
                    SmsThread.SmsThread(self.notebook, self.all_contacts[telnr], self)    
                else:
                    SmsThread.SmsThread(self.notebook, Contact.Contact(0, "", telnr), self)

            if telnr in self.all_contacts:
                noti = Notify.Notification.new("Incoming SMS", self.all_contacts[telnr].get_name() + ": " + sms.get_text(), PROJECT_ROOT_DIRECTORY + "/media/logo_new_small.png")
	            noti.show()
            else:
                noti = Notify.Notification.new("Incoming SMS", telnr + ": " + sms.get_text(), PROJECT_ROOT_DIRECTORY + "/media/logo_new_small.png")
	            noti.show()
        

    def shutdown_network(self):
        print "shutdown_network"
        self.status.shutdown_network()
        
    def get_all_contacts(self):
        return self.all_contacts_list

    def get_all_sms(self, number):
        if number in self.all_sms:
            return self.all_sms[number]
        else:
            return []

    def register_write_tab(self, tab):
        pass
        #print "register_write_Tab"
        #self.all_write_tabs.append(tab)

    def unregister_write_tab(self, tab):
        pass
        '''print "unregister_write_Tab"
        self.all_write_tabs.remove(tab)
        for index in range(0, len(self.all_write_tabs)):
            if self.all_write_tabs[index] == tab:
                print "found tab"
                self.all_write_tabs.remove(index)
                break'''

    def register_sms_thread(self, contact, thread):
        telnr = contact.get_telnr()
        if self.is_thread_already_open(contact):
            print "double threads!!!"
            return
		
        self.all_sms_threads[telnr] = thread

    def unregister_sms_thread(self, contact):
        telnr = contact.get_telnr()
        if self.is_thread_already_open(contact) == False:
            print "no thread to unregister"
            return
        del self.all_sms_threads[telnr]

    def is_thread_already_open(self, contact):
        telnr = contact.get_telnr()
        return telnr in self.all_sms_threads

    def focus_thread(self, contact):
        if self.is_thread_already_open(contact) == False:
            print "can't focus thread, becuase not in list"
            return
        print "todo: focus thread"

    def send_sms(self, contact, sms_text):
        return self.status.sendSms(contact.get_telnr(), sms_text)
        
    def listenerConnected(self, connected):
        
        if connected:
			self.newsms_btn.set_sensitive(True)
			self.status.ip_entry.set_sensitive(False)
			self.status.entry_field.set_sensitive(False)
            noti = Notify.Notification.new("Connected", "You are now connected with your Smartphone", PROJECT_ROOT_DIRECTORY + "/media/logo_new_small.png")
            noti.show()
        else:
			self.newsms_btn.set_sensitive(False)
			self.status.ip_entry.set_sensitive(True)
			self.status.entry_field.set_sensitive(True)
            noti = Notify.Notification.new("Disconnected", "You are now disconnected from your Smartphone", PROJECT_ROOT_DIRECTORY + "/media/logo_new_small.png")
            noti.show()
        
        if connected == False:
            print "disconnect"
            #while len(self.all_write_tabs) > 0:
            #    self.all_write_tabs[0].on_tabclose_clicked(None)
            #while len(self.all_sms_threads) > 0:
            #    for sms_tab in self.all_sms_threads.values():
            #        sms_tab.on_tabclose_clicked(None)
            #        break

            self.all_contacts = dict()
            self.all_contacts_list = []
            self.all_sms = dict()
            #self.all_sms_threads = dict()
            #self.all_write_tabs = []

	def disable_writebutton(self):
		self.newsms_btn.set_sensitive(False)

