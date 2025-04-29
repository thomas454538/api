# main.py
# Installer les dépendances avec :
# pip install fastapi uvicorn pdfminer.six python-multipart

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
import base64
import io
from pdfminer.high_level import extract_text_to_fp
from pdfminer.layout import LAParams
from pydantic import BaseModel

class PDFPayload(BaseModel):
    contentBytes: str
    name: str = None

# Initialiser l'application
app = FastAPI(
    title="PDF Text Extractor (adapté)",
    description="Extrait du texte d'un PDF envoyé en multipart/form-data base64.",
    version="2.1.0"
)

# Taille maximale acceptée : 10 Mo
MAX_FILE_SIZE = 10 * 1024 * 1024  # bytes

@app.get("/")
async def root():
    return {"message": "Bienvenue, l'API fonctionne correctement !"}

@app.post("/extract-text", response_class=JSONResponse)
async def extract_text(file: UploadFile = File(...)):
    """
    Extraction de texte depuis un fichier PDF uploadé en fichier classique.
    """
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Type de fichier invalide. Seuls les PDF sont acceptés.")
    
    contents = await file.read()

    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="Fichier trop volumineux. Maximum autorisé : 10 Mo.")

    try:
        output_string = io.StringIO()
        with io.BytesIO(contents) as fp:
            extract_text_to_fp(fp, output_string, laparams=LAParams())
        text = output_string.getvalue()
        cleaned_text = ' '.join(text.split())
        return {"text": cleaned_text}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'extraction : {str(e)}")

@app.post("/extract-text-base64", response_class=JSONResponse)
async def extract_text_base64(payload: PDFPayload):
    """
    Extraction de texte depuis un contenu base64 envoyé en JSON.
    """
    try:
        contents = base64.b64decode(payload.contentBytes)

        if len(contents) > MAX_FILE_SIZE:
            raise HTTPException(status_code=413, detail="Fichier trop volumineux. Maximum autorisé : 10 Mo.")
        
        output_string = io.StringIO()
        with io.BytesIO(contents) as fp:
            extract_text_to_fp(fp, output_string, laparams=LAParams())
        text = output_string.getvalue()
        cleaned_text = ' '.join(text.split())
        
        return {"filename": payload.name, "text": cleaned_text}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'extraction : {str(e)}")
