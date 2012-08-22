package com.mlanner.blubphone;

import android.app.PendingIntent;
import android.content.ContentValues;
import android.content.Context;
import android.content.Intent;
import android.net.Uri;
import android.telephony.SmsManager;

public class SmsWriter {
	private PendingIntent pendingIntent;
	private SmsManager smsManager;
	private Context context;
	
	public SmsWriter(Context context)
	{
		this.context = context; 
		pendingIntent = PendingIntent.getActivity(context, 0, new Intent(), 0);                
        smsManager = SmsManager.getDefault();
	}

	public void sendSMS(String phoneNumber, String message)
    {        
		smsManager.sendTextMessage(phoneNumber, null, message, pendingIntent, null);
		
		ContentValues values = new ContentValues();
		values.put("address", phoneNumber);
		values.put("body", message);
		context.getContentResolver().insert(Uri.parse("content://sms/sent"), values);
    }    
}
