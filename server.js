const express = require('express');
const path = require('path');
const expressStaticGzip = require('express-static-gzip');

const app = express();
const PORT = process.env.PORT || 3000;

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
});