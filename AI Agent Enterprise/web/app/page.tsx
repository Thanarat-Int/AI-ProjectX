"use client";

import { useMemo, useState } from "react";

type AskResponse = {
  answer?: string;
  sources?: string[];
};

const samplePrompts = [
  "How many leave days does E1001 have left?",
  "List employees in Engineering.",
  "Who is the manager of E1017?",
  "พนักงาน E1001 เหลือวันลาพักร้อนกี่วัน?",
  "E1012 อยู่แผนกอะไร?"
];

export default function HomePage() {
  const [question, setQuestion] = useState("");
  const [employeeId, setEmployeeId] = useState("");
  const [topK, setTopK] = useState(4);
  const [apiUrl, setApiUrl] = useState(
    process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/ask"
  );
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AskResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const canSubmit = useMemo(() => question.trim().length > 0, [question]);

  const submitQuestion = async () => {
    if (!canSubmit || loading) return;
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await fetch(apiUrl, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question,
          employee_id: employeeId || null,
          llm_provider: "none",
          llm_model: "gpt-4o-mini",
          top_k: topK
        })
      });

      if (!response.ok) {
        const text = await response.text();
        throw new Error(text || "Request failed");
      }

      const data = (await response.json()) as AskResponse;
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Request failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="relative min-h-screen overflow-hidden bg-ink text-white">
      <div className="absolute inset-0 neon-bg" />
      <div className="absolute inset-0 grid-overlay opacity-30" />

      <div className="relative mx-auto flex max-w-6xl flex-col gap-8 px-6 py-16 md:px-10">
        <header className="glass glow-ring rounded-3xl px-8 py-7">
          <p className="text-xs uppercase tracking-[0.3em] text-cyan">AI AGENT</p>
          <h1 className="mt-3 text-3xl font-semibold md:text-4xl">
            Neon Enterprise Knowledge Assistant
          </h1>
          <p className="mt-2 max-w-2xl text-sm text-white/70 md:text-base">
            Ask across internal policies and mock HR data with a fast, API-driven
            assistant. Free mode runs on BM25 retrieval only.
          </p>

          <div className="mt-5 grid gap-3 md:grid-cols-3">
            {[
              { label: "Mode", value: "Free • BM25" },
              { label: "Data", value: "Docs + HR Mock" },
              { label: "API", value: "/ask (FastAPI)" }
            ].map((item) => (
              <div
                key={item.label}
                className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm"
              >
                <p className="text-xs uppercase tracking-[0.2em] text-white/50">
                  {item.label}
                </p>
                <p className="mt-1 text-white">{item.value}</p>
              </div>
            ))}
          </div>
        </header>

        <section className="grid gap-6 lg:grid-cols-[1.3fr_0.7fr]">
          <div className="glass rounded-3xl p-6">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-semibold">Ask your agent</h2>
              <span className="rounded-full border border-white/10 px-3 py-1 text-xs text-white/70">
                API ready
              </span>
            </div>

            <div className="mt-5 grid gap-4">
              <label className="text-sm text-white/70">Employee ID (optional)</label>
              <input
                value={employeeId}
                onChange={(event) => setEmployeeId(event.target.value)}
                placeholder="E.g., E1001"
                className="rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none focus:border-cyan"
              />

              <label className="text-sm text-white/70">Your question</label>
              <textarea
                value={question}
                onChange={(event) => setQuestion(event.target.value)}
                placeholder="Ask about leave balance, departments, or policies..."
                rows={5}
                className="resize-none rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none focus:border-cyan"
              />

              <div className="grid gap-3 md:grid-cols-[1fr_auto] md:items-center">
                <div>
                  <label className="text-sm text-white/70">Top K</label>
                  <input
                    type="range"
                    min={1}
                    max={10}
                    value={topK}
                    onChange={(event) => setTopK(Number(event.target.value))}
                    className="mt-2 w-full"
                  />
                </div>
                <button
                  onClick={submitQuestion}
                  disabled={!canSubmit || loading}
                  className="mt-4 rounded-xl bg-gradient-to-r from-cyan via-neon to-magenta px-6 py-3 text-sm font-semibold text-black shadow-glow transition disabled:cursor-not-allowed disabled:opacity-40 md:mt-0"
                >
                  {loading ? "Thinking..." : "Ask Agent"}
                </button>
              </div>

              <div>
                <label className="text-sm text-white/70">API URL</label>
                <input
                  value={apiUrl}
                  onChange={(event) => setApiUrl(event.target.value)}
                  className="mt-2 w-full rounded-xl border border-white/10 bg-white/5 px-4 py-2 text-xs text-white/80"
                />
              </div>

              <div className="flex flex-wrap gap-2">
                {samplePrompts.map((prompt) => (
                  <button
                    key={prompt}
                    onClick={() => setQuestion(prompt)}
                    className="rounded-full border border-white/10 px-3 py-1 text-xs text-white/70 hover:border-cyan hover:text-white"
                  >
                    {prompt}
                  </button>
                ))}
              </div>
            </div>
          </div>

          <div className="glass rounded-3xl p-6">
            <h2 className="text-xl font-semibold">Response</h2>
            <p className="mt-2 text-sm text-white/60">
              Results are generated from document retrieval and HR mock tools.
            </p>

            <div className="mt-6 min-h-[220px] rounded-2xl border border-white/10 bg-white/5 p-4 text-sm">
              {error && <p className="text-magenta">{error}</p>}
              {!error && !result && (
                <p className="text-white/50">Ask a question to see the answer here.</p>
              )}
              {result?.answer && <p className="whitespace-pre-wrap">{result.answer}</p>}
            </div>

            {result?.sources && result.sources.length > 0 && (
              <div className="mt-4">
                <p className="text-xs uppercase tracking-[0.2em] text-white/50">
                  Sources
                </p>
                <div className="mt-2 flex flex-wrap gap-2">
                  {result.sources.map((source) => (
                    <span
                      key={source}
                      className="rounded-full border border-white/10 px-3 py-1 text-xs text-white/70"
                    >
                      {source}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </section>
      </div>
    </main>
  );
}
