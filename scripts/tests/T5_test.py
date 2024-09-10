import requests

API_URL = "https://api-inference.huggingface.co/models/OMazzuzi90/Ita2Sql"
headers = {"Authorization": "Bearer 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"}

def query(payload):
	response = requests.post(API_URL, headers=headers, json=payload)
	return response.json()
	
output = query({
	"inputs": "Write an SQL query to find the total number of singers in the singer table.", 
	"options": {"wait_for_model": True},
	"max_time": 120.0
}) # more parameters can be set here

print(output)