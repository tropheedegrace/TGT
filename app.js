const sections = [
  { id: 'entrees', label: 'Entrées', icon: 'truck', description: 'Enregistrez un achat et mettez le stock à jour.', placeholder: 'Ex. 12 cartons de savon, prix d’achat 15000 FC, prix de vente 19000 FC', hint: 'Produit, quantité, prix d’achat et prix de vente sont obligatoires.', columns: ['Date', 'Produit', 'Code-barres', 'Quantité', 'Prix achat', 'Prix vente'] },
  { id: 'ventes', label: 'Ventes', icon: 'sale', description: 'Scannez les articles comme en caisse de supermarché ou saisissez une vente.', placeholder: 'Ex. 2 cartons de savon vendus à 19000 FC l’unité à Maman Julie', hint: 'Produit et quantité requis. Sans prix précisé, le prix catalogue est utilisé.', columns: ['Heure', 'Client', 'Produit', 'Quantité', 'Montant'] },
  { id: 'stock', label: 'Stock', icon: 'boxes', description: 'Suivez les quantités disponibles et les alertes de stock.', placeholder: 'Ex. vérifier le stock de savon', hint: 'Les entrées et ventes mettent les quantités à jour automatiquement.', columns: ['Produit', 'Forme', 'Quantité', 'Valeur achat', 'Observation'] },
  { id: 'depenses', label: 'Dépenses', icon: 'expense', description: 'Enregistrez les sorties de caisse et leur responsable.', placeholder: 'Ex. 20000 FC pour le carburant du groupe électrogène par Christian', hint: 'Montant, motif et responsable sont nécessaires.', columns: ['Heure', 'Motif', 'Montant', 'Responsable'] },
  { id: 'credits', label: 'Crédits', icon: 'credit', description: 'Suivez les dettes clients et leurs échéances.', placeholder: 'Ex. Maman Julie prend 2 cartons de biscuits à crédit, 18000 FC, téléphone 0851234567, paiement dans 5 jours', hint: 'Client, produit, quantité, montant et délai de paiement requis.', columns: ['Client', 'Produit', 'Quantité', 'Solde', 'Échéance', 'Observation'] },
  { id: 'portefeuille', label: 'Portefeuille', icon: 'wallet', description: 'Consignez les avances ou montants confiés aux agents.', placeholder: 'Ex. avance sur salaire de 50000 FC accordée à Christian', hint: 'Montant et nom de l’agent requis.', columns: ['Agent', 'Montant', 'Date', 'Observation'] },
  { id: 'inventaire', label: 'Inventaire', icon: 'inventory', description: 'Consultez les mouvements et le résultat calculé du jour.', placeholder: 'Les entrées et sorties sont intégrées automatiquement à l’inventaire.', hint: 'Le bilan journalier est calculé à partir des mouvements enregistrés.', columns: ['Produit', 'Prix achat', 'Prix vente', 'Bénéfice estimé', 'Observation'] },
  { id: 'bible', label: 'Bible', icon: 'bible', description: 'Un espace de lecture et de motivation.', placeholder: 'Espace de lecture', hint: '', columns: [] },
];

const bibleReadings = [
  { motivation: 'La confiance se construit dans la fidélité des petites choses.', verse: '« Celui qui est fidèle dans les moindres choses l’est aussi dans les grandes. »', reference: 'Luc 16:10' },
  { motivation: 'Tu peux avancer avec courage, même lorsque le chemin est difficile.', verse: '« Je puis tout par celui qui me fortifie. »', reference: 'Philippiens 4:13' },
  { motivation: 'Confie tes projets à Dieu et avance avec confiance.', verse: '« Recommande à l’Éternel tes œuvres, et tes projets réussiront. »', reference: 'Proverbes 16:3' },
  { motivation: 'Ne te lasse pas de faire le bien : les efforts fidèles portent leur fruit.', verse: '« Ne nous lassons pas de faire le bien; car nous moissonnerons au temps convenable. »', reference: 'Galates 6:9' },
  { motivation: 'Même dans les moments incertains, tu peux trouver un appui solide.', verse: '« Mon secours vient de l’Éternel, qui a fait les cieux et la terre. »', reference: 'Psaume 121:2' },
  { motivation: 'Que tes actions apportent une lumière et un encouragement autour de toi.', verse: '« Que votre lumière luise ainsi devant les hommes. »', reference: 'Matthieu 5:16' },
  { motivation: 'Fais confiance à Dieu dans tes décisions et tes projets.', verse: '« Confie-toi en l’Éternel de tout ton cœur. »', reference: 'Proverbes 3:5' },
];

const iconArt = {
  home: '<path d="m4 11 8-7 8 7v9h-6v-6h-4v6H4z"/><path d="M9 20v-6h6v6"/>',
  truck: '<path d="M2.5 7h11v10h-11z"/><path d="M13.5 10h4l4 4v3h-8z"/><circle cx="7" cy="18" r="2"/><circle cx="18" cy="18" r="2"/><path d="M5 10h5M5 13h5"/>',
  sale: '<path d="M3 10h18l-2-6H5z"/><path d="M5 10v10h14V10M9 20v-6h6v6"/><path d="M4 10a2 2 0 0 0 4 0 2 2 0 0 0 4 0 2 2 0 0 0 4 0 2 2 0 0 0 4 0"/>',
  boxes: '<path d="m12 3 8 4-8 4-8-4zM4 7v9l8 5 8-5V7M12 11v10"/><path d="m8 5 8 4"/>',
  expense: '<rect x="3" y="5" width="15" height="16" rx="2"/><path d="M7 9h7M7 13h5"/><path d="M18 9h3v10h-3M15 15l-3 3m0 0 3 3m-3-3h6"/>',
  credit: '<rect x="4" y="3" width="15" height="18" rx="2"/><path d="M8 7h7M8 11h7"/><circle cx="15" cy="16" r="3"/><path d="M15 14v2l1.5 1"/>',
  wallet: '<rect x="3" y="6" width="18" height="15" rx="2"/><path d="M3 9V6l14-3v3M15 13h6v5h-6a2.5 2.5 0 0 1 0-5Z"/><circle cx="16" cy="15.5" r=".6"/>',
  inventory: '<rect x="5" y="4" width="14" height="17" rx="2"/><path d="M9 4V2h6v2M8 9h8M8 13h8M8 17h5"/><path d="m16 15 1 1 2-3"/>',
  bible: '<path d="M4 5.5A2.5 2.5 0 0 1 6.5 3H20v17H6.5A2.5 2.5 0 0 0 4 22z"/><path d="M4 5.5v16.2M9 7h7M9 11h7"/><path d="M13 13v5m-2.5-2.5h5"/>',
  scan: '<path d="M4 7V4h3M17 4h3v3M20 17v3h-3M7 20H4v-3M7 9v6m3-6v6m3-6v6m3-6v6"/>',
};

function icon(name, className = '') {
  return `<svg class="${className}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${iconArt[name] || iconArt.home}</svg>`;
}

const initialData = { profile: {}, entries: [], stock: [], sales: [], expenses: [], credits: [], wallet: [] };
let data = structuredClone(initialData);
let activeSection = 'accueil';
let activeRole = 'gerant';
const workspaceSearches = {};
let saleCart = [];
let cameraStream = null;
let cameraTimer = null;
let authToken = sessionStorage.getItem('uzaapp.session') || '';
let currentUser = null;
let toastTimer;
let bibleTimer = null;
let bibleReadingIndex = 0;

const navigation = document.querySelector('#navigation');
const content = document.querySelector('#page-content');
const welcome = document.querySelector('#welcome');
const appShell = document.querySelector('#app-shell');
const toast = document.querySelector('#toast');

