import json
from datasets import load_dataset

dataset = load_dataset('xlangai/spider', split="validation")

data = dataset

def get_queries_by_db_id(data):
    results = []
    db_dict = {}
    for entry in data:
        db_id = entry.get('db_id')
        question = entry.get('question')
        gold_query = entry.get('query')  
        if question and gold_query:
            if db_id not in db_dict:
                db_dict[db_id] = 0
            if db_dict[db_id] < 3:
                db_dict[db_id] += 1
                results.append({
                    "db_id": db_id,
                    "question": question,
                    "gold_query": gold_query
                })
    return results

queries = get_queries_by_db_id(data)

with open('queries.json', 'w', encoding='utf-8') as f:
    json.dump(queries, f, ensure_ascii=False, indent=4)

for idx, query in enumerate(queries, start=1):
    print(f"Beispiel {idx}:")
    print(f"db_id: {query['db_id']}")
    print(f"Frage: {query['question']}")
    print(f"Gold Query: {query['gold_query']}\n")
