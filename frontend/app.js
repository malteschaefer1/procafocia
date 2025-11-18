const API_BASE = 'http://localhost:8000';

function getProductId() {
  return document.getElementById('product-id').value || 'prod-frontend';
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
  const response = await fetch(`${API_BASE}/bom/upload`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(bom),
  });
  display(await response.json());
}

async function runPCF() {
  const productId = getProductId();
  const response = await fetch(`${API_BASE}/pcf/run`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ product_id: productId }),
  });
  display(await response.json());
}

async function runCircularity() {
  const productId = getProductId();
  const response = await fetch(`${API_BASE}/circularity/run`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ product_id: productId }),
  });
  display(await response.json());
}

async function reviewMapping() {
  const productId = getProductId();
  const response = await fetch(`${API_BASE}/mapping/review/${productId}`);
  display(await response.json());
}

document.getElementById('review-mapping').addEventListener('click', reviewMapping);
  });
  display(await response.json());
}

function display(data) {
  document.getElementById('output').textContent = JSON.stringify(data, null, 2);
}

document.getElementById('upload-bom').addEventListener('click', uploadBOM);
document.getElementById('run-pcf').addEventListener('click', runPCF);
document.getElementById('run-circularity').addEventListener('click', runCircularity);
