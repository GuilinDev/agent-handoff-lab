import { readFileSync, writeFileSync, existsSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const engine = path.join(root, '.runtime/agentworld');
const apiFile = path.join(engine, 'packages/server/src/network/api.ts');
let api = readFileSync(apiFile, 'utf8');
const marker = '// AGENT HANDOFF LAB: local observer camera';
if (!api.includes(marker)) {
  const anchor = 'private handleRouter(router: express.Router): void {';
  if (!api.includes(anchor)) throw new Error('Pinned upstream API anchor changed');
  api = api.replace(anchor, `${anchor}
        ${marker}
        // This fixture endpoint only exists in the explicitly enabled local lab.
        if (process.env.AGENT_HANDOFF_LAB === '1') {
            router.post('/lab/observer', (_request, response) => {
                const observer = this.world.getPlayerByName('lab_viewer');
                if (!observer) return response.status(404).json({ status: 'error', message: 'Log in as lab_viewer first' });
                observer.teleport(89, 34, false);
                return response.json({ status: 'success', x: observer.x, y: observer.y });
            });
        }
  `);
  api = api.replace(".listen(config.apiPort, () =>", ".listen(config.apiPort, '127.0.0.1', () =>");
  writeFileSync(apiFile, api);
}
const viteFile = path.join(engine, 'packages/client/vite.config.ts');
let vite = readFileSync(viteFile, 'utf8').replace("host: '0.0.0.0'", "host: '127.0.0.1'").replace("process.env.VITE_HMR_PORT || '7030'", "process.env.VITE_HMR_PORT || '7032'");
writeFileSync(viteFile, vite);
console.log('Applied local observer and loopback binding patches. No game recipes or task outcomes modified.');
