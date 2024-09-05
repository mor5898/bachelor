import google.generativeai as genai
import os

genai.configure(api_key="")

model = genai.GenerativeModel('gemini-1.5-flash')

response = model.generate_content("Write a story about an AI and magic")
print(response.text)
