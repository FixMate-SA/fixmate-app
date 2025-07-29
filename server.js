const express = require('express');
const path = require('path');
const expressStaticGzip = require('express-static-gzip');
const { createProxyMiddleware } = require('http-proxy-middleware');
const { spawn } = require('child_process');

const app = express();
const PORT = process.env.PORT || 3000;

// Start the Python backend in the background
console.log('Starting Python backend...');
const backendProcess = spawn('python', ['-m', 'uvicorn', 'server:app', '--host', '0.0.0.0', '--port', '8001'], {
  cwd: path.join(__dirname, 'backend'),
  stdio: 'inherit'
});

// Handle backend process errors
backendProcess.on('error', (error) => {
  console.error('Backend process error:', error);
});

backendProcess.on('exit', (code) => {
  console.log(`Backend process exited with code ${code}`);
});

// Wait a moment for backend to start
setTimeout(() => {
  console.log('Backend should be ready now');
}, 3000);

// Proxy API requests to backend
app.use('/api', createProxyMiddleware({
  target: 'http://localhost:8001',
  changeOrigin: true,
  logLevel: 'debug',
  onError: (err, req, res) => {
    console.error('Proxy error:', err);
    res.status(500).json({ error: 'Backend service unavailable' });
  }
}));

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

app.listen(PORT, () => {
  console.log(`Frontend server running on port ${PORT}`);
  console.log(`API requests will be proxied to backend on port 8001`);
});

// Cleanup on exit
process.on('SIGTERM', () => {
  console.log('Terminating processes...');
  backendProcess.kill();
  process.exit(0);
});

process.on('SIGINT', () => {
  console.log('Terminating processes...');
  backendProcess.kill();
  process.exit(0);
});