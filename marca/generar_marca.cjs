// Genera las imágenes de marca de ChipZone con el logo nuevo (6/10/2026):
//   perfil.png    500x500    ícono del sitio / foto de perfil
//   portada.png  1640x624    portada de la página de Facebook
//   og.png       1200x630    vista previa del sitio al compartir el link (og:image)
// Uso: node marca/generar_marca.cjs   (necesita Node + Playwright con Chromium)
// Usa las fuentes de marca/fuentes/, así sale igual en cualquier máquina.
const { chromium } = require('playwright');
const fs = require('fs'); const path = require('path');
const AQUI = __dirname;
const F = n => 'file://' + path.join(AQUI, 'fuentes', n);

const ISO = fs.readFileSync(path.join(AQUI, 'perfil.svg'), 'utf8')
  .match(/<g transform="translate\(270 256\) scale\(1\.16\)">([\s\S]*?)\n  <\/g>\n<\/svg>/)[1];
const isotipo = alto => `<svg viewBox="-138 -138 252 276" style="height:${alto}px;width:auto;display:block" aria-hidden="true">
  <defs><mask id="vias" maskUnits="userSpaceOnUse" x="-70" y="-70" width="140" height="140"><rect x="-70" y="-70" width="140" height="140" fill="#fff"/><circle cx="-36" cy="-36" r="8" fill="#000"/><circle cx="36" cy="36" r="8" fill="#000"/></mask></defs>${ISO}</svg>`;

const BASE = `
@font-face{font-family:Archivo;font-weight:800;src:url(${F('Archivo-800.ttf')})}
@font-face{font-family:Plex;font-weight:500;src:url(${F('IBMPlexSans-500.ttf')})}
@font-face{font-family:Plex;font-weight:600;src:url(${F('IBMPlexSans-600.ttf')})}
*{margin:0;box-sizing:border-box}
body{background:radial-gradient(ellipse at 50% 35%,#14264F 0%,#0B1530 70%);color:#fff;font-family:Plex;overflow:hidden;position:relative}
.pistas{position:absolute;inset:0}
.marca{display:flex;align-items:center;justify-content:center;gap:.4em;font-family:Archivo;font-weight:800;letter-spacing:-.02em;line-height:1}
.marca span{color:#00C8FF}
.c{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center}`;

// pistas de circuito finas entrando por los costados
const pistas = (W, H) => {
  const y = f => Math.round(H * f), xs = W * 0.09;
  const lado = (x0, dir) => [[.24, .34], [.6, .5], [.84, .74]].map(([a, b], i) => {
    const x1 = x0 + dir * (xs - i * 30), x2 = x1 + dir * 70;
    return `<path d="M${x0} ${y(a)}H${x1}L${x2} ${y(b)}"/><circle cx="${x2 + dir * 10}" cy="${y(b)}" r="10"/>`;
  }).join('');
  return `<svg class="pistas" width="${W}" height="${H}" fill="none" stroke="#00C8FF" stroke-width="4" opacity=".3">${lado(0, 1)}${lado(W, -1)}</svg>`;
};

const PIEZAS = {
  'perfil.png': [500, 500, () => `<div class="c">${isotipo(290).replace('style="', 'style="margin-left:14px;')}</div>`],
  'og.png': [1200, 630, (W, H) => `${pistas(W, H)}<div class="c">
    <div class="marca" style="font-size:112px">${isotipo(160)}<div>Chip<span>Zone</span></div></div>
    <div style="font-size:44px;font-weight:600;margin-top:40px;line-height:1.2">Reparación de computadoras<br>y notebooks en CABA</div>
    <div style="font-size:26px;color:#9DAED0;margin-top:22px">14 años · Presupuesto sin cargo · Garantía por escrito</div>
    <div style="font-size:28px;font-weight:600;color:#00C8FF;margin-top:22px">chipzoneinformatica.com.ar</div></div>`],
  // Portada de Facebook: en compu la foto de perfil tapa abajo a la izquierda y en el celular
  // se recortan los costados, así que todo va al centro y arriba.
  'portada.png': [1640, 624, (W, H) => `${pistas(W, H)}<div class="c" style="justify-content:flex-start;padding-top:120px">
    <div class="marca" style="font-size:120px">${isotipo(170)}<div>Chip<span>Zone</span></div></div>
    <div style="font-size:42px;font-weight:500;color:#C9D5EA;margin-top:34px">Servicio técnico de notebooks y PC · Congreso, CABA</div></div>`],
};

(async () => {
  const b = await chromium.launch();
  for (const [nombre, [W, H, cuerpo]] of Object.entries(PIEZAS)) {
    const p = await b.newPage({ viewport: { width: W, height: H } });
    const tmp = path.join(AQUI, '.tmp-' + nombre + '.html'); // archivo local: así carga las fuentes de marca/fuentes
    fs.writeFileSync(tmp, `<!doctype html><meta charset="utf-8"><style>${BASE} body{width:${W}px;height:${H}px}</style>${cuerpo(W, H)}`);
    await p.goto('file://' + tmp);
    await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(200);
    await p.screenshot({ path: path.join(AQUI, nombre) });
    await p.close(); fs.unlinkSync(tmp); console.log('ok', nombre);
  }
  await b.close();
})();
