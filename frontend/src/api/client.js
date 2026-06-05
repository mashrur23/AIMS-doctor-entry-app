const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api";
const isLocalFrontend = ["localhost", "127.0.0.1"].includes(window.location.hostname);

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });

  const contentType = response.headers.get("content-type") || "";
  const body = contentType.includes("application/json") ? await response.json() : await response.text();

  if (!response.ok) {
    throw new Error(body?.error || "Request failed.");
  }

  return body;
}

export function saveConsultation(payload) {
  return request("/consultations/", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function getExcelExportUrl() {
  return `${API_BASE_URL}/export/excel/`;
}

export async function exportAllConsultationsExcel() {
  if (isLocalFrontend) {
    return request("/export/excel/save-to-downloads/");
  }

  window.location.href = getExcelExportUrl();
  return {
    filename: "aims_consultations_export.xlsx",
    path: "Browser download started",
    rows: "all",
  };
}
