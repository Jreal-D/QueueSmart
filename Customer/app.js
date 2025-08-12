// Customer Interface Application
class CustomerApp {
    constructor() {
        this.apiBaseUrl = 'https://queuesmart-production.up.railway.app';
        this.currentBranch = null;
        this.currentService = null;
        this.queueActive = false;
        this.queueTimer = null;
        this.lastWaitTime = null;
        
        this.init();
    }

    async init() {
        console.log('Initializing Customer Interface...');
        
        // Load initial data
        await this.loadBranches();
        await this.loadServices();
        
        // Setup event listeners
        this.setupEventListeners();
        
        // Check if user is already in queue (from localStorage)
        this.checkExistingQueue();
        
        console.log('Customer interface ready');
    }

    async loadBranches() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/api/branches`);
            const data = await response.json();
            
            const branchSelect = document.getElementById('customerBranch');
            branchSelect.innerHTML = '<option value="">Choose a branch...</option>';
            
            data.branches.forEach(branch => {
                const option = document.createElement('option');
                option.value = branch;
                option.textContent = branch;
                branchSelect.appendChild(option);
            });
            
        } catch (error) {
            console.error('Failed to load branches:', error);
            this.showError('Unable to load branches. Please check your connection.');
        }
    }

    async loadServices() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/api/services`);
            const data = await response.json();
            
            const serviceSelect = document.getElementById('customerService');
            serviceSelect.innerHTML = '<option value="">Select service...</option>';
            
            data.services.forEach(service => {
                const option = document.createElement('option');
                option.value = service;
                option.textContent = service;
                serviceSelect.appendChild(option);
            });
            
        } catch (error) {
            console.error('Failed to load services:', error);
            this.showError('Unable to load services. Please check your connection.');
        }
    }

    setupEventListeners() {
        // Check wait time button
        document.getElementById('checkWaitTime').addEventListener('click', () => {
            this.checkWaitTime();
        });

        // Get best times button
        document.getElementById('getBestTimes').addEventListener('click', () => {
            this.showBestTimes();
        });

        // Join queue button
        document.getElementById('joinQueue').addEventListener('click', () => {
            this.joinVirtualQueue();
        });

        // Branch/service change handlers
        document.getElementById('customerBranch').addEventListener('change', (e) => {
            this.currentBranch = e.target.value;
        });

        document.getElementById('customerService').addEventListener('change', (e) => {
            this.currentService = e.target.value;
        });
    }

    async checkWaitTime() {
        const branch = document.getElementById('customerBranch').value;
        const service = document.getElementById('customerService').value;

        if (!branch || !service) {
            this.showError('Please select both branch and service type.');
            return;
        }

        const button = document.getElementById('checkWaitTime');
        const originalText = button.innerHTML;
        
        // Show loading
        button.innerHTML = '<div class="spinner"></div> Checking...';
        button.disabled = true;

        try {
            // Get current time and day
            const now = new Date();
            const currentHour = now.getHours();
            const dayOfWeek = now.getDay() === 0 ? 6 : now.getDay() - 1; // Convert to our format
            
            // Handle banking hours (8 AM - 4 PM)
            let predictionHour;
            let isCurrentTime = true;
            
            if (currentHour < 8) {
                // Before banking hours - predict for 8 AM today
                predictionHour = 8;
                isCurrentTime = false;
            } else if (currentHour >= 16) {
                // After banking hours - predict for 8 AM tomorrow
                predictionHour = 8;
                isCurrentTime = false;
            } else {
                // During banking hours - use current time
                predictionHour = currentHour;
            }
            
            // Simulate queue length (in real app, this would come from sensors)
            const simulatedQueueLength = Math.floor(Math.random() * 8) + 1;
            
            const requestData = {
                branch: branch,
                service_type: service,
                hour: predictionHour,
                day_of_week: dayOfWeek,
                service_duration: this.getEstimatedServiceDuration(service),
                current_queue_length: simulatedQueueLength
            };

            console.log('Sending request:', requestData); // Debug log

            const response = await fetch(`${this.apiBaseUrl}/api/predict`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestData)
            });

            const data = await response.json();

            if (response.ok) {
                this.displayWaitTimeResult(data, simulatedQueueLength, isCurrentTime, predictionHour);
            } else {
                throw new Error(`API Error: ${data.message || data.details || 'Unknown error'}`);
            }

        } catch (error) {
            console.error('Wait time check failed:', error);
            this.showError(`Unable to get wait time: ${error.message}`);
        } finally {
            button.innerHTML = originalText;
            button.disabled = false;
        }
    }

    getEstimatedServiceDuration(service) {
        // Estimated service durations based on service type
        const durations = {
            "Cash Withdrawal": 3,
            "Transfer": 5,
            "Account Opening": 25,
            "Loan Application": 35,
            "General Inquiry": 3
        };
        return durations[service] || 5;
    }

    displayWaitTimeResult(data, queueLength, isCurrentTime, predictionHour) {
        // Store the wait time for queue calculations
        this.lastWaitTime = data.wait_time_minutes;
        
        const resultDiv = document.getElementById('waitTimeResult');
        const waitTimeValue = document.getElementById('waitTimeValue');
        const queuePosition = document.getElementById('queuePosition');
        const serviceTime = document.getElementById('serviceTime');
        const confidence = document.getElementById('confidence');

        waitTimeValue.textContent = Math.round(data.wait_time_minutes);
        queuePosition.textContent = `${queueLength + 1} of ${queueLength + 1}`;
        serviceTime.textContent = data.estimated_service_time;
        confidence.textContent = data.confidence_level;

        // Add color coding based on wait time
        waitTimeValue.className = '';
        if (data.wait_time_minutes <= 10) {
            waitTimeValue.style.color = '#28a745'; // Green
        } else if (data.wait_time_minutes <= 20) {
            waitTimeValue.style.color = '#ffc107'; // Yellow
        } else {
            waitTimeValue.style.color = '#dc3545'; // Red
        }

        // Add banking hours context
        const resultHeader = resultDiv.querySelector('.result-header h3');
        if (!isCurrentTime) {
            const currentHour = new Date().getHours();
            if (currentHour < 8) {
                resultHeader.textContent = `Predicted Wait Time (when bank opens at 8:00 AM)`;
            } else {
                resultHeader.textContent = `Predicted Wait Time (for tomorrow at 8:00 AM)`;
            }
            resultHeader.style.color = '#ffc107';
        } else {
            resultHeader.textContent = `Current Wait Time`;
            resultHeader.style.color = '#667eea';
        }

        resultDiv.style.display = 'block';
        resultDiv.scrollIntoView({ behavior: 'smooth' });

        // Show banking hours message if outside hours
        if (!isCurrentTime) {
            setTimeout(() => {
                const currentHour = new Date().getHours();
                let message = '';
                if (currentHour < 8) {
                    message = 'Bank opens at 8:00 AM. This prediction is for opening time.';
                } else {
                    message = 'Banking hours are 8:00 AM - 4:00 PM. This prediction is for tomorrow morning.';
                }
                this.showInfo(message);
            }, 1000);
        }
    }

    showBestTimes() {
        const section = document.getElementById('bestTimesSection');
        
        // Generate recommendations
        this.generateTimeRecommendations();
        
        section.style.display = 'block';
        section.scrollIntoView({ behavior: 'smooth' });
    }

    generateTimeRecommendations() {
        const now = new Date();
        
        // Today's recommendations
        this.generateDayRecommendations('todayRecommendations', now);
        
        // Tomorrow's recommendations
        const tomorrow = new Date(now);
        tomorrow.setDate(tomorrow.getDate() + 1);
        this.generateDayRecommendations('tomorrowRecommendations', tomorrow);
        
        // Week recommendations
        this.generateWeekRecommendations();
    }

    generateDayRecommendations(containerId, date) {
        const container = document.getElementById(containerId);
        container.innerHTML = '';
        
        const bankingHours = [8, 9, 10, 11, 12, 13, 14, 15];
        const currentHour = new Date().getHours();
        const isToday = date.toDateString() === new Date().toDateString();
        
        bankingHours.forEach(hour => {
            // Skip past hours for today
            if (isToday && hour <= currentHour) return;
            
            const timeSlot = document.createElement('div');
            timeSlot.className = 'time-slot';
            
            // Simulate wait times for different hours
            const estimatedWait = this.getHourlyWaitEstimate(hour);
            
            if (estimatedWait <= 10) {
                timeSlot.classList.add('recommended');
            } else if (estimatedWait >= 20) {
                timeSlot.classList.add('busy');
            }
            
            timeSlot.innerHTML = `
                <div>${hour}:00</div>
                <div style="font-size: 0.7rem; margin-top: 2px;">~${estimatedWait}min</div>
            `;
            
            timeSlot.addEventListener('click', () => {
                this.selectRecommendedTime(hour, date);
            });
            
            container.appendChild(timeSlot);
        });
    }

    generateWeekRecommendations() {
        const container = document.getElementById('weekRecommendations');
        container.innerHTML = '';
        
        const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'];
        const dayWaitTimes = [15, 8, 6, 7, 12]; // Simulated average wait times
        
        days.forEach((day, index) => {
            const daySlot = document.createElement('div');
            daySlot.className = 'time-slot';
            
            if (dayWaitTimes[index] <= 8) {
                daySlot.classList.add('recommended');
            } else if (dayWaitTimes[index] >= 12) {
                daySlot.classList.add('busy');
            }
            
            daySlot.innerHTML = `
                <div>${day}</div>
                <div style="font-size: 0.7rem; margin-top: 2px;">~${dayWaitTimes[index]}min avg</div>
            `;
            
            container.appendChild(daySlot);
        });
    }

    getHourlyWaitEstimate(hour) {
        // Simulate realistic wait time patterns
        const patterns = {
            8: 5,   // Early morning - low
            9: 15,  // Rush hour - high
            10: 18, // Peak - high
            11: 12, // Moderate
            12: 8,  // Lunch break - low
            13: 20, // After lunch rush - high
            14: 15, // Afternoon - moderate
            15: 10  // Late afternoon - low
        };
        
        return patterns[hour] + Math.floor(Math.random() * 5) - 2; // Add some randomness
    }

    selectRecommendedTime(hour, date) {
        const timeString = `${hour}:00 on ${date.toLocaleDateString()}`;
        alert(`Great choice! ${timeString} is typically a good time with shorter wait times.`);
    }

    // Enhanced Virtual Queue System
    joinVirtualQueue() {
        if (!this.currentBranch || !this.currentService) {
            this.showError('Please check wait time first.');
            return;
        }

        // Show travel time selection modal
        this.showTravelTimeModal();
    }

    showTravelTimeModal() {
        const modal = document.getElementById('travelTimeModal');
        modal.style.display = 'flex';
        
        // Remove previous event listeners
        document.querySelectorAll('.travel-option').forEach(option => {
            option.replaceWith(option.cloneNode(true));
        });
        
        // Handle travel option selection
        document.querySelectorAll('.travel-option').forEach(option => {
            option.addEventListener('click', (e) => {
                // Remove previous selections
                document.querySelectorAll('.travel-option').forEach(opt => opt.classList.remove('selected'));
                
                // Select current option
                e.target.classList.add('selected');
                const travelMinutes = parseInt(e.target.dataset.minutes);
                
                setTimeout(() => {
                    this.confirmQueueJoin(travelMinutes);
                    modal.style.display = 'none';
                }, 300);
            });
        });
        
        // Handle custom time
        const useCustomBtn = document.getElementById('useCustomTime');
        const newUseCustomBtn = useCustomBtn.cloneNode(true);
        useCustomBtn.parentNode.replaceChild(newUseCustomBtn, useCustomBtn);
        
        newUseCustomBtn.addEventListener('click', () => {
            const customMinutes = parseInt(document.getElementById('customMinutes').value);
            if (customMinutes && customMinutes > 0 && customMinutes <= 180) {
                this.confirmQueueJoin(customMinutes);
                modal.style.display = 'none';
            } else {
                this.showError('Please enter a valid time between 1 and 180 minutes.');
            }
        });
        
        // Handle cancel
        const cancelBtn = document.getElementById('cancelJoinQueue');
        const newCancelBtn = cancelBtn.cloneNode(true);
        cancelBtn.parentNode.replaceChild(newCancelBtn, cancelBtn);
        
        newCancelBtn.addEventListener('click', () => {
            modal.style.display = 'none';
        });
    }

    confirmQueueJoin(travelMinutes) {
        const currentWaitTime = this.lastWaitTime || 15; // Use last predicted wait time
        const notifyInMinutes = Math.max(1, currentWaitTime - travelMinutes);
        
        const queueData = {
            branch: this.currentBranch,
            service: this.currentService,
            position: Math.floor(Math.random() * 5) + 2,
            originalWaitTime: currentWaitTime,
            travelTime: travelMinutes,
            notifyTime: notifyInMinutes,
            joinTime: new Date().toISOString(),
            phase: 'waiting', // waiting, traveling, ready, missed
            notified: false
        };

        localStorage.setItem('queueData', JSON.stringify(queueData));
        this.queueActive = true;
        
        this.showQueueStatus(queueData);
        this.startQueueTimer();
        
        // Show smart confirmation message
        let message = '';
        if (notifyInMinutes <= 1) {
            message = `You should start heading to the bank now! Your turn will be ready in ${currentWaitTime} minutes.`;
        } else {
            message = `Perfect! We'll notify you in ${notifyInMinutes} minutes to start heading to the bank. Your turn will be ready when you arrive.`;
        }
        
        this.showSuccess(message);
    }

    showQueueStatus(queueData) {
        const section = document.getElementById('queueStatusSection');
        const phaseDisplay = document.getElementById('queuePhaseDisplay');
        const actionsDisplay = document.getElementById('queueActionsDisplay');
        
        section.style.display = 'block';
        
        // Calculate current status
        const joinTime = new Date(queueData.joinTime);
        const now = new Date();
        const elapsedMinutes = Math.floor((now - joinTime) / (1000 * 60));
        const remainingWait = Math.max(0, queueData.originalWaitTime - elapsedMinutes);
        const timeToNotify = Math.max(0, queueData.notifyTime - elapsedMinutes);
        
        // Determine phase
        let currentPhase = queueData.phase;
        if (timeToNotify <= 0 && !queueData.notified && remainingWait > 0) {
            currentPhase = 'traveling';
        } else if (remainingWait <= 0) {
            currentPhase = 'ready';
        }
        
        // Update phase in localStorage
        queueData.phase = currentPhase;
        localStorage.setItem('queueData', JSON.stringify(queueData));
        
        // Render phase-specific content
        this.renderQueuePhase(phaseDisplay, actionsDisplay, queueData, timeToNotify, remainingWait);
        
        section.scrollIntoView({ behavior: 'smooth' });
    }

    renderQueuePhase(phaseDisplay, actionsDisplay, queueData, timeToNotify, remainingWait) {
        switch (queueData.phase) {
            case 'waiting':
                phaseDisplay.innerHTML = `
                    <div class="phase-waiting">
                        <h3><i class="fas fa-clock"></i> Waiting Phase</h3>
                        <div class="queue-timer">${timeToNotify} min</div>
                        <p>Time until we notify you to leave</p>
                        <div class="queue-details">
                            <div class="queue-detail-item">
                                <span>Queue Position:</span>
                                <span>${queueData.position} in line</span>
                            </div>
                            <div class="queue-detail-item">
                                <span>Branch:</span>
                                <span>${queueData.branch}</span>
                            </div>
                            <div class="queue-detail-item">
                                <span>Travel Time:</span>
                                <span>${queueData.travelTime} minutes</span>
                            </div>
                        </div>
                    </div>
                `;
                actionsDisplay.innerHTML = `
                    <button id="refreshStatus" class="btn-info">
                        <i class="fas fa-sync"></i> Refresh Status
                    </button>
                    <button id="leaveQueue" class="btn-danger">
                        <i class="fas fa-times"></i> Leave Queue
                    </button>
                `;
                break;
                
            case 'traveling':
                phaseDisplay.innerHTML = `
                    <div class="phase-traveling">
                        <h3><i class="fas fa-route"></i> Time to Leave!</h3>
                        <div class="queue-timer">${remainingWait} min</div>
                        <p>Your turn will be ready when you arrive</p>
                        <div class="queue-details">
                            <div class="queue-detail-item">
                                <span>Status:</span>
                                <span>Head to the bank now</span>
                            </div>
                            <div class="queue-detail-item">
                                <span>Travel Time:</span>
                                <span>${queueData.travelTime} minutes</span>
                            </div>
                            <div class="queue-detail-item">
                                <span>Branch:</span>
                                <span>${queueData.branch}</span>
                            </div>
                        </div>
                    </div>
                `;
                actionsDisplay.innerHTML = `
                    <button id="arrivedAtBank" class="btn-success">
                        <i class="fas fa-check"></i> I've Arrived
                    </button>
                    <button id="needMoreTime" class="btn-info">
                        <i class="fas fa-clock"></i> Need More Time
                    </button>
                    <button id="leaveQueue" class="btn-danger">
                        <i class="fas fa-times"></i> Cancel
                    </button>
                `;
                break;
                
            case 'ready':
                phaseDisplay.innerHTML = `
                    <div class="phase-ready">
                        <h3><i class="fas fa-bell"></i> You're Next!</h3>
                        <div class="queue-timer">NOW</div>
                        <p>Please proceed to the next available teller</p>
                        <div class="queue-details">
                            <div class="queue-detail-item">
                                <span>Service:</span>
                                <span>${queueData.service}</span>
                            </div>
                            <div class="queue-detail-item">
                                <span>Branch:</span>
                                <span>${queueData.branch}</span>
                            </div>
                        </div>
                    </div>
                `;
                actionsDisplay.innerHTML = `
                    <button id="serviceCompleted" class="btn-success">
                        <i class="fas fa-check-circle"></i> Service Completed
                    </button>
                    <button id="rejoinQueue" class="btn-info">
                        <i class="fas fa-redo"></i> I Missed My Turn - Rejoin
                    </button>
                `;
                break;
        }
        
        // Add event listeners for new buttons
        this.addQueueActionListeners(queueData);
    }

    addQueueActionListeners(queueData) {
        // Refresh status
        const refreshBtn = document.getElementById('refreshStatus');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                this.updateQueueStatus();
            });
        }
        
        // Leave queue
        const leaveBtn = document.getElementById('leaveQueue');
        if (leaveBtn) {
            leaveBtn.addEventListener('click', () => {
                this.leaveQueue();
            });
        }
        
        // Arrived at bank
        const arrivedBtn = document.getElementById('arrivedAtBank');
        if (arrivedBtn) {
            arrivedBtn.addEventListener('click', () => {
                queueData.phase = 'ready';
                localStorage.setItem('queueData', JSON.stringify(queueData));
                this.showQueueStatus(queueData);
                this.showSuccess('Great! You should be called shortly.');
            });
        }
        
        // Need more time
        const moreTimeBtn = document.getElementById('needMoreTime');
        if (moreTimeBtn) {
            moreTimeBtn.addEventListener('click', () => {
                this.handleNeedMoreTime(queueData);
            });
        }
        
        // Service completed
        const completedBtn = document.getElementById('serviceCompleted');
        if (completedBtn) {
            completedBtn.addEventListener('click', () => {
                this.completeService();
            });
        }
        
        // Rejoin queue
        const rejoinBtn = document.getElementById('rejoinQueue');
        if (rejoinBtn) {
            rejoinBtn.addEventListener('click', () => {
                this.rejoinQueue();
            });
        }
    }

    handleNeedMoreTime(queueData) {
        const extraTime = prompt('How many extra minutes do you need?', '10');
        if (extraTime && !isNaN(extraTime)) {
            queueData.originalWaitTime += parseInt(extraTime);
            queueData.phase = 'waiting';
            queueData.notifyTime += parseInt(extraTime);
            localStorage.setItem('queueData', JSON.stringify(queueData));
            
            this.showQueueStatus(queueData);
            this.showSuccess(`Your slot has been extended by ${extraTime} minutes.`);
        }
    }

    rejoinQueue() {
        if (confirm('Would you like to rejoin the queue? You\'ll get a new estimated wait time.')) {
            // Simulate new wait time (in real app, this would call the API)
            const newWaitTime = Math.floor(Math.random() * 20) + 15;
            
            const travelTime = JSON.parse(localStorage.getItem('queueData')).travelTime;
            this.lastWaitTime = newWaitTime;
            this.confirmQueueJoin(travelTime);
            
            this.showSuccess(`You've rejoined the queue. New wait time: ${newWaitTime} minutes.`);
        }
    }

    completeService() {
        localStorage.removeItem('queueData');
        this.queueActive = false;
        this.stopQueueTimer();
        document.getElementById('queueStatusSection').style.display = 'none';
        
        this.showSuccess('Thank you for using QueueSmart! We hope we saved you time today.');
    }

    updateQueueStatus() {
        const queueData = JSON.parse(localStorage.getItem('queueData') || '{}');
        
        if (queueData.joinTime) {
            this.showQueueStatus(queueData);
        }
    }

    leaveQueue() {
        if (confirm('Are you sure you want to leave the queue?')) {
            localStorage.removeItem('queueData');
            this.queueActive = false;
            this.stopQueueTimer();
            document.getElementById('queueStatusSection').style.display = 'none';
            this.showSuccess('You have left the virtual queue.');
        }
    }

    checkExistingQueue() {
        const queueData = JSON.parse(localStorage.getItem('queueData') || '{}');
        
        if (queueData.joinTime) {
            this.queueActive = true;
            this.currentBranch = queueData.branch;
            this.currentService = queueData.service;
            this.showQueueStatus(queueData);
            this.startQueueTimer();
        }
    }

    startQueueTimer() {
        this.stopQueueTimer(); // Clear any existing timer
        
        this.queueTimer = setInterval(() => {
            const queueData = JSON.parse(localStorage.getItem('queueData') || '{}');
            if (queueData.joinTime) {
                this.showQueueStatus(queueData);
            }
        }, 60000); // Update every minute
    }

    stopQueueTimer() {
        if (this.queueTimer) {
            clearInterval(this.queueTimer);
            this.queueTimer = null;
        }
    }

    getOrdinalSuffix(number) {
        const suffixes = ['th', 'st', 'nd', 'rd'];
        const value = number % 100;
        return suffixes[(value - 20) % 10] || suffixes[value] || suffixes[0];
    }

    showError(message) {
        // Simple error display - in real app, use proper toast/notification
        alert('Error: ' + message);
    }

    showSuccess(message) {
        // Simple success display - in real app, use proper toast/notification
        alert('Success: ' + message);
    }

    showInfo(message) {
        // Simple info display - you can improve this with proper notifications
        const infoDiv = document.createElement('div');
        infoDiv.style.cssText = `
            background: #d1ecf1;
            border: 1px solid #bee5eb;
            color: #0c5460;
            padding: 1rem;
            border-radius: 8px;
            margin: 1rem 0;
            text-align: center;
        `;
        infoDiv.innerHTML = `<i class="fas fa-info-circle"></i> ${message}`;
        
        const resultDiv = document.getElementById('waitTimeResult');
        resultDiv.appendChild(infoDiv);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (infoDiv.parentNode) {
                infoDiv.parentNode.removeChild(infoDiv);
            }
        }, 5000);
    }
}

// Initialize the customer app when page loads
document.addEventListener('DOMContentLoaded', () => {
    window.customerApp = new CustomerApp();
});

// Auto-refresh queue status if active
setInterval(() => {
    if (window.customerApp && window.customerApp.queueActive) {
        window.customerApp.updateQueueStatus();
    }
}, 30000); // Every 30 seconds
