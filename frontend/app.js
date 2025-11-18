const API_BASE = 'http://localhost:8000';

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
  const response = await fetch(`${API_BASE}/pcf/run`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ product_id: 'prod-frontend' }),
  });
  display(await response.json());
}

async function runCircularity() {
  const response = await fetch(`${API_BASE}/circularity/run`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ product_id: 'prod-frontend' }),
  });
  display(await response.json());
}

function display(data) {
  document.getElementById('output').textContent = JSON.stringify(data, null, 2);
}

document.getElementById('upload-bom').addEventListener('click', uploadBOM);
document.getElementById('run-pcf').addEventListener('click', runPCF);
document.getElementById('run-circularity').addEventListener('click', runCircularity);
