import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import Database from 'better-sqlite3';
import { GoogleGenAI, Type } from '@google/genai';

dotenv.config();

const app = express();
app.use(cors());
app.use(express.json());

// 1. Initialize Database
const db = new Database('orbitdesk.db');

db.exec(`
  CREATE TABLE IF NOT EXISTS orders (
    id TEXT PRIMARY KEY,
    status TEXT NOT NULL,
    carrier TEXT NOT NULL,
    estimated_delivery TEXT NOT NULL,
    checkpoint TEXT NOT NULL
  );

  CREATE TABLE IF NOT EXISTS tickets (
    id TEXT PRIMARY KEY,
    customer_name TEXT,
    email TEXT NOT NULL,
    issue_description TEXT NOT NULL,
    status TEXT DEFAULT 'Open',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
  );
`);

// Seed default orders if table is empty
const orderCount = db.prepare('SELECT count(*) AS count FROM orders').get();
if (orderCount.count === 0) {
  const insertOrder = db.prepare(`
    INSERT INTO orders (id, status, carrier, estimated_delivery, checkpoint)
    VALUES (?, ?, ?, ?, ?)
  `);
  insertOrder.run('ORD-1001', 'In Transit', 'ExpressCourier', '2 business days', 'Out for delivery');
  insertOrder.run('ORD-2045', 'Delivered', 'FedEx', 'Delivered yesterday', 'Front porch');
  insertOrder.run('ORD-3099', 'Processing', 'DHL', '4 business days', 'Fulfillment center');
}

// 2. Database Action Handlers
function executeTrackOrder(orderId) {
  const row = db.prepare('SELECT * FROM orders WHERE id = ?').get(orderId.toUpperCase());
  if (!row) {
    return { error: `Order ID ${orderId} was not found in the database.` };
  }
  return {
    orderId: row.id,
    status: row.status,
    carrier: row.carrier,
    estimatedDelivery: row.estimated_delivery,
    checkpoint: row.checkpoint
  };
}

function executeCreateTicket(customerName = 'Guest', email, issueDescription) {
  const ticketId = 'TICK-' + Math.floor(1000 + Math.random() * 9000);
  const insertTicket = db.prepare(`
    INSERT INTO tickets (id, customer_name, email, issue_description)
    VALUES (?, ?, ?, ?)
  `);
  insertTicket.run(ticketId, customerName, email, issueDescription);

  return {
    ticketId,
    status: 'Open',
    customerName,
    email,
    issueDescription,
    assignedTo: 'Tier-2 Support Queue'
  };
}

// 3. Gemini Setup & Tool Declarations
const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY });

const trackOrderTool = {
  name: 'trackOrder',
  description: 'Lookup tracking timeline and delivery status for a customer order ID.',
  parameters: {
    type: Type.OBJECT,
    properties: {
      orderId: { type: Type.STRING, description: 'Order ID, e.g., ORD-1001' }
    },
    required: ['orderId']
  }
};

const createTicketTool = {
  name: 'createTicket',
  description: 'Create a support ticket in the database when a user requests human escalation or submits an issue.',
  parameters: {
    type: Type.OBJECT,
    properties: {
      customerName: { type: Type.STRING, description: 'Customer full name' },
      email: { type: Type.STRING, description: 'Customer email address' },
      issueDescription: { type: Type.STRING, description: 'Details of the customer issue' }
    },
    required: ['email', 'issueDescription']
  }
};

// 4. API Endpoints
app.post('/api/chat', async (req, res) => {
  const { message } = req.body;
  if (!message) return res.status(400).json({ error: 'Message required' });

  try {
    const response = await ai.models.generateContent({
      model: 'gemini-2.5-flash',
      contents: message,
      config: {
        tools: [{ functionDeclarations: [trackOrderTool, createTicketTool] }],
        systemInstruction: "You are OrbitDesk AI. Use provided database tools whenever an order ID is mentioned or when a ticket needs creation."
      }
    });

    const functionCalls = response.functionCalls;

    if (functionCalls && functionCalls.length > 0) {
      const call = functionCalls[0];
      let toolData = null;

      if (call.name === 'trackOrder') {
        toolData = executeTrackOrder(call.args.orderId);
      } else if (call.name === 'createTicket') {
        toolData = executeCreateTicket(call.args.customerName, call.args.email, call.args.issueDescription);
      }

      const finalResponse = await ai.models.generateContent({
        model: 'gemini-2.5-flash',
        contents: [
          { role: 'user', parts: [{ text: message }] },
          { role: 'model', parts: response.candidates[0].content.parts },
          {
            role: 'user',
            parts: [{
              functionResponse: { name: call.name, response: toolData }
            }]
          }
        ]
      });

      return res.json({
        reply: finalResponse.text,
        toolUsed: call.name,
        toolResult: toolData
      });
    }

    res.json({ reply: response.text, toolUsed: null });

  } catch (err) {
    console.error("Chat Error:", err);
    res.status(500).json({ error: "Failed to process chat action" });
  }
});

app.get('/api/tickets', (req, res) => {
  try {
    const tickets = db.prepare('SELECT * FROM tickets ORDER BY created_at DESC').all();
    res.json({ success: true, tickets });
  } catch (err) {
    res.status(500).json({ success: false, error: 'Failed to fetch tickets' });
  }
});

app.put('/api/tickets/:id/status', (req, res) => {
  const { id } = req.params;
  const { status } = req.body;

  try {
    const stmt = db.prepare('UPDATE tickets SET status = ? WHERE id = ?');
    const result = stmt.run(status || 'Closed', id);

    if (result.changes === 0) {
      return res.status(404).json({ success: false, error: 'Ticket ID not found' });
    }

    res.json({ success: true, message: `Ticket ${id} status updated` });
  } catch (err) {
    res.status(500).json({ success: false, error: 'Database update failed' });
  }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`OrbitDesk Backend running on http://localhost:${PORT}`));