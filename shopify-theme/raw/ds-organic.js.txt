/* Doolittle Scuba: "Make it organic" cart converter.
   Swaps any or all cart lines for their organic twin (same art, same price, 100% organic cotton), and shows every colour
   change before it happens: the organic line has no pastels, so some garments land on a different colour.
   Data: assets/ds-organic-map.json, built by tools/organic_cart_map.py (regular SKU key -> organic key, handle, colours).
   Uses only Shopify's Ajax Cart API (/cart.js, /cart/add.js, /cart/update.js) and /products/<handle>.js. */
(() => {
  'use strict';
  const ROOT = (window.Shopify && Shopify.routes && Shopify.routes.root) || '/';
  const cfg = document.getElementById('ds-organic-config');
  if (!cfg) return;
  const MAP_URL = cfg.dataset.map;
  let MAP = null, CART = null, busy = false;
  const prodCache = {};

  const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const getJSON = (u) => fetch(u, { headers: { Accept: 'application/json' } }).then((r) => { if (!r.ok) throw new Error(r.status); return r.json(); });
  const postJSON = (u, body) => fetch(ROOT + u, { method: 'POST', headers: { 'Content-Type': 'application/json', Accept: 'application/json' }, body: JSON.stringify(body) })
    .then(async (r) => { const j = await r.json().catch(() => ({})); if (!r.ok) throw new Error(j.description || j.message || r.status); return j; });

  // regular cart line -> its organic twin, or null
  function twin(item) {
    const sku = item.sku || '';
    if (!sku) return null;
    let key = sku, e = MAP[sku];
    if (!e) { key = sku.slice(0, sku.lastIndexOf('-')); e = MAP[key]; }
    if (!e) return null;
    const [okey, handle, from, fromHex, to, toHex, mode] = e;
    const size = sku.slice(sku.lastIndexOf('-') + 1);
    const target = mode === 's' ? `${okey}-${size}` : okey;   // '1' one size (caps), 'b' full SKU already (beanie)
    return { target, handle, from, fromHex, to, toHex, changes: from !== to };
  }
  const isOrganic = (item) => /-(T|TD)O-|-CO$|-BNO-/.test(item.sku || '');

  async function organicVariant(handle, sku) {
    if (!prodCache[handle]) prodCache[handle] = getJSON(`${ROOT}products/${handle}.js`).catch(() => null);
    const p = await prodCache[handle];
    if (!p) return null;
    return p.variants.find((v) => v.sku === sku && v.available) || null;
  }

  function sw(hex, name) {
    return `<span class="dso-sw" style="--c:${esc(hex)}" title="${esc(name)}"></span><span class="dso-cn">${esc(name)}</span>`;
  }

  function render(panel) {
    const items = (CART && CART.items) || [];
    const rows = [], skipped = [];
    let organicAlready = 0;
    items.forEach((it) => {
      if (isOrganic(it)) { organicAlready++; return; }
      const t = twin(it);
      if (!t) { skipped.push(it); return; }
      rows.push({ it, t });
    });
    if (!rows.length) {
      panel.hidden = !organicAlready;
      panel.innerHTML = organicAlready ? `<p class="dso-done"><strong>Your order is 100% organic cotton.</strong></p>` : '';
      return;
    }
    panel.hidden = false;
    const nChange = rows.filter((r) => r.t.changes).length;
    panel.innerHTML = `
      <div class="dso-head">
        <p class="dso-kicker">Organic cotton option</p>
        <h3 class="dso-title">Make your order organic</h3>
        <p class="dso-sub">Same art, same price, printed on 100% organic ring-spun cotton (caps and beanie on organic blanks).
          The organic line has <strong>no pastels</strong>, so ${nChange ? `<strong>${nChange} of ${rows.length} item${rows.length > 1 ? 's' : ''} change colour</strong>` : 'every colour here stays the same'}.
          Check each colour below, then convert the whole order or just the pieces you pick.</p>
      </div>
      <ul class="dso-list">
        ${rows.map(({ it, t }, i) => `
          <li class="dso-row${t.changes ? ' dso-row--change' : ''}">
            <label>
              <input type="checkbox" class="dso-pick" data-i="${i}" checked>
              <span class="dso-name">${esc(it.product_title)}${it.variant_title ? ` <span class="dso-var">${esc(it.variant_title)}</span>` : ''}${it.quantity > 1 ? ` <span class="dso-var">× ${it.quantity}</span>` : ''}</span>
            </label>
            <span class="dso-swap">
              ${sw(t.fromHex, t.from)}<span class="dso-arrow" aria-hidden="true">→</span>${sw(t.toHex, t.to)}
              <span class="dso-badge">${t.changes ? 'Colour changes' : 'Same colour'}</span>
            </span>
          </li>`).join('')}
      </ul>
      ${skipped.length ? `<p class="dso-note">${skipped.length} item${skipped.length > 1 ? 's have' : ' has'} no organic edition and stay${skipped.length > 1 ? '' : 's'} as is.</p>` : ''}
      ${organicAlready ? `<p class="dso-note">${organicAlready} item${organicAlready > 1 ? 's are' : ' is'} already organic.</p>` : ''}
      <div class="dso-actions">
        <button type="button" class="dso-btn dso-btn--all">Convert whole order to organic</button>
        <button type="button" class="dso-btn dso-btn--sel">Convert selected (<span class="dso-n">${rows.length}</span>)</button>
      </div>
      <p class="dso-msg" role="status" aria-live="polite"></p>`;
    const picks = [...panel.querySelectorAll('.dso-pick')];
    const n = panel.querySelector('.dso-n');
    picks.forEach((p) => p.addEventListener('change', () => { n.textContent = picks.filter((x) => x.checked).length; }));
    panel.querySelector('.dso-btn--all').addEventListener('click', () => convert(panel, rows));
    panel.querySelector('.dso-btn--sel').addEventListener('click', () => convert(panel, rows.filter((_, i) => picks[i].checked)));
  }

  async function convert(panel, rows) {
    if (busy || !rows.length) return;
    const msg = panel.querySelector('.dso-msg');
    const changing = rows.filter((r) => r.t.changes);
    if (changing.length && !window.confirm(
      'These items change colour on organic cotton:\n\n' +
      changing.map((r) => `• ${r.it.product_title}: ${r.t.from} → ${r.t.to}`).join('\n') + '\n\nConvert them?')) return;
    busy = true; panel.classList.add('dso-busy'); msg.textContent = 'Switching to organic…';
    const adds = [], removes = {}, missing = [];
    for (const { it, t } of rows) {
      const v = await organicVariant(t.handle, t.target);
      if (!v) { missing.push(it.product_title); continue; }
      const props = Object.assign({}, it.properties || {}, { _organic_from: it.sku });
      adds.push({ id: v.id, quantity: it.quantity, properties: props });
      removes[it.key] = 0;
    }
    try {
      if (adds.length) {
        await postJSON('cart/add.js', { items: adds });          // add first, so nothing is lost if a step fails
        await postJSON('cart/update.js', { updates: removes });
      }
      msg.textContent = adds.length
        ? `Done: ${adds.length} item${adds.length > 1 ? 's' : ''} now organic.${missing.length ? ` Not available yet: ${missing.join(', ')}.` : ''}`
        : `The organic edition isn't available yet for: ${missing.join(', ')}.`;
      if (adds.length) setTimeout(() => { window.location.href = ROOT + 'cart'; }, 600);
    } catch (e) {
      msg.textContent = `Couldn't convert (${e.message}). Your cart is unchanged where it failed; please try again.`;
    } finally { busy = false; panel.classList.remove('dso-busy'); }
  }

  function mountAll() {
    const spots = document.querySelectorAll('.cart-page__items, .cart-drawer__items');
    spots.forEach((spot) => {
      let panel = spot.parentElement.querySelector(':scope > .dso-panel');
      if (!panel) {
        panel = document.createElement('section');
        panel.className = 'dso-panel'; panel.hidden = true;
        panel.setAttribute('aria-label', 'Organic cotton option');
        spot.insertAdjacentElement('afterend', panel);
      }
      render(panel);
    });
  }

  let timer = null;
  async function refresh() {
    clearTimeout(timer);
    timer = setTimeout(async () => {
      try { CART = await getJSON(ROOT + 'cart.js'); mountAll(); } catch (e) { /* cart not reachable: show nothing */ }
    }, 150);
  }

  async function init() {
    try { MAP = (await getJSON(MAP_URL)).map; } catch (e) { return; }
    await refresh();
    // the theme re-renders the cart page and drawer on every change; re-attach when it does
    new MutationObserver((muts) => {
      if (busy) return;
      if (muts.some((m) => [...m.addedNodes].some((n) => n.nodeType === 1 && !n.closest('.dso-panel') &&
          (n.matches('.cart-page__items, .cart-drawer__items, .cart-items-component, cart-items-component') ||
           n.querySelector && n.querySelector('.cart-page__items, .cart-drawer__items'))))) refresh();
    }).observe(document.body, { childList: true, subtree: true });
    document.addEventListener('cart:update', refresh);
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
