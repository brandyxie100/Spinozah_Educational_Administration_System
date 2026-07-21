/**
 * Guard: page components must not call fetch directly (use lib/api + hooks).
 */

import fs from 'node:fs';
import path from 'node:path';

const APP_ROOT = path.join(process.cwd(), 'app');

function collectPageFiles(dir: string): string[] {
  const entries = fs.readdirSync(dir, { withFileTypes: true });
  const files: string[] = [];
  for (const entry of entries) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      if (entry.name === 'api') {
        continue;
      }
      files.push(...collectPageFiles(full));
      continue;
    }
    if (entry.name === 'page.tsx' || entry.name === 'page.ts') {
      files.push(full);
    }
  }
  return files;
}

describe('page components', () => {
  it('do not call fetch directly', () => {
    const pages = collectPageFiles(APP_ROOT);
    expect(pages.length).toBeGreaterThan(0);

    const violations: string[] = [];
    for (const file of pages) {
      const source = fs.readFileSync(file, 'utf8');
      if (/\bfetch\s*\(/.test(source)) {
        violations.push(path.relative(process.cwd(), file));
      }
    }

    expect(violations).toEqual([]);
  });
});
