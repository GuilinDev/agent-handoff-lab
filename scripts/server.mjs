import http from 'node:http';
import { spawn } from 'node:child_process';
import { readFile, readdir } from 'node:fs/promises';
import { existsSync, mkdirSync, createWriteStream, readFileSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const port = Number(process.env.LAB_PORT || 7331);
mkdirSync(path.join(root, '.runtime'), { recursive: true });
const envPath = path.join(root, '.env');
if (existsSync(envPath)) for (const line of readFileSync(envPath, 'utf8').split(/\r?\n/)) {
  const match = line.match(/^([A-Z_]+)=(.*)$/);
  if (match && !process.env[match[1]]) process.env[match[1]] = match[2].trim().replace(/^['"]|['"]$/g, '');
}
let runner;
const types = { '.html': 'text/html', '.css': 'text/css', '.js': 'text/javascript', '.json': 'application/json', '.png': 'image/png', '.jpg': 'image/jpeg', '.woff2': 'font/woff2', '.svg': 'image/svg+xml', '.mp4': 'video/mp4' };
function json(res, data, status = 200) { res.writeHead(status, { 'Content-Type': 'application/json', 'Cache-Control': 'no-store' }); res.end(JSON.stringify(data)); }
async function jsonFile(file, fallback) { try { return JSON.parse(await readFile(file, 'utf8')); } catch { return fallback; } }
const server = http.createServer(async (req, res) => {
  try {
    const url = new URL(req.url, `http://127.0.0.1:${port}`);
    if (url.pathname === '/api/status') {
      let engine = false;
      try { const r = await fetch('http://127.0.0.1:7031/ai/observe', { signal: AbortSignal.timeout(1500) }); engine = r.status === 400; } catch {}
      return json(res, { engine, running: !!runner, llmConfigured: !!(process.env.LLM_API_KEY && process.env.LLM_MODEL) });
    }
    if (url.pathname === '/api/live') return json(res, await jsonFile(path.join(root, '.runtime/live.json'), null));
    if (url.pathname === '/api/runs') {
      const files = await readdir(path.join(root, 'artifacts/runs')).catch(() => []);
      const runs = await Promise.all(files.filter(f => f.endsWith('.json')).sort().reverse().map(async f => {
        const r = await jsonFile(path.join(root, 'artifacts/runs', f), {});
        return { id: r.id, mode: r.mode, condition: r.condition, status: r.status, started_at: r.started_at, evaluation: r.evaluation };
      }));
      return json(res, runs);
    }
    if (url.pathname === '/api/suite') return json(res, await jsonFile(path.join(root, 'artifacts/suite.json'), null));
    if (url.pathname === '/api/run' && req.method === 'POST') {
      const origin = req.headers.origin;
      if (origin && ![`http://127.0.0.1:${port}`, `http://localhost:${port}`].includes(origin)) return json(res, { error: 'Origin not allowed' }, 403);
      if (runner) return json(res, { error: 'An experiment is already running' }, 409);
      let body = ''; for await (const part of req) { body += part; if (body.length > 2048) return json(res, { error: 'Request too large' }, 413); }
      const { mode = 'scripted', condition = 'normal' } = JSON.parse(body || '{}');
      if (!['scripted', 'llm'].includes(mode) || !['normal', 'partial-delivery', 'delayed-request'].includes(condition)) return json(res, { error: 'Invalid experiment' }, 400);
      if (mode === 'llm' && !(process.env.LLM_API_KEY && process.env.LLM_MODEL)) return json(res, { error: 'Configure LLM_API_KEY and LLM_MODEL in .env, then restart the dashboard' }, 400);
      runner = spawn(process.env.PYTHON || 'python', ['-m', 'lab.run', '--mode', mode, '--condition', condition, '--pace', '0.2'], { cwd: root, windowsHide: true, stdio: ['ignore', 'pipe', 'pipe'] });
      const log = createWriteStream(path.join(root, '.runtime/runner.log'));
      runner.stdout.pipe(log); runner.stderr.pipe(log);
      runner.once('error', () => { runner = null; }); runner.once('exit', () => { runner = null; });
      return json(res, { started: true });
    }
    let base = path.join(root, 'web');
    let relative = url.pathname === '/' ? 'index.html' : decodeURIComponent(url.pathname.slice(1));
    if (relative.startsWith('runs/')) { base = path.join(root, 'artifacts/runs'); relative = relative.slice(5); }
    if (relative.startsWith('engine-assets/')) { base = path.join(root, '.runtime/agentworld/packages/client/public'); relative = relative.slice(14); }
    const target = path.resolve(base, relative);
    if (!target.startsWith(path.resolve(base) + path.sep)) return json(res, { error: 'Invalid path' }, 403);
    const data = await readFile(target);
    res.writeHead(200, { 'Content-Type': types[path.extname(target)] || 'application/octet-stream', 'Cache-Control': 'no-cache' }); res.end(data);
  } catch (error) { json(res, { error: error.code === 'ENOENT' ? 'Not found' : 'Request failed' }, error.code === 'ENOENT' ? 404 : 500); }
});
server.listen(port, '127.0.0.1', () => console.log(`Agent Handoff Lab on http://127.0.0.1:${port}`));
