package com.mlanner.blubphone;

import java.util.ArrayList;

import android.content.Context;
import android.database.Cursor;
import android.provider.ContactsContract;

public class ContactReader {
	
	/**
	 * reads all contacs
	 * @param context
	 * @return
	 */
	public static ArrayList<MyContact> readAllContacts(Context context)
	{
		Cursor cursor = context.getContentResolver().query(ContactsContract.Contacts.CONTENT_URI,
				new String [] {"_id", "display_name"}, 
				" has_phone_number = 1 ", 
				null, "display_name");
		
		if (cursor == null)
		{
			return null;
		}
		
		ArrayList<MyContact> result = new ArrayList<MyContact>(); 
			
		while (cursor.moveToNext()) { 

			String contactId = cursor.getString(0);
			long id = cursor.getLong(0);
			String name = cursor.getString(1);
					   
			Cursor phones = context.getContentResolver().query( ContactsContract.CommonDataKinds.Phone.CONTENT_URI, 
					new String [] {ContactsContract.CommonDataKinds.Phone.NUMBER}, 
					ContactsContract.CommonDataKinds.Phone.CONTACT_ID + " = " + contactId, 
					null, null);
		
			while (phones.moveToNext()) 
			{ 
				String phoneNumber = phones.getString(0);
				
				result.add(new MyContact(id, phoneNumber, name));
			} 
			
			phones.close(); 
		}
		
		cursor.close();

			
		return result;
	}
	
	
}
