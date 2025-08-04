// Dashboard Application
class QueueSmartDashboard {
    constructor() {
        this.charts = {};
        this.refreshInterval = null;
        this.simulationInterval = null;
        this.isConnected = false;
        
        this.init();
    }

    async init() {
        console.log('Initializing QueueSmart Dashboard...');
        
        // Check API connection
        await this.checkSystemStatus();
        
        // Load initial data
        await this.loadInitialData();
        
        // Setup event listeners
        this.setupEventListeners();
        
        // Initialize charts
        this.initializeCharts();
        
        // Start auto-refresh
        this.startAutoRefresh();
        
        // Start simulation (for demo purposes)
        if (DASHBOARD_CONFIG.SIMULATION.ENABLED) {
            this.startSimulation();
        }
        
        console.log('Dashboard initialized successfully');
    }

    async checkSystemStatus() {
        try {
            const response = await API_UTILS.makeRequest(API_CONFIG.ENDPOINTS.HEALTH);
            this.isConnected = true;
            this.updateSystemStatus('online', `Connected - ${response.service} v${response.version}`);
        } catch (error) {
            this.isConnected = false;
            this.updateSystemStatus('offline', 'API Connection Failed');
            console.error('System status check failed:', error);
        }
    }

    updateSystemStatus(status, message) {
        const indicator = document.getElementById('statusIndicator');
        const text = document.getElementById('statusText');
        
        indicator.className = `status-indicator ${status}`;
        text.textContent = message;
    }

    async loadInitialData() {
        try {
            // Load branches and services
            await this.loadBranches();
            await this.loadServices();
            await this.loadModelInfo();
            
            // Update overview cards
            this.updateOverviewCards();
            
        } catch (error) {
            console.error('Failed to load initial data:', error);
        }
    }

    async loadBranches() {
        try {
            const response = await API_UTILS.makeRequest(API_CONFIG.ENDPOINTS.BRANCHES);
            this.branches = response.branches;
            
            // Update branches dropdown
            const branchSelect = document.getElementById('testBranch');
            branchSelect.innerHTML = '<option value="">Select Branch...</option>';
            
            this.branches.forEach(branch => {
                const option = document.createElement('option');
                option.value = branch;
                option.textContent = branch;
                branchSelect.appendChild(option);
            });
            
            // Update active branches count
            document.getElementById('activeBranches').textContent = this.branches.length;
            
            // Update branch monitor
            this.updateBranchMonitor();
            
        } catch (error) {
            console.error('Failed to load branches:', error);
        }
    }

    async loadServices() {
        try {
            const response = await API_UTILS.makeRequest(API_CONFIG.ENDPOINTS.SERVICES);
            this.services = response.services;
            
            // Update services dropdown
            const serviceSelect = document.getElementById('testService');
            serviceSelect.innerHTML = '<option value="">Select Service...</option>';
            
            this.services.forEach(service => {
                const option = document.createElement('option');
                option.value = service;
                option.textContent = service;
                serviceSelect.appendChild(option);
            });
            
        } catch (error) {
            console.error('Failed to load services:', error);
        }
    }

    async loadModelInfo() {
        try {
            const response = await API_UTILS.makeRequest(API_CONFIG.ENDPOINTS.MODEL_STATUS);
            this.modelInfo = response.model_info;
            
            // Update model details
            this.updateModelDetails();
            
        } catch (error) {
            console.error('Failed to load model info:', error);
        }
    }

    updateModelDetails() {
        if (!this.modelInfo) return;
        
        const modelDetails = document.getElementById('modelDetails');
        const featureList = document.getElementById('featureList');
        
        modelDetails.innerHTML = `
            <div class="model-detail-item">
                <span>Model Name:</span>
                <span>${this.modelInfo.model_name}</span>
            </div>
            <div class="model-detail-item">
                <span>Status:</span>
                <span style="color: #28a745; font-weight: bold;">${this.modelInfo.status.toUpperCase()}</span>
            </div>
            <div class="model-detail-item">
                <span>Trained:</span>
                <span>${this.modelInfo.trained_date}</span>
            </div>
        `;
        
        featureList.innerHTML = this.modelInfo.features.map(feature => 
            `<div class="feature-item">${feature.replace(/_/g, ' ').toUpperCase()}</div>`
        ).join('');
    }

