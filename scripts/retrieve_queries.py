import google.generativeai as genai
import os
from datasets import load_dataset
import re
from langchain_community.llms.ollama import Ollama
import time

# Configure the Gemini API key
genai.configure(api_key="AIzaSyCRZ7NHAT23Ecth7A2AEC_M4fB1OqdbzNE ")

# Model config
generation_config = {
  "temperature": 0, # Controls randomness; low value -> deterministic; high value -> more creative
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
    
def normalize_query(query):
    query = re.sub(r'```sql|```', '', query).strip()
    query = re.sub(r'\s+', ' ', query).strip()
    return query

def normalize_query_from_deep_seek(query):
    sql_code_block = re.search(r'```sql(.*?)```', query, re.DOTALL)
    
    if sql_code_block:
        sql_query = sql_code_block.group(1).strip()
    else:
        sql_query = ''
    
    sql_query = re.sub(r'\s+', ' ', sql_query).strip()
    
    return sql_query

def create_eval_files(gen_query, gold_query, db_id, gen_file='gen.txt', gold_file='gold.txt'):
    """
    Creates gen.txt and gold.txt for evaluation based on generated and gold SQL queries.
    
    :param gen_query: generated SQL query
    :param gold_query: gold SQL query
    :param db_id: Database identifier (same for all queries)
    :param gen_file: File name for generated queries (default: gen.txt)
    :param gold_file: File name for gold queries (default: gold.txt)
    """

    # gen
    with open(gen_file, 'a') as gen_f:
        gen_f.write(f"{gen_query.strip()}\n")
    
    # gold
    with open(gold_file, 'a') as gold_f:
        gold_f.write(f"{gold_query.strip()}\t{db_id}\n")

    print(f"Successfully written to files {gen_file} and {gold_file}.")

def get_sql_query_from_gemini(question, schema, prompt_template):
    prompt = prompt_template.format(schema=schema, question=question)
    try:
        response = model.generate_content(prompt)
        #print(f"Raw API Response: {response}")
        print(response)
        if response and hasattr(response, 'text'):
            return response.text
        else:
            print("No text content returned from API.")
            return None
    except Exception as e:
        print(f"Error during query generation: {e}")
        return None

def get_sql_query_from_ollama_deepSeek(schema, question, prompt_template):
    ollama = Ollama(model="deepseek-coder-v2")
    prompt = prompt_template.format(schema=schema, question=question)
    try:
        # Make the request using the Ollama wrapper
        response = ollama.invoke(prompt)
        return response
    except Exception as e:
        print(f"Error querying deepSeek: {e}")
        return None
    
# Factory for handling dataset-specific logic
class DatasetFactory:
    def __init__(self, dataset_name):
        self.dataset_name = dataset_name
        self.dataset = self.load_dataset()

    def load_dataset(self):
        if self.dataset_name == "spider":
            return load_dataset("xlangai/spider")['validation'] # Should be changed!!!
        else:
            raise ValueError(f"Unknown dataset: {self.dataset_name}")

    def get_database_schema(self, db_id):
        schema_file_path = f"./spider/database/{db_id}/schema.sql"
        schema_file_path_alternative = f"./spider/database/{db_id}/{db_id}.sql"

        if os.path.exists(schema_file_path):
            with open(schema_file_path, 'r', encoding='utf-8') as schema_file:
                schema = schema_file.read()
            return schema
        elif os.path.exists(schema_file_path_alternative):
            with open(schema_file_path_alternative, 'r', encoding='utf-8') as schema_file:
                schema = schema_file.read()
            return schema
        else:
            print(f"Schema file not found for database {db_id}")
            return None

    def get_gold_query_for_instance(self, example):
        try:
            return example['query']
        except:
            print(f"Gold query not found for instance {example}")
            return None

# Main function to run SQL generation
def generate_sql_queries(dataset_name, prompt_templates, model, limit=5):
    factory = DatasetFactory(dataset_name)

    # Loop through different prompts
    for prompt_key, prompt_template in prompt_templates:    
        base_filename_gen = f'generated_{prompt_key}_{model}.txt'
        base_filename_gold = f'gold_{prompt_key}_{model}.txt'
        # Loop through the dataset examples
        for idx, example in enumerate(factory.dataset):
            if idx < 444:  
                continue
            if idx >= limit:
                break
            
            db_id = example['db_id']
            question = example['question']
            gold_sql_query = factory.get_gold_query_for_instance(example)

            # Get the schema for the current database
            schema = factory.get_database_schema(db_id)

            # Generate SQL query from model
            if model == 'gemini':
                generated_sql_query = normalize_query(get_sql_query_from_gemini(
                    question=question, 
                    schema=schema, 
                    prompt_template=prompt_template))
            elif model == 'deepseek':
                generated_sql_query = normalize_query_from_deep_seek(get_sql_query_from_ollama_deepSeek(
                    question=question, 
                    schema=schema, 
                    prompt_template=prompt_template))

            print(f"DB ID: {db_id}")
            print(f"Question: {question}")
            print(f"Generated SQL Query: {generated_sql_query}")
            print(f"Gold SQL Query: {gold_sql_query}"),

            create_eval_files(
                gen_query=generated_sql_query,
                gold_query=gold_sql_query,
                db_id=db_id,
                gen_file=base_filename_gen,
                gold_file=base_filename_gold
            )

            print("-" * 40)
            time.sleep(20)  # Sleep to avoid API rate limits; value can be adjusted
        break    

if __name__ == "__main__":
    prompt_schemas = [
#        "Translate the following question into an SQL query:\nSchema: {schema}\nQuestion: {question}",
#        "Please generate an SQL query based on this schema: {schema}, and the question: {question}",
#        """Create a valid SQL query for the given schema and question:\n\nSchema:\n{schema}\n\nQuestion:\n{question}""",
        ["example_prompt_key", """Generate an SQL query for the given database schema and the user's question. Schema:\n{schema}\n\nQuestion:\n{question}"""]
    ]  

    # For SPIDER dataset and Gemini model
    generate_sql_queries(
        dataset_name='spider',
        prompt_templates=prompt_schemas,
        model='gemini',
        limit=1034
    )

    # For SPIDER dataset and deepSeek-Coder-V2 model
    # generate_sql_queries(
    #     dataset_name='spider',
    #     prompt_templates=prompt_schemas,
    #     model='deepseek',
    #     limit=5
    # )