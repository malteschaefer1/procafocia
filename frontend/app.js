const API_BASE = 'http://localhost:8000';

function getProductId() {
  return document.getElementById('product-id').value || 'prod-frontend';
}

function getSelectedMethodId() {
  const select = document.getElementById('pcf-method');
  return select && select.value ? select.value : null;
}

async function uploadBOM() {
  const bomText = document.getElementById('bom-input').value;
  let bom;
  try {
    bom = JSON.parse(bomText);
  } catch (err) {
    display(JSON.stringify({ error: 'Invalid JSON' }, null, 2));
    return;
  }
  const productId = getProductId();
  await ensureProductExists(productId);
  const response = await safeFetch(`${API_BASE}/bom/upload`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(bom),
  });
  display(response);
}

async function runPCF() {
  const productId = getProductId();
  const payload = { product_id: productId };
  const methodId = getSelectedMethodId();
  if (methodId) {
    payload.pcf_method_id = methodId;
  }
  await ensureProductExists(productId);
  const response = await safeFetch(`${API_BASE}/pcf/run`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  display(response);
}

async function runCircularity() {
  const productId = getProductId();
  await ensureProductExists(productId);
  const response = await safeFetch(`${API_BASE}/circularity/run`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ product_id: productId }),
  });
  display(response);
}

async function reviewMapping() {
  const productId = getProductId();
  await ensureProductExists(productId);
  const response = await safeFetch(`${API_BASE}/mapping/review/${productId}`);
  display(response);
}

async function loadMethods() {
  const select = document.getElementById('pcf-method');
  if (!select) return;
  try {
    const data = await safeFetch(`${API_BASE}/pcf/methods`);
    select.innerHTML = '';
    (data.methods || []).forEach((method) => {
      const option = document.createElement('option');
      option.value = method.id;
      option.textContent = `${method.name} (${method.system_boundary})`;
      option.title = method.short_description;
      select.appendChild(option);
    });
  } catch (err) {
    console.error('Failed to load PCF methods', err);
    select.innerHTML = '<option value="">Unavailable</option>';
  }
}

async function ensureProductExists(productId) {
  const payload = {
    id: productId,
    name: productId,
    version: '1',
    functional_unit: '1 unit',
  };
  try {
    await safeFetch(`${API_BASE}/products`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
  } catch (err) {
    // Ignore if product already exists
  }
}

async function safeFetch(url, options) {
  try {
    const response = await fetch(url, options);
    const text = await response.text();
    const data = text ? JSON.parse(text) : {};
    if (!response.ok) {
      return { error: data.detail || data.error || 'Request failed', status: response.status };
    }
    return data;
  } catch (err) {
    return { error: err.message || 'Network error' };
  }
}

function display(data) {
  document.getElementById('output').textContent = JSON.stringify(data, null, 2);
}

document.addEventListener('DOMContentLoaded', () => {
  loadMethods();
  document.getElementById('upload-bom').addEventListener('click', uploadBOM);
  document.getElementById('run-pcf').addEventListener('click', runPCF);
  document.getElementById('run-circularity').addEventListener('click', runCircularity);
  document.getElementById('review-mapping').addEventListener('click', reviewMapping);
});
