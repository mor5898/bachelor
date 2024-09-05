from langchain import LLMChain, PromptTemplate
from langchain.llms import HuggingFaceHub

llm = HuggingFaceHub(
    repo_id="gpt2",  
    huggingfacehub_api_token=""  
)

prompt = PromptTemplate.from_template("Translate the following natural language query to SQL: '{query}'")

chain = LLMChain(llm=llm, prompt=prompt)

query = "Get all records where the user is older than 30."
result = chain.run(query=query)

print("Generated SQL:", result)
