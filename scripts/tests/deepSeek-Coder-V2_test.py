from langchain_community.llms.ollama import Ollama

# Initialize the Ollama instance with the model name
ollama = Ollama(model="deepseek-coder-v2")

# Function to query DeepSeek-Coder-v2 model via Langchain Ollama wrapper
def query_deepseek_coder_v2(prompt):
    try:
        # Make the request using the Ollama wrapper
        response = ollama.invoke(prompt)

        return response
    except Exception as e:
        print(f"Error querying the model: {e}")
        return None

if __name__ == "__main__":
    prompt = "Write an SQL query to retrieve the name and age of all employees from the employees table where age is greater than 30."
    response = query_deepseek_coder_v2(prompt)

    if response:
        print("Model Response:")
        print(response)
