# main.py
# Pour installer les dépendances :
# pip install fastapi uvicorn pdfminer.six python-multipart

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import base64
import io
from pdfminer.high_level import extract_text_to_fp
from pdfminer.layout import LAParams

# Initialiser l'application FastAPI
app = FastAPI(
    title="PDF Text Extractor",
    description="API pour extraire du texte à partir de fichiers PDF envoyés en fichier ou en base64.",
    version="2.0.0"
)

# Taille maximale acceptée : 10 Mo
MAX_FILE_SIZE = 10 * 1024 * 1024  # bytes

# Modèle pour réceptionner un fichier encodé en base64
class PDFBase64Request(BaseModel):
    file_base64: str

@app.get("/")
async def root():
    return {"message": "Bienvenue ! L'API fonctionne correctement."}

@app.post("/extract-text", response_class=JSONResponse)
async def extract_text(file: UploadFile = File(...)):
    """
    Extraction de texte depuis un fichier PDF uploadé en multipart/form-data.
    """
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Type de fichier invalide. Seuls les PDF sont autorisés.")
    
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
async def extract_text_base64(request: PDFBase64Request):
    """
    Extraction de texte depuis un PDF encodé en base64 envoyé via JSON.
    """
    try:
        contents = base64.b64decode(request.file_base64)

        if len(contents) > MAX_FILE_SIZE:
            raise HTTPException(status_code=413, detail="Fichier trop volumineux. Maximum autorisé : 10 Mo.")
        
        output_string = io.StringIO()
        with io.BytesIO(contents) as fp:
            extract_text_to_fp(fp, output_string, laparams=LAParams())
        text = output_string.getvalue()
        cleaned_text = ' '.join(text.split())
        return {"text": cleaned_text}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'extraction : {str(e)}")

# Pour lancer l'application directement
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=10000, reload=True)
