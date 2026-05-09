#!/usr/bin/env node
const { spawn } = require('child_process');
const path = require('path');

// Get the path to the main.py file relative to this script
const mainPyPath = path.join(__dirname, '../main.py');

// Forward all arguments to the python process
const args = [mainPyPath, ...process.argv.slice(2)];

const pythonProcess = spawn('python3', args, {
    stdio: 'inherit',
    env: { ...process.env, PYTHONPATH: path.join(__dirname, '..') }
});

pythonProcess.on('exit', (code) => {
    process.exit(code || 0);
});

pythonProcess.on('error', (err) => {
    console.error('Failed to start AWSTUI. Make sure python3 is installed.');
    console.error(err);
    process.exit(1);
});
