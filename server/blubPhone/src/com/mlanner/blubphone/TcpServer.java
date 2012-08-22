package com.mlanner.blubphone;

import java.io.BufferedReader;
import java.io.DataOutputStream;
import java.io.InputStreamReader;
import java.net.ServerSocket;
import java.net.Socket;
import java.util.logging.Logger;

import org.json.JSONException;
import org.json.JSONObject;

public class TcpServer implements Runnable {
	
	private Thread thread;
	private DataOutputStream outToClient;
    private Socket connectionSocket;
    private ServerSocket serverSocket;
    private ITcpServerReceiver callBackReceiver;
    private boolean connected = false;
    private boolean listening = false;
    private String password;
    
    private MyBroadcast broadcast;
    
    public TcpServer()
    {
    	broadcast = new MyBroadcast(); 
    }
    
    public void setCallBackReceiver(ITcpServerReceiver callBackReceiver) {
		this.callBackReceiver = callBackReceiver;
	}

	public String getPassword() {
		return password;
	}

	public void setPassword(String password) {
		this.password = password;
	}

	public boolean isConnected() {
		return connected;
	}

	
	public boolean isListening() {
		return listening;
	}

	public void startListening()
	{
		listening = true;
		connected = false;
		thread = new Thread(this);
		thread.start();
		broadcast.start();
	}
	
	public void stopListening()
	{
		listening = false;
		connected = false;
		try {
			connectionSocket.close();
		} catch (Exception e) {
			;
		}
		try {
			serverSocket.close();
		} catch (Exception e) {
			;
		}
	}

	public void run() 
	{
		Logger.getLogger("blubPhone").info("thread start");
		try {
			serverSocket = new ServerSocket(7897);
			BufferedReader inFromClient;
						
			Logger.getLogger("blubPhone").info("waiting for connection");
			
			listening = true;
			if ((connectionSocket = serverSocket.accept()) != null)
			{
				broadcast.stop();
				listening = false;
				connected = true;
				callBackReceiver.connected(true);
				
				boolean validatedConnect = false;
				
				StringBuilder builder = new StringBuilder();
				String line;
				
				Logger.getLogger("blubPhone").info("connected");
				
				inFromClient = new BufferedReader(new InputStreamReader(connectionSocket.getInputStream()));
				outToClient = new DataOutputStream(connectionSocket.getOutputStream());
				
				while ((line = inFromClient.readLine()) != null)
				{
					Logger.getLogger("blubPhone").info("line: " + line);
					
					builder.append(line);
					
					JSONObject jsonMsg = null;
					
					try {
						jsonMsg = new JSONObject(builder.toString());
					}
					catch (JSONException ex)
					{
						continue;
					}
					Logger.getLogger("blubPhone").info(jsonMsg.toString());
					
					String type = jsonMsg.getString("type");
					if (type.equals("validate"))
					{
						if (validatedConnect)
						{
							throw new Exception("connection already validated");
						}
						String password = jsonMsg.getString("password");
						String version = jsonMsg.getString("version");
						
						if (!callBackReceiver.isVersionValid(version))
						{
							throw new Exception("invalid version");
						}
						if (!callBackReceiver.isPasswordValid(password))
						{
							throw new Exception("invalid password");
						}
						
						validatedConnect = true;
						callBackReceiver.validConnect();
					}
					else
					{
						if (!validatedConnect)
						{
							throw new Exception("connection not validated");
						}
						if (type.equals("send_sms"))
						{
							String receiver = jsonMsg.getString("receiver");
							String message = jsonMsg.getString("message");
							callBackReceiver.sendSms(receiver, message);
						}
						else
						{
							throw new Exception("invalid msgType");
						}
					}
					builder = new StringBuilder();
				}
				
				Logger.getLogger("blubPhone").info("connection closed");
			}
			
		} catch (Exception ex) 
		{
			ex.printStackTrace();
			error(ex.getMessage());		
		}
		
		try {
			connectionSocket.close();
		} catch (Exception e) 
		{;}
		
		try {
			serverSocket.close();
		} catch (Exception e) 
		{;}

		listening = false;
		connected = false;
		callBackReceiver.connected(false);
		
		broadcast.stop();
		
		Logger.getLogger("blubPhone").info("tcpServer --> finito");
	}
	
	public void error(String err)
	{
		sendError(err);
		callBackReceiver.error(err);
	}
	
	public void sendError(String err)
	{
		try {
			JSONObject errorMessage = new JSONObject();
			errorMessage.put("type", "error");
			errorMessage.put("text", err);
			send(errorMessage.toString() + "\n");
		}
		catch (JSONException e) {
			e.printStackTrace();
		}
	}
	
	public synchronized boolean send(String toSend)
	{
		try {
			outToClient.write(toSend.getBytes());
		} catch (Exception e) {
			e.printStackTrace();
			return false;
		}
		return true;
	}
	
}