    updateOverviewCards() {
        // Simulate some data for demo purposes
        const simulatedData = {
            predictionsToday: Math.floor(Math.random() * 500) + 100,
            avgWaitTime: (Math.random() * 20 + 5).toFixed(1),
            modelAccuracy: '38.2%' // From our actual model results
        };
        
        document.getElementById('predictionsToday').textContent = simulatedData.predictionsToday;
        document.getElementById('avgWaitTime').textContent = `${simulatedData.avgWaitTime} min`;
        document.getElementById('modelAccuracy').textContent = simulatedData.modelAccuracy;
    }

    updateBranchMonitor() {
        if (!this.branches) return;
        
        const branchMonitor = document.getElementById('branchMonitor');
        branchMonitor.innerHTML = '';
        
        this.branches.forEach(branch => {
            const waitTime = Math.floor(Math.random() * 30 + 5); // Simulate wait times
            const branchElement = document.createElement('div');
            branchElement.className = 'branch-status';
            branchElement.innerHTML = `
                <span class="branch-name">${branch}</span>
                <span class="branch-wait">${waitTime} min</span>
            `;
            branchMonitor.appendChild(branchElement);
        });
    }

    setupEventListeners() {
        // Refresh monitor button
        document.getElementById('refreshMonitor').addEventListener('click', () => {
            this.updateBranchMonitor();
        });
        
        // Run prediction button
        document.getElementById('runPrediction').addEventListener('click', () => {
            this.runTestPrediction();
        });
        
        // Auto-update last updated time
        document.getElementById('lastUpdated').textContent = new Date().toLocaleString();
    }

    async runTestPrediction() {
        const branch = document.getElementById('testBranch').value;
        const service = document.getElementById('testService').value;
        const hour = parseInt(document.getElementById('testHour').value);
        const queueLength = parseInt(document.getElementById('testQueueLength').value);
        
        if (!branch || !service) {
            alert('Please select branch and service type');
            return;
        }
        
        const testBtn = document.getElementById('runPrediction');
        const resultDiv = document.getElementById('predictionResult');
        const outputP = document.getElementById('predictionOutput');
        
        // Show loading
        testBtn.innerHTML = '<div class="spinner"></div> Running...';
        testBtn.disabled = true;
        
        try {
            const requestData = {
                branch: branch,
                service_type: service,
                hour: hour,
                day_of_week: new Date().getDay() === 0 ? 6 : new Date().getDay() - 1, // Convert to our format
                service_duration: 5, // Default service duration
                current_queue_length: queueLength
            };
            
            const response = await API_UTILS.makeRequest(API_CONFIG.ENDPOINTS.PREDICT, {
                method: 'POST',
                body: JSON.stringify(requestData)
            });
            
            // Show result
            outputP.innerHTML = `
                <strong>Wait Time:</strong> ${API_UTILS.formatWaitTime(response.wait_time_minutes)}<br>
                <strong>Confidence:</strong> ${response.confidence_level}<br>
                <strong>Queue Position:</strong> ${response.queue_position}<br>
                <strong>Estimated Service Time:</strong> ${response.estimated_service_time}
            `;
            resultDiv.style.display = 'block';
            
        } catch (error) {
            outputP.innerHTML = `<strong style="color: #dc3545;">Error:</strong> ${error.message}`;
            resultDiv.style.display = 'block';
        } finally {
            testBtn.innerHTML = '<i class="fas fa-play"></i> Run Prediction';
            testBtn.disabled = false;
        }
    }

    initializeCharts() {
        this.createWaitTimeChart();
        this.createBranchChart();
        this.createServiceChart();
        this.createHourlyChart();
    }

