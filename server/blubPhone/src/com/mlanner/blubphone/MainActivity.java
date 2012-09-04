package com.mlanner.blubphone;

import java.util.ArrayList;
import java.util.Random;
import java.util.logging.Logger;

import org.json.JSONObject;

import android.app.AlertDialog;
import android.app.Notification;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.Context;
import android.content.DialogInterface;
import android.content.Intent;
import android.os.Bundle;
import android.preference.Preference;
import android.preference.Preference.OnPreferenceClickListener;
import android.preference.PreferenceActivity;
import android.preference.PreferenceScreen;
import android.view.KeyEvent;
import android.widget.Toast;

public class MainActivity extends PreferenceActivity implements OnPreferenceClickListener, ITcpServerReceiver, ISmsReadReceiver {
	private Preference changePassword;
	private Random random = new Random();
	private SmsReader smsReceiver;
	private SmsWriter smsSender;
	private TcpServer tcpServer;
	private static final String networkVersion = "1.1";
	private String lastError = new String(); 
	private NotificationManager mNotificationManager;
	private Notification notification;
	private boolean savedInstance = false; 
	
	private static final int NOTIFICATION_ID = 1;
	
	@Override
	public void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		
		tcpServer = (TcpServer)getLastNonConfigurationInstance();
		if (tcpServer == null)
		{
			tcpServer = new TcpServer();
			createNewPassword();
		}
		tcpServer.setCallBackReceiver(this);

		addPreferencesFromResource(R.xml.main_activity);

		PreferenceScreen screen = getPreferenceScreen();
		
		// Preference welcome = screen.getPreference(0);
		changePassword = screen.getPreference(1);
		
		changePassword.setOnPreferenceClickListener(this);
		
		smsSender = new SmsWriter(getApplicationContext());
		smsReceiver = new SmsReader(getBaseContext(), this);
		
		updateConnectionStatus();
		
		String ns = Context.NOTIFICATION_SERVICE;
		mNotificationManager = (NotificationManager) getSystemService(ns);
		
		int icon = R.drawable.ic_launcher;
		CharSequence tickerText = "blubPhone connected";
		long when = System.currentTimeMillis();

		notification = new Notification(icon, tickerText, when);
		
		Context context = getApplicationContext();
		CharSequence contentTitle = "You are connected";
		CharSequence contentText = "You successfully connected to Ubuntu";
		Intent notificationIntent = getIntent();
		PendingIntent contentIntent = PendingIntent.getActivity(this, 0, notificationIntent, 0);

