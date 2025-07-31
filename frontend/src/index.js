import React from "react";
import ReactDOM from "react-dom/client";
import "./index.css";
import App from "./App";
import PWAService from "./services/pwa_service";

// Initialize PWA Service
const pwaService = new PWAService();

// Make PWA service globally available
window.pwaService = pwaService;

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
