require('dotenv').config();
const express = require('express');
const http = require('http');
const WebSocket = require('ws');
const cors = require('cors');
const crypto = require('crypto');

const app = express();
app.use(cors());
app.use(express.json());

const PASSWORD = process.env.PASSWORD || '123456';
const TOKEN_SECRET = process.env.TOKEN_SECRET || crypto.randomBytes(32).toString('hex');
const tokens = new Set();

function generateToken() {
    return crypto.randomBytes(32).toString('hex');
}

function authMiddleware(req, res, next) {
    const token = req.headers.authorization?.replace('Bearer ', '');
    if (!token || !tokens.has(token)) {
        return res.status(401).json({ error: 'Unauthorized' });
    }
    next();
}

const server = http.createServer(app);
const wss = new WebSocket.Server({ server });

const clients = new Map();

wss.on('connection', (ws, req) => {
    const clientId = Date.now().toString();
    let deviceId = null;

    ws.on('message', (message) => {
        try {
            const data = JSON.parse(message);
            
            if (data.type === 'register') {
                deviceId = data.deviceId;
                clients.set(deviceId, { ws, info: data.info || {} });
                console.log(`Device registered: ${deviceId}`);
                broadcastStatus();
            } else if (data.type === 'heartbeat') {
                if (deviceId && clients.has(deviceId)) {
                    clients.get(deviceId).lastHeartbeat = Date.now();
                }
            }
        } catch (e) {
            console.error('Parse error:', e.message);
        }
    });

    ws.on('close', () => {
        if (deviceId && clients.has(deviceId)) {
            clients.delete(deviceId);
            console.log(`Device disconnected: ${deviceId}`);
            broadcastStatus();
        }
    });
});

function broadcastStatus() {
    const status = {};
    clients.forEach((client, deviceId) => {
        status[deviceId] = {
            online: true,
            ...client.info,
            lastHeartbeat: client.lastHeartbeat
        };
    });
    
    wss.clients.forEach(client => {
        if (client.readyState === WebSocket.OPEN) {
            client.send(JSON.stringify({ type: 'status', devices: status }));
        }
    });
}

app.post('/api/login', (req, res) => {
    const { password } = req.body;
    if (password === PASSWORD) {
        const token = generateToken();
        tokens.add(token);
        res.json({ success: true, token });
    } else {
        res.status(401).json({ error: 'Invalid password' });
    }
});

app.post('/api/logout', (req, res) => {
    const token = req.headers.authorization?.replace('Bearer ', '');
    if (token) tokens.delete(token);
    res.json({ success: true });
});

app.use(express.static('../web'));

app.get('/api/check-auth', authMiddleware, (req, res) => {
    res.json({ authenticated: true });
});

app.post('/api/device/:deviceId/command', authMiddleware, (req, res) => {
    const { deviceId } = req.params;
    const { command, params } = req.body;
    
    const client = clients.get(deviceId);
    if (!client) {
        return res.status(404).json({ error: 'Device not found' });
    }
    
    client.ws.send(JSON.stringify({ type: 'command', command, params }));
    res.json({ success: true, message: 'Command sent' });
});

app.get('/api/devices', authMiddleware, (req, res) => {
    const devices = {};
    clients.forEach((client, deviceId) => {
        devices[deviceId] = {
            online: true,
            ...client.info
        };
    });
    res.json(devices);
});

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});