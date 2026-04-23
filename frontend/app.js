async function updateStats() {
    try {
        const response = await fetch('/api/stats');
        const data = await response.json();
        document.getElementById('cpu-val').innerText = data.cpu_percent + '%';
        document.getElementById('ram-val').innerText = data.ram_percent + '%';
        document.getElementById('junk-val').innerText = data.temp_files_size;
    } catch (e) {
        console.error("Error updating stats", e);
    }
}

async function updateHardware() {
    try {
        const response = await fetch('/api/hardware');
        const data = await response.json();
        document.getElementById('hardware-quick').innerHTML = `
            ${data.processor} <br>
            RAM: ${data.memory} | Batería: ${data.battery}
        `;
    } catch (e) {}
}

async function fetchAds() {
    try {
        const response = await fetch('/api/ads');
        const data = await response.json();
        document.getElementById('ad-box').innerHTML = `
            ${data.text} <a href="${data.link}" target="_blank">Saber más</a>
        `;
    } catch (e) {}
}

async function runTask(endpoint) {
    const log = document.getElementById('progress-log');
    const status = document.getElementById('status-text');
    
    log.innerHTML += `> Iniciando ${endpoint}...<br>`;
    status.innerText = `Ejecutando ${endpoint}...`;
    
    try {
        const response = await fetch(`/api/${endpoint}`, { method: 'POST' });
        const result = await response.json();
        
        if (result.error) {
            log.innerHTML += `<span style="color: #f44336">> ⚠️ Error: ${result.error}</span><br>`;
        } else if (result.status) {
            log.innerHTML += `<span style="color: #4CAF50">> ${result.status}</span><br>`;
            
            // Si hay detalles de limpieza (para Optimización Total)
            if (result.details) {
                result.details.forEach(msg => {
                    log.innerHTML += `<span style="color: #4CAF50; font-size: 0.8rem; margin-left: 15px;">- ${msg}</span><br>`;
                });
            }
            
            // Si hay tareas en segundo plano
            if (result.background) {
                log.innerHTML += `<span style="color: var(--accent-blue)">> ℹ️ ${result.background}</span><br>`;
            }
        } else if (result.results) {
            result.results.forEach(msg => {
                log.innerHTML += `<span style="color: #4CAF50">> ${msg}</span><br>`;
            });
        }
        
        status.innerText = "Acción completada";
        updateStats();
    } catch (e) {
        log.innerHTML += `<span style="color: #f44336">> ❌ Error de conexión: ${e.message}</span><br>`;
        status.innerText = "Error en la operación";
    }
}

// Polling de estadísticas
setInterval(updateStats, 3000);
setInterval(fetchAds, 10000); // Rotar publicidad cada 10s

// Carga inicial
updateStats();
updateHardware();
fetchAds();
