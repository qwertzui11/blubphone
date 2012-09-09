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

import SmsThread
import Contact
from gi.repository import Gtk, Gdk, GLib
import os
import sys

PROJECT_ROOT_DIRECTORY = os.path.abspath(
        os.path.dirname(os.path.dirname(os.path.realpath(sys.argv[0])))) + "/data/"

        
class Write:
	
	def __init__(self, notebook, main_window):
		self.notebook = notebook
        self.main_window = main_window

        self.main_window.register_write_tab(self)

		write_builder = Gtk.Builder()
		write_builder.add_from_file(PROJECT_ROOT_DIRECTORY + "ui/Write.ui")
		self.write = write_builder.get_object("box1")
		self.write.unparent()  

		self.phonenr_field = write_builder.get_object("entry1")  
		self.search_field = write_builder.get_object("entry2")  
		
		#self.search_field.connect('backspace', self.on_search_changed)
        self.search_field.connect('key-press-event', self.on_search_changed)
        
		write_builder.add_from_file(PROJECT_ROOT_DIRECTORY + "ui/Close.ui")
		close = write_builder.get_object("box1")
		close.unparent()

		close_btn = write_builder.get_object("TabClose1")
		close_btn.connect("clicked", self.on_tabclose_clicked)

		ok_btn = write_builder.get_object("ok_btn")
		ok_btn.connect("clicked", self.on_ok_clicked)

		self.box2 = write_builder.get_object("box2")

		pagenum = self.notebook.append_page(self.write, close)
		self.notebook.set_current_page(pagenum)
		# self.notebook.show_all()

		self.liststore = Gtk.ListStore(str, str)
		self.treeview = write_builder.get_object("treeview1")
		
		# build the columns            
		renderer = Gtk.CellRendererText()
		column0 = Gtk.TreeViewColumn("Name", renderer, text=0)
		column1 = Gtk.TreeViewColumn("Telephone Number", renderer, text=1)
		self.treeview.append_column(column0)
		self.treeview.append_column(column1)
		
        self.contacts = self.main_window.get_all_contacts()
        self.contacts_dict = self.main_window.all_contacts

        # display the contact list in the treeview
        for contact in self.contacts:
            self.liststore.append([contact.get_name(), contact.get_telnr()])
			
		self.treeview.set_model(self.liststore)  

		self.treeview.connect('cursor-changed', self.row_activated_click)		
        self.treeview.connect('row-activated', self.row_activated_enter)	
	
    def row_activated_enter(self, widget, a, b):
        print "row_activated_enter"
        self.row_activated_click(widget)
        self.on_ok_clicked(widget)

	def search_dict(self):
		text = self.search_field.get_text()	
		self.searched_contacts = []
		for key in self.contacts_dict.keys():
			if (text in key):
				self.searched_contacts.append(self.contacts_dict[key])
		
		for value in self.contacts_dict.values():
			if (text.lower() in value.name.lower()):
				self.searched_contacts.append(value)
			
			
		self.liststore.clear()
		
		for contact in self.searched_contacts:
			self.liststore.append([contact.get_name(), contact.get_telnr()])
		
		self.treeview.set_model(self.liststore)
	
	
    def on_ok_clicked(self, widget):
        if (self.phonenr_field.get_text() != ""):
            self.activate_answer_view()
            self.write.destroy()
            
    def on_search_changed(self, widget, abc):
		GLib.idle_add(self.search_dict)
    
    
    # gets called when a row is clicked in the telephonebook
    def row_activated_click(self, widget):
        try:
            treeselection = widget.get_selection()
            (model, iter) = treeselection.get_selected()
            value = self.liststore.get_value(iter, 1)

            print treeselection.get_selected_rows()[1][0]
            self.selected_row = int(str(treeselection.get_selected_rows()[1][0]))

            self.phonenr_field.set_text(value)
        
        except: ()
        
        
    # opens the read/write view
    def activate_answer_view(self):
        # if a row (contact) is chosen 
        try:
			
            cur_contact = self.searched_contacts[self.selected_row]
            
            # if the selected contact has no phone nr entry
            if (cur_contact.get_telnr() == ""):
                cur_contact = Contact.Contact(0, "", self.phonenr_field.get_text())

        # if a phonenr is typed in
        except:
            cur_contact = Contact.Contact(0, "", self.phonenr_field.get_text())

        if self.main_window.is_thread_already_open(cur_contact):
            self.main_window.focus_thread(cur_contact)
        else:
            SmsThread.SmsThread(self.notebook, cur_contact, self.main_window)
		
	def on_tabclose_clicked(self, widget):


        self.main_window.unregister_write_tab(self)
        self.write.hide()


