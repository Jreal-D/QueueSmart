// API Configuration
const API_CONFIG = {
    BASE_URL: 'https://queuesmart-production.up.railway.app',
    ENDPOINTS: {
        HEALTH: '/',
        PREDICT: '/api/predict',
        MODEL_STATUS: '/api/model/status',
        BRANCHES: '/api/branches',
        SERVICES: '/api/services'
    },
    REFRESH_INTERVAL: 30000, // 30 seconds
    REQUEST_TIMEOUT: 5000    // 5 seconds
};

// Dashboard Configuration
const DASHBOARD_CONFIG = {
    CHARTS: {
        COLORS: {
            PRIMARY: '#667eea',
            SECONDARY: '#764ba2',
            SUCCESS: '#28a745',
            WARNING: '#ffc107',
            DANGER: '#dc3545',
            INFO: '#17a2b8'
        },
        ANIMATION_DURATION: 1000
    },
    SIMULATION: {
        ENABLED: true, // Enable simulation data for demo
        UPDATE_INTERVAL: 5000 // 5 seconds
    }
};

// Utility Functions
const API_UTILS = {
    makeRequest: async function(endpoint, options = {}) {
        const url = `${API_CONFIG.BASE_URL}${endpoint}`;
        const defaultOptions = {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
            timeout: API_CONFIG.REQUEST_TIMEOUT
        };
        
        try {
            const response = await fetch(url, { ...defaultOptions, ...options });
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.message || `HTTP ${response.status}`);
            }
            
            return data;
        } catch (error) {
            console.error(`API request failed: ${endpoint}`, error);
            throw error;
        }
    },

    formatWaitTime: function(minutes) {
        if (minutes < 1) return '< 1 min';
        if (minutes < 60) return `${Math.round(minutes)} min`;
        const hours = Math.floor(minutes / 60);
        const mins = Math.round(minutes % 60);
        return `${hours}h ${mins}m`;
    },

    formatTimestamp: function(timestamp) {
        return new Date(timestamp).toLocaleString();
    }
};
