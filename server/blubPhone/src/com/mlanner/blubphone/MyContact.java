package com.mlanner.blubphone;

import org.json.JSONException;
import org.json.JSONObject;

public class MyContact {

	private long id;
	private String phoneNumber;
	private String name;
	
	
	public MyContact(long id, String phoneNumber, String name) {
		super();
		this.id = id;
		this.phoneNumber = phoneNumber;
		this.name = name;
	}


	@Override
	public String toString() {
		return "MyContact [id= " + id + ", phoneNumber=" + phoneNumber + ", name=" + name + "]";
	}
	
	
	public JSONObject toJSONObject()
	{
		try {
			JSONObject result = new JSONObject();
			result.put("type", "contact");
			result.put("id", id);
			result.put("phoneNumber", phoneNumber);
			result.put("name", name);
			
			return result;
		} catch (JSONException e) {
			e.printStackTrace();
		}
		
		return null;
	}
		
	
}
