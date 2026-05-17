import React, { useState, useRef, useCallback } from 'react';
import axios from 'axios';

/* ─── Types ──────────────────────────────────────────────────────────────── */
interface JobMatch {
  score: number;
  title: string;
  company: string;
  job_type: string;
  location: string;
  is_remote: boolean;
  job_date: string;
  job_url: string;
}

/* ─── Inline SVG Icons ───────────────────────────────────────────────────── */
const Icon = {
  Upload: () => (
    <svg width="22" height="22" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5" />
    </svg>
  ),
  File: () => (
    <svg width="18" height="18" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
    </svg>
  ),
  X: ({ size = 16 }: { size?: number }) => (
    <svg width={size} height={size} fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
    </svg>
  ),
  Sparkles: () => (
    <svg width="14" height="14" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.456 2.456L21.75 6l-1.035.259a3.375 3.375 0 00-2.456 2.456zM16.894 20.567L16.5 21.75l-.394-1.183a2.25 2.25 0 00-1.423-1.423L13.5 18.75l1.183-.394a2.25 2.25 0 001.423-1.423l.394-1.183.394 1.183a2.25 2.25 0 001.423 1.423l1.183.394-1.183.394a2.25 2.25 0 00-1.423 1.423z" />
    </svg>
  ),
  MapPin: () => (
    <svg width="14" height="14" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" d="M15 10.5a3 3 0 11-6 0 3 3 0 016 0z" /><path strokeLinecap="round" strokeLinejoin="round" d="M19.5 10.5c0 7.142-7.5 11.25-7.5 11.25S4.5 17.642 4.5 10.5a7.5 7.5 0 1115 0z" />
    </svg>
  ),
  Briefcase: () => (
    <svg width="14" height="14" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" d="M20.25 14.15v4.25c0 1.094-.787 2.036-1.872 2.18-2.087.277-4.216.42-6.378.42s-4.291-.143-6.378-.42c-1.085-.144-1.872-1.086-1.872-2.18v-4.25m16.5 0a2.18 2.18 0 00.75-1.661V8.706c0-1.081-.768-2.015-1.837-2.175a48.114 48.114 0 00-3.413-.387m4.5 8.006c-.194.165-.42.295-.673.38A23.978 23.978 0 0112 15.75c-2.648 0-5.195-.429-7.577-1.22a2.016 2.016 0 01-.673-.38m0 0A2.18 2.18 0 013 12.489V8.706c0-1.081.768-2.015 1.837-2.175a48.111 48.111 0 013.413-.387m7.5 0V5.25A2.25 2.25 0 0013.5 3h-3a2.25 2.25 0 00-2.25 2.25v.894m7.5 0a48.667 48.667 0 00-7.5 0" />
    </svg>
  ),
  Calendar: () => (
    <svg width="14" height="14" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" d="M6.75 3v2.25M17.25 3v2.25M3 18.75V7.5a2.25 2.25 0 012.25-2.25h13.5A2.25 2.25 0 0121 7.5v11.25m-18 0A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75m-18 0v-7.5A2.25 2.25 0 015.25 9h13.5A2.25 2.25 0 0121 11.25v7.5" />
    </svg>
  ),
  ExternalLink: () => (
    <svg width="13" height="13" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 6H5.25A2.25 2.25 0 003 8.25v10.5A2.25 2.25 0 005.25 21h10.5A2.25 2.25 0 0018 18.75V10.5m-10.5 6L21 3m0 0h-5.25M21 3v5.25" />
    </svg>
  ),
  Wifi: () => (
    <svg width="14" height="14" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" d="M8.288 15.038a5.25 5.25 0 017.424 0M5.106 11.856c3.807-3.808 9.98-3.808 13.788 0M1.924 8.674c5.565-5.565 14.587-5.565 20.152 0M12.53 18.22l-.53.53-.53-.53a.75.75 0 011.06 0z" />
    </svg>
  ),
  Loader: () => (
    <svg width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24" style={{ animation: 'spin 0.8s linear infinite' }}>
      <path strokeLinecap="round" d="M12 3v3m9 9h-3M12 21v-3M3 12h3" />
      <path strokeLinecap="round" strokeOpacity="0.3" d="M18.364 5.636l-2.121 2.121M18.364 18.364l-2.121-2.121M5.636 18.364l2.121-2.121M5.636 5.636l2.121 2.121" />
    </svg>
  ),
  ArrowRight: () => (
    <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 4.5L21 12m0 0l-7.5 7.5M21 12H3" />
    </svg>
  ),
  Search: () => (
    <svg width="32" height="32" fill="none" stroke="currentColor" strokeWidth="1.2" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 15.803a7.5 7.5 0 0010.607 10.607z" />
    </svg>
  ),
};

