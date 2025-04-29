# main.py
# Sauvegardez ce fichier sous le nom "main.py" dans votre répertoire de projet.
# Pour installer les dépendances :
# pip install fastapi uvicorn pdfminer.six python-multipart

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import io
from pdfminer.high_level import extract_text_to_fp
from pdfminer.layout import LAParams

app = FastAPI(
    title="PDF Text Extractor",
    description="Receive a PDF via POST and return its extracted text in JSON",
    version="1.0.1"  # bumped version
)

# Taille maximale acceptée : 10 Mo
MAX_FILE_SIZE = 10 * 1024 * 1024  # bytes

@app.get("/")
async def root():
    return {"message": "bonjour l'api marche"}

@app.post("/extract-text", response_class=JSONResponse)
async def extract_text(file: UploadFile = File(...)):
    # Vérification du type de fichier
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid file type. Only 'application/pdf' allowed.")

    # Lecture en mémoire
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large. Maximum size is 10 MB.")

    try:
        # Extraction de texte via pdfminer
        output_string = io.StringIO()
        with io.BytesIO(contents) as fp:
            extract_text_to_fp(fp, output_string, laparams=LAParams())
        text = output_string.getvalue()

        # Nettoyage : normalisation des espaces
        cleaned = ' '.join(text.split())

        return {"text": cleaned}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to extract text: {e}")

# Permet de lancer directement l'application avec Python
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
