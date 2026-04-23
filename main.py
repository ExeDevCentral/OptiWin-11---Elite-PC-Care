from fastapi import FastAPI, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from system_manager import SystemManager
import uvicorn
import os
import random

app = FastAPI(title="OptiWin 11 API")
manager = SystemManager()

# Servir archivos estáticos
app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/")
async def read_index():
    return FileResponse("frontend/index.html")

@app.get("/api/stats")
async def get_stats():
    return manager.get_system_stats()

@app.get("/api/hardware")
async def get_hardware():
    return manager.get_hardware_info()

@app.post("/api/clean")
async def clean_junk(background_tasks: BackgroundTasks):
    # En un entorno real esto sería asíncrono
    return manager.clean_junk()

@app.post("/api/repair")
async def repair_system(background_tasks: BackgroundTasks):
    background_tasks.add_task(manager.run_repair)
    return {"status": "Reparación iniciada en segundo plano"}

@app.post("/api/update")
async def update_all(background_tasks: BackgroundTasks):
    background_tasks.add_task(manager.update_everything)
    return {"status": "Actualización universal iniciada"}

@app.post("/api/debloat")
async def debloat(background_tasks: BackgroundTasks):
    background_tasks.add_task(manager.apply_debloat)
    return {"status": "Optimización de aplicaciones iniciada"}

@app.post("/api/turbo")
async def turbo_mode():
    return manager.set_turbo_mode()

@app.get("/api/ads")
async def get_ads():
    ads = [
        {"text": "¡Obtén OptiWin Ultra Pro para soporte 24/7!", "link": "#"},
        {"text": "Tu PC merece lo mejor. Descarga nuestras herramientas de red.", "link": "#"},
        {"text": "Publicidad: Los mejores servidores dedicados aquí.", "link": "#"}
    ]
    return random.choice(ads)

@app.post("/api/full_optimization")
async def full_optimization(background_tasks: BackgroundTasks):
    # 1. Limpieza inmediata (retorna resultados)
    clean_results = manager.clean_junk()
    
    # 2. Modo Turbo inmediato
    manager.set_turbo_mode()
    
    # 3. Tareas pesadas en segundo plano
    background_tasks.add_task(manager.run_repair)
    background_tasks.add_task(manager.apply_debloat)
    background_tasks.add_task(manager.update_everything)
    
    return {
        "status": "¡Optimización Total Iniciada!",
        "details": clean_results.get("results", []),
        "background": "Reparación, Debloat y Actualizaciones ejecutándose en segundo plano."
    }

if __name__ == "__main__":
    import sys
    import ctypes
    
    def is_admin():
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    if not is_admin():
        # Solicitar permisos de administrador y cerrar este proceso
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()
        
    uvicorn.run(app, host="127.0.0.1", port=8000)
