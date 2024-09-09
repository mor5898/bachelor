import google.generativeai as genai
import os
from datasets import load_dataset
import csv
import re
import time

genai.configure(api_key="AIzaSyCRZ7NHAT23Ecth7A2AEC_M4fB1OqdbzNE ")

# Load SPIDER dataset
dataset = load_dataset("xlangai/spider")

# Define Gemini model 
model = genai.GenerativeModel('gemini-1.5-flash')

def get_sql_query_from_gemini(question, schema):
    # Prompt schema
    prompt = f"Translate the following question into an SQL query:\n\nSchema: {schema}\n\nQuestion: {question}"
    
    # Send request to Gemini API
    response = model.generate_content(prompt)
    
    return response.text

# Function to normalize and clean SQL queries
def normalize_query(query):
    # Strip backticks or any special formatting (like ```sql blocks)
    query = re.sub(r'```sql|```', '', query).strip()
    
    # Replace multiple spaces, newlines, and tabs with a single space
    query = re.sub(r'\s+', ' ', query).lower().strip()
    
    return query

def save_results_to_csv(results, file_path='generated_sql_queries_spider.csv'):
    with open(file_path, mode='w', newline='') as file:
        writer = csv.writer(file, delimiter='|')
        writer.writerow(['db_id', 'question', 'generated_sql_query', 'gold_sql_query'])
        for result in results:
            writer.writerow([result['db_id'], result['question'], result['generated_sql_query'], result['gold_sql_query']])

def get_database_schema(db_id):
    schema_file_path = f"./spider/database/{db_id}/schema.sql"
    
    if os.path.exists(schema_file_path):
        with open(schema_file_path, 'r', encoding='utf-8') as schema_file:
            schema = schema_file.read()
        return schema
    else:
        print(f"Schema file not found for database {db_id}")
        return None

# Main function to iterate over the SPIDER dataset and generate SQL queries
def generate_sql_queries():
    results = []
    
    # Loop through each example in the validation set
    for idx, example in enumerate(dataset['validation']):
        if idx >= 250:  # Stop after the first five examples
            break
        db_id = example['db_id']
        question = example['question']
        gold_sql_query = normalize_query(example['query'])

        # Get the schema for the current database
        schema = get_database_schema(db_id)

        # Get the generated SQL query from the Gemini API
        generated_sql_query = normalize_query(get_sql_query_from_gemini(question, schema))
        
        # Store the result (including the original question and gold query for comparison)
        results.append({
            'db_id': db_id,
            'question': question,
            'generated_sql_query': generated_sql_query,
            'gold_sql_query': gold_sql_query
        })

        print(f"DB ID: {db_id}")
        print(f"Question: {question}")
        print(f"Generated SQL Query: {generated_sql_query}")
        print(f"Gold SQL Query: {gold_sql_query}")
        print("-" * 40)

        save_results_to_csv(results)

        time.sleep(15)

if __name__ == "__main__":
    generate_sql_queries()
