const express = require('express');
const path = require('path');
const expressStaticGzip = require('express-static-gzip');
const { spawn } = require('child_process');

const app = express();
const PORT = process.env.PORT || 3000;

// Start the Python backend in the background
const backendProcess = spawn('python', ['-m', 'uvicorn', 'server:app', '--host', '0.0.0.0', '--port', '8001'], {
  cwd: path.join(__dirname, 'backend'),
  stdio: 'inherit'
});

// Handle backend process errors
backendProcess.on('error', (error) => {
  console.error('Backend process error:', error);
});

// Proxy API requests to backend
app.use('/api', (req, res) => {
  const backendUrl = `http://localhost:8001${req.url}`;
  
  // Forward the request to the backend
  const options = {
    method: req.method,
    headers: req.headers,
    body: req.method !== 'GET' && req.method !== 'HEAD' ? JSON.stringify(req.body) : undefined
  };
  
  fetch(backendUrl, options)
    .then(response => {
      res.status(response.status);
      response.headers.forEach((value, key) => {
        res.setHeader(key, value);
      });
      return response.text();
    })
    .then(data => {
      res.send(data);
    })
    .catch(error => {
      console.error('Proxy error:', error);
      res.status(500).json({ error: 'Backend unavailable' });
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

app.listen(PORT, () => {
  console.log(`Frontend server running on port ${PORT}`);
  console.log(`Backend process started`);
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