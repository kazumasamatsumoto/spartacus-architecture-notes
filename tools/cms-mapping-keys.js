#!/usr/bin/env node
// List every CMS component mapping key registered in a Spartacus checkout.
// usage: node cms-mapping-keys.js <spartacus root> [typescript module path]
// output (TSV):
//   map   <key> <file:line> <component expression> <other mapping properties>
//   lazy  <key> <file:line>        (listed in featureModules.*.cmsComponents)
const path = require('path'), fs = require('fs');
const root = path.resolve(process.argv[2]);
const ts = require(process.argv[3] || 'typescript');
const out = [];
const skip = /^(node_modules|dist|\.git|.*e2e.*|.*cypress.*|schematics)$/;

function walk(d) {
  for (const f of fs.readdirSync(d)) {
    if (skip.test(f)) continue;
    const p = path.join(d, f);
    if (fs.statSync(p).isDirectory()) walk(p);
    else if (p.endsWith('.ts') && !p.endsWith('.spec.ts')) {
      const t = fs.readFileSync(p, 'utf8');
      if (t.includes('cmsComponents') || t.includes('CMS_COMPONENTS')) parse(p, t);
    }
  }
}
function parse(p, t) {
  const sf = ts.createSourceFile(p, t, ts.ScriptTarget.Latest, true);
  const loc = (n) => path.relative(root, p) + ':' + (sf.getLineAndCharacterOfPosition(n.getStart()).line + 1);
  const strings = (arr) => arr.elements.filter(ts.isStringLiteral).forEach((e) => out.push(['lazy', e.text, loc(e)].join('\t')));
  (function visit(n) {
    if (ts.isPropertyAssignment(n) && n.name.getText() === 'cmsComponents') {
      const init = n.initializer;
      if (ts.isObjectLiteralExpression(init)) {
        for (const pr of init.properties) {
          if (!pr.name) continue;
          const key = pr.name.getText().replace(/['"]/g, '');
          let comp = '', other = [];
          if (ts.isPropertyAssignment(pr) && ts.isObjectLiteralExpression(pr.initializer)) {
            for (const q of pr.initializer.properties) {
              const nm = q.name && q.name.getText();
              if (nm === 'component') comp = q.initializer.getText().replace(/\s+/g, ' ').slice(0, 80);
              else if (nm) other.push(nm);
            }
          }
          out.push(['map', key, loc(pr), comp, other.join(',')].join('\t'));
        }
      } else if (ts.isArrayLiteralExpression(init)) strings(init);
    }
    if (ts.isVariableDeclaration(n) && /CMS_COMPONENTS/.test(n.name.getText()) && n.initializer && ts.isArrayLiteralExpression(n.initializer)) strings(n.initializer);
    ts.forEachChild(n, visit);
  })(sf);
}
walk(root);
console.log(out.join('\n'));
