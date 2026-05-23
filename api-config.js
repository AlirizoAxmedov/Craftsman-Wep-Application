/**
 * Kandakorlik Platform — API Client Config
 *
 * When the HTML is opened as a local file (file://), the browser sends
 * Origin: null which does not match wildcard '*' — so we point all requests
 * explicitly to http://localhost:8000.
 */

const ApiConfig = (() => {
  const BASE_URL =
    window.location.origin === 'null' || window.location.protocol === 'file:'
      ? 'http://localhost:8000'
      : window.location.origin;

  async function request(endpoint, options = {}) {
    const token = localStorage.getItem('knd_token');

    const headers = {
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    };
    if (token) headers['Authorization'] = 'Bearer ' + token;

    let response;
    try {
      response = await fetch(BASE_URL + endpoint, { ...options, headers });
    } catch (networkErr) {
      throw new Error(
        'Backend bilan aloqa yo\'q. Backend ishlaydimi? (http://localhost:8000)'
      );
    }

    if (response.status === 204) return null;

    if (response.status === 401) {
      localStorage.removeItem('knd_token');
      throw new Error('Sessiya tugadi. Qayta kiring.');
    }

    if (!response.ok) {
      let detail = 'Server xatosi';
      try {
        const body = await response.json();
        detail = body.detail || detail;
      } catch (_) {}
      throw new Error(detail);
    }

    return response.json();
  }

  return { baseURL: BASE_URL, request };
})();
