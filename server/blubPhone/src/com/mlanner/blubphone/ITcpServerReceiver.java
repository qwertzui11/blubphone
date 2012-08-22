package com.mlanner.blubphone;

public interface ITcpServerReceiver {
	public void connected(boolean conn);
	public void validConnect();
	public void sendSms(String receiver, String message);
	public boolean isPasswordValid(String password);
	public boolean isVersionValid(String version);
	public void error(String err);
}
