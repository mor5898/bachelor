from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from datasets import load_dataset
import os
import requests

# os.environ["HF_API_TOKEN"] = "hf_"

# tokenizer = AutoTokenizer.from_pretrained("meta-llama/Meta-Llama-3-8B", use_auth_token=os.environ["HF_API_TOKEN"])
# model = AutoModelForSeq2SeqLM.from_pretrained("meta-llama/Meta-Llama-3-8B", use_auth_token=os.environ["HF_API_TOKEN"])

dataset = load_dataset('spider', split='train')
print(dataset)
# input_text = "Find all the students who scored more than 90 in math."
# inputs = tokenizer(input_text, return_tensors="pt")

# outputs = model.generate(inputs["input_ids"])

# decoded_output = tokenizer.decode(outputs[0], skip_special_tokens=True)
# print(f"Generated SQL Query: {decoded_output}")

headers = {"Authorization": "Bearer hf_"}
API_URL = "https://api-inference.huggingface.co/models/meta-llama/Meta-Llama-3-8B"

def query(payload):
	response = requests.post(API_URL, headers=headers, json=payload)
	print(response.json())
	return response.json()
	
output = query({
	"inputs": "Can you please let us know more details about your ",
})