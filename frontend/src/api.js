const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, options);
  if (!response.ok) {
    let payload;
    try {
      payload = await response.json();
    } catch {
      payload = null;
    }

    const detail = payload?.detail || payload?.message || `Request failed with status ${response.status}`;
    throw new Error(detail);
  }

  return response.json();
}

export function formatApiError(error) {
  return error?.message || 'Unable to connect with backend. Please check API server.';
}

export async function createComplaint(form) {
  const payload = {
    description: form.description,
    location: form.location,
    citizen_name: form.citizen_name || null,
    contact_number: form.contact_number || null,
    reported_via: 'web'
  };

  return request('/complaints', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
}

export async function uploadComplaint({ image, ...form }) {
  const body = new FormData();
  body.append('description', form.description);
  body.append('location', form.location);
  body.append('reported_via', 'web');
  if (form.citizen_name) {
    body.append('citizen_name', form.citizen_name);
  }
  if (form.contact_number) {
    body.append('contact_number', form.contact_number);
  }
  if (image) {
    body.append('image', image);
  }

  return request('/complaints/upload', {
    method: 'POST',
    body
  });
}

export async function classifyImage(image) {
  const body = new FormData();
  body.append('image', image);
  const payload = await request('/complaints/classify-image', {
    method: 'POST',
    body
  });
  return payload.data;
}

export async function fetchComplaintList() {
  return request('/complaints?limit=10');
}

export async function fetchDashboardSummary() {
  return request('/dashboard/summary');
}
