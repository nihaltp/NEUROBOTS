document.addEventListener('DOMContentLoaded', () => {
    const socket = io();
    const video = document.getElementById('videoStream');
    const canvas = document.getElementById('overlayCanvas');
    const ctx = canvas.getContext('2d');
    const toggleBtn = document.getElementById('toggleBtn');
    const detectionStatusDot = document.getElementById('detectionStatusDot');
    const detectionStatusText = document.getElementById('detectionStatusText');
    const detectionList = document.getElementById('detectionList');
    const totalCountDisplay = document.getElementById('totalCountDisplay');
    const diseaseCountsList = document.getElementById('diseaseCountsList');

    let detectionEnabled = true;
    
    // Setup canvas resolution to match natural video resolution (assume 640x480 for now)
    // CSS will stretch it to match the object-fit of the video.
    canvas.width = 640;
    canvas.height = 480;

    toggleBtn.addEventListener('click', () => {
        detectionEnabled = !detectionEnabled;
        
        socket.emit('toggle_detection', { enabled: detectionEnabled });
        
        if (detectionEnabled) {
            toggleBtn.textContent = 'Disable Detection';
            toggleBtn.classList.remove('btn-primary');
            toggleBtn.classList.add('btn-danger');
            
            detectionStatusDot.classList.add('active');
            detectionStatusText.textContent = 'Detection Enabled';
        } else {
            toggleBtn.textContent = 'Enable Detection';
            toggleBtn.classList.remove('btn-danger');
            toggleBtn.classList.add('btn-primary');
            
            detectionStatusDot.classList.remove('active');
            detectionStatusText.textContent = 'Detection Disabled';
            
            // Clear canvas immediately
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            detectionList.innerHTML = '<p class="empty-state">No threats detected.</p>';
        }
    });

    socket.on('connect', () => {
        console.log('Connected to server');
    });

    function updateDiseaseCounts(counts) {
        if (!diseaseCountsList) return;
        diseaseCountsList.innerHTML = '';
        for (const [disease, count] of Object.entries(counts)) {
            const p = document.createElement('p');
            p.innerHTML = `${disease}: <strong>${count}</strong>`;
            diseaseCountsList.appendChild(p);
        }
    }

    socket.on('stats_update', (data) => {
        if (data.total_count !== undefined && totalCountDisplay) {
            totalCountDisplay.textContent = data.total_count;
        }
        if (data.disease_counts !== undefined) {
            updateDiseaseCounts(data.disease_counts);
        }
    });

    socket.on('detections', (data) => {
        if (!detectionEnabled) return;
        
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        if (data.total_count !== undefined && totalCountDisplay) {
            totalCountDisplay.textContent = data.total_count;
        }
        if (data.disease_counts !== undefined) {
            updateDiseaseCounts(data.disease_counts);
        }

        const detections = data.detections;
        
        if (detections.length > 0) {
            detectionList.innerHTML = ''; // clear empty state
            
            detections.forEach((det, index) => {
                const className = det.class_name;
                const conf = (det.confidence * 100).toFixed(1) + '%';
                
                // Draw the text at the top left of the canvas.
                const yPos = 30 + (index * 30);
                
                // Draw Label Text
                ctx.fillStyle = '#2ecc71';
                ctx.font = '20px Inter, sans-serif';
                ctx.fontWeight = 'bold';
                ctx.fillText(`${className}: ${conf}`, 10, yPos);
                
                // Update UI list
                const item = document.createElement('div');
                item.className = 'detection-item';
                item.innerHTML = `<strong>${className}</strong> - ${conf} confidence`;
                detectionList.appendChild(item);
            });
        } else {
            detectionList.innerHTML = '<p class="empty-state">No threats detected.</p>';
        }
    });
});
