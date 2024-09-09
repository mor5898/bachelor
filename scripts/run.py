import google.generativeai as genai
import os
from datasets import load_dataset
import csv
import re
import time
from datetime import datetime 
import sqlite3
from google.cloud import bigquery

# Big Query credentials for SPIDER2-lite
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./spider2-lite/credentials/bigquery_credential.json"

# Configure the Gemini API key
genai.configure(api_key="AIzaSyCRZ7NHAT23Ecth7A2AEC_M4fB1OqdbzNE ")

# Model config
generation_config = {
  "temperature": 1, # Controls randomness; low value -> deterministic; high value -> more creative
  "top_p": 0.95, # Impements nucleus sampling
  "top_k": 64, # Tokens are taken from the top k most probable tokens -> K-Nearest Neighbour
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain", # JSON?
}

# Define Gemini model 
model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    generation_config=generation_config
    # Safety settings could be set here
)

# SQLite Query Executor for SPIDER dataset
def execute_sqlite_query(db_id, query):
    db_path = f"./spider/database/{db_id}/{db_id}.sqlite"
    
    if not os.path.exists(db_path):
        print(f"SQLite database file not found for {db_id}")
        return None
    
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        return None

# BigQuery Query Executor for SPIDER2-lite dataset
def execute_bigquery_query(query, project_id):
    client = bigquery.Client(project=project_id)
    
    try:
        query_job = client.query(query)
        results = query_job.result()  # Wait for query to finish
        return [row for row in results]
    except Exception as e:
        print(f"BigQuery error: {e}")
        return None
    
def normalize_query(query):
    # Remove SQL formatting blocks and normalize whitespace
    query = re.sub(r'```sql|```', '', query).strip()
    query = re.sub(r'\s+', ' ', query).lower().strip()
    return query

def save_results_to_csv(results, base_filename, formatted_time): 
    file_path = f"{base_filename}_{formatted_time}.csv"

    with open(file_path, mode='w', newline='') as file:
        writer = csv.writer(file, delimiter='|')
        writer.writerow(['db_id', 'question', 'generated_sql_query', 'gold_sql_query', 'result'])
        for result in results:
            writer.writerow([result['db_id'], result['question'], result['generated_sql_query'], result['gold_sql_query'], result['execution_result']])

def get_sql_query_from_gemini(question, schema, prompt_template):
    prompt = prompt_template.format(schema=schema, question=question)
    try:
        response = model.generate_content(prompt)
        #print(f"Raw API Response: {response}")
        if response and hasattr(response, 'text'):
            return response.text
        else:
            print("No text content returned from API.")
            return None
    except Exception as e:
        print(f"Error during query generation: {e}")
        return None


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

            if dataset_name == 'spider2-lite':
                execution_result = execute_bigquery_query(generated_sql_query, project_id="vital-reef-433920-s5")
            else:
                execution_result = execute_sqlite_query(db_id, generated_sql_query)

            # Store the result (including the original question and gold query for comparison)
            results.append({
                'db_id': db_id,
                'question': question,
                'generated_sql_query': generated_sql_query,
                'gold_sql_query': gold_sql_query,
                'execution_result': execution_result
            })

            print(f"DB ID: {db_id}")
            print(f"Question: {question}")
            print(f"Generated SQL Query: {generated_sql_query}")
            print(f"Gold SQL Query: {gold_sql_query}"),
            print(f"Resulting data: {execution_result}")
            print("-" * 40)

            save_results_to_csv(
                results=results, 
                base_filename=base_filename, 
                formatted_time=formatted_time)

            time.sleep(30)  # Sleep to avoid API rate limits; value can be adjusted
        break    

if __name__ == "__main__":
    prompt_schemas = [
#        "Translate the following question into an SQL query:\nSchema: {schema}\nQuestion: {question}",
#        "Please generate an SQL query based on this schema: {schema}, and the question: {question}",
#        """Create a valid SQL query for the given schema and question:\n\nSchema:\n{schema}\n\nQuestion:\n{question}""",
        """Generate an SQL query for the given database schema and the user's question. Schema:\n{schema}\n\nQuestion:\n{question}"""
    ]

    # For SPIDER2-lite dataset
    generate_sql_queries(
        dataset_name="spider2-lite",
        base_filename='generated_sql_queries_spider2-lite',
        prompt_templates=prompt_schemas,
        limit=2
    )    

    # For SPIDER dataset
    generate_sql_queries(
        dataset_name="spider",
        base_filename='generated_sql_queries_spider',
        prompt_templates=prompt_schemas,
        limit=2
    )