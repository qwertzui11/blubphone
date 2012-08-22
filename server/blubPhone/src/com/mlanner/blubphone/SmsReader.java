package com.mlanner.blubphone;

import java.util.ArrayList;
import java.util.logging.Logger;

import android.content.ContentResolver;
import android.content.Context;
import android.database.ContentObserver;
import android.database.Cursor;
import android.net.Uri;
import android.os.Handler;

public class SmsReader extends ContentObserver
{
	private Context context;
	private static final String[] fields = new String[] {"_id", "thread_id", "address", "person", "date", "type", "body", "read" }; // type 2 == sended from me, type 1 received
	private ContentResolver contentResolver;
	private ISmsReadReceiver callbackReceiver;

	public SmsReader(Context context, ISmsReadReceiver callback) {
		super(new Handler());
		
		this.context = context;
		this.callbackReceiver = callback;
		
		Logger.getLogger("blubPhone").info("register observer");
		
		contentResolver = context.getContentResolver();
		contentResolver.registerContentObserver(Uri.parse("content://sms"), true, this);
	}
	
	public void shutdown ()
	{
		Logger.getLogger("blubPhone").info("unregister observer");
		contentResolver.unregisterContentObserver(this);
	}
	
	@Override
    public void onChange(boolean selfChange) {
        super.onChange(selfChange);

        Cursor cursor = context.getContentResolver().query(
				Uri.parse("content://sms"), 
				fields,
				null, null, null);
        
        if (cursor.moveToNext()) 
		{
           MySmsMessage toAdd = parseCursorLine(cursor);          
           Logger.getLogger("blubPhone").info(toAdd.toString());
           callbackReceiver.newSms(toAdd);
		} 
    }


	public static ArrayList<MySmsMessage> readAllSms(Context context)
	{
		Cursor cursor = context.getContentResolver().query(
				Uri.parse("content://sms"), 
				fields,
				null, null, 
				"date ASC");
					
		ArrayList<MySmsMessage> result = new ArrayList<MySmsMessage>();
		
		while (cursor.moveToNext()) 
		{
           MySmsMessage toAdd = parseCursorLine(cursor);          
           result.add(toAdd);
		} 
		
		cursor.close();
		
		return result;
	}
	
	private static MySmsMessage parseCursorLine(Cursor cursor)
	{
		long id = cursor.getLong(0);
		long threadId = cursor.getLong(1);
		String address = cursor.getString(2);
		long person = -1;
		if (cursor.getString(3) != null)
			person = cursor.getLong(3);
		long timestamp = cursor.getLong(4);
		long type = cursor.getLong(5);
		String body = cursor.getString(6);
		boolean read = cursor.getInt(7) > 0;
       
       return new MySmsMessage(id, threadId, address, person, timestamp, type, body, read);
	}
	

	
}