/* ─── Helpers ─────────────────────────────────────────────────────────────── */
const formatDate = (d: string) => {
  if (!d) return null;
  try { return new Date(d).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }); }
  catch { return d; }
};

const scoreLabel = (s: number) => {
  if (s >= 0.80) return { text: 'Excellent', cls: 'tag-excellent' };
  if (s >= 0.65) return { text: 'Strong', cls: 'tag-strong' };
  if (s >= 0.50) return { text: 'Good', cls: 'tag-good' };
  return { text: 'Fair', cls: 'tag-fair' };
};

/* ─── Styles ─────────────────────────────────────────────────────────────── */
const css = `
@import url('https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Geist:wght@300;400;450;500;600&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
  --bg:        #0c0c10;
  --bg-2:      #13131a;
  --bg-3:      #1a1a24;
  --bg-4:      #22222e;
  --line:      rgba(255,255,255,0.07);
  --line-2:    rgba(255,255,255,0.12);
  --line-3:    rgba(255,255,255,0.18);
  --text:      #f0f0f8;
  --text-2:    #9898b0;
  --text-3:    #5a5a72;
  --accent:    #6c63ff;
  --accent-d:  #4f48d4;
  --accent-bg: rgba(108,99,255,0.12);
  --accent-brd:rgba(108,99,255,0.25);
  --green:     #34d399;
  --green-bg:  rgba(52,211,153,0.1);
  --green-brd: rgba(52,211,153,0.2);
  --green-text:#6ee7b7;
  --amber:     #fbbf24;
  --amber-bg:  rgba(251,191,36,0.1);
  --amber-text:#fcd34d;
  --red:       #f87171;
  --red-bg:    rgba(248,113,113,0.1);
  --red-brd:   rgba(248,113,113,0.2);
  --red-text:  #fca5a5;
  --radius:    12px;
  --radius-sm: 6px;
  --font-serif:'Instrument Serif', Georgia, serif;
  --font-sans: 'Geist', -apple-system, sans-serif;
}

html, body { height: 100%; overflow: hidden; }
body {
  background: var(--bg);
  color: var(--text);
  font-family: var(--font-sans);
  -webkit-font-smoothing: antialiased;
}

#root { height: 100%; }

@keyframes spin    { to { transform: rotate(360deg); } }
@keyframes fadeUp  { from { opacity:0; transform:translateY(12px); } to { opacity:1; transform:translateY(0); } }
@keyframes shimmer { 0%,100% { opacity:.3; } 50% { opacity:.7; } }

/* ── App shell: full-viewport, no outer scroll ── */
.app {
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
  background: var(--bg);
}

/* ── Top bar ── */
.topbar {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 40px;
  height: 58px;
  background: var(--bg-2);
  border-bottom: 1px solid var(--line);
  z-index: 100;
}

.topbar-logo {
  display: flex;
  align-items: center;
  gap: 10px;
}

.logo-mark {
  width: 30px;
  height: 30px;
  background: var(--accent);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.logo-mark svg { color: #fff; }

.logo-name {
  font-size: 15px;
  font-weight: 600;
  letter-spacing: -0.02em;
  color: var(--text);
}

.topbar-tag {
  font-size: 12px;
  background: var(--accent-bg);
  color: var(--accent);
  border: 1px solid var(--accent-brd);
  padding: 4px 12px;
  border-radius: 100px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 5px;
}

/* ── Main: takes remaining height, no overflow ── */
.main {
  flex: 1;
  min-height: 0;
  display: grid;
  grid-template-columns: 360px 1fr;
  overflow: hidden;
}

/* ── Left panel: fixed height, no scroll ── */
.panel-left {
  display: flex;
  flex-direction: column;
  padding: 28px 28px 24px;
  border-right: 1px solid var(--line);
  background: var(--bg-2);
  overflow-y: auto;
  overflow-x: hidden;
  scrollbar-width: none;
}

.panel-left::-webkit-scrollbar { display: none; }

.panel-hero { margin-bottom: 20px; flex-shrink: 0; }

.hero-eyebrow {
  font-size: 11px;
  font-weight: 500;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--text-3);
  margin-bottom: 10px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.hero-eyebrow::before {
  content: '';
  display: block;
  width: 18px;
  height: 1px;
  background: var(--text-3);
}

.hero-title {
  font-family: var(--font-serif);
  font-size: clamp(22px, 2.4vw, 30px);
  font-weight: 400;
  line-height: 1.2;
  letter-spacing: -0.01em;
  color: var(--text);
  margin-bottom: 10px;
}

.hero-title em {
  font-style: italic;
  color: var(--accent);
}

.hero-body {
  font-size: 13px;
  line-height: 1.6;
  color: var(--text-2);
  font-weight: 400;
}

/* ── Upload card ── */
.upload-card {
  flex-shrink: 0;
  background: var(--bg-3);
  border: 1px solid var(--line);
  border-radius: var(--radius);
  padding: 16px;
}

.dropzone-wrap {
  border: 1.5px dashed rgba(108,99,255,0.3);
  border-radius: 10px;
  background: rgba(108,99,255,0.04);
  padding: 22px 16px;
  text-align: center;
  cursor: pointer;
  transition: border-color 0.2s, background 0.2s;
  display: block;
  width: 100%;
  outline: none;
}

.dropzone-wrap:hover,
.dropzone-wrap.drag-over {
  border-color: var(--accent);
  background: var(--accent-bg);
}

.dropzone-wrap input { display: none; }

.drop-icon-wrap {
  width: 44px;
  height: 44px;
  border-radius: 10px;
  background: var(--bg-4);
  border: 1px solid var(--line-2);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 12px;
  color: var(--text-2);
  transition: transform 0.2s, color 0.2s;
}

.dropzone-wrap:hover .drop-icon-wrap,
.dropzone-wrap.drag-over .drop-icon-wrap {
  transform: translateY(-2px);
  color: var(--accent);
}

.drop-text-main {
  font-size: 13px;
  font-weight: 500;
  color: var(--text);
  margin-bottom: 4px;
}

.drop-text-sub {
  font-size: 12px;
  color: var(--text-3);
}

.drop-text-sub span { color: var(--accent); font-weight: 500; }

/* File row */
.file-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 12px;
  padding: 10px 12px;
  background: var(--green-bg);
  border: 1px solid var(--green-brd);
  border-radius: 8px;
  animation: fadeUp 0.25s ease;
}

.file-row-icon { color: var(--green); flex-shrink: 0; }
.file-row-name {
  flex: 1;
  font-size: 12px;
  font-weight: 500;
  color: var(--green-text);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.file-row-size { font-size: 11px; color: var(--green); flex-shrink: 0; }
.file-row-remove {
  color: var(--green);
  opacity: 0.6;
  cursor: pointer;
  transition: opacity 0.15s;
  flex-shrink: 0;
  background: none;
  border: none;
  padding: 0;
  display: flex;
  align-items: center;
}
.file-row-remove:hover { opacity: 1; }

/* Error */
.err-row {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  margin-top: 12px;
  padding: 10px 12px;
  background: var(--red-bg);
  border: 1px solid var(--red-brd);
  border-radius: 8px;
  font-size: 12px;
  color: var(--red-text);
  animation: fadeUp 0.25s ease;
  line-height: 1.5;
}

/* Submit button */
.btn-submit {
  width: 100%;
  margin-top: 12px;
  padding: 12px 20px;
  background: var(--accent);
  color: #fff;
  border: none;
  border-radius: 10px;
  font-family: var(--font-sans);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s, transform 0.15s, box-shadow 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.btn-submit:hover:not(:disabled) {
  background: var(--accent-d);
  box-shadow: 0 4px 20px rgba(108,99,255,0.35);
  transform: translateY(-1px);
}

.btn-submit:active:not(:disabled) { transform: translateY(0); }

.btn-submit:disabled {
  background: var(--bg-4);
  color: var(--text-3);
  cursor: not-allowed;
}

/* Stats row */
.info-row {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-top: 14px;
  padding-top: 14px;
  border-top: 1px solid var(--line);
  flex-shrink: 0;
}

.info-stat { display: flex; flex-direction: column; gap: 2px; }
.info-stat-num {
  font-size: 15px;
  font-weight: 600;
  color: var(--text);
  letter-spacing: -0.03em;
}
.info-stat-lbl {
  font-size: 10px;
  color: var(--text-3);
  text-transform: uppercase;
  letter-spacing: 0.06em;
  font-weight: 500;
}
.info-divider { width: 1px; height: 26px; background: var(--line-2); }

/* ── Right panel: scrollable results ── */
.panel-right {
  overflow-y: auto;
  padding: 36px 36px 48px;
  background: var(--bg);
  scrollbar-width: thin;
  scrollbar-color: var(--bg-4) transparent;
}

.panel-right::-webkit-scrollbar { width: 4px; }
.panel-right::-webkit-scrollbar-track { background: transparent; }
.panel-right::-webkit-scrollbar-thumb { background: var(--bg-4); border-radius: 2px; }

/* Results bar */
.results-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.results-heading {
  font-size: 15px;
  font-weight: 600;
  color: var(--text);
  letter-spacing: -0.02em;
}

.results-chip {
  font-size: 11px;
  font-weight: 500;
  background: var(--accent-bg);
  color: var(--accent);
  border: 1px solid var(--accent-brd);
  padding: 3px 10px;
  border-radius: 100px;
}

/* Empty / idle state */
.empty-state {
  background: var(--bg-2);
  border: 1px solid var(--line);
  border-radius: var(--radius);
  padding: 64px 40px;
  text-align: center;
}

.empty-icon {
  width: 56px;
  height: 56px;
  border-radius: 14px;
  background: var(--bg-3);
  border: 1px solid var(--line-2);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 16px;
  color: var(--text-3);
}

.empty-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text);
  margin-bottom: 8px;
}

.empty-body {
  font-size: 13px;
  color: var(--text-2);
  line-height: 1.6;
  max-width: 260px;
  margin: 0 auto;
}

/* Skeleton */
.skeleton-list { display: flex; flex-direction: column; gap: 12px; }

.skeleton-card {
  background: var(--bg-2);
  border: 1px solid var(--line);
  border-radius: var(--radius);
  padding: 24px;
  animation: shimmer 1.6s ease-in-out infinite;
}

.sk { background: var(--bg-4); border-radius: 4px; }
.sk-title { height: 16px; width: 55%; margin-bottom: 8px; }
.sk-sub   { height: 12px; width: 32%; margin-bottom: 22px; }
.sk-row   { height: 11px; width: 75%; }
.sk-row-2 { height: 11px; width: 50%; margin-top: 8px; }

/* ── Job cards ── */
.job-card {
  background: var(--bg-2);
  border: 1px solid var(--line);
  border-radius: var(--radius);
  padding: 22px 24px;
  margin-bottom: 10px;
  transition: border-color 0.2s, background 0.2s, transform 0.2s;
  animation: fadeUp 0.35s ease both;
  position: relative;
  overflow: hidden;
}

.job-card::after {
  content: '';
  position: absolute;
  left: 0; top: 14px; bottom: 14px;
  width: 3px;
  background: linear-gradient(180deg, var(--accent), var(--green));
  border-radius: 0 3px 3px 0;
  opacity: 0;
  transition: opacity 0.2s;
}

.job-card:hover {
  border-color: var(--line-2);
  background: var(--bg-3);
  transform: translateX(3px);
}

.job-card:hover::after { opacity: 1; }

.jc-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
  margin-bottom: 16px;
}

.jc-main { flex: 1; min-width: 0; }

.jc-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text);
  letter-spacing: -0.02em;
  margin-bottom: 5px;
  line-height: 1.3;
}

.jc-company {
  font-size: 12px;
  color: var(--text-2);
  display: flex;
  align-items: center;
  gap: 5px;
}

/* Score badge */
.score-badge {
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  min-width: 72px;
}

.score-ring { position: relative; width: 52px; height: 52px; margin-bottom: 6px; }
.score-ring svg { transform: rotate(-90deg); }
.score-ring-bg   { fill: none; stroke: var(--bg-4); stroke-width: 3.5; }
.score-ring-fill { fill: none; stroke-width: 3.5; stroke-linecap: round; }

.score-center {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.score-num {
  font-size: 13px;
  font-weight: 600;
  color: var(--text);
  letter-spacing: -0.03em;
}

/* Tags */
.tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 2px 8px;
  border-radius: 100px;
  font-size: 10px;
  font-weight: 500;
  letter-spacing: 0.02em;
}

.tag-excellent { background: var(--green-bg); color: var(--green-text); border: 1px solid var(--green-brd); }
.tag-strong    { background: var(--accent-bg); color: var(--accent); border: 1px solid var(--accent-brd); }
.tag-good      { background: var(--amber-bg); color: var(--amber-text); border: 1px solid rgba(251,191,36,0.2); }
.tag-fair      { background: var(--bg-4); color: var(--text-3); border: 1px solid var(--line-2); }
.tag-remote    { background: var(--green-bg); color: var(--green-text); border: 1px solid var(--green-brd); }
.tag-onsite    { background: var(--bg-4); color: var(--text-3); border: 1px solid var(--line-2); }

/* Meta row */
.jc-meta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px;
  row-gap: 6px;
}

.meta-pill {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 11px;
  color: var(--text-2);
  padding: 4px 10px;
  background: var(--bg-4);
  border: 1px solid var(--line);
  border-radius: 100px;
}

.jc-divider { height: 1px; background: var(--line); margin: 16px 0; }

.jc-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  flex-wrap: wrap;
}

.score-bar-wrap {
  flex: 1;
  max-width: 150px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.score-bar-track {
  flex: 1;
  height: 3px;
  background: var(--bg-4);
  border-radius: 2px;
  overflow: hidden;
}

.score-bar-fill {
  height: 100%;
  border-radius: 2px;
  transition: width 0.6s cubic-bezier(0.4,0,0.2,1);
}

.btn-view {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 11px;
  font-weight: 500;
  color: var(--accent);
  background: var(--accent-bg);
  border: 1px solid var(--accent-brd);
  border-radius: 8px;
  padding: 5px 12px;
  text-decoration: none;
  transition: background 0.15s, box-shadow 0.15s;
}

.btn-view:hover {
  background: rgba(108,99,255,0.2);
  box-shadow: 0 2px 10px rgba(108,99,255,0.2);
}

/* Footer */
.footer {
  flex-shrink: 0;
  text-align: center;
  padding: 14px 40px;
  border-top: 1px solid var(--line);
  font-size: 11px;
  color: var(--text-3);
  background: var(--bg-2);
  letter-spacing: 0.01em;
}

/* ── Responsive ── */
@media (max-width: 860px) {
  html, body { overflow: auto; }
  .app { height: auto; overflow: visible; }
  .main { grid-template-columns: 1fr; overflow: visible; }
  .panel-left { border-right: none; border-bottom: 1px solid var(--line); padding: 28px 24px; }
  .panel-right { overflow: visible; padding: 24px; }
  .topbar { padding: 0 24px; }
}

@media (max-width: 480px) {
  .topbar-tag { display: none; }
  .jc-top { flex-direction: column; gap: 10px; }
  .score-badge { flex-direction: row; align-items: center; gap: 10px; }
  .score-ring { margin-bottom: 0; }
}
`

