/**
 * ContributorCard — renders the mjlab contributor card from the JSON the
 * profile-repo workflow publishes daily. Zero dependencies; drop into any
 * React/Next.js project (client component).
 *
 *   <ContributorCard />                                   // defaults to mjlab card
 *   <ContributorCard src="https://cdn.jsdelivr.net/gh/sxngt/sxngt@main/assets/mjlab-card.json" theme="light" />
 *   <ContributorCard data={prefetchedJson} />             // SSR / static
 */
"use client";

import { useEffect, useState, type CSSProperties } from "react";

export type ContributorCardData = {
  repo: string;
  url: string;
  description: string;
  stars: number;
  forks: number;
  language: string;
  ogImage: string;
  contributor: {
    login: string;
    verified: boolean;
    mergedPrs: number;
    commits: number;
    prsUrl: string;
  };
  updatedAt: string;
};

type Props = {
  src?: string;
  data?: ContributorCardData;
  theme?: "light" | "dark" | "auto";
  showImage?: boolean;
  width?: number | string;
};

const DEFAULT_SRC = "https://cdn.jsdelivr.net/gh/sxngt/sxngt@main/assets/mjlab-card.json";

const fmt = (n: number) =>
  n >= 1_000_000 ? `${(n / 1_000_000).toFixed(1).replace(/\.0$/, "")}M`
  : n >= 1_000 ? `${(n / 1_000).toFixed(1).replace(/\.0$/, "")}k`
  : String(n);

const palette = {
  light: { bg: "#ffffff", border: "#d0d7de", fg: "#1f2328", muted: "#656d76", accent: "#0969da", okBg: "#dafbe1", okFg: "#1a7f37", warnBg: "#fff8c5", warnFg: "#9a6700", merge: "#8250df", star: "#e3b341" },
  dark:  { bg: "#0d1117", border: "#30363d", fg: "#e6edf3", muted: "#8b949e", accent: "#2f81f7", okBg: "#238636", okFg: "#ffffff", warnBg: "#9e6a03", warnFg: "#ffffff", merge: "#a371f7", star: "#e3b341" },
};

function useTheme(pref: Props["theme"]) {
  const [sys, setSys] = useState<"light" | "dark">("light");
  useEffect(() => {
    if (pref !== "auto" && pref !== undefined) return;
    const mq = window.matchMedia("(prefers-color-scheme: dark)");
    const apply = () => setSys(mq.matches ? "dark" : "light");
    apply();
    mq.addEventListener("change", apply);
    return () => mq.removeEventListener("change", apply);
  }, [pref]);
  return pref && pref !== "auto" ? pref : sys;
}

const Icon = ({ d, fill, size = 16 }: { d: string; fill: string; size?: number }) => (
  <svg width={size} height={size} viewBox="0 0 16 16" aria-hidden="true"><path fill={fill} d={d} /></svg>
);
const STAR = "M8 .25a.75.75 0 0 1 .673.418l1.882 3.815 4.21.612a.75.75 0 0 1 .416 1.279l-3.046 2.97.719 4.192a.751.751 0 0 1-1.088.791L8 12.347l-3.766 1.98a.75.75 0 0 1-1.088-.79l.72-4.194L.818 6.374a.75.75 0 0 1 .416-1.28l4.21-.611L7.327.668A.75.75 0 0 1 8 .25Z";
const FORK = "M5 5.372v.878c0 .414.336.75.75.75h4.5a.75.75 0 0 0 .75-.75v-.878a2.25 2.25 0 1 1 1.5 0v.878a2.25 2.25 0 0 1-2.25 2.25h-1.5v2.128a2.251 2.251 0 1 1-1.5 0V8.5h-1.5A2.25 2.25 0 0 1 3.5 6.25v-.878a2.25 2.25 0 1 1 1.5 0ZM5 3.25a.75.75 0 1 0-1.5 0 .75.75 0 0 0 1.5 0Zm6.75.75a.75.75 0 1 0 0-1.5.75.75 0 0 0 0 1.5Zm-3 8.75a.75.75 0 1 0-1.5 0 .75.75 0 0 0 1.5 0Z";
const MERGE = "M5.45 5.154A4.25 4.25 0 0 0 9.25 7.5h1.378a2.251 2.251 0 1 1 0 1.5H9.25A5.734 5.734 0 0 1 5 7.123v3.505a2.25 2.25 0 1 1-1.5 0V5.372a2.25 2.25 0 1 1 1.95-.218ZM4.25 13.5a.75.75 0 1 0 0-1.5.75.75 0 0 0 0 1.5Zm8.5-4.5a.75.75 0 1 0 0-1.5.75.75 0 0 0 0 1.5ZM5 3.25a.75.75 0 1 0 0 .005V3.25Z";
const CHECK = "M13.78 4.22a.75.75 0 0 1 0 1.06l-7.25 7.25a.75.75 0 0 1-1.06 0L2.22 9.28a.751.751 0 0 1 .018-1.042.751.751 0 0 1 1.042-.018L6 10.94l6.72-6.72a.75.75 0 0 1 1.06 0Z";

