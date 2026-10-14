"use client";

import { useEffect, useRef, useState } from "react";

type Guide = { id: string; title: string; url?: string; description?: string; category?: string; date?: string; heading?: string; excerpt?: string; section?: number };
type Reply = { id: string; conversationId?: string; answer: string; status?: string; sources: Guide[]; followups: string[]; feedback?: number; bridge?: { text: string; label: string } };
type Turn = { question: string; reply?: Reply; error?: string };
const API = "/api/ask-dr-mortgage";
const EXAMPLES = [
  ["Cash to close", "Can my parents help with my down payment?"],
  ["Self-employed", "I’m self-employed. What income will count?"],
  ["VA benefits", "Can I use my VA loan a second time?"],
  ["My payment", "Why did my mortgage payment go up?"],
];

async function api<T>(endpoint: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API}/${endpoint}`, init);
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || "The answer service is unavailable. Please try again.");
  return data as T;
}

function guideUrl(guide: Guide) {
  const fallback = `/blog/${encodeURIComponent(guide.id)}`;
  if (!guide.url) return fallback;
  try {
    const url = new URL(guide.url, "https://drmortgageusa.com");
    if (url.protocol === "https:" && url.hostname === "drmortgageusa.com" && url.pathname.startsWith("/blog/")) return url.pathname + url.search + url.hash;
  } catch { /* Reject non-library URLs. */ }
  return fallback;
}

function Feedback({ reply }: { reply: Reply }) {
  const [value, setValue] = useState(reply.feedback || 0);
  const [failed, setFailed] = useState(false);
  const [saving, setSaving] = useState(false);
  async function send(next: number) {
    setSaving(true); setFailed(false);
    try {
      await api("feedback", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ id: reply.id, value: next, reason: "" }) });
      setValue(next);
    } catch { setFailed(true); } finally { setSaving(false); }
  }
  return <div className="ask-feedback">
    <span>{value ? "Thanks. That helps improve the answers." : "Did this help?"}</span>
    {!value && <><button type="button" disabled={saving} onClick={() => void send(1)}>Yes</button><button type="button" disabled={saving} onClick={() => void send(-1)}>Not yet</button></>}
    {failed && <span role="alert">Feedback was not saved. Please try again.</span>}
  </div>;
}

export default function AskExperience() {
  const [tab, setTab] = useState("ask");
  const [question, setQuestion] = useState("");
  const [turns, setTurns] = useState<Turn[]>([]);
  const [conversationId, setConversationId] = useState("");
  const [guides, setGuides] = useState<Guide[]>([]);
  const [matches, setMatches] = useState<Guide[]>([]);
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("All guides");
  const [busy, setBusy] = useState(false);
  const [loading, setLoading] = useState(true);
  const [notice, setNotice] = useState("");
  const [libraryFailed, setLibraryFailed] = useState(false);
  const [searchFailed, setSearchFailed] = useState(false);
  const [searching, setSearching] = useState(false);
  const inFlight = useRef(false);
  const controller = useRef<AbortController | null>(null);
  const input = useRef<HTMLTextAreaElement>(null);
  const end = useRef<HTMLDivElement>(null);

  useEffect(() => {
    let active = true;
    api<{ turns: Turn[]; id?: string }>("conversation")
      .then((data) => { if (active) { setTurns(data.turns || []); setConversationId(data.id || ""); } })
      .catch(() => { if (active) setNotice("Your previous conversation could not load. Refresh to try again."); })
      .finally(() => { if (active) setLoading(false); });
    api<{ articles: Guide[] }>("library")
      .then((data) => { if (active) setGuides(data.articles || []); })
      .catch(() => { if (active) setLibraryFailed(true); });
    const initial = new URLSearchParams(window.location.search).get("question");
    void Promise.resolve().then(() => {
      if (!active) return;
      if (initial) setQuestion(initial.slice(0, 1200));
      if (window.location.hash === "#library") setTab("library");
    });
    return () => { active = false; controller.current?.abort(); };
  }, []);

  useEffect(() => {
    if (!search.trim()) return;
    const abort = new AbortController();
    const timer = setTimeout(() => {
      api<{ results: Guide[] }>(`search?q=${encodeURIComponent(search)}`, { signal: abort.signal })
        .then((data) => { if (!abort.signal.aborted) setMatches(data.results || []); })
        .catch(() => { if (!abort.signal.aborted) setSearchFailed(true); })
        .finally(() => { if (!abort.signal.aborted) setSearching(false); });
    }, 220);
    return () => { clearTimeout(timer); abort.abort(); };
  }, [search]);

  useEffect(() => { if (turns.length) end.current?.scrollIntoView({ block: "nearest", behavior: "smooth" }); }, [turns]);

  async function ask(text = question) {
    const cleaned = text.trim();
    if (!cleaned || inFlight.current || loading) return;
    inFlight.current = true; setBusy(true); setNotice(""); setQuestion(""); setTab("ask");
    const abort = new AbortController(); controller.current = abort;
    const history = turns.filter((turn) => turn.reply).slice(-5).map((turn) => ({ question: turn.question, answer: turn.reply!.answer, articleIds: turn.reply!.sources.map((guide) => guide.id) }));
    setTurns((current) => [...current, { question: cleaned }]);
    try {
      const reply = await api<Reply>("ask", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ question: cleaned, conversationId, history }), signal: abort.signal });
      if (reply.conversationId) setConversationId(reply.conversationId);
      setTurns((current) => current.map((turn, index) => index === current.length - 1 ? { ...turn, reply } : turn));
    } catch (error) {
      const message = error instanceof Error && error.name === "AbortError" ? "Answer stopped. You can ask again." : error instanceof Error ? error.message : "Please try again.";
      setTurns((current) => current.map((turn, index) => index === current.length - 1 ? { ...turn, error: message } : turn));
    } finally { setBusy(false); inFlight.current = false; controller.current = null; }
  }

  async function reset(remove: boolean) {
    if (busy || loading || (remove && !window.confirm("Delete this conversation and its saved feedback and activity? This cannot be undone."))) return;
    setLoading(true); setNotice("");
    try {
      const data = await api<{ id?: string }>("conversation", { method: remove ? "DELETE" : "POST" });
      setTurns([]); setConversationId(data.id || ""); setQuestion(""); input.current?.focus();
    } catch { setNotice("Could not update the conversation. Your current questions are still here."); }
    finally { setLoading(false); }
  }

  function articleClick(reply: Reply, guide: Guide) {
    void api("events", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ kind: "article_click", questionId: reply.id, articleId: guide.id }), keepalive: true }).catch(() => {});
  }

  const visible = (search.trim() ? matches : guides).filter((guide) => category === "All guides" || guide.category === category);
  return <section className="section ask-mortgage-section">
    <div className="shell">
      <div className="ask-tabs" role="tablist" aria-label="Ask Dr. Mortgage">
        <button id="ask-tab" type="button" role="tab" aria-selected={tab === "ask"} aria-controls="ask-panel" onClick={() => setTab("ask")}>Ask a question</button>
        <button id="guides-tab" type="button" role="tab" aria-selected={tab === "library"} aria-controls="guides-panel" onClick={() => setTab("library")}>Browse the guides</button>
      </div>
      {notice && <p className="ask-error" role="alert">{notice}</p>}
      {tab === "ask" ? <div id="ask-panel" role="tabpanel" aria-labelledby="ask-tab" className="ask-panel">
        <div className="ask-heading"><div><p className="eyebrow">Ask Dr. Mortgage</p><p>Answers from Dennis’s blog library</p></div>
          {turns.length > 0 && <div className="ask-actions"><button type="button" disabled={busy || loading} onClick={() => void reset(false)}>New conversation</button><button type="button" disabled={busy || loading} onClick={() => void reset(true)}>Delete conversation</button></div>}
        </div>
        {!turns.length && <><h2>Start wherever you are.</h2><p>The down payment. Your credit. Something your lender said. Ask it here, and we’ll find the guide that helps.</p>
          <div className="ask-examples">{EXAMPLES.map(([label, text]) => <button type="button" key={text} disabled={busy || loading} onClick={() => { setQuestion(text); input.current?.focus(); }}><small>{label}</small><span>{text}</span></button>)}</div>
        </>}
        <div className="ask-conversation" aria-live="polite">{turns.map((turn, index) => <article className="ask-turn" key={index}>
          <p className="ask-user-question">{turn.question}</p>
          {turn.reply && <div className="ask-answer"><p className="eyebrow">From Dennis’s guides</p><div className="ask-answer-text">{turn.reply.answer}</div>
            {turn.reply.bridge?.text && <p>{turn.reply.bridge.text}</p>}
            {turn.reply.sources?.length > 0 && <div className="ask-sources">{turn.reply.sources.map((guide) => <div key={`${guide.id}-${guide.section}`}><a href={guideUrl(guide)} onClick={() => articleClick(turn.reply!, guide)}>{guide.title} →</a>{guide.heading && <small>Found in: {guide.heading}</small>}{guide.excerpt && <blockquote>{guide.excerpt}</blockquote>}</div>)}</div>}
            {turn.reply.status !== "acknowledgment" && <Feedback reply={turn.reply} />}
            {index === turns.length - 1 && turn.reply.followups?.length > 0 && <div className="ask-followups">{turn.reply.followups.map((text) => <button type="button" disabled={busy || loading} key={text} onClick={() => void ask(text)}>{text} →</button>)}</div>}
          </div>}
          {turn.error && <p className="ask-error" role="alert">{turn.error} <button type="button" disabled={busy} onClick={() => void ask(turn.question)}>Try again</button></p>}
        </article>)}</div>
        {busy && <p className="ask-thinking" role="status">Looking through Dennis’s guides… <button type="button" onClick={() => controller.current?.abort()}>Stop</button></p>}
        <div ref={end} />
        <form className="ask-composer" onSubmit={(event) => { event.preventDefault(); void ask(); }}>
          <label className="sr-only" htmlFor="mortgage-question">Your mortgage question</label>
          <textarea ref={input} id="mortgage-question" maxLength={1200} rows={3} value={question} onChange={(event) => setQuestion(event.target.value)} placeholder="Type your question the way you’d ask Dennis…" onKeyDown={(event) => { if (event.key === "Enter" && !event.shiftKey && !event.nativeEvent.isComposing) { event.preventDefault(); void ask(); } }} />
          <div className="ask-composer-footer"><small>Enter to ask · Shift + Enter for a new line</small><button className="button button-gold" type="submit" disabled={busy || loading || !question.trim()}>{loading ? "Loading…" : "Ask your question"}</button></div>
        </form>
        <p className="ask-disclosure">Answers come from Dennis’s guides, not a live chat with Dennis. Resume this conversation on this browser for seven days. Questions and feedback are saved for research, with a 90-day retention period. Please leave out names, account numbers, and private details. <a href="/ask-dr-mortgage/privacy">Privacy and saved questions</a></p>
      </div> : <div id="guides-panel" role="tabpanel" aria-labelledby="guides-tab" className="ask-panel">
        <h2>Browse Dennis’s guides.</h2><p>{guides.length ? `${guides.length} published guides, connected to the live blog library.` : "Guides from the live DR. Mortgage USA blog."}</p>
        <label className="ask-search-label" htmlFor="ask-guide-search">Search the library</label><input id="ask-guide-search" type="search" value={search} maxLength={1200} onChange={(event) => { setSearch(event.target.value); setMatches([]); setSearchFailed(false); setSearching(!!event.target.value.trim()); }} placeholder="Search the way you’d ask the question" />
        <div className="ask-categories">{["All guides", "Buying", "VA loans", "Self-employed", "Homeownership", "Market strategy"].map((name) => <button type="button" aria-pressed={category === name} key={name} onClick={() => setCategory(name)}>{name}</button>)}</div>
        {(libraryFailed || searchFailed) && <p role="alert" className="ask-error">The guides could not load. Please try again, or <a href="/blog">browse the blog directly</a>.</p>}
        {searching && <p role="status">Searching the guides…</p>}
        <div className="ask-guide-grid">{visible.map((guide) => <article key={`${guide.id}-${guide.section}`}><p className="eyebrow">{guide.category}</p><h3><a href={guideUrl(guide)}>{guide.title}</a></h3>{guide.heading && <small>Found in: {guide.heading}</small>}<p>{guide.excerpt || guide.description}</p><a href={guideUrl(guide)}>Read the guide →</a></article>)}</div>
        {!searching && !libraryFailed && !searchFailed && guides.length > 0 && !visible.length && <p>No matching guides yet. Try a different search or ask your question.</p>}
      </div>}
    </div>
  </section>;
}
