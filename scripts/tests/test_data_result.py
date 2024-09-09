import sqlite3
from google.cloud import bigquery
import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./spider2-lite/credentials/bigquery_credential.json"

# SQLite Query Executor for SPIDER dataset
def execute_sqlite_query(db_id, query):
    db_path = f"./spider/database/{db_id}/{db_id}.sqlite"
    
    if not os.path.exists(db_path):
        print(f"SQLite database file not found for {db_id}")
        return None
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        conn.close()
        return results
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        return None

# BigQuery Query Executor for SPIDER2-lite dataset
def execute_bigquery_query(db_id, query, project_id):
    client = bigquery.Client(project=project_id)
    
    try:
        query_job = client.query(query)
        results = query_job.result()  # Wait for query to finish
        return [row for row in results]
    except Exception as e:
        print(f"BigQuery error: {e}")
        return None

# Testing execution function
if __name__ == "__main__":
    spider_db_id = "concert_singer"  
    spider_query = "SELECT name , country ,  age FROM singer ORDER BY age DESC;"
    sqlite_results = execute_sqlite_query(spider_db_id, spider_query)
    if sqlite_results:
        print("SQLite Results:", sqlite_results)
    else:
        print("ERROR!!!!!!!!!!!!!!!!!!!!!!")

    #Test BigQuery query execution for SPIDER2-lite dataset
    spider2lite_db_id = "bigquery-public-data"  
    spider2lite_query = """
    with lines as ( select split(content, '\\n') as line, id from `bigquery-public-data.github_repos.sample_contents` where sample_path like "%.sql" ) select indentation, count(indentation) as number_of_occurence from ( select case when min(char_length(regexp_extract(flatten_line, r"\s+$")))>=1 then 'trailing' when min(char_length(regexp_extract(flatten_line, r"^ +")))>=1 then 'space' else 'other' end as indentation from lines cross join unnest(lines.line) as flatten_line group by id) group by indentation order by number_of_occurence desc
    """  
    bigquery_results = execute_bigquery_query(spider2lite_db_id, spider2lite_query, project_id="corded-fragment-411603")
    print("BigQuery Results:", bigquery_results)
