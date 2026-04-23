import os
import shutil
import subprocess
import psutil
import winshell
import ctypes
import json
import time

class SystemManager:
    @staticmethod
    def is_admin():
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    @staticmethod
    def get_system_stats():
        return {
            "cpu_percent": psutil.cpu_percent(interval=None),
            "ram_percent": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage('C:').percent,
            "temp_files_size": SystemManager.get_temp_size()
        }

    @staticmethod
    def get_temp_size():
        total_size = 0
        paths = [
            os.environ.get('TEMP'),
            os.path.join(os.environ.get('SystemRoot', 'C:\\Windows'), 'Temp'),
            os.path.join(os.environ.get('SystemRoot', 'C:\\Windows'), 'Prefetch')
        ]
        for path in paths:
            if path and os.path.exists(path):
                for dirpath, dirnames, filenames in os.walk(path):
                    for f in filenames:
                        fp = os.path.join(dirpath, f)
                        try:
                            total_size += os.path.getsize(fp)
                        except:
                            pass
        return f"{total_size / (1024*1024):.2f} MB"

    @staticmethod
    def _clean_directory(path):
        """Helper to clean a directory and return count of deleted items."""
        deleted_count = 0
        if not path or not os.path.exists(path):
            return 0
        
        for filename in os.listdir(path):
            file_path = os.path.join(path, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                    deleted_count += 1
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
                    deleted_count += 1
            except:
                pass
        return deleted_count

    @staticmethod
    def clean_junk():
        results = []
        is_admin = SystemManager.is_admin()
        
        if not is_admin:
            results.append("⚠️ Ejecutando sin permisos de Administrador. Algunas áreas serán omitidas.")
        
        # 1. Recycle Bin
        try:
            winshell.recycle_bin().empty(confirm=False, show_progress=False, sound=False)
            results.append("✅ Papelera de reciclaje vaciada")
        except:
            results.append("❌ Error al vaciar papelera (puede requerir Admin)")

        # 2. Windows Temp Folders
        temp_paths = {
            "Archivos temporales de usuario": os.environ.get('TEMP'),
            "Archivos temporales del sistema": os.path.join(os.environ.get('SystemRoot', 'C:\\Windows'), 'Temp'),
            "Prefetch (optimización)": os.path.join(os.environ.get('SystemRoot', 'C:\\Windows'), 'Prefetch')
        }
        
        for name, path in temp_paths.items():
            if not is_admin and ("sistema" in name.lower() or "prefetch" in name.lower()):
                results.append(f"🔒 {name}: Acceso denegado (requiere Admin)")
                continue
                
            count = SystemManager._clean_directory(path)
            if count > 0:
                results.append(f"✅ {name}: {count} elementos eliminados")
            else:
                results.append(f"ℹ️ {name}: Ya estaba limpio")

        # 3. Browser Caches
        local_app_data = os.environ.get('LOCALAPPDATA')
        browser_paths = {
            "Caché de Google Chrome": os.path.join(local_app_data, 'Google', 'Chrome', 'User Data', 'Default', 'Cache', 'Cache_Data'),
            "Caché de Microsoft Edge": os.path.join(local_app_data, 'Microsoft', 'Edge', 'User Data', 'Default', 'Cache', 'Cache_Data'),
            "Caché de Brave Browser": os.path.join(local_app_data, 'BraveSoftware', 'Brave-Browser', 'User Data', 'Default', 'Cache', 'Cache_Data')
        }

        for name, path in browser_paths.items():
            if os.path.exists(path):
                count = SystemManager._clean_directory(path)
                if count > 0:
                    results.append(f"✅ {name}: {count} archivos de caché eliminados")
                else:
                    results.append(f"ℹ️ {name}: Sin caché acumulada")
            else:
                results.append(f"🔍 {name}: No encontrado o ruta personalizada")

        return {"results": results}

    @staticmethod
    def run_repair():
        # This is a blocking process, in a real app we'd use a thread
        # For simplicity in this script, we'll return a status
        commands = [
            ["dism", "/Online", "/Cleanup-Image", "/RestoreHealth"],
            ["sfc", "/scannow"]
        ]
        for cmd in commands:
            subprocess.run(cmd, capture_output=True)
        return {"status": "Reparación completada"}

    @staticmethod
    def update_everything():
        # Winget update
        subprocess.run(["winget", "upgrade", "--all", "--accept-source-agreements", "--accept-package-agreements"], capture_output=True)
        # Windows Update trigger (USOClient)
        subprocess.run(["usoclient", "StartInteractiveScan"], capture_output=True)
        return {"status": "Proceso de actualización iniciado"}

    @staticmethod
    def apply_debloat():
        # PowerShell script to remove common bloatware
        ps_script = """
        $apps = @("Microsoft.ZuneVideo", "Microsoft.ZuneMusic", "Microsoft.SkypeApp", "Microsoft.YourPhone", "Microsoft.BingNews", "Microsoft.BingWeather")
        foreach ($app in $apps) {
            Get-AppxPackage -Name $app | Remove-AppxPackage -ErrorAction SilentlyContinue
        }
        """
        subprocess.run(["powershell", "-Command", ps_script], capture_output=True)
        return {"status": "Debloat completado"}

    @staticmethod
    def set_turbo_mode():
        # Set High Performance power plan
        subprocess.run(["powercfg", "/setactive", "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c"], capture_output=True)
        return {"status": "Modo Turbo activado"}

    @staticmethod
    def get_hardware_info():
        # Basic hardware info
        info = {
            "processor": psutil.cpu_freq().max if psutil.cpu_freq() else "N/A",
            "memory": f"{psutil.virtual_memory().total / (1024**3):.2f} GB",
            "battery": psutil.sensors_battery().percent if psutil.sensors_battery() else "Desktop/AC"
        }
        return info
