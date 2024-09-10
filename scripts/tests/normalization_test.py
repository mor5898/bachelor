import re

def normalize_query(query):
    """
    Normalize the SQL query by removing unwanted text and extracting the actual SQL code.
    
    Args:
        query (str): The raw query string containing unwanted text and formatting blocks.
        
    Returns:
        str: The normalized SQL query.
    """
    # Extract SQL code block from the text
    sql_code_block = re.search(r'```sql(.*?)```', query, re.DOTALL)
    
    if sql_code_block:
        sql_query = sql_code_block.group(1).strip()
    else:
        # If no SQL code block is found, return an empty string or handle as needed
        sql_query = ''
    
    # Normalize whitespace in the extracted SQL query
    sql_query = re.sub(r'\s+', ' ', sql_query).strip()
    
    return sql_query

if __name__ == "__main__":
    query = """
    To find the total number of singers in the database, you can use a simple SQL query to count the unique entries in the `singer` table. Here's how you can do it:    

    ```sql
    SELECT COUNT(*) AS Total_Singers FROM singer;
    ```

    This query counts all rows in the `singer` table, which represents the total number of singers based on the data inserted into the table so far.
    """
    print(normalize_query(query))