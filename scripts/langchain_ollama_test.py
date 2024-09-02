from langchain_community.llms.ollama import Ollama
from langchain import LLMChain, PromptTemplate

# Initialize the Ollama model
llm = Ollama(model="llama3.1")  

# Define a prompt template
prompt = PromptTemplate.from_template("Translate the following natural language query to SQL: '{query}'")

# Create an LLMChain with the prompt template and Ollama LLM
chain = LLMChain(llm=llm, prompt=prompt)

# Run the chain with an example input
query = "Get all records where the user is older than 30."
result = chain.run(query=query)

# Print the result
print("Generated SQL:", result)