		notification.setLatestEventInfo(context, contentTitle, contentText, contentIntent);
	}
	
	
	@Override
	public void onDestroy()
	{
		super.onDestroy();

		if (smsReceiver != null)
		{
			smsReceiver.shutdown();
		}
		
		if (!savedInstance)
		{
			mNotificationManager.cancel(NOTIFICATION_ID);
			tcpServer.stopListening();
		}
	}
	

	@Override
	public boolean onKeyDown(int keyCode, KeyEvent event)
	{
		if(keyCode == KeyEvent.KEYCODE_BACK) {
	        //Ask the user if they want to quit
	        new AlertDialog.Builder(this)
	        .setIcon(android.R.drawable.ic_dialog_alert)
	        .setTitle(R.string.quit)
	        .setMessage(R.string.really_quit)
	        .setPositiveButton(R.string.yes, new DialogInterface.OnClickListener() {

	            public void onClick(DialogInterface dialog, int which) {

	                //Stop the activity
	            	MainActivity.this.finish();    
	            }

	        })
	        .setNegativeButton(R.string.no, null)
	        .show();

	        return true;
		}

	    return super.onKeyDown(keyCode, event);
	}
	
	@Override 
	public Object onRetainNonConfigurationInstance ()
	{
		savedInstance = true;
		return (Object)tcpServer;
	}	
	
	
	@Override 
	public void onResume()
	{
		super.onResume();
		savedInstance = false;
	}
	
	
	private void createNewPassword()
	{
		int newRand = 0;
		while (newRand < 9999)
		{
			newRand = random.nextInt() % 100000;
			// newRand = 12345;
			if (newRand < 0) 
			{
				newRand *= -1;
			}
		}
		tcpServer.setPassword(Integer.toString(newRand));
	}
	
	
	private void updateConnectionStatus()
	{
		String resultHeader = new String();
		String resultText = new String();
		if (!tcpServer.isConnected() && !tcpServer.isListening())
		{
			resultHeader = "Enable Connection";
			resultText = "Click here to allow Ubuntu to connect to this Smartphone. You have to be in the same WLAN as your computer.";
		}
		if (!tcpServer.isConnected() && tcpServer.isListening())
		{
			resultHeader = "Password: " + tcpServer.getPassword();
			resultText = "blubPhone is waiting for a connection from Ubuntu. Click here to cancel.";
		}
		if (tcpServer.isConnected())
		{
			resultHeader = "You are connected!";
			resultText = "Enjoy writing and receiving SMS on your Ubuntu. Click to disconnect.";
		}
		
		changePassword.setTitle(resultHeader);
		changePassword.setSummary(resultText);
	}
	

	public boolean onPreferenceClick(Preference preference) {
		if (preference == changePassword)
		{
			createNewPassword();
			
			if (!tcpServer.isConnected() && !tcpServer.isListening())
			{
				tcpServer.startListening();
			}
			else if (!tcpServer.isConnected() && tcpServer.isListening())
			{
				tcpServer.stopListening();
			} else if (tcpServer.isConnected())
			{
				tcpServer.stopListening();
			}
			
			updateConnectionStatus();
						
			return true;
		}
		return false;
	}
	
	public void connectedGuiThread() {
		updateConnectionStatus();
		if (tcpServer.isConnected())
		{
			mNotificationManager.notify(NOTIFICATION_ID, notification);
		}
		else
		{
			mNotificationManager.cancel(NOTIFICATION_ID);
		}
	}

	public void connected(boolean conn) {
		if (conn)
		{
			Logger.getLogger("blubPhone").info("i'm connetced");
		}
		else
		{
			Logger.getLogger("blubPhone").info("i'm not connetced");
		}
		runOnUiThread(new Runnable() {
			public void run() {
				connectedGuiThread();
				
			}
		});
	}


	public void sendSms(String receiver, String message) {
		Logger.getLogger("blubPhone").info("sendSms");
		smsSender.sendSMS(receiver, message);
	}


	public boolean isPasswordValid(String password) {
		return tcpServer.getPassword().equals(password);
	}


	public boolean isVersionValid(String version) {
		return this.networkVersion.equals(version);
	}


	public void error(String err) {
		lastError = err;
		
		runOnUiThread(new Runnable() {
			public void run() {
				Context context = getApplicationContext();
				CharSequence text = "blubPhone info: " + lastError;
				int duration = Toast.LENGTH_LONG;
				
				Toast toast = Toast.makeText(context, text, duration);
				toast.show();
			}
		});
	}
	
	private void validConnectGuiThread() {
	
		Logger.getLogger("blubPhone").info("validVonnectGuiThread");
		
		ArrayList<MySmsMessage> allSms = SmsReader.readAllSms(getApplicationContext());
		Logger.getLogger("blubPhone").info("all sms count " + Integer.toString(allSms.size()));
		
		ArrayList<MyContact> allContacts = ContactReader.readAllContacts(getApplicationContext());
		Logger.getLogger("blubPhone").info("all contacts count " + Integer.toString(allContacts.size()));
		
		for (int ind = 0; ind < allContacts.size(); ++ind)
		{
			if (!sendContact(allContacts.get(ind)))
			{
				return;
			}
		}
		for (int ind = 0; ind < allSms.size(); ++ind)
		{
			MySmsMessage sms = allSms.get(ind);
			if (!sendSms(sms))
			{
				return;
			}
		}
	}
	
	
	private boolean sendSms(MySmsMessage sms)
	{
		if (!sms.isRead())
		{
			smsReceiver.markSmsAsRead(sms.getId());
		}
		JSONObject msg = sms.toJSONObject();
		return tcpServer.send(msg.toString() + "\n");
	}
	
	
	private boolean sendContact(MyContact contact)
	{
		JSONObject msg = contact.toJSONObject();
		return tcpServer.send(msg.toString() + "\n");
	}


	public void validConnect() {
		runOnUiThread(new Runnable() {
			public void run() {
				validConnectGuiThread();
			}
		});
	}


	public void newSms(MySmsMessage sms) {
		if (tcpServer.isConnected())
		{
			sendSms(sms);
		}
	}

}
