/**
 * server.ts
 * ---------
 * Express server that acts as the middleman between the React frontend
 * and the Python FastAPI backend.
 *
 * All AI logic (matching, translation, pathway generation) lives in the
 * Python backend. This file just proxies requests to it.
 *
 * ENDPOINTS:
 *   POST /api/match-noc  → proxies to Python /match
 *   POST /api/pathway    → proxies to Python /pathway
 */

import express from 'express';
import path from 'path';
import { fileURLToPath } from 'url';
import dotenv from 'dotenv';
import { createServer as createViteServer } from 'vite';

dotenv.config();

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = 3000;
const PYTHON_BACKEND = process.env.PYTHON_BACKEND_URL || 'http://localhost:8000';

app.use(express.json());

// ---------------------------------------------------------------------------
// POST /api/match-noc
// Receives user description from frontend, forwards to Python /match endpoint
// which runs translator.py + matcher.py and returns top NOC matches
// ---------------------------------------------------------------------------
app.post('/api/match-noc', async (req, res) => {
  try {
    const { description, language } = req.body;

    if (!description || typeof description !== 'string') {
      return res.status(400).json({ error: "Missing or invalid description" });
    }

    // Forward to Python backend
    const pythonRes = await fetch(`${PYTHON_BACKEND}/match`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        description,
        source_lang: language || 'auto'
      }),
    });

    if (!pythonRes.ok) {
      throw new Error(`Python backend error: ${pythonRes.status}`);
    }

    const data = await pythonRes.json();

    // Reshape Python response to match what MatchResults.tsx expects
    // Python returns: { matches: [{ rank, job_title, job_description, full_job_description }] }
    // Frontend expects: { matches: [{ nocCode, title, description, confidence, category, definition }] }
    const matches = data.matches.map((m: any, index: number) => ({
      nocCode: String(m.job_title),
      title: m.job_title,
      description: m.job_description,
      confidence: Math.max(95 - (index * 10), 60),
      category: 'General',
      definition: m.full_job_description,
    }));

    res.json({ matches });

  } catch (error: any) {
    console.error('Match error:', error);
    res.status(500).json({ error: error.message || 'Failed to match occupation codes.' });
  }
});

// ---------------------------------------------------------------------------
// POST /api/pathway
// Receives a NOC code + title from frontend, forwards to Python /pathway
// which runs pathway.py (Llama 3.1 8B) and returns a pathway card
// ---------------------------------------------------------------------------
app.post('/api/pathway', async (req, res) => {
  try {
    const { noc_code, title, definition } = req.body;

    const pythonRes = await fetch(`${PYTHON_BACKEND}/pathway`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        noc_code,
        title,
        definition: definition || ''
      }),
    });

    if (!pythonRes.ok) {
      throw new Error(`Python backend error: ${pythonRes.status}`);
    }

    const card = await pythonRes.json();
    res.json(card);

  } catch (error: any) {
    console.error('Pathway error:', error);
    res.status(502).json({ error: error.message || 'Failed to generate pathway.' });
  }
});

// ---------------------------------------------------------------------------
// Server setup — Vite middleware in dev, static files in production
// ---------------------------------------------------------------------------
const startServer = async () => {
  if (process.env.NODE_ENV !== 'production') {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: 'spa',
    });
    app.use(vite.middlewares);
  } else {
    const distPath = path.join(process.cwd(), 'dist');
    app.use(express.static(distPath));
    app.get('*', (req, res) => {
      res.sendFile(path.join(distPath, 'index.html'));
    });
  }

  app.listen(PORT, '0.0.0.0', () => {
    console.log(`[Rooted Server] Running successfully on port ${PORT}`);
  });
};

startServer();
