import os
import chainlit as cl
from dotenv import load_dotenv
from openai import AzureOpenAI
import requests
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import json

# Extracting prompts
with open("prompt.txt", "r") as f:
    system_prompt = f.read()

with open("summarize.txt", "r") as f1:
    summ_prompt = f1.read()

# Importing keys
load_dotenv()
endpoint = os.getenv("ENDPOINT_URL")
deployment = os.getenv("DEPLOYMENT_NAME")
api_key = os.getenv("AZURE_OPENAI_API_KEY")

SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
SEARCH_API_KEY = os.getenv("AZURE_SEARCH_API_KEY")
index_name_1 = os.getenv("AZURE_SEARCH_INDEX_NAME_1")
index_name_2 = os.getenv("AZURE_SEARCH_INDEX_NAME_2")
index_name_3 = os.getenv("AZURE_SEARCH_INDEX_NAME_3")

EMBEDDINGEP = os.getenv("EMBEDDING_EP")
empkey = os.getenv("KEY")

# Check for missing keys
if not endpoint or not deployment or not api_key:
    print("Missing keys!!! Try again")

# Set deployment model and initialize the Azure client
client = AzureOpenAI(
    azure_endpoint=endpoint,
    api_key=api_key,
    api_version="2025-01-01-preview",
)
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {empkey}"
}

# Function for embedding
def embedder(text: str):
    data = {
        "input": [text]
    }
    response = requests.post(
        EMBEDDINGEP,
        headers=headers,
        json=data
    )
    return response.json()['data'][0]['embedding']


# Breaking into chunks
def chunker(ip, chunk_size=1500):
    """Break the content into smaller chunks of defined size."""
    chunks = []
    for i in range(0, len(ip), chunk_size):
        chunks.append(ip[i:i + chunk_size])
    return chunks


# Vector search
def vector_search(query_embedding, embeddings):
    similarities = []
    # Compare query embedding with document embeddings
    for embed, chunk, act_name in embeddings:
        similarity_score = cosine_similarity([query_embedding], [embed])[0][0]
        similarities.append((similarity_score, chunk, act_name))
    
    # Sort by similarity score (highest first)
    similarities.sort(reverse=True, key=lambda x: x[0])
    
    # Return the most similar result
    return similarities[0]


# Keyword search
def keyword_search():
    """Search through the indexes and summarize content based on a query."""
    embedding_1 = []
    embedding_2 = []
    embedding_3 = []

    search_client_1 = SearchClient(SEARCH_ENDPOINT, index_name_1, AzureKeyCredential(SEARCH_API_KEY))
    search_client_2 = SearchClient(SEARCH_ENDPOINT, index_name_2, AzureKeyCredential(SEARCH_API_KEY))
    search_client_3 = SearchClient(SEARCH_ENDPOINT, index_name_3, AzureKeyCredential(SEARCH_API_KEY))
    query = "Under what can someone be punished for discrimination against the SC/ST community?"
        
    # Query index 1
    results_1 = search_client_1.search(
        search_text=query,
        top=1,
        select=['Act_name', 'Description', 'content', 'keyphrases']
    )
    
    for r1 in results_1:
        chunks = chunker(r1['content'])
        for c in chunks:
            embed = embedder(c)
            embedding_1.append((embed, c, r1['Act_name']))
        
        
    # Query index 2
    results_2 = search_client_2.search(
        search_text=query,
        top=1,
        select=['Act_name', 'Description', 'content', 'keyphrases']
    )

    for r2 in results_2:
        chunks = chunker(r2['content'])
        for c in chunks:
            embed = embedder(c)
            embedding_2.append((embed, c, r2['Act_name'])) 

    # Query index 3
    results_3 = search_client_3.search(
        search_text=query,
        top=2,
        select=['Act_name', 'Year', 'Description', 'content', 'keyphrases']
    )
    for r3 in results_3:
        chunks = chunker(r3['content'])
        for c in chunks:
            embed = embedder(c)
            embedding_3.append((embed, c, r3['Act_name']))

    # Combine all embeddings
    final_embedding = embedding_1 + embedding_2 + embedding_3
    final_query = embedder(query)

    # Perform vector search
    best_match = vector_search(final_query, final_embedding)

    # Prepare the context to send to the model
    ct = best_match[1]  # This would be the chunk of text that is most similar to the query

    # Send query and context to OpenAI for completion
    completion = client.chat.completions.create(
        model=deployment,
        messages=[
            {"role": "system", "content": system_prompt},
            {'role': "user", 
             'content': f"Here is some context that will help you provide the answer: Extracted Content{ct}. The question is:User Question {query}"
            }
        ],
    )
    
    # Print the response from OpenAI
    response = completion.choices[0].message.content
    print(response)

# Call the function
keyword_search()