    createWaitTimeChart() {
        const ctx = document.getElementById('waitTimeChart').getContext('2d');
        
        // Generate sample time series data
        const hours = Array.from({length: 9}, (_, i) => `${i + 8}:00`);
        const waitTimes = hours.map(() => Math.floor(Math.random() * 25 + 5));
        
        this.charts.waitTime = new Chart(ctx, {
            type: 'line',
            data: {
                labels: hours,
                datasets: [{
                    label: 'Average Wait Time (minutes)',
                    data: waitTimes,
                    borderColor: DASHBOARD_CONFIG.CHARTS.COLORS.PRIMARY,
                    backgroundColor: DASHBOARD_CONFIG.CHARTS.COLORS.PRIMARY + '20',
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Wait Time (minutes)'
                        }
                    }
                }
            }
        });
    }

    createBranchChart() {
        const ctx = document.getElementById('branchChart').getContext('2d');
        
        if (!this.branches) return;
        
        const branchData = this.branches.map(() => Math.floor(Math.random() * 100 + 20));
        
        this.charts.branch = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: this.branches,
                datasets: [{
                    label: 'Daily Customers',
                    data: branchData,
                    backgroundColor: DASHBOARD_CONFIG.CHARTS.COLORS.PRIMARY,
                    borderColor: DASHBOARD_CONFIG.CHARTS.COLORS.SECONDARY,
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Number of Customers'
                        }
                    }
                }
            }
        });
    }

    createServiceChart() {
        const ctx = document.getElementById('serviceChart').getContext('2d');
        
        if (!this.services) return;
        
        const serviceData = this.services.map(() => Math.floor(Math.random() * 50 + 10));
        
        this.charts.service = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: this.services,
                datasets: [{
                    data: serviceData,
                    backgroundColor: [
                        DASHBOARD_CONFIG.CHARTS.COLORS.PRIMARY,
                        DASHBOARD_CONFIG.CHARTS.COLORS.SECONDARY,
                        DASHBOARD_CONFIG.CHARTS.COLORS.SUCCESS,
                        DASHBOARD_CONFIG.CHARTS.COLORS.WARNING,
                        DASHBOARD_CONFIG.CHARTS.COLORS.INFO
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }

    createHourlyChart() {
        const ctx = document.getElementById('hourlyChart').getContext('2d');
        
        const hours = Array.from({length: 9}, (_, i) => `${i + 8}:00`);
        const queueLengths = hours.map(() => Math.floor(Math.random() * 10 + 1));
        
        this.charts.hourly = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: hours,
                datasets: [{
                    label: 'Average Queue Length',
                    data: queueLengths,
                    backgroundColor: DASHBOARD_CONFIG.CHARTS.COLORS.INFO,
                    borderColor: DASHBOARD_CONFIG.CHARTS.COLORS.PRIMARY,
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Queue Length (people)'
                        }
                    }
                }
            }
        });
    }

    startAutoRefresh() {
        this.refreshInterval = setInterval(async () => {
            await this.checkSystemStatus();
            this.updateOverviewCards();
            this.updateBranchMonitor();
            document.getElementById('lastUpdated').textContent = new Date().toLocaleString();
        }, API_CONFIG.REFRESH_INTERVAL);
    }

    startSimulation() {
        this.simulationInterval = setInterval(() => {
            // Update charts with new simulated data
            this.updateChartsWithNewData();
        }, DASHBOARD_CONFIG.SIMULATION.UPDATE_INTERVAL);
    }

    updateChartsWithNewData() {
        // Update wait time chart
        if (this.charts.waitTime) {
            const newData = this.charts.waitTime.data.datasets[0].data.map(() => 
                Math.floor(Math.random() * 25 + 5)
            );
            this.charts.waitTime.data.datasets[0].data = newData;
            this.charts.waitTime.update('none');
        }
        
        // Update branch monitor
        this.updateBranchMonitor();
    }

    destroy() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
        }
        if (this.simulationInterval) {
            clearInterval(this.simulationInterval);
        }
        
        Object.values(this.charts).forEach(chart => {
            if (chart) chart.destroy();
        });
    }
}

// Initialize dashboard when page loads
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new QueueSmartDashboard();
});

// Handle page unload
window.addEventListener('beforeunload', () => {
    if (window.dashboard) {
        window.dashboard.destroy();
    }
});