import React from "react";
import ReactDOM from "react-dom/client";
import "./index.css";
import App from "./App";

// Remove service worker registration to fix Heroku service worker conflicts
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.getRegistrations().then(registrations => {
    registrations.forEach(registration => registration.unregister())
    console.log('Service workers unregistered during cleanup')
  })
}

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
