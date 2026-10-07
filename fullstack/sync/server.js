import express from "express"; import helmet from "helmet"; import rateLimit from "express-rate-limit";
import jwt from "jsonwebtoken"; import bcrypt from "bcryptjs"; import pg from "pg";

const pool = new pg.Pool({ host: "postgres", user: "aura", password: process.env.PG_PASSWORD, database: "aura" });
const SECRET = process.env.JWT_SECRET;
await pool.query(`CREATE TABLE IF NOT EXISTS users(id serial PRIMARY KEY, email text UNIQUE, pw text, role text DEFAULT 'user');
 CREATE TABLE IF NOT EXISTS logs(id text PRIMARY KEY, user_id int, kind text, payload jsonb, ts timestamptz);`);

const app = express();
app.use(helmet(), express.json({ limit: "1mb" }), rateLimit({ windowMs: 60_000, limit: 120 }));
const sign = (u) => jwt.sign({ sub: u.id, role: u.role }, SECRET, { algorithm: "HS256", expiresIn: "1h" });
const auth = (req, res, next) => {
  try { req.user = jwt.verify((req.headers.authorization || "").slice(7), SECRET, { algorithms: ["HS256"] }); next(); }
  catch { res.status(401).json({ error: "invalid token" }); }
};

app.post("/auth/register", async (req, res) => {
  const { email, password } = req.body;
  if (!email || (password || "").length < 10) return res.status(422).json({ error: "email and 10+ char password required" });
  try {
    const { rows } = await pool.query("INSERT INTO users(email,pw) VALUES($1,$2) RETURNING id,role", [email, await bcrypt.hash(password, 12)]);
    res.status(201).json({ token: sign(rows[0]) });
  } catch { res.status(409).json({ error: "email already registered" }); }
});
app.post("/auth/login", async (req, res) => {
  const { rows } = await pool.query("SELECT * FROM users WHERE email=$1", [req.body.email]);
  if (!rows[0] || !(await bcrypt.compare(req.body.password || "", rows[0].pw))) return res.status(401).json({ error: "wrong email or password" });
  res.json({ token: sign(rows[0]) });
});
// Idempotent batch upload of offline logs (client-generated ids make retries safe).
app.post("/sync", auth, async (req, res) => {
  const items = Array.isArray(req.body.items) ? req.body.items.slice(0, 500) : [];
  for (const i of items)
    await pool.query("INSERT INTO logs VALUES($1,$2,$3,$4,$5) ON CONFLICT DO NOTHING", [i.id, req.user.sub, i.kind, i.payload, i.ts]);
  res.json({ accepted: items.map((i) => i.id) });
});
app.get("/health", (_, r) => r.json({ status: "ok" }));
app.listen(4000);
