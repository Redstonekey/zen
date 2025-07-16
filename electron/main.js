const { app, BrowserWindow } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

// Python backend server integration
let pyProc = null;
const pyPort = 5000;

function startServer() {
  const script = path.join(__dirname, 'server.py');
  pyProc = spawn('python', [script], { cwd: __dirname });
  if (pyProc) {
    console.log('Python server started on port', pyPort);
    pyProc.stdout.on('data', data => console.log(`PYTHON: ${data}`));
    pyProc.stderr.on('data', data => console.error(`PYTHON ERR: ${data}`));
  }
}

function stopServer() {
  if (pyProc) {
    pyProc.kill();
    pyProc = null;
  }
}

function createWindow() {
  const win = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: true,
      contextIsolation: false
    }
  });

  // Load the app from the Flask backend
  win.loadURL(`http://192.168.1.114:${pyPort}`);
}

// Start backend and window when Electron is ready
app.whenReady().then(() => {
  startServer();
  createWindow();
});

// Stop backend on all windows closed and quit
app.on('window-all-closed', () => {
  stopServer();
  if (process.platform !== 'darwin') app.quit();
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) createWindow();
});

// Ensure Python server is stopped on quit
app.on('quit', stopServer);
