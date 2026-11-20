// Shopify → GitHub relay for the custom-orders job (D16, Eric 16 Nov 2026).
//
// Shopify's own webhooks can't carry a GitHub token, and the Basic plan has no Flow "Send HTTP request",
// so this Cloudflare Worker (free tier) sits between them:
//   Shopify webhook "orders/paid"  →  POST https://<worker>.workers.dev/shopify
//   → verify X-Shopify-Hmac-Sha256 with the webhook's signing secret
//   → if the order has a custom line (a _design property, a name property, or a custom SKU)
//   → POST GitHub workflow_dispatch for custom-orders.yml (mode=run, that order only)
// The 15-minute schedule in GitHub stays as the backup.
//
// Secrets (Worker settings → Variables, type Secret; never in this file or in chat):
//   SHOPIFY_WEBHOOK_SECRET  the signing secret Shopify shows under Settings → Notifications → Webhooks
//   GITHUB_TOKEN            a fine-grained PAT: repository ScubaDoo-AI/doolittlescuba.com only, permission Actions: Read and write
// Plain variables: GITHUB_REPO = ScubaDoo-AI/doolittlescuba.com, WORKFLOW = custom-orders.yml, REF = main

const CUSTOM_SKU = /^DS-(MY[AB]-[TC]|AC[A-Z]*\d+|DIGI|HMP)/;

async function hmacOk(secret, body, header) {
  const key = await crypto.subtle.importKey('raw', new TextEncoder().encode(secret), { name: 'HMAC', hash: 'SHA-256' }, false, ['sign']);
  const sig = await crypto.subtle.sign('HMAC', key, new TextEncoder().encode(body));
  const b64 = btoa(String.fromCharCode(...new Uint8Array(sig)));
  if (!header || header.length !== b64.length) return false;
  let diff = 0;
  for (let i = 0; i < b64.length; i++) diff |= b64.charCodeAt(i) ^ header.charCodeAt(i);
  return diff === 0;
}

function isCustom(order) {
  for (const li of order.line_items || []) {
    const props = (li.properties || []).map(p => (p.name || '').toLowerCase());
    if (props.some(n => n === '_design' || n.startsWith('name') || n.startsWith('diver') || n === 'husband' || n === 'wife')) return true;
    if (CUSTOM_SKU.test(li.sku || '')) return true;
  }
  return false;
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (request.method !== 'POST' || url.pathname !== '/shopify') return new Response('not found', { status: 404 });
    const topic = request.headers.get('X-Shopify-Topic') || '';
    const shop = request.headers.get('X-Shopify-Shop-Domain') || '';
    if (!env.SHOPIFY_WEBHOOK_SECRET || !env.GITHUB_TOKEN) return new Response('relay not configured', { status: 503 });
    const body = await request.text();
    if (!(await hmacOk(env.SHOPIFY_WEBHOOK_SECRET, body, request.headers.get('X-Shopify-Hmac-Sha256')))) {
      console.log('bad signature', shop, topic);
      return new Response('bad signature', { status: 401 });
    }
    if (!topic.startsWith('orders/')) return new Response('ignored', { status: 200 });
    let order;
    try { order = JSON.parse(body); } catch { return new Response('bad json', { status: 400 }); }
    const num = String(order.order_number || order.name || '').replace('#', '');
    if (!isCustom(order)) { console.log('no custom lines', num); return new Response('no custom lines', { status: 200 }); }

    const gh = await fetch(`https://api.github.com/repos/${env.GITHUB_REPO}/actions/workflows/${env.WORKFLOW}/dispatches`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${env.GITHUB_TOKEN}`,
        'Accept': 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28',
        'User-Agent': 'doolittlescuba-relay',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ ref: env.REF || 'main', inputs: { mode: 'run', order: num } }),
    });
    // 204 = dispatched. Anything else is logged (no order data) and reported as 502 so Shopify retries later.
    if (gh.status !== 204) {
      console.log('dispatch failed', gh.status, num, (await gh.text()).slice(0, 300));
      return new Response('dispatch failed', { status: 502 });
    }
    console.log('dispatched', num);
    return new Response('dispatched', { status: 200 });
  },
};
