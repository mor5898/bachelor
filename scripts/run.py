import google.generativeai as genai
import os
from datasets import load_dataset
import csv
import re
import time
from datetime import datetime 

# Configure the Gemini API key
genai.configure(api_key="AIzaSyCRZ7NHAT23Ecth7A2AEC_M4fB1OqdbzNE ")

# Define Gemini model 
model = genai.GenerativeModel('gemini-1.5-flash')

def normalize_query(query):
    # Remove SQL formatting blocks and normalize whitespace
    query = re.sub(r'```sql|```', '', query).strip()
    query = re.sub(r'\s+', ' ', query).lower().strip()
    return query

def save_results_to_csv(results, base_filename, formatted_time): 
    file_path = f"{base_filename}_{formatted_time}.csv"

    with open(file_path, mode='w', newline='') as file:
        writer = csv.writer(file, delimiter='|')
        writer.writerow(['db_id', 'question', 'generated_sql_query', 'gold_sql_query'])
        for result in results:
            writer.writerow([result['db_id'], result['question'], result['generated_sql_query'], result['gold_sql_query']])

def get_sql_query_from_gemini(question, schema, prompt_template):
    prompt = prompt_template.format(schema=schema, question=question)
    response = model.generate_content(prompt)
    return response.text

# Factory for handling dataset-specific logic
class DatasetFactory:
    def __init__(self, dataset_name):
        self.dataset_name = dataset_name
        self.dataset = self.load_dataset()

    def load_dataset(self):
        if self.dataset_name == "spider2-lite":
            return load_dataset("xlangai/spider2-lite")['train']
        elif self.dataset_name == "spider":
            return load_dataset("xlangai/spider")['validation']
        else:
            raise ValueError(f"Unknown dataset: {self.dataset_name}")

    def get_database_schema(self, db_id):
        if self.dataset_name == "spider2-lite":
            schema_file_path = f"./spider2-lite/resource/databases/bigquery/{db_id}/DDL.csv"
        else:
            schema_file_path = f"./spider/database/{db_id}/schema.sql"
        
        if os.path.exists(schema_file_path):
            with open(schema_file_path, 'r', encoding='utf-8') as schema_file:
                schema = schema_file.read()
            return schema
        else:
            print(f"Schema file not found for database {db_id}")
            return None

    def get_gold_query_for_instance(self, example):
        if self.dataset_name == "spider2-lite":
            instance_id = example['instance_id']
            gold_query_file_path = f"./spider2-lite/evaluation_suite/gold/sql/{instance_id}.sql"
            if os.path.exists(gold_query_file_path):
                with open(gold_query_file_path, 'r', encoding='utf-8') as gold_query_file:
                    return normalize_query(gold_query_file.read())
            else:
                print(f"Gold query not found for instance {instance_id}")
                return None
        else:
            return normalize_query(example['query'])

# Main function to run SQL generation
def generate_sql_queries(dataset_name, base_filename, prompt_templates, limit=5):
    factory = DatasetFactory(dataset_name)
    results = []
    current_time = datetime.now()
    formatted_time = current_time.strftime('%Y-%m-%d_%H_%M_%S')

    # Loop through different prompts
    for prompt_template in prompt_templates:    
        # Loop through the dataset examples
        for idx, example in enumerate(factory.dataset):
            if idx >= limit:
                break
            
            db_id = example['db'] if dataset_name == "spider2-lite" else example['db_id']
            question = example['question']
            gold_sql_query = factory.get_gold_query_for_instance(example)

            # Get the schema for the current database
            schema = factory.get_database_schema(db_id)

            # Generate SQL query from the Gemini API
            generated_sql_query = normalize_query(get_sql_query_from_gemini(
                question=question, 
                schema=schema, 
                prompt_template=prompt_template))

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

            save_results_to_csv(
                results=results, 
                base_filename=base_filename, 
                formatted_time=formatted_time)

            time.sleep(15)  # Sleep to avoid API rate limits; value can be adjusted
        break    

if __name__ == "__main__":
    prompt_schemas = [
        "Translate the following question into an SQL query:\nSchema: {schema}\nQuestion: {question}",
        "Please generate an SQL query based on this schema: {schema}, and the question: {question}",
        """Create a valid SQL query for the given schema and question:\n\nSchema:\n{schema}\n\nQuestion:\n{question}""",
        """Generate an SQL query for the given database schema and the user's question. Schema:\n{schema}\n\nQuestion:\n{question}"""
    ]
    # For SPIDER2-lite dataset
    generate_sql_queries(
        dataset_name="spider2-lite",
        base_filename='generated_sql_queries_spider2-lite',
        prompt_templates=prompt_schemas,
        limit=5
    )    
    # For SPIDER dataset
    generate_sql_queries(
        dataset_name="spider",
        base_filename='generated_sql_queries_spider',
        prompt_templates=prompt_schemas,
        limit=5
    )