export default function ContributorCard({ src = DEFAULT_SRC, data: initial, theme = "auto", showImage = true, width = 480 }: Props) {
  const [data, setData] = useState<ContributorCardData | null>(initial ?? null);
  const [error, setError] = useState<string | null>(null);
  const t = palette[useTheme(theme)];

  useEffect(() => {
    if (initial) return;
    let alive = true;
    fetch(src)
      .then((r) => (r.ok ? r.json() : Promise.reject(new Error(`HTTP ${r.status}`))))
      .then((j: ContributorCardData) => alive && setData(j))
      .catch((e: Error) => alive && setError(e.message));
    return () => { alive = false; };
  }, [src, initial]);

  const font = '-apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif';
  const card: CSSProperties = { width, maxWidth: "100%", boxSizing: "border-box", border: `1px solid ${t.border}`, borderRadius: 10, background: t.bg, color: t.fg, fontFamily: font, overflow: "hidden", textDecoration: "none", display: "block" };

  if (error) return <div style={{ ...card, padding: 16, color: t.muted, fontSize: 13 }}>card unavailable ({error})</div>;
  if (!data) return <div style={{ ...card, height: showImage ? 408 : 168 }} aria-busy="true" />;

  const [owner, name] = data.repo.split("/");
  const c = data.contributor;
  const pill = c.verified ? { bg: t.okBg, fg: t.okFg, text: "Contributor" } : { bg: t.warnBg, fg: t.warnFg, text: "Not verified" };

  return (
    <a href={c.prsUrl} target="_blank" rel="noopener noreferrer" style={card} aria-label={`${data.repo} contributor card for @${c.login}`}>
      {showImage && data.ogImage && (
        <img src={data.ogImage} alt="" style={{ display: "block", width: "100%", aspectRatio: "2 / 1", objectFit: "cover", borderBottom: `1px solid ${t.border}` }} loading="lazy" />
      )}
      <div style={{ padding: "18px 24px 20px" }}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 12 }}>
          <div style={{ fontSize: 18, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
            <span style={{ color: t.muted }}>{owner}/</span><span style={{ color: t.accent, fontWeight: 700 }}>{name}</span>
          </div>
          <span style={{ display: "inline-flex", alignItems: "center", gap: 6, background: pill.bg, color: pill.fg, borderRadius: 13, padding: "5px 12px 5px 10px", fontSize: 12.5, fontWeight: 700, whiteSpace: "nowrap" }}>
            <Icon d={CHECK} fill={pill.fg} size={14} />{pill.text}
          </span>
        </div>
        <div style={{ color: t.muted, fontSize: 12.5, marginTop: 6, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>{data.description}</div>
        <hr style={{ border: 0, borderTop: `1px solid ${t.border}`, margin: "16px 0" }} />
        <div style={{ display: "flex", gap: 22, fontSize: 13, fontWeight: 600, alignItems: "center" }}>
          <span style={{ display: "inline-flex", alignItems: "center", gap: 6 }}><Icon d={STAR} fill={t.star} />{fmt(data.stars)}</span>
          <span style={{ display: "inline-flex", alignItems: "center", gap: 6 }}><Icon d={FORK} fill={t.muted} />{fmt(data.forks)}</span>
          {data.language && <span style={{ display: "inline-flex", alignItems: "center", gap: 6 }}><span style={{ width: 12, height: 12, borderRadius: 6, background: t.accent, display: "inline-block" }} />{data.language}</span>}
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 12.5, marginTop: 14 }}>
          <Icon d={MERGE} fill={t.merge} />
          <span>@{c.login} · {c.mergedPrs} merged PR{c.mergedPrs === 1 ? "" : "s"} · {c.commits} commit{c.commits === 1 ? "" : "s"}</span>
        </div>
      </div>
    </a>
  );
}