/* ─── Score ring component ───────────────────────────────────────────────── */
const ScoreRing: React.FC<{ score: number }> = ({ score }) => {
  const pct = score * 100;
  const r = 24;
  const circ = 2 * Math.PI * r;
  const dash = circ * score;
  const gap = circ - dash;
  const { text, cls } = scoreLabel(score);

  const color = score >= 0.80 ? '#12a05c' : score >= 0.65 ? '#2d2aee' : score >= 0.50 ? '#c47b00' : '#7a7a90';

  return (
    <div className="score-badge">
      <div className="score-ring">
        <svg width="56" height="56" viewBox="0 0 56 56">
          <circle className="score-ring-bg" cx="28" cy="28" r={r} />
          <circle
            className="score-ring-fill"
            cx="28" cy="28" r={r}
            stroke={color}
            strokeDasharray={`${dash} ${gap}`}
            strokeDashoffset="0"
          />
        </svg>
        <div className="score-center">
          <span className="score-num">{Math.round(pct)}%</span>
        </div>
      </div>
      <span className={`tag ${cls}`}>{text}</span>
    </div>
  );
};

/* ─── Job Card ───────────────────────────────────────────────────────────── */
const JobCard: React.FC<{ job: JobMatch; idx: number }> = ({ job, idx }) => {
  const date = formatDate(job.job_date);
  const barColor = job.score >= 0.80 ? '#12a05c' : job.score >= 0.65 ? '#2d2aee' : job.score >= 0.50 ? '#c47b00' : '#b0b0c4';

  return (
    <div className="job-card" style={{ animationDelay: `${idx * 0.06}s` }}>
      <div className="jc-top">
        <div className="jc-main">
          <div className="jc-title">{job.title}</div>
          <div className="jc-company">
            <Icon.Briefcase />
            {job.company}
          </div>
        </div>
        <ScoreRing score={job.score} />
      </div>

      <div className="jc-meta">
        {job.location && (
          <span className="meta-pill">
            <Icon.MapPin />{job.location}
          </span>
        )}
        {job.job_type && (
          <span className="meta-pill">
            {job.job_type}
          </span>
        )}
        <span className={`tag ${job.is_remote ? 'tag-remote' : 'tag-onsite'}`}>
          <Icon.Wifi />
          {job.is_remote ? 'Remote' : 'On-site'}
        </span>
        {date && (
          <span className="meta-pill">
            <Icon.Calendar />{date}
          </span>
        )}
      </div>

      <div className="jc-divider" />

      <div className="jc-footer">
        <div className="score-bar-wrap">
          <div className="score-bar-track">
            <div
              className="score-bar-fill"
              style={{ width: `${job.score * 100}%`, background: barColor }}
            />
          </div>
          <span style={{ fontSize: 11, color: 'var(--ink-4)', whiteSpace: 'nowrap' }}>
            Match score
          </span>
        </div>

        {job.job_url ? (
          <a
            href={job.job_url}
            target="_blank"
            rel="noopener noreferrer"
            className="btn-view"
          >
            View listing <Icon.ExternalLink />
          </a>
        ) : (
          <span style={{ fontSize: 12, color: 'var(--ink-4)' }}>No listing URL</span>
        )}
      </div>
    </div>
  );
};

