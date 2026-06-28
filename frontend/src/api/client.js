// Empty base = same-origin relative requests (production: nginx proxies /documents,
// /chat, etc. to the backend). For local `npm run dev`, set VITE_API_BASE in .env.
const BASE = import.meta.env.VITE_API_BASE || "";

async function request(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    throw new Error(`${res.status} ${res.statusText}`);
  }
  return res.status === 204 ? null : res.json();
}

export const api = {
  listDocuments: () => request("/documents"),
  createDocument: (doc) =>
    request("/documents", { method: "POST", body: JSON.stringify(doc) }),
  deleteDocument: (id) => request(`/documents/${id}`, { method: "DELETE" }),
  sendChat: (message, conversationId) =>
    request("/chat", {
      method: "POST",
      body: JSON.stringify({ message, conversation_id: conversationId }),
    }),
};
