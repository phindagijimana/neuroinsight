/**
 * Preload script for NeuroInsight Electron app
 * Exposes backend URL to the renderer process safely
 */

const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld(
  'electronAPI', {
    getBackendURL: () => ipcRenderer.invoke('get-backend-url'),
  }
);

