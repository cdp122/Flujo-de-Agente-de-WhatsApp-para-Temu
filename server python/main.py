from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import webbrowser
import pyautogui
import time
import base64
import io
import uvicorn

app = FastAPI()

class Item(BaseModel):
    url: str
    time: int

@app.post("/capturar")
async def capturar_pantalla(item: Item):
    try:
        print(f"Abriendo URL: {item.url}")
        
        # 1. Abrir el navegador predeterminado (Opera con tus cookies)
        webbrowser.open(item.url)
        
        # 2. Esperar a que cargue (ajusta el tiempo si tu internet es lento)
        time.sleep(item.time) 
        
        # 3. Tomar captura de pantalla
        # Si tienes varios monitores, captura el principal
        screenshot = pyautogui.screenshot()
        
        # 4. Cerrar la pestaña (Opcional - CTRL+W funciona en la mayoría de navegadores)
        # pyautogui.hotkey('ctrl', 'w') 
        
        # 5. Convertir imagen a Base64 para enviarla a n8n
        buffered = io.BytesIO()
        screenshot.save(buffered, format="JPEG", quality=70)
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return {"status": "success", "image_base64": img_str}
        
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    # Escucha en el puerto 8000 de tu red local
    # 0.0.0.0 permite que Docker se conecte a tu PC
    uvicorn.run(app, host="0.0.0.0", port=8000)