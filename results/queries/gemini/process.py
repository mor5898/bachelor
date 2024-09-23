import re

def process_sql_query(query):
    # Regex to find SELECT part of the query
    select_regex = re.compile(r"SELECT(.*?)FROM", re.DOTALL | re.IGNORECASE)
    select_match = select_regex.search(query)

    if not select_match:
        return query  # If there's no SELECT part, return the query as is

    # Extract the SELECT clause and process it
    select_clause = select_match.group(1)
    
    # Find all column aliases (anything after 'AS <alias>')
    alias_regex = re.compile(r"\s+AS\s+(\w+)", re.IGNORECASE)
    aliases = alias_regex.findall(select_clause)

    # Remove 'AS <alias>' from the SELECT clause
    select_clause_processed = alias_regex.sub('', select_clause)

    # Replace column aliases in other parts of the query
    processed_query = query.replace(select_match.group(1), select_clause_processed)

    # Now replace any aliases used elsewhere (like in ORDER BY, WHERE)
    for alias in aliases:
        # Use a word boundary '\b' to ensure we're replacing the exact alias
        processed_query = re.sub(rf"\b{alias}\b", select_clause_processed.strip(), processed_query)

    return processed_query.strip()

def process_sql_file(input_file, output_file):
    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
        for line in infile:
            processed_query = process_sql_query(line.strip())
            outfile.write(processed_query + '\n')

if __name__ == '__main__':
    input_file = 'results/queries/gemini/test.txt'
    output_file = 'processed_sql_queries.txt'
    
    process_sql_file(input_file, output_file)