// One shopper visit, shared by all four tests: home page -> category -> search -> product -> cart.
// No checkout: the brief forbids placing orders in a load test, so every cart is emptied again.
import http from 'k6/http';
import { check, group, sleep } from 'k6';
import { SHOP, API, THINK_MIN, THINK_MAX } from './config.js';

// Search words a shopper would type; each matches at least one demo product.
const SEARCH_TERMS = ['hoodie', 'beanie', 'shirt', 'cap', 'belt', 'album', 'polo', 'sunglasses'];
const SORT_ORDERS = ['date', 'price', 'popularity', 'title'];
// Share of visits that also use the cart (the rest only browse).
const CART_RATE = Number(__ENV.CART_RATE || 0.5);
// Products other groups created start with a group code (G01...) or are named "Product".
const OTHER_GROUP_PRODUCT = /^(G\d{2}|Product$)/i;

const pick = (list) => list[Math.floor(Math.random() * list.length)];
const think = () => sleep(THINK_MIN + Math.random() * (THINK_MAX - THINK_MIN));
const json = (r) => {
  try {
    return r.json();
  } catch (e) {
    return null;
  }
};

// Runs once before the test: finds the demo categories and the demo products a shopper can buy.
export function discoverCatalog() {
  const tags = { endpoint: 'setup' };
  const categories = (json(http.get(`${API}/products/categories`, { tags })) || []).filter(
    (c) => c.count > 0 && c.slug !== 'uncategorized',
  );
  const products = {};
  for (const c of categories) {
    const list = json(http.get(`${API}/products?category=${c.id}&per_page=100`, { tags })) || [];
    for (const p of list) {
      if (p.type === 'simple' && p.is_purchasable && p.is_in_stock && !OTHER_GROUP_PRODUCT.test(p.name)) {
        products[p.id] = { id: p.id, name: p.name };
      }
    }
  }
  const catalog = { categories: categories.map((c) => ({ id: c.id, name: c.name })), products: Object.values(products) };
  if (catalog.categories.length === 0 || catalog.products.length === 0) {
    throw new Error(`Catalog discovery failed at ${API}: ${JSON.stringify(catalog)}`);
  }
  console.log(`Catalog: ${catalog.categories.length} categories, ${catalog.products.length} demo products`);
  return catalog;
}

// Each virtual user keeps one cart for the whole test, as the API guide recommends.
let cart = null;

function cartHeaders() {
  const headers = { 'Content-Type': 'application/json', 'Cart-Token': cart.token };
  if (cart.nonce) headers.Nonce = cart.nonce;
  return headers;
}

function remember(r) {
  if (r.headers['Cart-Token']) cart.token = r.headers['Cart-Token'];
  if (r.headers.Nonce) cart.nonce = r.headers.Nonce;
}

function openCart() {
  const r = http.get(`${API}/cart`, { tags: { endpoint: 'cart_get' } });
  const ok = check(r, {
    'cart: status 200': (res) => res.status === 200,
    'cart: Cart-Token returned': (res) => Boolean(res.headers['Cart-Token']),
  });
  if (ok) cart = { token: r.headers['Cart-Token'], nonce: r.headers.Nonce };
  return ok;
}

function post(path, body, endpoint) {
  const r = http.post(`${API}${path}`, JSON.stringify(body), { headers: cartHeaders(), tags: { endpoint } });
  remember(r);
  // A rejected token or nonce means this cart is no longer usable; start a fresh one next visit.
  if (r.status === 401 || r.status === 403) cart = null;
  return r;
}

function useCart(product) {
  if (!cart && !openCart()) return;

  const add = post('/cart/add-item', { id: product.id, quantity: 1 }, 'cart_add');
  const line = ((json(add) || {}).items || []).find((i) => i.id === product.id);
  check(add, {
    'add-item: status 200/201': (r) => r.status === 200 || r.status === 201,
    'add-item: product is in the cart': () => Boolean(line),
    'add-item: total is in THB': (r) => ((json(r) || {}).totals || {}).currency_code === 'THB',
  });
  if (!line || !cart) return;
  think();

  const update = post('/cart/update-item', { key: line.key, quantity: 2 }, 'cart_update');
  check(update, {
    'update-item: status 200': (r) => r.status === 200,
    'update-item: quantity is 2': (r) => ((json(r) || {}).items || []).some((i) => i.key === line.key && i.quantity === 2),
  });
  if (!cart) return;
  think();

  const remove = post('/cart/remove-item', { key: line.key }, 'cart_remove');
  check(remove, {
    'remove-item: status 200': (r) => r.status === 200,
    'remove-item: line is gone': (r) => !((json(r) || {}).items || []).some((i) => i.key === line.key),
  });
}

export function shopperVisit(catalog) {
  group('1 home page', () => {
    const r = http.get(`${SHOP}/`, { tags: { endpoint: 'home' } });
    check(r, {
      'home: status 200': (res) => res.status === 200,
      'home: shop page rendered': (res) => typeof res.body === 'string' && res.body.includes('woocommerce'),
    });
  });
  think();

  group('2 browse a category', () => {
    const cats = http.get(`${API}/products/categories`, { tags: { endpoint: 'categories' } });
    check(cats, {
      'categories: status 200': (r) => r.status === 200,
      'categories: list not empty': (r) => (json(r) || []).length > 0,
    });
    const category = pick(catalog.categories);
    const r = http.get(`${API}/products?category=${category.id}&per_page=12&orderby=${pick(SORT_ORDERS)}`, {
      tags: { endpoint: 'list', name: `${API}/products?category={id}` },
    });
    const items = json(r) || [];
    check(r, {
      'list: status 200': (res) => res.status === 200,
      'list: products returned': () => items.length > 0,
      'list: all in the chosen category': () => items.every((p) => (p.categories || []).some((c) => c.id === category.id)),
    });
  });
  think();

  group('3 search', () => {
    const term = pick(SEARCH_TERMS);
    const r = http.get(`${API}/products?search=${term}`, {
      tags: { endpoint: 'search', name: `${API}/products?search={term}` },
    });
    check(r, {
      'search: status 200': (res) => res.status === 200,
      'search: at least one result': (res) => (json(res) || []).length > 0,
    });
  });
  think();

  const product = pick(catalog.products);
  group('4 product page', () => {
    const r = http.get(`${API}/products/${product.id}`, {
      tags: { endpoint: 'detail', name: `${API}/products/{id}` },
    });
    const body = json(r) || {};
    check(r, {
      'detail: status 200': (res) => res.status === 200,
      'detail: same product id': () => body.id === product.id,
      'detail: price in THB': () => (body.prices || {}).currency_code === 'THB',
    });
  });
  think();

  if (Math.random() < CART_RATE) {
    group('5 cart', () => useCart(product));
    think();
  }
}
