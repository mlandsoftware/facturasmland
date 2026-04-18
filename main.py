from fastapi import FastAPI, UploadFile, File
import uvicorn
from procesador import procesar_factura_pdf

app = FastAPI(title="Extractor SRI Ecuador")

@app.get("/")
def home():
    return {"status": "Servidor en línea"}

@app.post("/procesar")
async def api_procesar_factura(file: UploadFile = File(...)):
    contenido = await file.read()
    datos = procesar_factura_pdf(contenido)
    return {"datos": datos}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)