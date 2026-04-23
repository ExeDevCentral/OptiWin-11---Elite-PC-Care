// --- UI & Navigation Logic ---
document.addEventListener('DOMContentLoaded', () => {
    const navItems = document.querySelectorAll('.nav-item');
    const panels = document.querySelectorAll('.panel');
    const panelTitle = document.getElementById('current-panel-title');

    navItems.forEach(item => {
        item.addEventListener('click', () => {
            // Remove active from all nav items
            navItems.forEach(nav => nav.classList.remove('active'));
            // Add active to clicked
            item.classList.add('active');

            // Hide all panels
            panels.forEach(panel => panel.classList.remove('active'));
            
            // Show target panel
            const targetId = item.getAttribute('data-target');
            document.getElementById(targetId).classList.add('active');

            // Update Header Title
            panelTitle.innerText = item.querySelector('span').innerText;
        });
    });

    // Carga inicial
    updateStats();
    updateHardware();
    fetchAds();
    
    // Polling de estadísticas
    setInterval(updateStats, 3000);
    setInterval(fetchAds, 15000); // Rotar publicidad cada 15s
});

// --- API Interactions ---

function addLog(message, type = 'info') {
    const logContainer = document.getElementById('progress-log');
    let cssClass = 'log-info';
    
    if (type === 'success') cssClass = 'log-success';
    if (type === 'error') cssClass = 'log-error';
    if (type === 'warning') cssClass = 'log-warning';
    if (type === 'highlight') cssClass = 'log-highlight';

    const timestamp = new Date().toLocaleTimeString();
    logContainer.innerHTML += `<span class="${cssClass}">[${timestamp}] > ${message}</span><br>`;
    logContainer.scrollTop = logContainer.scrollHeight;
}

function updateStatus(text, type = 'info') {
    const statusText = document.getElementById('status-text');
    statusText.innerText = text;
    
    if(type === 'error') {
        statusText.style.backgroundColor = 'var(--danger)';
    } else if (type === 'success') {
        statusText.style.backgroundColor = 'var(--success)';
        statusText.style.color = '#000';
    } else {
        statusText.style.backgroundColor = 'var(--accent-primary)';
        statusText.style.color = '#fff';
    }
}

async function updateStats() {
    try {
        const response = await fetch('/api/stats');
        const data = await response.json();
        
        // Update Health Check Panel stats
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
        
        // Quick Header Update
        document.getElementById('hardware-quick').innerHTML = `
            <i class="fas fa-microchip"></i> ${data.processor} | 
            <i class="fas fa-memory"></i> ${data.memory}
        `;

        // Full Hardware Panel Update
        const hwDetails = document.getElementById('hardware-full-details');
        if (hwDetails) {
            hwDetails.innerHTML = `
                <div class="stat-card">
                    <i class="fas fa-microchip"></i>
                    <div>
                        <h4>Procesador</h4>
                        <div class="value" style="font-size:1.2rem">${data.processor} MHz (Max)</div>
                    </div>
                </div>
                <div class="stat-card">
                    <i class="fas fa-memory"></i>
                    <div>
                        <h4>Memoria RAM</h4>
                        <div class="value">${data.memory}</div>
                    </div>
                </div>
                <div class="stat-card">
                    <i class="fas fa-battery-full"></i>
                    <div>
                        <h4>Energía</h4>
                        <div class="value" style="font-size:1.2rem">${data.battery === "Desktop/AC" ? "Conectado a CA" : data.battery + "%"}</div>
                    </div>
                </div>
            `;
        }
    } catch (e) {
        console.error("Error updating hardware", e);
    }
}

async function fetchAds() {
    try {
        const response = await fetch('/api/ads');
        const data = await response.json();
        document.getElementById('ad-box').innerHTML = `
            <i class="fas fa-star" style="color:var(--warning)"></i> ${data.text} <br>
            <a href="${data.link}" target="_blank">Saber más <i class="fas fa-arrow-right"></i></a>
        `;
    } catch (e) {}
}

async function runTask(endpoint) {
    addLog(`Iniciando tarea: ${endpoint}...`, 'info');
    updateStatus('Procesando...', 'warning');
    
    try {
        const response = await fetch(`/api/${endpoint}`, { method: 'POST' });
        const result = await response.json();
        
        if (result.error) {
            addLog(`Error: ${result.error}`, 'error');
            updateStatus('Error', 'error');
        } else if (result.status) {
            addLog(result.status, 'success');
            
            // Si hay detalles de limpieza (para Optimización Total)
            if (result.details && result.details.length > 0) {
                result.details.forEach(msg => {
                    if(msg.includes('Error') || msg.includes('denegado')) {
                        addLog(`  - ${msg}`, 'warning');
                    } else if(msg.includes('No encontrado') || msg.includes('Ya estaba')) {
                         addLog(`  - ${msg}`, 'info');
                    } else {
                        addLog(`  - ${msg}`, 'success');
                    }
                });
            }
            
            // Si hay tareas en segundo plano
            if (result.background) {
                addLog(`Info: ${result.background}`, 'highlight');
            }
            
            updateStatus('Completado', 'success');
            setTimeout(() => updateStatus('Listo'), 3000);
            
        } else if (result.results) {
            result.results.forEach(msg => {
                 if(msg.includes('Error') || msg.includes('denegado')) {
                        addLog(msg, 'warning');
                    } else if(msg.includes('No encontrado') || msg.includes('Ya estaba')) {
                         addLog(msg, 'info');
                    } else {
                        addLog(msg, 'success');
                    }
            });
            updateStatus('Completado', 'success');
            setTimeout(() => updateStatus('Listo'), 3000);
        }
        
        updateStats(); // Force refresh stats after task
    } catch (e) {
        addLog(`Error de conexión al servidor: ${e.message}`, 'error');
        updateStatus('Desconectado', 'error');
    }
}
