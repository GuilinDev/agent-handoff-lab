import { spawnSync } from 'node:child_process';
import { existsSync, mkdirSync, readFileSync, writeFileSync, copyFileSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const engine = path.join(root, '.runtime/agentworld');
const lock = JSON.parse(readFileSync(path.join(root, 'upstream.lock.json'), 'utf8'));
function run(cmd, args, cwd = root) {
  const result = spawnSync(cmd, args, { cwd, stdio: 'inherit', env: { ...process.env, CYPRESS_INSTALL_BINARY: '0', HUSKY: '0' } });
  if (result.status !== 0) throw new Error(`${cmd} failed (${result.status})`);
}
mkdirSync(path.join(root, '.runtime'), { recursive: true });
if (!existsSync(path.join(engine, '.git'))) run('git', ['clone', '--depth', '1', '--branch', lock.branch, lock.repository, engine]);
const head = spawnSync('git', ['rev-parse', 'HEAD'], { cwd: engine, encoding: 'utf8' }).stdout.trim();
if (head !== lock.commit) {
  run('git', ['fetch', '--depth', '1', 'origin', lock.commit], engine);
  run('git', ['checkout', '--detach', lock.commit], engine);
}
if (!existsSync(path.join(engine, '.env'))) copyFileSync(path.join(engine, '.env.defaults'), path.join(engine, '.env'));
if (!existsSync(path.join(root, '.env'))) copyFileSync(path.join(root, '.env.example'), path.join(root, '.env'));
// Local-only development fixture. A clean upstream checkout remains reproducible.
let env = readFileSync(path.join(engine, '.env'), 'utf8').replace(/^HOST=.*$/m, "HOST='127.0.0.1'");
writeFileSync(path.join(engine, '.env'), env);
copyFileSync(path.join(root, 'engine/yarn.lock'), path.join(engine, 'yarn.lock'));
run(process.execPath, ['.yarn/releases/yarn-4.0.0-rc.40.cjs', 'install'], engine);
run(process.execPath, ['scripts/patch-engine.mjs']);
console.log('Engine ready. Run npm run dev, then open http://127.0.0.1:7331');
