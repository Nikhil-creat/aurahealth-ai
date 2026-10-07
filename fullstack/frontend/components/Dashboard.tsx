"use client";
import { useEffect, useMemo, useRef, useState } from "react";
import { motion } from "framer-motion";
import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

type Metrics = { bmi: number; bmr: number; tdee: number; target_kcal: number; body_fat_pct: number; lean_mass_kg: number };

/** kcal/step ≈ 0.5 kcal·kg⁻¹·km⁻¹ × weight × stride length. */
export const kcalPerStep = (kg: number, strideM: number) => (0.5 * kg * strideM) / 1000;

/** Peak-detection step counter on device acceleration (swap for HealthKit / Health Connect bridge). */
function useSteps(onMilestone: (n: number) => void) {
  const [steps, setSteps] = useState(0);
  const last = useRef(0);
  useEffect(() => {
    const h = (e: DeviceMotionEvent) => {
      const a = e.accelerationIncludingGravity; if (!a) return;
      const mag = Math.hypot(a.x ?? 0, a.y ?? 0, a.z ?? 0), now = Date.now();
      if (mag > 12 && now - last.current > 300) {
        last.current = now;
        setSteps((s) => { const n = s + 1; if (n % 1000 === 0) onMilestone(n); return n; });
      }
    };
    window.addEventListener("devicemotion", h);
    return () => window.removeEventListener("devicemotion", h);
  }, [onMilestone]);
  return [steps, setSteps] as const;
}

export default function Dashboard({ metrics, weightKg, heightCm }: { metrics: Metrics; weightKg: number; heightCm: number }) {
  const [toast, setToast] = useState<string | null>(null);
  const [steps, setSteps] = useSteps((n) => { setToast(`${n.toLocaleString()} steps reached`); setTimeout(() => setToast(null), 3000); });
  const per = kcalPerStep(weightKg, (heightCm * 0.415) / 100);
  const series = useMemo(() => Array.from({ length: 11 }, (_, i) => {
    const s = Math.round((Math.max(steps, 1000) / 10) * i); return { steps: s, kcal: +(s * per).toFixed(1) };
  }), [steps, per]);
  const cards: [string, number][] = [["BMI", metrics.bmi], ["Body fat %", metrics.body_fat_pct], ["Lean mass kg", metrics.lean_mass_kg],
    ["BMR kcal", metrics.bmr], ["TDEE kcal", metrics.tdee], ["Target kcal", metrics.target_kcal]];

  return (
    <section className="grid gap-6 p-6 md:grid-cols-3 bg-slate-950 text-slate-100">
      {cards.map(([l, v]) => (
        <motion.div key={l} layout className="rounded-xl border border-slate-800 p-4">
          <p className="text-sm text-slate-400">{l}</p><p className="text-3xl font-semibold tabular-nums">{v}</p>
        </motion.div>))}
      <div className="md:col-span-3 rounded-xl border border-slate-800 p-4">
        <div className="flex items-baseline justify-between">
          <h2 className="text-lg font-medium">Steps to active calories</h2>
          <p className="tabular-nums">{steps.toLocaleString()} steps · {(steps * per).toFixed(0)} kcal</p>
        </div>
        <div className="h-64" role="img" aria-label="Calories burned versus steps">
          <ResponsiveContainer><AreaChart data={series}>
            <CartesianGrid stroke="#1e293b" /><XAxis dataKey="steps" stroke="#64748b" /><YAxis stroke="#64748b" />
            <Tooltip contentStyle={{ background: "#0f172a", border: "1px solid #334155" }} />
            <Area dataKey="kcal" stroke="#2dd4bf" fill="#2dd4bf33" />
          </AreaChart></ResponsiveContainer>
        </div>
        <button className="mt-3 rounded bg-teal-400 px-3 py-1 text-slate-900" onClick={() => setSteps((s) => s + 100)}>Add 100 steps</button>
      </div>
      {toast && <div role="status" className="fixed bottom-4 right-4 rounded bg-teal-400 px-4 py-2 text-slate-900">{toast}</div>}
    </section>
  );
}
