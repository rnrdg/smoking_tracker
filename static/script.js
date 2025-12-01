document.addEventListener('DOMContentLoaded', () => {
    // Elements
    const todayCountEl = document.getElementById('today-count');
    const moneyTodayEl = document.getElementById('money-today');
    const moneyMonthEl = document.getElementById('money-month');
    const triggerSelect = document.getElementById('trigger-select');
    
    const logBtn = document.getElementById('log-btn');
    const undoBtn = document.getElementById('undo-btn');
    
    // Modal Elements
    const settingsBtn = document.getElementById('settings-btn');
    const settingsModal = document.getElementById('settings-modal');
    const closeModal = document.getElementById('close-modal');
    const saveSettingsBtn = document.getElementById('save-settings');
    const inputPrice = document.getElementById('pack-price');
    const inputSize = document.getElementById('pack-size');

    // Chart
    const ctx = document.getElementById('weeklyChart').getContext('2d');
    let weeklyChart = null;

    // --- Init ---
    init();

    function init() {
        fetch('/api/init')
            .then(res => res.json())
            .then(data => {
                // Set settings inputs
                if(data.settings) {
                    inputPrice.value = data.settings.pack_price;
                    inputSize.value = data.settings.pack_size;
                }
                // Set initial count
                todayCountEl.textContent = data.today_count;
                
                // Load stats
                loadStats();
            });
    }

    // --- Logic ---

    // Log Cigarette
    logBtn.addEventListener('click', () => {
        const trigger = triggerSelect.value;
        fetch('/api/log', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ trigger: trigger })
        })
        .then(res => res.json())
        .then(data => {
            todayCountEl.textContent = data.today_count;
            loadStats();
        });
    });

    // Undo
    undoBtn.addEventListener('click', () => {
        if(!confirm('Удалить последнюю за сегодня?')) return;
        
        fetch('/api/undo', { method: 'POST' })
        .then(res => res.json())
        .then(data => {
            if(data.status === 'success') {
                todayCountEl.textContent = data.today_count;
                loadStats();
            } else {
                alert('Нечего удалять!');
            }
        });
    });

    // Load Stats & Render Chart
    function loadStats() {
        fetch('/api/stats')
            .then(res => res.json())
            .then(data => {
                // Update Money
                moneyTodayEl.textContent = data.money.today + ' ₸';
                moneyMonthEl.textContent = data.money.month + ' ₸';
                
                // Update Chart
                updateChart(data.chart.labels, data.chart.data);
            });
    }

    function updateChart(labels, dataPoints) {
        if(weeklyChart) {
            weeklyChart.destroy();
        }
        
        weeklyChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Сигарет',
                    data: dataPoints,
                    backgroundColor: 'rgba(231, 76, 60, 0.7)',
                    borderColor: 'rgba(231, 76, 60, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: { stepSize: 1 }
                    }
                },
                plugins: {
                    legend: { display: false }
                }
            }
        });
    }

    // --- Settings Modal ---
    settingsBtn.addEventListener('click', () => {
        settingsModal.classList.add('visible');
    });

    closeModal.addEventListener('click', () => {
        settingsModal.classList.remove('visible');
    });
    
    window.addEventListener('click', (e) => {
        if(e.target === settingsModal) {
            settingsModal.classList.remove('visible');
        }
    });

    saveSettingsBtn.addEventListener('click', () => {
        const price = inputPrice.value;
        const size = inputSize.value;
        
        fetch('/api/settings', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                pack_price: price,
                pack_size: size
            })
        })
        .then(res => res.json())
        .then(data => {
            if(data.status === 'success') {
                settingsModal.classList.remove('visible');
                // Reload stats to reflect new price maybe? 
                // Note: The task says "When recording... calculate cost".
                // Changing settings usually applies to NEW records. 
                // Old records have 'cost' saved in DB. 
                // So we don't recalculate old history, just close modal.
                loadStats(); 
            }
        });
    });
});
