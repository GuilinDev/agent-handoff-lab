import { spawn, spawnSync } from 'node:child_process';
import { createWriteStream, existsSync, mkdirSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const engine = path.join(root, '.runtime/agentworld');
if (!existsSync(path.join(engine, 'node_modules'))) throw new Error('Run npm run setup first.');
mkdirSync(path.join(root, '.runtime/logs'), { recursive: true });
const children = [];
for (const [name, args, cwd] of [
  ['engine', ['.yarn/releases/yarn-4.0.0-rc.40.cjs', 'workspace', '@kaetram/server', 'dev'], engine],
  ['game-client', ['.yarn/releases/yarn-4.0.0-rc.40.cjs', 'workspace', '@kaetram/client', 'dev'], engine],
  ['dashboard', ['scripts/server.mjs'], root]
]) {
  const child = spawn(process.execPath, args, { cwd, stdio: ['ignore', 'pipe', 'pipe'], windowsHide: true, env: { ...process.env, AGENT_HANDOFF_LAB: '1' } });
  const log = createWriteStream(path.join(root, '.runtime/logs', `${name}.log`));
  child.stdout.pipe(log); child.stderr.pipe(log);
  child.on('exit', code => console.log(`${name} exited (${code}); see .runtime/logs/${name}.log`));
  children.push(child);
}
console.log('Agent Handoff Lab: http://127.0.0.1:7331 | Game: http://127.0.0.1:7032');
console.log('Processes run locally. Ctrl+C stops this launcher.');
for (const signal of ['SIGINT', 'SIGTERM']) process.on(signal, () => {
  for (const child of children) {
    if (process.platform === 'win32' && child.pid) spawnSync('taskkill', ['/PID', String(child.pid), '/T', '/F'], { windowsHide: true, stdio: 'ignore' });
    else child.kill();
  }
  process.exit(0);
});
