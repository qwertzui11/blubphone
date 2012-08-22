package com.mlanner.blubphone;

import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetSocketAddress;
import java.util.logging.Logger;

import org.json.JSONException;
import org.json.JSONObject;

public class MyBroadcast implements Runnable {
    private DatagramSocket broadcastSocket;
    private Thread thread;
    private boolean shallRun = false;
    private DatagramPacket packet;
    
    public MyBroadcast()
    {
		try {		
			broadcastSocket = new DatagramSocket(null);
			broadcastSocket.setBroadcast(true);
			
			JSONObject msg = new JSONObject();
			try {
				msg.put("type", "device");
				msg.put("model", android.os.Build.MODEL);
				// msg.put("address", InetAddress.getLocalHost().getHostAddress());
			} catch (JSONException ex) {
				ex.printStackTrace();
			}
			String jsonString = msg.toString();
			packet = new DatagramPacket(jsonString.getBytes(), jsonString.length(), new InetSocketAddress("255.255.255.255", 7897));
			
		} catch (Exception ex) {
			ex.printStackTrace();
		}
		
    }
    
    public void start()
    {
    	thread = new Thread(this);
    	shallRun = true;
    	thread.start();
    }
    
    public void stop()
    {
    	shallRun = false;
    	try {
    		thread.interrupt();
    	} catch (Exception ex) {
    		;
    	}
    }
    
	public void run() {
		while(shallRun)
		{
			try {
				Logger.getLogger("blubPhone").info("broadcastSocket.send(packet)");
				broadcastSocket.send(packet);
				
				Thread.sleep(5000);
			} catch (Exception ex) {
				ex.printStackTrace();
				return;
			}
			
		}
	}

}