function formatApiError(detail) {
  const message = detail && typeof detail === 'string' ? detail : 'Une erreur inattendue s’est produite.';
  return message
    .replace(/\s+/g, ' ')
    .replace(/\s*;\s*/g, ' · ')
    .replace(/^\s*Données invalides\s*[:.-]?\s*/i, 'Données invalides : ')
    .trim();
}

async function apiRequest(path, options = {}) {
  const headers = new Headers(options.headers || {});
  headers.set('Accept', 'application/json');
  if (authToken) headers.set('Authorization', `Bearer ${authToken}`);
  if (options.body) headers.set('Content-Type', 'application/json');
  const response = await fetch(path, { ...options, headers, cache: 'no-store' });
  if (response.status === 204) return null;
  const result = await response.json().catch(() => ({}));
  if (!response.ok) {
    const detail = Array.isArray(result.detail)
      ? result.detail.map((item) => item.msg || item).join(' · ')
      : result.detail;
    throw new Error(formatApiError(detail || `Erreur serveur (${response.status}).`));
  }
  return result;
}

async function refreshSharedData() {
  data = await apiRequest('/api/data');
  activeRole = currentUser?.role || 'agent';
}

function escapeHtml(value) {
  return String(value ?? '').replace(/[&<>"']/g, (character) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[character]);
}

function money(value) {
  return `${new Intl.NumberFormat('fr-FR', { maximumFractionDigits: 0 }).format(Number(value) || 0)} FC`;
}

function todayKey() {
  const now = new Date();
  return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`;
}

function formatDate(value, options = { day: '2-digit', month: 'short' }) {
  return new Intl.DateTimeFormat('fr-FR', options).format(new Date(value));
}

function numberFrom(value) {
  if (!value) return null;
  const normalized = String(value).replace(/\s/g, '').replace(/\.(?=\d{3}(?:\D|$))/g, '').replace(',', '.');
  const number = Number(normalized);
  return Number.isFinite(number) && number > 0 ? number : null;
}

function findAmount(message, patterns) {
  for (const pattern of patterns) {
    const match = message.match(pattern);
    if (match) {
      const value = numberFrom(match[1]);
      if (value) return value;
    }
  }
  return null;
}

function extractQuantity(message) {
  const explicit = message.match(/(?:quantit[eé]|qt[eé]|qte)\s*[:=]?\s*(\d+(?:[,.]\d+)?)/i);
  const beginning = message.match(/^\s*(\d+(?:[,.]\d+)?)\s+/);
  return explicit || beginning ? Number((explicit || beginning)[1].replace(',', '.')) : null;
}

function extractProduct(message) {
  const labeled = message.match(/produit\s*[:=]\s*([^,;]+)/i);
  let candidate = labeled?.[1] || message.replace(/^\s*\d+(?:[,.]\d+)?\s+/, '');
  candidate = candidate
    .replace(/\b(?:prix\s+d['’]achat|prix\s+de\s+vente|achat|vente|vendu(?:e|s|es)?|pour|par|à\s+crédit|au\s+crédit|téléphone|tel|paiement|payement)\b.*$/i, '')
    .replace(/\b(?:sacs?|cartons?|bo[iî]tes?|kg|kgs|kilogrammes?|litres?|litres?|pi[eè]ces?|unit[eé]s?)\b\s*(?:de\s+)?/i, '')
    .replace(/[,:;.\s]+$/, '').trim();
  return candidate || null;
}

function productRecord(name) {
  return data.entries.slice().reverse().find((entry) => entry.product.toLocaleLowerCase('fr') === name.toLocaleLowerCase('fr')) || null;
}

function parseMessage(sectionId, message) {
  const quantity = extractQuantity(message);
  const product = extractProduct(message);
  const amount = findAmount(message, [
    /(?:montant|solde|prix\s+unitaire|pour|de)\s*[:=]?\s*(\d[\d\s.,]*)\s*(?:fcfa|fc)?/i,
    /(\d[\d\s.,]*)\s*(?:fcfa|fc)\b/i,
  ]);

  if (sectionId === 'entrees') {
    const purchasePrice = findAmount(message, [/prix\s+d['’]achat\s*[:=]?\s*(\d[\d\s.,]*)/i, /achat\s*[:=]?\s*(\d[\d\s.,]*)/i]);
    const salePrice = findAmount(message, [/prix\s+de\s+vente\s*[:=]?\s*(\d[\d\s.,]*)/i, /vente\s*[:=]?\s*(\d[\d\s.,]*)/i]);
    const missing = [];
    if (!product) missing.push('le nom du produit');
    if (!quantity) missing.push('la quantité');
    if (!purchasePrice) missing.push('le prix d’achat');
    if (!salePrice) missing.push('le prix de vente');
    if (missing.length) return { error: `Message bloqué : il manque ${missing.join(', ')}.` };
    return { record: { product, quantity, purchasePrice, salePrice, createdAt: new Date().toISOString() } };
  }

  if (sectionId === 'ventes') {
    const client = message.match(/\b(?:à|pour)\s+([\p{L}][\p{L} '-]{1,35})\s*$/iu)?.[1]?.trim() || 'Vente comptoir';
    const item = product && productRecord(product);
    const unitPrice = findAmount(message, [/prix\s+unitaire\s*[:=]?\s*(\d[\d\s.,]*)/i, /(?:vendu(?:e|s|es)?\s+(?:à|a)|à)\s*(\d[\d\s.,]*)\s*(?:fcfa|fc)?/i]) || item?.salePrice;
    const missing = [];
    if (!product) missing.push('le nom du produit');
    if (!quantity) missing.push('la quantité');
    if (!unitPrice) missing.push('un prix de vente ou un produit déjà enregistré');
    if (missing.length) return { error: `Message bloqué : il manque ${missing.join(', ')}.` };
    const stock = currentStock(product);
    if (!stock || stock.quantity < quantity) return { error: `Stock insuffisant pour « ${product} » (${stock?.quantity ?? 0} disponible).` };
    return { record: { product, quantity, unitPrice, amount: quantity * unitPrice, client, createdAt: new Date().toISOString() } };
  }

  if (sectionId === 'depenses') {
    const motiveMatch = message.match(/(?:pour|motif\s*[:=]?)\s+(.+?)(?=\s+(?:par|pour)\s+[\p{L}][\p{L} '-]*$|$)/iu);
    const responsible = message.match(/\b(?:par|responsable\s*[:=]?)\s+([\p{L}][\p{L} '-]*)$/iu)?.[1]?.trim();
    const motive = motiveMatch?.[1]?.replace(/\b\d[\d\s.,]*\s*(?:fcfa|fc)?\b/ig, '').trim();
    if (!amount || !motive || !responsible) return { error: 'Message bloqué : indiquez le montant, le motif et la personne responsable.' };
    return { record: { amount, motive, responsible, createdAt: new Date().toISOString() } };
  }

  if (sectionId === 'credits') {
    const order = message.match(/\b(?:prend|prends|ach[eè]te|emprunte)\s+(\d+(?:[,.]\d+)?)\s+(.+?)(?=\s+(?:à\s+crédit|au\s+crédit|t[eé]l|payement|paiement)\b|[,;]|$)/iu);
    const client = message.match(/^\s*([\p{L}][\p{L} '-]{1,35})\s+(?:prend|prends|ach[eè]te|emprunte)/iu)?.[1]?.trim();
    const creditQuantity = order ? Number(order[1].replace(',', '.')) : quantity;
    const creditProduct = (order?.[2] || product || '')
      .replace(/^(?:sacs?|cartons?|bo[iî]tes?|kg|kgs|kilogrammes?|litres?|pi[eè]ces?|unit[eé]s?)\s+(?:de\s+)?/i, '')
      .trim();
    const catalogueItem = creditProduct ? productRecord(creditProduct) : null;
    const creditAmount = amount || (catalogueItem ? creditQuantity * catalogueItem.salePrice : null);
    const dueDays = Number(message.match(/(?:dans|en)\s+(\d+)\s+jours?/i)?.[1]);
    if (!client || !creditProduct || !creditQuantity || !creditAmount || !dueDays) return { error: 'Message bloqué : indiquez le client, le produit, la quantité et le délai. Le montant est calculé depuis le catalogue.' };
    if (!catalogueItem) return { error: `Produit « ${creditProduct} » absent du catalogue. Enregistrez d’abord une entrée complète.` };
    const stock = currentStock(creditProduct);
    if (!stock || stock.quantity < creditQuantity) return { error: `Stock insuffisant pour « ${creditProduct} » (${stock?.quantity ?? 0} disponible).` };
    const phone = message.match(/(?:t[eé]l(?:[eé]phone)?\s*[:=]?)\s*([+\d][\d\s-]{6,})/i)?.[1]?.trim() || '';
    const dueAt = new Date();
    dueAt.setDate(dueAt.getDate() + dueDays);
    return { record: { client, product: creditProduct, quantity: creditQuantity, unitPrice: creditAmount / creditQuantity, amount: creditAmount, balance: creditAmount, dueAt: dueAt.toISOString(), phone, createdAt: new Date().toISOString(), status: 'À payer' } };
  }

  if (sectionId === 'portefeuille') {
    const agent = message.match(/(?:à|pour|accord[eé]e?\s+à)\s+([\p{L}][\p{L} '-]*)/iu)?.[1]?.trim();
    if (!amount || !agent) return { error: 'Message bloqué : indiquez le montant et le nom de l’agent.' };
    return { record: { agent, amount, createdAt: new Date().toISOString(), observation: /avance/i.test(message) ? 'Avance' : 'À régler' } };
  }

  return { error: 'Cette rubrique ne reçoit pas de saisie textuelle.' };
}

function currentStock(product) {
  if (Array.isArray(data.stock)) {
    return data.stock.find((item) => item.product.toLocaleLowerCase('fr') === product.toLocaleLowerCase('fr')) || null;
  }
  const key = product.toLocaleLowerCase('fr');
  const entries = data.entries.filter((entry) => entry.product.toLocaleLowerCase('fr') === key);
  const sales = data.sales.filter((sale) => sale.product.toLocaleLowerCase('fr') === key);
  const credits = data.credits.filter((credit) => credit.product.toLocaleLowerCase('fr') === key);
  const quantity = entries.reduce((sum, entry) => sum + entry.quantity, 0)
    - sales.reduce((sum, sale) => sum + sale.quantity, 0)
    - credits.reduce((sum, credit) => sum + credit.quantity, 0);
  const latest = entries.at(-1);
  return latest ? { product: latest.product, barcode: latest.barcode || '', quantity, purchasePrice: latest.purchasePrice, salePrice: latest.salePrice, updatedAt: latest.createdAt } : null;
}

function allStock() {
  if (Array.isArray(data.stock)) return data.stock;
  return [...new Set(data.entries.map((entry) => entry.product))].map(currentStock).filter(Boolean);
}

function dailyRecords(records) {
  return records.filter((record) => record.createdAt.slice(0, 10) === todayKey());
}

function dailyTotals() {
  const sales = dailyRecords(data.sales).reduce((sum, item) => sum + item.amount, 0);
  const expenses = dailyRecords(data.expenses).reduce((sum, item) => sum + item.amount, 0);
  const purchases = dailyRecords(data.entries).reduce((sum, item) => sum + item.quantity * item.purchasePrice, 0);
  return { sales, expenses, purchases, cash: sales - expenses };
}

function showToast(message) {
  toast.textContent = message;
  toast.classList.add('show');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toast.classList.remove('show'), 2600);
}

function renderNavigation() {
  const items = [{ id: 'accueil', label: 'Vue d’ensemble', icon: 'home' }, ...sections];
  navigation.innerHTML = items.map((item) => `<button class="nav-item ${activeSection === item.id ? 'active' : ''}" data-section="${item.id}" type="button">${icon(item.icon, 'nav-icon')}<span>${item.label}</span></button>`).join('');
  navigation.querySelectorAll('[data-section]').forEach((button) => button.addEventListener('click', () => navigate(button.dataset.section)));
}

function navigate(sectionId) {
  if (sectionId !== 'bible') {
    clearInterval(bibleTimer);
    bibleTimer = null;
  }
  activeSection = sectionId;
  renderNavigation();
  renderPage();
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function setHeading(kicker, title, subtitle) {
  document.querySelector('#page-kicker').textContent = kicker;
  document.querySelector('#page-title').textContent = title;
  document.querySelector('#page-subtitle').textContent = subtitle;
  document.querySelector('#today').textContent = new Intl.DateTimeFormat('fr-FR', { weekday: 'long', day: 'numeric', month: 'long' }).format(new Date());
  document.querySelector('#date-label').textContent = formatDate(new Date(), { day: '2-digit', month: 'short', year: 'numeric' });
}

function renderPage() {
  const notice = document.querySelector('#prototype-notice');
  notice.textContent = activeRole === 'gerant'
    ? 'Session gérant sécurisée. Les prix d’achat et les réglages ne sont accessibles qu’à votre compte.'
    : 'Session agent sécurisée. Les données affichées sont limitées à votre compte et aux informations nécessaires à la caisse.';
  notice.hidden = activeRole !== 'gerant';
  if (activeSection === 'accueil') return renderDashboard();
  const section = sections.find((item) => item.id === activeSection);
  setHeading('ESPACE DE TRAVAIL', section.label, section.description);
  if (section.id === 'bible') {
    renderBible();
    attachWorkspaceSearch(section);
    return;
  }
  if (section.id === 'ventes') {
    renderSalesRegister(section);
    attachWorkspaceSearch(section);
    return;
  }
  content.innerHTML = `<div class="entry-layout">${renderComposer(section)}${renderTablePanel(section)}</div>`;
  bindComposer(section);
  attachWorkspaceSearch(section);
}

async function renderDashboard() {
  setHeading('VOTRE ACTIVITÉ', data.profile.nom || 'Vue d’ensemble', 'Les repères essentiels de votre établissement, aujourd’hui.');
  const totals = dailyTotals();
  const stock = allStock();
  const lowStock = stock.filter((item) => item.quantity <= 5).length;
  const outstandingCredits = data.credits.filter((credit) => Number(credit.balance) > 0).reduce((sum, credit) => sum + Number(credit.balance), 0);
  const defaultReportEnd = todayKey();
  const defaultReportStart = `${defaultReportEnd.slice(0, 7)}-01`;
  const reportStart = document.querySelector('#report-start')?.value || defaultReportStart;
  const reportEnd = document.querySelector('#report-end')?.value || defaultReportEnd;
  const params = new URLSearchParams();
  if (reportStart) params.set('start_date', reportStart);
  if (reportEnd) params.set('end_date', reportEnd);
  let reportSummary = null;
  try {
    reportSummary = await apiRequest(`/api/reports/summary${params.size ? `?${params.toString()}` : ''}`);
  } catch {
    reportSummary = { sales_total: totals.sales, expenses_total: totals.expenses, cashflow_total: totals.cash, credits_outstanding: outstandingCredits, stock_low_count: lowStock, stock_value: stock.reduce((sum, item) => sum + (Number(item.quantity) * Number(item.purchasePrice || 0)), 0), top_products: [] };
  }
  const comparison = reportSummary.comparison || {};
  const alertList = Array.isArray(reportSummary.alerts) ? reportSummary.alerts : [];
  const previousSales = Number(comparison.previous_sales_total || 0);
  const deltaSales = Number(comparison.delta_sales_total || 0);
  const metrics = [
    { label: 'Ventes sur la période', icon: 'sale', value: money(reportSummary.sales_total ?? totals.sales) },
    { label: 'Dépenses sur la période', icon: 'expense', value: money(reportSummary.expenses_total ?? totals.expenses) },
    { label: 'Solde de la période', icon: 'wallet', value: money(reportSummary.cashflow_total ?? totals.cash) },
    { label: 'Crédits à recouvrer', icon: 'credit', value: money(reportSummary.credits_outstanding || outstandingCredits) },
    { label: 'Stock bas / faible', icon: 'boxes', value: `${reportSummary.stock_low_count ?? lowStock} <small>produit(s)</small>` },
  ];
  const topProducts = Array.isArray(reportSummary.top_products) ? reportSummary.top_products.slice(0, 5) : [];
  const recent = [
    ...data.sales.map((item) => ({ ...item, label: `Vente · ${item.product}`, amount: item.amount, color: 'var(--blue)' })),
    ...data.entries.map((item) => ({ ...item, label: `Entrée · ${item.product}`, amount: item.quantity * item.purchasePrice, color: 'var(--forest-2)' })),
    ...data.expenses.map((item) => ({ ...item, label: `Dépense · ${item.motive}`, amount: -item.amount, color: 'var(--coral)' })),
  ].sort((a, b) => b.createdAt.localeCompare(a.createdAt)).slice(0, 5);

  content.innerHTML = `
    <div class="panel">
      <div class="panel-heading">
        <div><h3>Rapport commercial</h3><p>Suivez vos ventes, crédits et stock selon une période donnée</p></div>
      </div>
      <div class="form-row-inline">
        <label>Du<input id="report-start" type="date" value="${escapeHtml(reportStart)}"></label>
        <label>Au<input id="report-end" type="date" value="${escapeHtml(reportEnd)}"></label>
        <button class="button button-secondary" id="report-refresh" type="button">Appliquer</button>
        <button class="button button-primary" id="export-report" type="button">Exporter CSV</button>
        <button class="button button-secondary" id="export-pdf" type="button">Exporter PDF</button>
      </div>
    </div>
    <div class="metrics">${metrics.map((item) => `<article class="metric"><div class="metric-head"><span>${item.label}</span><span class="metric-icon">${icon(item.icon)}</span></div><div class="metric-value">${item.value}</div></article>`).join('')}</div>
    <div class="dashboard-grid">
      <section class="panel">
        <div class="panel-heading">
          <div><h3>Performance mensuelle</h3><p>Comparatif avec la période précédente</p></div>
        </div>
        <div class="activity-list">
          <div class="activity-row">
            <div class="activity-name"><span>Ventes sur la période</span></div>
            <span class="activity-meta">${money(reportSummary.sales_total || totals.sales)}</span>
          </div>
          <div class="activity-row">
            <div class="activity-name"><span>Période précédente${comparison.previous_start && comparison.previous_end ? ` (${escapeHtml(comparison.previous_start)} au ${escapeHtml(comparison.previous_end)})` : ''}</span></div>
            <span class="activity-meta">${money(previousSales)}</span>
          </div>
          <div class="activity-row">
            <div class="activity-name"><span>Évolution</span></div>
            <span class="activity-meta ${deltaSales >= 0 ? 'positive' : 'negative'}">${deltaSales >= 0 ? '+' : ''}${money(deltaSales)}</span>
          </div>
          <div class="activity-row">
            <div class="activity-name"><span>Alertes automatiques</span></div>
            <span class="activity-meta">${alertList.length} signal${alertList.length > 1 ? 's' : ''}</span>
          </div>
        </div>
        <div class="activity-list">
          ${alertList.length ? alertList.map((alert) => `<div class="activity-row"><div class="activity-name"><span>${escapeHtml(alert.title || 'Alerte')}</span></div><span class="activity-meta">${escapeHtml(alert.message || '')}</span></div>`).join('') : '<div class="activity-empty">Aucune alerte sur cette période.</div>'}
        </div>
      </section>
      <section class="panel"><div class="panel-heading"><div><h3>Top produits</h3><p>Produits les plus vendus sur la période</p></div></div><div class="activity-list">${topProducts.length ? topProducts.map((item, index) => `<div class="activity-row"><div class="activity-name"><span>#${index + 1} · ${escapeHtml(item.product)}</span></div><span class="activity-meta">${money(item.revenue)} · ${item.quantity} vendu(s)</span></div>`).join('') : '<div class="activity-empty">Aucun produit vendu sur cette période.</div>'}</div></section>
      <section class="panel"><div class="panel-heading"><div><h3>Activité récente</h3><p>Les derniers mouvements enregistrés</p></div><button class="text-link" data-go="inventaire" type="button">Voir l’inventaire →</button></div><div class="activity-list">${recent.length ? recent.map((item) => `<div class="activity-row"><div class="activity-name"><i class="activity-dot" style="background:${item.color}"></i><span>${escapeHtml(item.label)}</span></div><span class="activity-meta">${money(item.amount)} · ${formatDate(item.createdAt)}</span></div>`).join('') : '<div class="activity-empty">Aucun mouvement pour le moment.</div>'}</div></section>
      <section class="panel"><div class="panel-heading"><div><h3>Accès rapide</h3><p>Choisissez une opération</p></div></div><div class="quick-actions">${sections.map((item) => `<button class="quick-action quick-${item.id}" data-go="${item.id}" type="button">${icon(item.icon, 'quick-illustration')}<b>${item.label}</b></button>`).join('')}</div></section>
    </div>`;
  content.querySelectorAll('[data-go]').forEach((button) => button.addEventListener('click', () => navigate(button.dataset.go)));
  const refreshButton = document.querySelector('#report-refresh');
  refreshButton?.addEventListener('click', () => renderDashboard());
  const exportButton = document.querySelector('#export-report');
  exportButton?.addEventListener('click', async () => {
    const start = document.querySelector('#report-start')?.value || '';
    const end = document.querySelector('#report-end')?.value || '';
    const exportParams = new URLSearchParams();
    if (start) exportParams.set('start_date', start);
    if (end) exportParams.set('end_date', end);
    try {
      const response = await fetch(`/api/reports/export${exportParams.size ? `?${exportParams.toString()}` : ''}`, { headers: { Authorization: `Bearer ${authToken}` } });
      if (!response.ok) throw new Error('Impossible d’exporter le rapport.');
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement('a');
      anchor.href = url;
      anchor.download = 'uzaapp-rapport.csv';
      anchor.click();
      URL.revokeObjectURL(url);
      showToast('Rapport exporté en CSV');
    } catch (error) {
      showToast(error.message);
    }
  });
  const exportPdfButton = document.querySelector('#export-pdf');
  exportPdfButton?.addEventListener('click', async () => {
    const start = document.querySelector('#report-start')?.value || '';
    const end = document.querySelector('#report-end')?.value || '';
    const exportParams = new URLSearchParams();
    if (start) exportParams.set('start_date', start);
    if (end) exportParams.set('end_date', end);
    try {
      const response = await fetch(`/api/reports/pdf${exportParams.size ? `?${exportParams.toString()}` : ''}`, { headers: { Authorization: `Bearer ${authToken}` } });
      if (!response.ok) throw new Error('Impossible d’exporter le rapport PDF.');
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement('a');
      anchor.href = url;
      anchor.download = 'uzaapp-performance.pdf';
      anchor.click();
      URL.revokeObjectURL(url);
      showToast('Rapport exporté en PDF');
    } catch (error) {
      showToast(error.message);
    }
  });
  attachWorkspaceSearch({ id: 'accueil', label: 'Vue d’ensemble' });
}

function normalizedSearchText(value) {
  return String(value || '').normalize('NFD').replace(/\p{Diacritic}/gu, '').toLocaleLowerCase('fr');
}

function attachWorkspaceSearch(section) {
  content.insertAdjacentHTML('afterbegin', `<section class="workspace-search" role="search"><label class="workspace-search-field">${icon('scan')}<input id="workspace-search-input" type="search" autocomplete="off" value="${escapeHtml(workspaceSearches[section.id] || '')}" placeholder="Rechercher un produit, un code-barres…" aria-label="Rechercher dans ${escapeHtml(section.label)}"><kbd>⌕</kbd></label><div class="workspace-search-results" id="workspace-search-results" hidden></div></section>`);
  const input = document.querySelector('#workspace-search-input');
  input.addEventListener('input', () => {
    workspaceSearches[section.id] = input.value;
    applyWorkspaceSearch(section);
  });
  applyWorkspaceSearch(section);
}

function applyWorkspaceSearch(section) {
  const query = normalizedSearchText(workspaceSearches[section.id]);
  const table = content.querySelector('.data-table');
  if (table) {
    const body = table.tBodies[0];
    const rows = [...body.rows].filter((row) => !row.classList.contains('empty-row') && !row.classList.contains('search-no-results'));
    let matches = 0;
    body.querySelector('.search-no-results')?.remove();
    rows.forEach((row) => {
      const visible = !query || normalizedSearchText(row.textContent).includes(query);
      row.hidden = !visible;
      if (visible) matches += 1;
    });
    if (query && rows.length && !matches) body.insertAdjacentHTML('beforeend', `<tr class="search-no-results"><td colspan="${table.tHead.rows[0].cells.length}">Aucun résultat dans cette rubrique.</td></tr>`);
  }
  content.querySelectorAll('.activity-row').forEach((row) => { row.hidden = Boolean(query) && !normalizedSearchText(row.textContent).includes(query); });
  renderWorkspaceSearchResults(section, query);
}

function renderWorkspaceSearchResults(section, query) {
  const results = document.querySelector('#workspace-search-results');
  if (!results) return;
  const matches = query ? allStock().filter((item) => normalizedSearchText(`${item.product} ${item.barcode}`).includes(query)).slice(0, 6) : [];
  if (!matches.length) {
    results.hidden = true;
    results.innerHTML = '';
    return;
  }
  results.hidden = false;
  results.innerHTML = `<p class="search-results-title">${matches.length === 1 ? 'Produit trouvé dans le catalogue' : 'Produits trouvés dans le catalogue'}</p>${matches.map((item, index) => `<div class="search-result"><span class="search-result-art">${icon('boxes')}</span><span class="search-result-name"><b>${escapeHtml(item.product)}</b><small>${item.barcode ? `Code ${escapeHtml(item.barcode)} · ` : ''}${item.quantity} en stock · ${money(item.salePrice)} / unité</small></span><button class="button button-small ${section.id === 'ventes' ? 'button-primary' : 'button-secondary'}" data-search-product="${index}" type="button">${section.id === 'ventes' ? 'Ajouter' : 'Voir le stock'}</button></div>`).join('')}`;
  results.querySelectorAll('[data-search-product]').forEach((button) => button.addEventListener('click', () => {
    const product = matches[Number(button.dataset.searchProduct)];
    if (section.id === 'ventes') {
      const result = addProductToCart(product.product, 1);
      const feedback = document.querySelector('#scanner-feedback');
      feedback.textContent = result.error || `${product.product} ajouté au panier · ${money(product.salePrice)}.`;
      feedback.className = `scanner-hint feedback ${result.error ? 'error' : 'success'}`;
      if (!result.error) refreshCart();
      return;
    }
    workspaceSearches.stock = product.product;
    navigate('stock');
  }));
}

function renderSalesRegister(section) {
  content.innerHTML = `
    <div class="register-layout">
      <section class="panel scanner-panel">
        <div class="scanner-heading"><span class="scanner-emblem">${icon('scan')}</span><div><p class="eyebrow">CAISSE RAPIDE</p><h3>Scanner un article</h3><p>Lecteur USB, douchette ou caméra du téléphone</p></div></div>
        <form class="barcode-form" id="barcode-form"><label class="visually-hidden" for="barcode-input">Code-barres du produit</label><input id="barcode-input" name="barcode" type="search" autocomplete="off" placeholder="Scannez ou saisissez le code-barres" autofocus><button class="button button-primary" type="submit">Ajouter</button><button class="camera-button" id="open-scan" type="button" aria-label="Ouvrir la caméra" title="Scanner avec la caméra">${icon('scan')}</button></form>
        <p class="scanner-hint" id="scanner-feedback" role="status">Après chaque bip du lecteur, l’article rejoint le panier. Associez d’abord un code-barres à l’article dans Entrées.</p>
      </section>
      <section class="panel cart-panel"><div class="panel-heading"><div><h3>Panier de vente</h3><p id="cart-count">${saleCart.reduce((sum, item) => sum + item.quantity, 0)} article(s)</p></div><button class="text-link" id="clear-cart" type="button">Vider</button></div><div class="cart-lines" id="cart-lines">${renderCartLines()}</div><div class="checkout-bar"><label class="checkout-client">Client (facultatif)<input id="checkout-client" maxlength="80" placeholder="Vente comptoir"></label><div class="checkout-total"><span>Total à payer</span><strong id="cart-total">${money(cartTotal())}</strong></div><button class="button button-primary checkout-button" id="checkout-button" type="button" ${saleCart.length ? '' : 'disabled'}>Valider la vente</button></div></section>
    </div>
    <div class="register-lower">${renderComposer(section)}${renderTablePanel(section)}</div>`;
  bindScanner(section);
  bindComposer(section);
  document.querySelector('#barcode-input').focus({ preventScroll: true });
}

function renderCartLines() {
  if (!saleCart.length) return '<div class="cart-empty"><span>▤</span><b>Votre panier est vide</b><p>Scannez un produit pour commencer la vente.</p></div>';
  return saleCart.map((item, index) => `<div class="cart-line"><div class="cart-product"><b>${escapeHtml(item.product)}</b><small>${money(item.unitPrice)} / unité</small></div><div class="quantity-stepper"><button data-cart-action="minus" data-index="${index}" type="button" aria-label="Retirer une unité de ${escapeHtml(item.product)}">−</button><span>${item.quantity}</span><button data-cart-action="plus" data-index="${index}" type="button" aria-label="Ajouter une unité de ${escapeHtml(item.product)}">+</button></div><strong class="cart-line-total">${money(item.quantity * item.unitPrice)}</strong><button class="remove-line" data-cart-action="remove" data-index="${index}" type="button" aria-label="Retirer ${escapeHtml(item.product)} du panier">×</button></div>`).join('');
}

function cartTotal() {
  return saleCart.reduce((sum, item) => sum + item.quantity * item.unitPrice, 0);
}

function refreshCart() {
  const lines = document.querySelector('#cart-lines');
  if (!lines) return;
  lines.innerHTML = renderCartLines();
  document.querySelector('#cart-count').textContent = `${saleCart.reduce((sum, item) => sum + item.quantity, 0)} article(s)`;
  document.querySelector('#cart-total').textContent = money(cartTotal());
  document.querySelector('#checkout-button').disabled = saleCart.length === 0;
  lines.querySelectorAll('[data-cart-action]').forEach((button) => button.addEventListener('click', () => {
    const index = Number(button.dataset.index);
    const item = saleCart[index];
    if (button.dataset.cartAction === 'remove') saleCart.splice(index, 1);
    if (button.dataset.cartAction === 'minus') {
      item.quantity -= 1;
      if (!item.quantity) saleCart.splice(index, 1);
    }
    if (button.dataset.cartAction === 'plus') {
      const result = addProductToCart(item.product, 1);
      if (result.error) {
        const feedback = document.querySelector('#scanner-feedback');
        feedback.textContent = result.error;
        feedback.className = 'scanner-hint feedback error';
      }
    }
    refreshCart();
  }));
}

function addProductToCart(productName, quantity) {
  const stock = currentStock(productName);
  const catalog = productRecord(productName);
  if (!stock || !catalog) return { error: `Produit « ${productName} » absent du stock.` };
  const cartItem = saleCart.find((item) => item.product.toLocaleLowerCase('fr') === productName.toLocaleLowerCase('fr'));
  const alreadyInCart = cartItem?.quantity || 0;
  if (stock.quantity - alreadyInCart < quantity) return { error: `Stock insuffisant pour ${productName}. Disponible : ${Math.max(stock.quantity - alreadyInCart, 0)}.` };
  if (cartItem) cartItem.quantity += quantity;
  else saleCart.push({ product: catalog.product, unitPrice: catalog.salePrice, quantity });
  return { record: catalog };
}

function addScannedBarcode(barcode) {
  const code = String(barcode || '').trim();
  const entry = data.entries.slice().reverse().find((item) => item.barcode && item.barcode === code);
  const feedback = document.querySelector('#scanner-feedback');
  if (!entry) {
    feedback.textContent = `Code ${code} inconnu. Enregistrez-le d’abord avec le produit dans Entrées.`;
    feedback.className = 'scanner-hint feedback error';
    return false;
  }
  const result = addProductToCart(entry.product, 1);
  if (result.error) {
    feedback.textContent = result.error;
    feedback.className = 'scanner-hint feedback error';
    return false;
  }
  feedback.textContent = `${entry.product} ajouté au panier · ${money(entry.salePrice)}.`;
  feedback.className = 'scanner-hint feedback success';
  showToast(`${entry.product} ajouté au panier`);
  refreshCart();
  return true;
}

function bindScanner() {
  document.querySelector('#barcode-form').addEventListener('submit', (event) => {
    event.preventDefault();
    const input = document.querySelector('#barcode-input');
    if (input.value.trim()) addScannedBarcode(input.value);
    input.value = '';
    input.focus();
  });
  document.querySelector('#clear-cart').addEventListener('click', () => {
    saleCart = [];
    refreshCart();
  });
  document.querySelector('#checkout-button').addEventListener('click', async () => {
    if (!saleCart.length) return;
    const client = document.querySelector('#checkout-client').value.trim() || 'Vente comptoir';
    try {
      await apiRequest('/api/sales', {
        method: 'POST',
        body: JSON.stringify({ items: saleCart.map(({ product, quantity }) => ({ product, quantity })), client }),
      });
      saleCart = [];
      await refreshSharedData();
      showToast('Vente validée, stock partagé mis à jour');
      renderPage();
    } catch (error) {
      const feedback = document.querySelector('#scanner-feedback');
      feedback.textContent = error.message;
      feedback.className = 'scanner-hint feedback error';
      await refreshSharedData().catch(() => {});
      refreshCart();
    }
  });
  document.querySelector('#open-scan').addEventListener('click', openCameraScanner);
  refreshCart();
}

async function openCameraScanner() {
  const modal = document.querySelector('#scan-modal');
  const status = document.querySelector('#camera-status');
  const placeholder = document.querySelector('#camera-placeholder');
  if (!modal.open) modal.showModal();
  if (!navigator.mediaDevices?.getUserMedia) {
    status.textContent = 'Caméra indisponible ici. Utilisez un lecteur USB ou saisissez le code dans la caisse.';
    return;
  }
  if (!('BarcodeDetector' in window)) {
    status.textContent = 'Le scan caméra n’est pas pris en charge par ce navigateur. Utilisez une douchette USB ou saisissez le code-barres dans la caisse.';
    return;
  }
  status.textContent = 'Démarrage de la caméra…';
  try {
    const supported = await window.BarcodeDetector.getSupportedFormats();
    const formats = ['ean_13', 'ean_8', 'upc_a', 'upc_e', 'code_128', 'code_39', 'itf', 'qr_code'].filter((format) => supported.includes(format));
    const detector = new window.BarcodeDetector({ formats });
    cameraStream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: { ideal: 'environment' } }, audio: false });
    const video = document.querySelector('#scan-video');
    video.srcObject = cameraStream;
    await video.play();
    placeholder.hidden = true;
    status.textContent = 'Placez un code-barres dans le cadre.';
    scanCameraFrame(detector, video);
  } catch (error) {
    stopCameraScanner();
    placeholder.hidden = false;
    status.textContent = error.name === 'NotAllowedError'
      ? 'Accès caméra refusé. Autorisez la caméra dans le navigateur ou utilisez une douchette USB.'
      : 'Impossible d’ouvrir la caméra. Vérifiez ses permissions ou utilisez une douchette USB.';
  }
}

async function scanCameraFrame(detector, video) {
  if (!cameraStream || !document.querySelector('#scan-modal').open) return;
  if (video.readyState >= HTMLMediaElement.HAVE_CURRENT_DATA) {
    try {
      const [match] = await detector.detect(video);
      if (match?.rawValue) {
        const added = addScannedBarcode(match.rawValue);
        if (added) {
          document.querySelector('#scan-modal').close();
          return;
        }
      }
    } catch {
      document.querySelector('#camera-status').textContent = 'Lecture impossible. Rapprochez le code du cadre ou utilisez une douchette USB.';
    }
  }
  cameraTimer = setTimeout(() => scanCameraFrame(detector, video), 220);
}

function stopCameraScanner() {
  clearTimeout(cameraTimer);
  cameraTimer = null;
  cameraStream?.getTracks().forEach((track) => track.stop());
  cameraStream = null;
  const video = document.querySelector('#scan-video');
  if (video) video.srcObject = null;
  const placeholder = document.querySelector('#camera-placeholder');
  if (placeholder) placeholder.hidden = false;
}

function renderComposer(section) {
  if (activeRole === 'agent' && ['entrees', 'stock', 'inventaire', 'portefeuille'].includes(section.id)) return '<section class="panel composer"><div class="composer-label">Accès réservé au gérant <span>Compte agent</span></div><p class="page-subtitle">Seul le gérant peut modifier le catalogue, les prix d’achat et le portefeuille.</p></section>';
  const disabled = ['stock', 'inventaire'].includes(section.id);
  const barcodeField = section.id === 'entrees' ? '<label class="barcode-catalog-field">Code-barres (facultatif)<input id="entry-barcode" name="barcode" inputmode="numeric" autocomplete="off" placeholder="Scannez ici avec votre douchette"></label>' : '';
  return `<form class="panel composer" id="message-form"><label class="composer-label" for="message-input">${disabled ? 'Zone de consultation' : 'Saisie rapide'}<span>${activeRole === 'agent' ? 'Espace agent' : 'Espace gérant'}</span></label><textarea class="message-box" id="message-input" name="message" ${disabled ? 'readonly' : ''} placeholder="${escapeHtml(section.placeholder)}" aria-describedby="message-hint"></textarea>${barcodeField}<p class="message-hint" id="message-hint">${section.hint}</p>${disabled ? '' : `<div class="composer-actions"><button class="button button-primary button-small" type="submit">Enregistrer <span aria-hidden="true">→</span></button><button class="button button-secondary button-small" id="clear-message" type="button">Effacer</button></div>`}<div class="feedback" id="feedback" aria-live="polite"></div></form>`;
}

function rowsForSection(sectionId) {
  if (sectionId === 'entrees') return dailyRecords(data.entries).slice().reverse().map((item) => [formatDate(item.createdAt, { hour: '2-digit', minute: '2-digit' }), item.product, item.barcode || '—', item.quantity, money(item.purchasePrice), money(item.salePrice)]);
  if (sectionId === 'ventes') return dailyRecords(data.sales).slice().reverse().map((item) => [formatDate(item.createdAt, { hour: '2-digit', minute: '2-digit' }), item.client, item.product, item.quantity, money(item.amount)]);
  if (sectionId === 'depenses') return dailyRecords(data.expenses).slice().reverse().map((item) => [formatDate(item.createdAt, { hour: '2-digit', minute: '2-digit' }), item.motive, money(item.amount), item.responsible]);
  if (sectionId === 'credits') return data.credits.slice().reverse().map((item) => [item.client, item.product, item.quantity, money(item.balance), formatDate(item.dueAt), item.status]);
  if (sectionId === 'portefeuille') return dailyRecords(data.wallet).slice().reverse().map((item) => [item.agent, money(item.amount), formatDate(item.createdAt), item.observation]);
  if (sectionId === 'stock') return allStock().map((item) => {
    const state = item.quantity <= 0 ? ['Vide', 'empty'] : item.quantity <= 5 ? ['Stock bas', 'low'] : new Date(item.updatedAt).getTime() < Date.now() - 7 * 86400000 ? ['À écouler', 'stale'] : ['Disponible', ''];
    return [item.product, 'Unité', item.quantity, money(item.quantity * item.purchasePrice), `<span class="stock-state ${state[1]}"><i></i>${state[0]}</span>`];
  });
  if (sectionId === 'inventaire') return allStock().map((item) => {
    const sold = dailyRecords(data.sales).filter((sale) => sale.product === item.product).reduce((sum, sale) => sum + sale.quantity, 0);
    const profit = dailyRecords(data.sales).filter((sale) => sale.product === item.product).reduce((sum, sale) => sum + sale.quantity * (sale.unitPrice - item.purchasePrice), 0);
    return [item.product, money(item.purchasePrice), money(item.salePrice), money(profit), sold ? `${sold} vendu(s) aujourd’hui` : 'Aucun mouvement aujourd’hui'];
  });
  return [];
}

function renderTablePanel(section) {
  if (activeRole === 'agent') return `<section class="panel composer"><div class="composer-label">Tableau gérant <span>Accès limité</span></div><p class="page-subtitle">Les détails et les totaux sont réservés au gérant.</p></section>`;
  if (section.id === 'stock') {
    const stock = allStock();
    const totalValue = stock.reduce((sum, item) => sum + Math.max(item.quantity, 0) * item.purchasePrice, 0);
    return `<section class="panel table-panel"><div class="panel-heading"><div><h3>État du stock</h3><p>Quantités après entrées et ventes</p></div></div><div class="stock-summary"><span>Références<b>${stock.length}</b></span><span>Valeur d’achat estimée<b>${money(totalValue)}</b></span></div>${renderTable(section, rowsForSection(section.id))}</section>`;
  }
  const rows = rowsForSection(section.id);
  let total = null;
  if (section.id === 'ventes') total = ['Solde des ventes du jour', money(dailyTotals().sales)];
  if (section.id === 'depenses') total = ['Solde des dépenses du jour', money(dailyTotals().expenses)];
  if (section.id === 'entrees') total = ['Achats du jour', money(dailyTotals().purchases)];
  return `<section class="panel table-panel"><div class="panel-heading"><div><h3>${section.id === 'credits' ? 'Suivi des échéances' : section.id === 'inventaire' ? 'Bilan du jour' : `Mouvements du jour`}</h3><p>${section.id === 'credits' ? 'Les soldes restants à recouvrer' : 'Calculé à partir des opérations saisies'}</p></div></div>${renderTable(section, rows)}${total ? `<div class="total-strip"><span>${total[0]}</span><strong>${total[1]}</strong></div>` : ''}</section>`;
}

function renderTable(section, rows) {
  const headings = section.columns.map((column) => `<th>${escapeHtml(column)}</th>`).join('');
  const body = rows.length ? rows.map((row) => `<tr>${row.map((cell) => `<td>${String(cell).startsWith('<span class="stock-state') ? cell : escapeHtml(cell)}</td>`).join('')}</tr>`).join('') : `<tr class="empty-row"><td colspan="${section.columns.length}">Aucune donnée pour le moment.</td></tr>`;
  return `<div class="table-scroll"><table class="data-table"><thead><tr>${headings}</tr></thead><tbody>${body}</tbody></table></div>`;
}

function renderBible() {
  const reading = bibleReadings[bibleReadingIndex];
  const panel = content.querySelector('.bible-panel');
  const readingMarkup = `<p class="eyebrow">MOTIVATION</p><h3>${reading.motivation}</h3><p>${reading.verse}</p><div class="bible-ref">${reading.reference}</div>`;
  if (panel) panel.innerHTML = readingMarkup;
  else content.insertAdjacentHTML('beforeend', `<section class="panel bible-panel">${readingMarkup}</section>`);

  if (!bibleTimer) {
    bibleTimer = setInterval(() => {
      if (activeSection !== 'bible') return;
      bibleReadingIndex = (bibleReadingIndex + 1) % bibleReadings.length;
      renderBible();
    }, 5 * 60 * 1000);
  }
}

function bindComposer(section) {
  const form = document.querySelector('#message-form');
  if (!form) return;
  const clearButton = document.querySelector('#clear-message');
  clearButton?.addEventListener('click', () => {
    form.reset();
    const feedback = document.querySelector('#feedback');
    feedback.textContent = '';
    feedback.className = 'feedback';
  });
  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    const message = new FormData(form).get('message')?.toString().trim() || '';
    const result = parseMessage(section.id, message);
    const feedback = document.querySelector('#feedback');
    if (result.error) {
      feedback.textContent = result.error;
      feedback.className = 'feedback error';
      return;
    }
    const record = result.record;
    if (section.id === 'entrees') {
      record.barcode = new FormData(form).get('barcode')?.toString().trim() || '';
      const existing = data.entries.find((entry) => entry.barcode === record.barcode && record.barcode);
      if (existing && existing.product.toLocaleLowerCase('fr') !== record.product.toLocaleLowerCase('fr')) {
        feedback.textContent = 'Ce code-barres est déjà associé à un autre produit.';
        feedback.className = 'feedback error';
        return;
      }
    }
    const endpoints = {
      entrees: ['/api/entries', { ...record }],
      ventes: ['/api/sales', { items: [{ product: record.product, quantity: record.quantity }], client: record.client }],
      depenses: ['/api/expenses', { motive: record.motive, amount: record.amount, responsible: record.responsible }],
      credits: ['/api/credits', { client: record.client, product: record.product, quantity: record.quantity, phone: record.phone, dueAt: record.dueAt }],
      portefeuille: ['/api/wallet', { agent: record.agent, amount: record.amount, observation: record.observation }],
    };
    try {
      const [endpoint, body] = endpoints[section.id];
      await apiRequest(endpoint, { method: 'POST', body: JSON.stringify(body) });
      await refreshSharedData();
      showToast('Opération enregistrée et partagée');
      renderPage();
    } catch (error) {
      feedback.textContent = error.message;
      feedback.className = 'feedback error';
    }
  });
}

let authMode = 'login';
let authSettings = { initialized: true, setupConfigured: false, publicRegistrationEnabled: false };

function setAuthenticatedView() {
  activeRole = currentUser.role;
  welcome.hidden = true;
  appShell.hidden = false;
  document.querySelector('#account-badge').textContent = `${activeRole === 'gerant' ? 'Gérant' : 'Agent'} · ${currentUser.username}`;
  document.querySelector('#settings-button').hidden = activeRole !== 'gerant';
  document.querySelector('#prototype-notice').hidden = activeRole !== 'gerant';
  renderNavigation();
  renderPage();
}

function showAuthMode(settings) {
  authSettings = settings;
  authMode = settings.initialized ? 'login' : 'setup';
  updateAuthMode();
}

function updateAuthMode() {
  const setupMode = authMode === 'setup';
  const registerMode = authMode === 'register';
  const fields = document.querySelector('#setup-fields');
  fields.hidden = !setupMode && !registerMode;
  fields.querySelectorAll('input').forEach((input) => { input.disabled = !setupMode && !registerMode; });
  const setupKey = document.querySelector('#setup-key-field');
  setupKey.hidden = !setupMode;
  setupKey.querySelector('input').required = setupMode;
  document.querySelector('#setup-explainer').textContent = setupMode
    ? authSettings.setupConfigured
      ? 'Saisissez le code secret défini par l’administrateur du serveur pour créer le premier compte gérant.'
      : 'L’administrateur doit d’abord définir UZAA_SETUP_KEY dans la configuration du serveur.'
    : 'Créez le compte de votre établissement. Le gérant crée ensuite les comptes des agents.';
  document.querySelector('#auth-title').textContent = setupMode ? 'Initialiser le commerce' : registerMode ? 'Créer le compte de mon commerce' : 'Connexion';
  document.querySelector('#auth-submit').textContent = setupMode ? 'Créer le compte gérant' : registerMode ? 'Créer mon compte commerce' : 'Se connecter';
  document.querySelector('#auth-form [name="password"]').setAttribute('autocomplete', setupMode || registerMode ? 'new-password' : 'current-password');
  const modeToggle = document.querySelector('#auth-mode-toggle');
  modeToggle.hidden = !authSettings.publicRegistrationEnabled;
  modeToggle.textContent = registerMode
    ? authSettings.initialized ? 'Déjà inscrit ? Se connecter' : 'Retour à l’initialisation'
    : 'Créer un compte commerce';
  const feedback = document.querySelector('#auth-feedback');
  feedback.textContent = '';
  feedback.className = 'feedback';
}

async function openAuthDialog() {
  const feedback = document.querySelector('#auth-feedback');
  try {
    const authStatus = await apiRequest('/api/auth/status');
    showAuthMode(authStatus);
  } catch (error) {
    showAuthMode({ initialized: true, setupConfigured: false, publicRegistrationEnabled: false });
    feedback.textContent = `Serveur indisponible : ${error.message}`;
    feedback.className = 'feedback error';
  }
  document.querySelector('#auth-modal').showModal();
}

document.querySelector('#open-app').addEventListener('click', openAuthDialog);
document.querySelector('#auth-mode-toggle').addEventListener('click', () => {
  authMode = authMode === 'register' ? (authSettings.initialized ? 'login' : 'setup') : 'register';
  updateAuthMode();
});
document.querySelector('#auth-form').addEventListener('submit', async (event) => {
  event.preventDefault();
  const form = event.currentTarget;
  const values = Object.fromEntries(new FormData(form).entries());
  const feedback = document.querySelector('#auth-feedback');
  feedback.textContent = '';
  feedback.className = 'feedback';
  try {
    const result = authMode === 'setup'
      ? await apiRequest('/api/auth/setup', { method: 'POST', body: JSON.stringify({
        setup_key: values.setup_key,
        username: values.username,
        password: values.password,
        establishment: values.establishment,
        address: values.address,
        telephone: values.telephone,
        email: values.email,
      }) })
      : authMode === 'register'
      ? await apiRequest('/api/auth/register', { method: 'POST', body: JSON.stringify({
        username: values.username,
        password: values.password,
        establishment: values.establishment,
        address: values.address,
        telephone: values.telephone,
        email: values.email,
        website: values.website,
      }) })
      : await apiRequest('/api/auth/login', { method: 'POST', body: JSON.stringify({ username: values.username, password: values.password }) });
    authToken = result.token;
    currentUser = result.user;
    sessionStorage.setItem('uzaapp.session', authToken);
    await refreshSharedData();
    form.reset();
    document.querySelector('#auth-modal').close();
    setAuthenticatedView();
    showToast(authMode === 'setup' || authMode === 'register' ? 'Compte gérant créé' : 'Connexion réussie');
  } catch (error) {
    feedback.textContent = error.message;
    feedback.className = 'feedback error';
  }
});

document.querySelector('#logout-button').addEventListener('click', async () => {
  try { await apiRequest('/api/auth/logout', { method: 'POST' }); } catch { /* La session locale est quand même supprimée. */ }
  authToken = '';
  currentUser = null;
  data = structuredClone(initialData);
  sessionStorage.removeItem('uzaapp.session');
  appShell.hidden = true;
  welcome.hidden = false;
  showToast('Vous êtes déconnecté');
});

document.querySelector('#settings-button').addEventListener('click', () => {
  if (activeRole !== 'gerant') return;
  const form = document.querySelector('#profile-form');
  for (const [key, value] of Object.entries(data.profile)) if (form.elements[key]) form.elements[key].value = value;
  document.querySelector('#team-section').hidden = activeRole !== 'gerant';
  document.querySelector('#settings-modal').showModal();
  refreshAgentList();
});

document.querySelector('#backup-button').addEventListener('click', async () => {
  try {
    const result = await apiRequest('/api/backup', { method: 'POST' });
    showToast(`Sauvegarde créée : ${result.name}`);
  } catch (error) {
    showToast(error.message);
  }
});

async function refreshAgentList() {
  const list = document.querySelector('#agent-list');
  try {
    const agents = await apiRequest('/api/agents');
    list.innerHTML = agents.length ? agents.map((agent) => `
      <div class="agent-row"><span><b>${escapeHtml(agent.username)}</b> <small>${agent.active ? 'Actif' : 'Désactivé'}</small></span>
      ${agent.active ? `<button class="agent-revoke" data-revoke-agent="${agent.id}" type="button">Révoquer l’accès</button>` : ''}</div>`).join('') : '<p class="modal-hint">Aucun compte agent créé.</p>';
    list.querySelectorAll('[data-revoke-agent]').forEach((button) => button.addEventListener('click', async () => {
      if (!window.confirm('Révoquer cet accès ? Toutes les sessions de cet agent seront fermées.')) return;
      try {
        await apiRequest(`/api/agents/${button.dataset.revokeAgent}`, { method: 'DELETE' });
        showToast('Accès agent révoqué');
        await refreshAgentList();
      } catch (error) {
        showToast(error.message);
      }
    }));
  } catch (error) {
    list.textContent = error.message;
  }
}

document.querySelector('#profile-form').addEventListener('submit', async (event) => {
  event.preventDefault();
  const profile = Object.fromEntries(new FormData(event.currentTarget).entries());
  try {
    await apiRequest('/api/profile', { method: 'PUT', body: JSON.stringify(profile) });
    await refreshSharedData();
    document.querySelector('#settings-modal').close();
    renderPage();
    showToast('Profil de l’établissement enregistré');
  } catch (error) {
    showToast(error.message);
  }
});
document.querySelector('#agent-form').addEventListener('submit', async (event) => {
  event.preventDefault();
  const form = event.currentTarget;
  const feedback = document.querySelector('#agent-feedback');
  try {
    const result = await apiRequest('/api/agents', { method: 'POST', body: JSON.stringify(Object.fromEntries(new FormData(form).entries())) });
    feedback.textContent = `Compte agent « ${result.username} » créé. Remettez son mot de passe en privé.`;
    feedback.className = 'feedback success';
    form.reset();
    await refreshAgentList();
  } catch (error) {
    feedback.textContent = error.message;
    feedback.className = 'feedback error';
  }
});
document.querySelector('#date-button').addEventListener('click', () => showToast('Les totaux affichés correspondent à la journée en cours.'));
document.querySelector('#close-scan').addEventListener('click', () => document.querySelector('#scan-modal').close());
document.querySelector('#retry-camera').addEventListener('click', openCameraScanner);
document.querySelector('#scan-modal').addEventListener('close', stopCameraScanner);

async function restoreSession() {
  if (!authToken) return;
  try {
    currentUser = await apiRequest('/api/auth/me');
    await refreshSharedData();
    setAuthenticatedView();
  } catch {
    authToken = '';
    currentUser = null;
    sessionStorage.removeItem('uzaapp.session');
  }
}

window.addEventListener('focus', async () => {
  if (!currentUser || document.activeElement?.matches('input, textarea')) return;
  try {
    await refreshSharedData();
    renderPage();
  } catch (error) {
    showToast(error.message);
  }
});

if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => navigator.serviceWorker.register('./service-worker.js').catch(() => {}));
}

restoreSession();
