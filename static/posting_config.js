function getAllFormData() {
    const data = {};
    document.querySelectorAll('input, textarea, select').forEach(el => {
        if (!el.id) return; // Only save elements with IDs
        if (el.type === 'checkbox') {
            data[el.id] = el.checked;
        } else {
            data[el.id] = el.value;
        }
    });
    return data;
}

function setAllFormData(data) {
    Object.entries(data).forEach(([id, value]) => {
        const el = document.getElementById(id);
        if (el) {
            if (el.type === 'checkbox') {
                el.checked = value;
            } else {
                el.value = value;
            }
        }
    });
}

document.addEventListener('DOMContentLoaded', function() {
    const saveBtn = document.getElementById('saveConfigBtn');
    const loadBtn = document.getElementById('loadConfigBtn');
    if (saveBtn) {
        saveBtn.addEventListener('click', function() {
            const data = getAllFormData();
            fetch('/save-posting-config', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            })
            .then(res => res.json())
            .then(() => {
                alert('Configuration saved to server!');
            })
            .catch(() => {
                alert('Failed to save configuration.');
            });
        });
    }
    if (loadBtn) {
        loadBtn.addEventListener('click', function() {
            fetch('/load-posting-config')
            .then(res => {
                if (!res.ok) throw new Error('No config found');
                return res.json();
            })
            .then(data => {
                setAllFormData(data);
                alert('Configuration loaded from server!');
            })
            .catch(() => {
                alert('No saved configuration found.');
            });
        });
    }
}); 