import google.generativeai as genai
import os
from datasets import load_dataset
import csv
import re

genai.configure(api_key="AIzaSyCRZ7NHAT23Ecth7A2AEC_M4fB1OqdbzNE ")

# Load the SPIDER dataset
dataset = load_dataset("xlangai/spider2-lite")

print(dataset['train']) # Only split 

columns = dataset['train'].column_names
print("Column names:", columns)

for i in range(3):  # Change the range to print more or fewer examples
    example = dataset['train'][i]
    print(f"\nExample {i+1}:")
    for column in columns:
        print(f"{column}: {example[column]}")