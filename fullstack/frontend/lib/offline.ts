/** Offline-first queue: log locally in IndexedDB, flush to /sync when back online. */
const DB = "aura", STORE = "outbox";
const open = () => new Promise<IDBDatabase>((ok, fail) => {
  const r = indexedDB.open(DB, 1);
  r.onupgradeneeded = () => r.result.createObjectStore(STORE, { keyPath: "id" });
  r.onsuccess = () => ok(r.result); r.onerror = () => fail(r.error);
});
const tx = async <T,>(mode: IDBTransactionMode, fn: (s: IDBObjectStore) => IDBRequest<T>) => {
  const db = await open();
  return new Promise<T>((ok, fail) => { const q = fn(db.transaction(STORE, mode).objectStore(STORE)); q.onsuccess = () => ok(q.result); q.onerror = () => fail(q.error); });
};
export async function logEvent(kind: string, payload: unknown) {
  await tx("readwrite", (s) => s.put({ id: crypto.randomUUID(), kind, payload, ts: new Date().toISOString() }));
  if (navigator.onLine) flush();
}
export async function flush(token = localStorage.getItem("aura_token") ?? "") {
  const items = await tx("readonly", (s) => s.getAll());
  if (!items.length || !token) return;
  const r = await fetch(`${process.env.NEXT_PUBLIC_SYNC_URL}/sync`, { method: "POST", headers: { "content-type": "application/json", authorization: `Bearer ${token}` }, body: JSON.stringify({ items }) });
  if (r.ok) for (const id of (await r.json()).accepted) await tx("readwrite", (s) => s.delete(id));
}
if (typeof window !== "undefined") window.addEventListener("online", () => flush());
