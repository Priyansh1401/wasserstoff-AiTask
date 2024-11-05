from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import torch
from sentence_transformers import SentenceTransformer
from transformers import AutoModelForCausalLM, AutoTokenizer
import faiss
import numpy as np
from typing import List, Dict, Optional
import logging
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="RAG Chatbot API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize models
try:
    sentence_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-base")
    model = AutoModelForCausalLM.from_pretrained("google/flan-t5-base")
except Exception as e:
    logger.error(f"Error loading models: {str(e)}")
    raise

# Initialize FAISS index
vector_dimension = 384  # Matches the sentence-transformer model's output dimension
index = faiss.IndexFlatL2(vector_dimension)

# In-memory storage for content (in production, use a proper database)
content_store = {}

class Content(BaseModel):
    id: str
    text: str
    metadata: Optional[Dict] = None

class Query(BaseModel):
    text: str
    context: Optional[List[str]] = None

class ChatResponse(BaseModel):
    response: str
    thought_process: List[str]
    relevant_sources: List[str]

def generate_embedding(text: str) -> np.ndarray:
    """Generate embeddings for given text."""
    try:
        embedding = sentence_model.encode([text])[0]
        return embedding
    except Exception as e:
        logger.error(f"Error generating embedding: {str(e)}")
        raise

def chain_of_thought_reasoning(query: str, relevant_content: List[str], context: List[str] = None) -> List[str]:
    thoughts = [
        f"1. Received query: '{query}'",
        "2. Retrieved relevant content based on query embedding",
        "3. Analyzing content to find common themes and extract key information",
        "4. Formulating a detailed response considering the logical sequence"
    ]
    # Add additional custom logic to analyze retrieved content here
    return thoughts


@app.post("/content")
async def add_content(content: Content):
    """Add new content to the vector database."""
    try:
        embedding = generate_embedding(content.text)
        index.add(np.array([embedding]).astype('float32'))
        content_store[content.id] = {
            "text": content.text,
            "metadata": content.metadata
        }
        return {"status": "success", "message": "Content added successfully"}
    except Exception as e:
        logger.error(f"Error adding content: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query")
async def process_query(query: Query) -> ChatResponse:
    """Process a query and return a response using RAG and Chain of Thought."""
    try:
        # Generate query embedding
        query_embedding = generate_embedding(query.text)
        
        # Search for relevant content
        k = 3  # Number of relevant documents to retrieve
        D, I = index.search(np.array([query_embedding]).astype('float32'), k)
        
        # Retrieve relevant content
        relevant_content = []
        relevant_sources = []
        for idx in I[0]:
            if idx < len(content_store):
                content_id = list(content_store.keys())[idx]
                relevant_content.append(content_store[content_id]["text"])
                relevant_sources.append(content_id)
        
        # Generate chain of thought reasoning
        thought_process = chain_of_thought_reasoning(
            query.text,
            relevant_content,
            query.context
        )
        
        # Generate response using the language model
        context_text = " ".join(relevant_content)
        input_text = f"Context: {context_text}\nQuestion: {query.text}\nAnswer:"
        
        inputs = tokenizer(input_text, return_tensors="pt", max_length=512, truncation=True)
        outputs = model.generate(
            inputs.input_ids,
            max_length=150,
            num_beams=4,
            temperature=0.7,
            no_repeat_ngram_size=2
        )
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        return ChatResponse(
            response=response,
            thought_process=thought_process,
            relevant_sources=relevant_sources
        )
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)