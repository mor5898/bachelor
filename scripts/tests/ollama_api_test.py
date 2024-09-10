import requests
import json

# Function to interact with DeepSeek-Coder-v2 model via Ollama API
def query_deepseek_coder_v2(prompt):
    url = "http://localhost:11434/api/generate"  # Ollama runs locally on port 11434 by default

    payload = {
        "model": "deepseek-coder-v2",  
        "prompt": prompt
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
      #  print(response.text)
        if response.status_code == 200:
            full_response = ""

            # Process each line of the response text -> line = 1 token
            for line in response.text.splitlines():
                try:
                    response_data = json.loads(line)
                    full_response += response_data.get('response', '')
                except json.JSONDecodeError as e:
                    print(f"Error parsing line: {e}, content: {line}")

            return full_response
        else:
            print(f"Error: Got status code {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None

if __name__ == "__main__":
    prompt = "Write an SQL query to retrieve the name and age of all employees from the employees table where age is greater than 30."
    response = query_deepseek_coder_v2(prompt)

    if response:
        print("Model Response:")
        print(response)