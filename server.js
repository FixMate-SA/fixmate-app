const express = require('express');
const path = require('path');
const expressStaticGzip = require('express-static-gzip');
const { createProxyMiddleware } = require('http-proxy-middleware');
const { spawn } = require('child_process');

const app = express();
const PORT = process.env.PORT || 3000;

// Environment variables for backend
const BACKEND_PORT = process.env.BACKEND_PORT || '8001';
const BACKEND_HOST = process.env.BACKEND_HOST || 'localhost';

let backendReady = false;

// Start the Python backend in the background
console.log('Starting Python backend...');
const backendProcess = spawn('python', ['-m', 'uvicorn', 'server:app', '--host', '0.0.0.0', '--port', BACKEND_PORT], {
  cwd: path.join(__dirname, 'backend'),
  stdio: ['ignore', 'pipe', 'pipe'],
  env: { ...process.env, PORT: BACKEND_PORT }
});

// Handle backend stdout
backendProcess.stdout.on('data', (data) => {
  const output = data.toString();
  console.log('Backend:', output);
  
  // Check if backend is ready
  if (output.includes('Uvicorn running on') || output.includes('Application startup complete')) {
    backendReady = true;
    console.log('✅ Backend is ready!');
  }
});

// Handle backend stderr
backendProcess.stderr.on('data', (data) => {
  const error = data.toString();
  console.error('Backend Error:', error);
});

// Handle backend process errors
backendProcess.on('error', (error) => {
  console.error('Backend process error:', error);
});

backendProcess.on('exit', (code) => {
  console.log(`Backend process exited with code ${code}`);
  backendReady = false;
});

// Wait for backend to be ready before setting up proxy
setTimeout(() => {
  console.log('Setting up proxy after backend startup delay...');
}, 5000);

// Proxy API requests to backend
app.use('/api', createProxyMiddleware({
  target: `http://${BACKEND_HOST}:${BACKEND_PORT}`,
  changeOrigin: true,
  logLevel: 'debug',
  timeout: 30000,
  proxyTimeout: 30000,
  onError: (err, req, res) => {
    console.error('Proxy error:', err.message);
    res.status(503).json({ 
      error: 'Backend service unavailable', 
      message: 'The API backend is starting up. Please try again in a moment.',
      backend_ready: backendReady 
    });
  },
  onProxyReq: (proxyReq, req, res) => {
    console.log(`Proxying ${req.method} ${req.url} to backend`);
  }
}));

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    frontend: 'running',
    backend_ready: backendReady,
    timestamp: new Date().toISOString()
  });
});

// Serve compressed static files from React build
app.use('/', expressStaticGzip(path.join(__dirname, 'frontend/build'), {
  enableBrotli: true,
  orderPreference: ['br', 'gz'],
  setHeaders: function (res, path) {
    res.setHeader("Cache-Control", "public, max-age=31536000");
  }
}));

// Handle React Router routes (SPA)
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'frontend/build', 'index.html'));
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`🚀 Frontend server running on port ${PORT}`);
  console.log(`🔄 API requests will be proxied to backend on port ${BACKEND_PORT}`);
  console.log(`🌐 Visit: https://fixmate-sa-app-a448c751e1d2.herokuapp.com`);
});

// Cleanup on exit
const cleanup = () => {
  console.log('Terminating processes...');
  if (backendProcess && !backendProcess.killed) {
    backendProcess.kill('SIGTERM');
    setTimeout(() => {
      if (!backendProcess.killed) {
        backendProcess.kill('SIGKILL');
      }
    }, 5000);
  }
  process.exit(0);
};

process.on('SIGTERM', cleanup);
process.on('SIGINT', cleanup);
process.on('SIGQUIT', cleanup);