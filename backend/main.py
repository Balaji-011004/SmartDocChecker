# Document analysis endpoint
from fastapi import UploadFile, File
from typing import List
import time,chardet


import uvicorn
from fastapi import FastAPI, WebSocket, Depends, HTTPException, status, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import logging
from ai_engine import detect_contradiction, semantic_similarity, extract_entities, get_entity_embedding, extract_sentences, get_sentence_containing
from sentence_transformers import util


app = FastAPI(title="SmartDocChecker API", description="Enterprise-grade contradiction detection API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# JWT Auth
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

class User(BaseModel):
    username: str
    role: str

class Document(BaseModel):
    id: str
    name: str
    status: str
    upload_date: str
    contradictions: List[str]

class Contradiction(BaseModel):
    id: str
    type: str
    description: str
    confidence: float
    document_id: str

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # Replace with real user validation
    if form_data.username == "admin" and form_data.password == "admin":
        return {"access_token": "admin-token", "token_type": "bearer", "role": "admin"}
    elif form_data.username == "user" and form_data.password == "user":
        return {"access_token": "user-token", "token_type": "bearer", "role": "user"}
    else:
        raise HTTPException(status_code=400, detail="Invalid credentials")

@app.get("/users/me", response_model=User)
async def get_me(token: str = Depends(oauth2_scheme)):
    # Replace with real token decoding
    if token == "admin-token":
        return User(username="admin", role="admin")
    elif token == "user-token":
        return User(username="user", role="user")
    raise HTTPException(status_code=401, detail="Invalid token")

@app.post("/documents/upload")
async def upload_document(file: UploadFile = File(...), token: str = Depends(oauth2_scheme)):
    # Save file and process
    logger.info(f"Received file: {file.filename}")
    return {"id": "doc1", "name": file.filename, "status": "pending", "upload_date": "2025-09-21", "contradictions": []}

@app.get("/documents", response_model=List[Document])
async def list_documents(token: str = Depends(oauth2_scheme)):
    # Return mock documents
    return [Document(id="doc1", name="Sample.pdf", status="completed", upload_date="2025-09-21", contradictions=["c1"])]

@app.get("/contradictions", response_model=List[Contradiction])
async def list_contradictions(token: str = Depends(oauth2_scheme)):
    # Return mock contradictions
    return [Contradiction(id="c1", type="temporal", description="Date mismatch", confidence=0.98, document_id="doc1")]

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text("Processing started...")
    await websocket.send_text("Processing completed!")
    await websocket.close()

@app.post("/api/analyze")
async def analyze(files: list[UploadFile] = File(...)):
    texts = []
    file_names = []
    for file in files:
        content = await file.read()
        detected = chardet.detect(content)
        encoding = detected['encoding']
        try:
            if encoding:
                text = content.decode(encoding)
            else:
                text = content.decode('utf-8', errors='ignore')
        except UnicodeDecodeError:
            text = content.decode('utf-8', errors='replace')
        texts.append(text)
        file_names.append(file.filename)

    contradictions = []
    num_contradictions = 0
    total_confidence = 0.0
    for i in range(len(texts)):
        for j in range(i + 1, len(texts)):
            # Detect contradiction score and similarity
            contradiction_score = detect_contradiction(texts[i], texts[j])
            similarity_score = semantic_similarity(texts[i], texts[j])
            # Extract entities for both docs
            entities_doc1 = extract_entities(texts[i])  # List of (entity_text, entity_type)
            entities_doc2 = extract_entities(texts[j])

            # Extract sentences from texts (replace with your NLP sentence splitter)
            sentences_doc1 = extract_sentences(texts[i])  # List of sentence strings
            sentences_doc2 = extract_sentences(texts[j])

            # Find contradiction pairs between entities of the same type
            contradiction_pairs = []
            threshold = 0.7  # similarity threshold for matching

            for ent1_text, ent1_type in entities_doc1:
                emb1 = get_entity_embedding(ent1_text)
                sent1 = get_sentence_containing(ent1_text, sentences_doc1)
                for ent2_text, ent2_type in entities_doc2:
                    if ent1_type == ent2_type:
                        emb2 = get_entity_embedding(ent2_text)
                        sent2 = get_sentence_containing(ent2_text, sentences_doc2)
                        similarity = util.pytorch_cos_sim(emb1, emb2).item()
                        if similarity > threshold and ent1_text != ent2_text:

                            # Calculate contradiction score for sentences
                            sent_contradiction_score = detect_contradiction(sent1, sent2)

                            contradiction_pairs.append({
                                'entity_doc1': (ent1_text, ent1_type),
                                'sentence_doc1': sent1,
                                'entity_doc2': (ent2_text, ent2_type),
                                'sentence_doc2': sent2,
                                'similarity': similarity,
                                'sentence_contradiction_score': sent_contradiction_score,
                                'explanation': f"Contradiction between '{ent1_text}' and '{ent2_text}'."
                            })
                            num_contradictions += 1
                            total_confidence += sent_contradiction_score
            
            contradictions.append({
                'doc_pair': (i, j),
                'docs_contradiction_score': contradiction_score,
                'docs_similarity_score': similarity_score,
                'contradiction_pairs': contradiction_pairs
            })
    contradictions.append({'totalContradictions': num_contradictions,
                        'averageConfidence': (total_confidence / num_contradictions) if num_contradictions > 0 else 0.0
                          })
    
    # print(f"Total contradictions found: {len(contradictions)}")
    # print(f"Contradictions details: {contradictions}")

    return contradictions