/* ─── Skeleton loaders ───────────────────────────────────────────────────── */
const SkeletonCards = () => (
  <div className="skeleton-list">
    {[0, 1, 2].map(i => (
      <div className="skeleton-card" key={i} style={{ animationDelay: `${i * 0.15}s` }}>
        <div className="sk sk-title" />
        <div className="sk sk-sub" />
        <div className="sk sk-row" />
        <div className="sk sk-row-2" />
      </div>
    ))}
  </div>
);

/* ─── Main App ───────────────────────────────────────────────────────────── */
const App: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<JobMatch[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [dragOver, setDragOver] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const formatSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const acceptFile = useCallback((f: File) => {
    if (!f.name.toLowerCase().endsWith('.pdf')) {
      setError('Only PDF files are accepted. Please upload a PDF version of your CV.');
      return;
    }
    if (f.size > 10 * 1024 * 1024) {
      setError('File must be under 10 MB.');
      return;
    }
    setFile(f);
    setError(null);
    setResults(null);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    if (e.dataTransfer.files?.[0]) acceptFile(e.dataTransfer.files[0]);
  }, [acceptFile]);

  const handleSubmit = async () => {
    if (!file) { setError('Please upload a PDF CV first.'); return; }
    setLoading(true);
    setError(null);
    setResults(null);
    const formData = new FormData();
    formData.append('file', file);
    try {
      const { data } = await axios.post<{ matches: JobMatch[] }>('http://localhost:8000/match-cv', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setResults(data.matches);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Something went wrong. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const clearFile = () => {
    setFile(null);
    setResults(null);
    setError(null);
  };

  const showEmpty = !loading && results !== null && results.length === 0;
  const showResults = !loading && results !== null && results.length > 0;

  return (
    <>
      <style>{css}</style>
      <div className="app">

        {/* Top bar */}
        <header className="topbar">
          <div className="topbar-logo">
            <div className="logo-mark">
              <Icon.Search />
            </div>
            <span className="logo-name">Recruit<span style={{ fontWeight: 300 }}>Match</span></span>
          </div>
          <div className="topbar-tag">
            <Icon.Sparkles /> Semantic AI
          </div>
        </header>

        {/* Main grid */}
        <main className="main">

          {/* ── Left panel ── */}
          <div className="panel-left">
            <div className="panel-hero">
              <div className="hero-eyebrow">CV Job Matcher</div>
              <h1 className="hero-title">
                Find roles that truly <em>fit</em> your profile
              </h1>
              <p className="hero-body">
                Upload your CV and our semantic matching engine ranks the most
                relevant opportunities from our live database — scored by
                real compatibility, not keyword overlap.
              </p>
            </div>

            <div className="upload-card">
              {/* Drop zone */}
              <input
                ref={inputRef}
                type="file"
                accept=".pdf"
                style={{ display: 'none' }}
                onChange={(e) => e.target.files?.[0] && acceptFile(e.target.files[0])}
              />
              <div
                className={`dropzone-wrap${dragOver ? ' drag-over' : ''}`}
                onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
                onDragLeave={() => setDragOver(false)}
                onDrop={handleDrop}
                onClick={() => inputRef.current?.click()}
                role="button"
                tabIndex={0}
                onKeyDown={(e) => (e.key === 'Enter' || e.key === ' ') && inputRef.current?.click()}
                aria-label="Upload CV PDF"
              >
                <div className="drop-icon-wrap">
                  <Icon.Upload />
                </div>
                <div className="drop-text-main">
                  {dragOver ? 'Release to upload' : 'Drop your CV here'}
                </div>
                <div className="drop-text-sub">
                  or <span>browse files</span> · PDF only · max 10 MB
                </div>
              </div>

              {/* File row */}
              {file && (
                <div className="file-row">
                  <div className="file-row-icon"><Icon.File /></div>
                  <span className="file-row-name">{file.name}</span>
                  <span className="file-row-size">{formatSize(file.size)}</span>
                  <button className="file-row-remove" onClick={clearFile} aria-label="Remove file">
                    <Icon.X size={14} />
                  </button>
                </div>
              )}

              {/* Error */}
              {error && (
                <div className="err-row">
                  <Icon.X size={14} />
                  {error}
                </div>
              )}

              {/* Submit */}
              <button
                className="btn-submit"
                onClick={handleSubmit}
                disabled={!file || loading}
              >
                {loading ? (
                  <><Icon.Loader /> Analyzing your CV…</>
                ) : (
                  <>Match My CV <Icon.ArrowRight /></>
                )}
              </button>

              {/* Stats */}
              <div className="info-row">
                <div className="info-stat">
                  <span className="info-stat-num">10k+</span>
                  <span className="info-stat-lbl">Live Jobs</span>
                </div>
                <div className="info-divider" />
                <div className="info-stat">
                  <span className="info-stat-num">&lt; 5s</span>
                  <span className="info-stat-lbl">Match Time</span>
                </div>
                <div className="info-divider" />
                <div className="info-stat">
                  <span className="info-stat-num">AI</span>
                  <span className="info-stat-lbl">Semantic</span>
                </div>
              </div>
            </div>
          </div>

          {/* ── Right panel ── */}
          <div className="panel-right">

            {/* Loading */}
            {loading && (
              <>
                <div className="results-bar">
                  <span className="results-heading">Finding matches…</span>
                </div>
                <SkeletonCards />
              </>
            )}

            {/* Results */}
            {showResults && (
              <>
                <div className="results-bar">
                  <span className="results-heading">Top Matches</span>
                  <span className="results-chip">{results!.length} jobs found</span>
                </div>
                {results!.map((job, i) => (
                  <JobCard key={i} job={job} idx={i} />
                ))}
              </>
            )}

            {/* Empty */}
            {showEmpty && (
              <>
                <div className="results-bar">
                  <span className="results-heading">Results</span>
                </div>
                <div className="empty-state">
                  <div className="empty-icon"><Icon.Search /></div>
                  <div className="empty-title">No matches found</div>
                  <p className="empty-body">
                    We couldn't find close matches for this CV. Try uploading a
                    different version or check back as new jobs are added daily.
                  </p>
                </div>
              </>
            )}

            {/* Default idle state */}
            {!loading && results === null && (
              <div className="empty-state">
                <div className="empty-icon"><Icon.Search /></div>
                <div className="empty-title">Your matches will appear here</div>
                <p className="empty-body">
                  Upload a PDF CV on the left and click <strong>Match My CV</strong> to
                  see ranked job opportunities tailored to your experience.
                </p>
              </div>
            )}

          </div>
        </main>

        <footer className="footer">
          RecruitMatch · Semantic matching powered by sentence-transformers · © {new Date().getFullYear()}
        </footer>
      </div>
    </>
  );
};

export default App;