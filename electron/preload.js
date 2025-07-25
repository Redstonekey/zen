const { contextBridge, ipcRenderer } = require('electron');

// Expose window control APIs to renderer
contextBridge.exposeInMainWorld('electronAPI', {
    minimize: () => ipcRenderer.invoke('window-minimize'),
    maximize: () => ipcRenderer.invoke('window-maximize'),
    close: () => ipcRenderer.invoke('window-close')
});
