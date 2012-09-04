package com.mlanner.blubphone;

import org.json.JSONException;
import org.json.JSONObject;

public class MySmsMessage {
	private long id;
	private long threadId;
	private String address;
	private long person;
	private long timestamp;
	private long type;
	private String body;
	private boolean read;
	
	
	public MySmsMessage(long id, long threadId, String address, long person, long timestamp,
			long type, String body, boolean read) {
		super();
		this.id = id;
		this.threadId = threadId;
		this.address = address;
		this.person = person;
		this.timestamp = timestamp;
		this.type = type;
		this.body = body;
		this.read = read;
	}
	
	
	@Override
	public String toString() {
		return "MySmsMessage [id=" + id + ", threadId=" + threadId
				+ ", address=" + address + ", person=" + person + ", timestamp=" + timestamp
				+ ", type=" + type + ", body=" + body + ", read=" + read + "]";
	}
	
	
	public JSONObject toJSONObject()
	{
		try {
			JSONObject result = new JSONObject();
			result.put("type", "sms");
			result.put("id", id);
			result.put("threadId", threadId);
			result.put("address", address);
			result.put("person", person);
			result.put("timestamp", timestamp);
			result.put("sms_type", type);
			result.put("read", read);
			result.put("body", body);
		
			return result;
		} catch (JSONException e) {
			e.printStackTrace();
		}
		
		return null;
	}


	public long getId() {
		return id;
	}


	public void setId(long id) {
		this.id = id;
	}


	public long getThreadId() {
		return threadId;
	}


	public void setThreadId(long threadId) {
		this.threadId = threadId;
	}


	public String getAddress() {
		return address;
	}


	public void setAddress(String address) {
		this.address = address;
	}


	public long getPerson() {
		return person;
	}


	public void setPerson(long person) {
		this.person = person;
	}


	public long getTimestamp() {
		return timestamp;
	}


	public void setTimestamp(long timestamp) {
		this.timestamp = timestamp;
	}


	public long getType() {
		return type;
	}


	public void setType(long type) {
		this.type = type;
	}


	public String getBody() {
		return body;
	}


	public void setBody(String body) {
		this.body = body;
	}


	public boolean isRead() {
		return read;
	}


	public void setRead(boolean read) {
		this.read = read;
	}
	
	
	
	
}
