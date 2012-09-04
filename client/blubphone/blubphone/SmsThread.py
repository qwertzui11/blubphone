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
import Message
import os
import sys

PROJECT_ROOT_DIRECTORY = os.path.abspath(
        os.path.dirname(os.path.dirname(os.path.realpath(sys.argv[0])))) + "/data/"

class SmsThread:
	
	def __init__(self, notebook, contact, main_window):
		self.contact = contact
		self.notebook = notebook
        self.main_window = main_window

        main_window.register_sms_thread(contact, self)

		answer_builder = Gtk.Builder()
        answer_builder.add_from_file(PROJECT_ROOT_DIRECTORY + "ui/Answer.ui")
        self.answer = answer_builder.get_object("box1")
        self.answer.unparent()

        answer_builder.add_from_file(PROJECT_ROOT_DIRECTORY + "ui/Close.ui")
        close = answer_builder.get_object("box3")
        close.unparent()

        close_btn = answer_builder.get_object("TabClose3")
        close_btn.connect("clicked", self.on_tabclose_clicked)

        self.tab_label = answer_builder.get_object("Status3")
        
        self.set_label()

        pagenum = self.notebook.append_page(self.answer, close)
        self.notebook.set_current_page(pagenum)
        # self.notebook.show_all()

        self.sms_textfield = answer_builder.get_object("write_sms")
        #self.sms_textfield.props.wrap_mode = Gtk.WrapMode.WORD
        self.sms_textfield.connect('backspace', self.delete_text)

        self.sms_statuslabel = answer_builder.get_object("status_label")
        
        self.textbuffer = self.sms_textfield.get_buffer()
        self.textbuffer.connect('insert_text', self.insert_text)

        self.send_btn = answer_builder.get_object("send_btn")
        self.send_btn.connect("clicked", self.on_send_clicked)
        
        messages = self.main_window.get_all_sms(self.contact.get_telnr())
        # msg_id, thread_id, person_telnr, person_id, msg_timestamp, msg_type, msg_text
        '''
        messages.append(Message.Message(0, 10, "0699/19478701", "manu", "30.10.2012 13:00", 2, "hallo markus hallo markus hallo markus hallo markus hallo markus hallo markus hallo markus hallo markus"))
        messages.append(Message.Message(0, 10, "0699/55555555", "markus", "30.10.2012 14:15", 1, "hallo manu"))
        messages.append(Message.Message(0, 10, "0699/55555555", "markus", "30.10.2012 14:16", 1, "schön von dir zu hören"))
        messages.append(Message.Message(0, 10, "0699/19478701", "manu", "30.10.2012 16:04", 2, "wie gehts?"))
        '''
        self.liststore = Gtk.ListStore(str, str, str, str)
        self.treeview = answer_builder.get_object("treeview1")

        self.scroll = answer_builder.get_object("scrolledwindow2")
		
		# build the columns            
		renderer = Gtk.CellRendererText()
		renderer2 = Gtk.CellRendererText()
		
		renderer.set_fixed_size(200, -1)
		renderer2.props.wrap_mode = Gtk.WrapMode.WORD
		
		renderer2.props.wrap_width = 400
		
		column0 = Gtk.TreeViewColumn("Sender", renderer, text=0, foreground=2, background=3)
		column1 = Gtk.TreeViewColumn("Text", renderer2, text=1, foreground=2, background=3)
		self.treeview.append_column(column0)
		self.treeview.append_column(column1)
		
		# add dummy data
		for msg in messages:
            self.append_sms(msg)
		
		# self.liststore.append(["Manu", "0650/2040726"])
		
		self.treeview.set_model(self.liststore)  

		self.treeview.show_all() 
		
	def set_focus(self):
        pass

    # sets the label of the tab
	def set_label(self):
        # if the contact is known, just display the name
        if (self.contact.get_name() != ""):
            self.tab_label.set_text(self.contact.get_name()) 
        # else display the telephonenr
        else:
            self.tab_label.set_text(self.contact.get_telnr()) 

	
    # gets called when text is deleted in the write_sms textfield
    def delete_text(self, widget):
        size = self.textbuffer.get_char_count() - 1 

        if (size < 0): ()
        elif (size <= 160):
            self.sms_statuslabel.set_text(str(size) + "/480 [1 SMS]")
        elif (size <= 320):
            self.sms_statuslabel.set_text(str(size) + "/480 [2 SMS]")
        elif (size <= 480):
            self.sms_statuslabel.set_text(str(size) + "/480 [3 SMS]")
        else:
            self.sms_statuslabel.set_text(str(size) + "/480 [Text is too long]")


    # gets called when text is inserted in the write_sms textfield
    def insert_text(self, widget, iter, text, len):
        size = self.textbuffer.get_char_count() + 1
        if (size <= 160):
            self.sms_statuslabel.set_text(str(size) + "/480 [1 SMS]")
        elif (size <= 320):
            self.sms_statuslabel.set_text(str(size) + "/480 [2 SMS]")
        elif (size <= 480):
            self.sms_statuslabel.set_text(str(size) + "/480 [3 SMS]")
        else:
            self.sms_statuslabel.set_text(str(size) + "/480 [Text is too long]")
		
		
	def on_send_clicked(self, widget):
        # max 480 chars allowed
        if (self.textbuffer.get_char_count() + 1 <= 480):
            sms_text = self.textbuffer.get_text(self.textbuffer.get_start_iter() , self.textbuffer.get_end_iter(),
                    include_hidden_chars=True)
        else:
            sms_text = "too long!"

        if len(sms_text) < 1:
            return
        self.main_window.send_sms(self.contact, sms_text)
        self.textbuffer.set_text("")
        self.sms_statuslabel.set_text("0/480 [1 SMS]")
        
        
		
	def on_tabclose_clicked(self, widget):
		'''pagenum = self.notebook.page_num(self.answer)
        if pagenum < 0:
            print "invalid pagenum"
            return
		self.notebook.remove_page(pagenum)	'''
        self.answer.hide()
        self.main_window.unregister_sms_thread(self.contact)



    def append_sms(self, msg):
        if (msg.get_type() == 2):
			self.liststore.prepend(["me\n" + msg.get_time_string(), msg.get_text(), "#179920", "#FFFFFF"])
		else:
			self.liststore.prepend([self.contact.get_name() + "\n" + msg.get_time_string(), msg.get_text(), "#175E99", "#FFFFFF"])
        GLib.timeout_add(100, self.updateVScroll)
        

    def updateVScroll(self):
        self.scroll.get_vscrollbar().set_value(0)














