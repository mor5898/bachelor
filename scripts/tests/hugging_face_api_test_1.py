import requests
from huggingface_hub import InferenceClient

API_URL = "https://api-inference.huggingface.co/models/deepset/roberta-base-squad2"
headers = {"Authorization": "Bearer hf_"}

def query(payload):
	response = requests.post(API_URL, headers=headers, json=payload)
	print(response.json())
	return response.json()
	
# output = query({
# 	"inputs": {
# 	"question": "Give me the SQL Query for all the people who are called 'Max' by first name.",
# 	"context": "You are an data expert and want to help me retrieve data from the following table: CREATE TABLE Persons (PersonID int,LastName varchar(255),FirstName varchar(255),Address varchar(255),City varchar(255));"
# },
# })







client = InferenceClient(
    "meta-llama/Meta-Llama-3-8B-Instruct",
    token="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",
)

# for message in client.chat_completion(
# 	messages=[{"role": "user", "content": "You are an data expert and want to help me retrieve data from the following table: CREATE TABLE Persons (PersonID int,LastName varchar(255),FirstName varchar(255),Address varchar(255),City varchar(255));.Give me the SQL Query for all the people who are called 'Max' by first name."}],
# 	max_tokens=1000,
# 	stream=True,
# ):
#     print(message.choices[0].delta.content, end="")


API_URL = "https://api-inference.huggingface.co/models/unitary/toxic-bert"
headers = {"Authorization": "Bearer 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"}

def query(payload):
	response = requests.post(API_URL, headers=headers, json=payload)
	print(response.json())
	return response.json()
	
output = query({
	"inputs": "I hate you and I will kill you",
})