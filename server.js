#!/usr/bin/env node
/**
 * Simple Node.js server for Dr.MortgageUSA
 * Alternative deployment option for hosting platforms
 */

const express = require('express');
const path = require('path');

const PORT = process.env.PORT || 5000;

// Try to use express if available, otherwise use our custom server
let useExpress = false;
try {
    require.resolve('express');
    useExpress = true;
} catch (e) {
    // Express not available, fall back to custom server
    console.log('Express not available, using custom HTTP server');
}

if (useExpress) {
    // Express-based server
    const app = express();
    
    // Serve static files
    app.use(express.static('.'));
    
    // CORS headers
    app.use((req, res, next) => {
        res.header('Access-Control-Allow-Origin', '*');
        res.header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
        res.header('Access-Control-Allow-Headers', 'Content-Type');
        next();
    });
    
    // Serve index.html for root and any unmatched routes
    app.get('*', (req, res) => {
        res.sendFile(path.join(__dirname, 'index.html'));
    });
    
    app.listen(PORT, '0.0.0.0', () => {
        console.log(`✅ Dr.MortgageUSA Express server running on http://0.0.0.0:${PORT}`);
    });
} else {
    // Fall back to our custom server
    require('./start-server.js');
}