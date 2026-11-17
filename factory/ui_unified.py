"""Unified Command 2500: one ergonomic, grounded AIOS workspace.

Presentation only. Reads task state and Acceptance Gate verdicts through
read-only SQLite. Never runs an agent, mutates a task, approves a gate or starts
a developer server. All user-controlled text is HTML-escaped.
"""
from __future__ import annotations

from html import escape
import re
import sqlite3

from factory import cli
from factory.live_studio import preview_port, worker_state
from factory.pixel_office import office_html
from factory.ui_campus import approval_panel, stage_track, task_hero

TASK_ID = re.compile(r"^[0-9a-f]{12}$")

COMMAND_CSS = r"""
/* Unified Command 2500 — functional space-station UI, not ornament overload */
:root{--bg:#080d18;--panel:#101b2b;--edge:#284055;--cyan:#95f3e4;--violet:#a8bcff;--light:#eaf5fb;--soft:#8ea8ba;--gold:#f5c586;--green:#8ddab9}
html{scroll-padding-top:90px}
body{background:radial-gradient(ellipse at 67% -9%,rgba(48,114,143,.19),transparent 43%),linear-gradient(180deg,#080e19,#090e17 70%);font-family:Segoe UI,Arial,sans-serif;color:#eaf4f9}
body:before{display:none}body:after{display:none}
.shell{max-width:1690px;padding:0 28px 35px}
.topbar{height:72px;min-height:72px;background:rgba(8,16,29,.91);position:sticky;top:0;z-index:30;border-bottom:1px solid #294055;backdrop-filter:blur(14px)}
.brand .mark{width:39px;height:39px}
.brand-text strong{font-size:16px;letter-spacing:.4px}
.brand-text small{letter-spacing:1.6px;color:#6f96ac}
.topnav{display:flex;gap:6px}
.topnav a{padding:8px 14px;color:#acc4d4;border:1px solid transparent;border-radius:9px}
.topnav .nav-approval{color:#e6d8bc;background:transparent;border-color:transparent}
.topnav .nav-approval:hover{background:#263b46}
.pill{padding:5px 11px;border-color:#315267;font-size:10px}
.panel{background:#101b2b;border-color:#274159;box-shadow:none}
.action{box-shadow:none}
.command-intro{display:flex;align-items:center;justify-content:space-between;gap:15px;padding:26px 2px 22px;border-bottom:1px solid #21374b}
.command-headline .eyebrow{font-size:9px;color:#89d9d2;letter-spacing:1.9px;margin:0 0 5px}
.command-headline h1{font-size:clamp(25px,3vw,37px);line-height:1.25;margin:0;letter-spacing:-.7px;font-weight:780}
.command-headline h1 em{background:none;color:#9de6df}
.command-headline p{color:#92b0c1;font-size:12px;line-height:1.8;margin:8px 0 0}
.command-new-btn{white-space:nowrap;text-align:center;border:1px solid #60bfb8;background:#143b42;color:#c2fff2;padding:11px 16px;border-radius:10px;font-size:12px;font-weight:800}
.command-new-btn:hover{background:#21545a;color:white}
.command-grid{display:grid;grid-template-columns:170px minmax(0,1fr) 258px;gap:17px;padding-top:21px;align-items:start}
.command-rail{position:sticky;top:92px;border:1px solid #263f51;border-radius:14px;padding:10px;background:#101b2b;display:grid;gap:3px}
.command-rail .rail-caption{font-size:9px;color:#678da0;letter-spacing:2px;padding:8px 12px 12px;text-transform:uppercase}
.command-rail a{display:flex;align-items:center;gap:9px;border-radius:9px;padding:11px 12px;color:#adcad8;font-size:12px}
.command-rail a:hover,.command-rail a.rail-active{background:#1b3645;color:#b9f3e9}
.command-rail a .rail-icon{font-size:15px;opacity:.9;width:19px;text-align:center}
.command-rail .rail-divider{height:1px;background:#294054;margin:9px 10px}
.command-main{min-width:0}
.command-metrics{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:11px;margin-bottom:13px}
.command-metric{border:1px solid #29435a;background:#111f30;border-radius:12px;padding:12px 17px;display:flex;align-items:center;justify-content:space-between;gap:8px}
.command-metric span{font-size:11px;color:#8eaabd;line-height:1.5}
.command-metric strong{font-size:23px;color:#f0f8fb;font-weight:740;line-height:1}
.command-metric.priority{border-color:#856947;background:#241f23}
.command-metric.priority strong{color:#ffd5a2}
.command-card{scroll-margin-top:94px;border:1px solid #2b455b;border-radius:15px;background:linear-gradient(160deg,#112035,#0d1929);padding:19px;margin-bottom:13px;min-width:0}
.command-card h2{margin:0;font-size:15px;font-weight:780;color:#e6f4f8}
.command-card h3{font-size:13px;margin:0}
.command-card-header{display:flex;justify-content:space-between;align-items:center;gap:11px;margin:0 0 14px}
.command-card-header small{color:#7ea9b7;font-size:10px}
.command-card-sub{color:#8faac0;font-size:11px}
.command-subline{margin:9px 0 0;color:#adc3d1;font-size:11px;overflow-wrap:anywhere}
.command-badge{font-size:10px;border:1px solid #426579;color:#abdbdb;border-radius:7px;padding:5px 8px;white-space:nowrap}
.command-badge[data-state="WAITING_APPROVAL"]{border-color:#a27b4d;color:#f2d1a3}
.command-badge[data-state="NEEDS_WORK"],.command-badge[data-state="BLOCKED"],.command-badge[data-state="FAILED"]{border-color:#92565c;color:#f2b5b5}
.command-badge[data-state="RUNNING"]{border-color:#3d8c80;color:#a1efd2}
.command-badge[data-state="DONE"]{border-color:#487965;color:#a1dfb6}
.command-badge[data-state="LEGACY_DONE"]{border-color:#a27b4d;color:#f2d1a3}
.command-focus-heading{display:flex;align-items:center;justify-content:space-between;gap:12px}
.command-focus-heading a{color:#e5f6fa;max-width:85%;font-size:19px;font-weight:760;overflow-wrap:anywhere}
.command-focus-heading a:hover{color:#9df4e9}
.command-focus-meta{margin-top:11px;display:flex;flex-wrap:wrap;gap:9px}
.command-chip{padding:5px 9px;border:1px solid #345168;background:#17283c;border-radius:8px;color:#aac2d2;font-size:10px}
.command-chip strong{color:#d9edf4}
.command-focus-note{margin-top:12px;color:#9bb6c6;font-size:12px;line-height:1.8;max-width:700px}
.command-focus-links{display:flex;flex-wrap:wrap;gap:7px;margin-top:14px}
.command-link{color:#b8f0e8;display:inline-flex;align-items:center;justify-content:center;padding:8px 12px;border:1px solid #3c6979;border-radius:9px;font-size:11px;font-weight:740;background:#16313e}
.command-link.secondary{background:transparent;border-color:#36536a;color:#c3d5e3}
.command-link:hover{background:#234b57;color:#fff}
.command-working-grid{display:grid;grid-template-columns:minmax(0,1.27fr) minmax(235px,.73fr);gap:13px}
.command-preview-screen{border:1px solid #38536a;border-radius:12px;overflow:hidden;background:#091829;min-height:295px}
.command-preview-placeholder{min-height:295px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:12px;text-align:center;padding:27px;background:radial-gradient(circle at 50% 24%,#1b394c,#0d1b2d 62%)}
.command-preview-placeholder .preview-icon{font-size:37px;color:#8cdbd3}
.command-preview-placeholder strong{font-size:14px}
.command-preview-placeholder p{font-size:11px;color:#92afc0;line-height:1.9;max-width:290px;margin:0}
.command-preview-screen iframe{width:100%;height:340px;background:white;border:0;display:block}
.command-preview-actions{display:flex;gap:10px;flex-wrap:wrap;align-items:center;justify-content:space-between;margin-top:11px}
.command-preview-actions small{font-size:10px;color:#89a7b9}
.command-approval-stack{display:grid;gap:8px}
.command-approval-item{border:1px solid #796043;background:#26212a;border-radius:10px;padding:11px}
.command-approval-item strong{display:block;font-size:12px;overflow-wrap:anywhere}
.command-approval-item p{font-size:10px;color:#c7b9b0;margin:7px 0}
.command-approval-item a{font-size:11px;color:#ffdab0;font-weight:790}
.command-approval-empty{font-size:12px;color:#9fc5ba;display:flex;align-items:center;gap:8px;line-height:1.7}
.command-approval-help{font-size:10px;color:#96acba;line-height:1.8;margin-top:10px}
.command-issue{margin-top:12px;padding:11px;border:1px solid #845866;border-radius:9px;color:#e8bcc2;background:#301f2e;font-size:12px}
.command-inspector{position:sticky;top:92px;display:grid;gap:12px}
.command-inspector .command-card{margin:0}
.command-inspector h2{font-size:13px}
.command-inspector p{font-size:11px;color:#92b0c2;line-height:1.8}
.command-health{display:grid;gap:9px}
.command-health-line{display:flex;align-items:center;justify-content:space-between;gap:8px;color:#9ab0c5;font-size:11px}
.command-health-line strong{color:#d3e9ef;max-width:140px;text-align:left;overflow-wrap:anywhere}
.command-health-line strong.warn{color:#ffcb93}
.command-health-line strong.ok{color:#94e4c4}
.command-mission-list{display:grid;gap:5px}
.command-mission-list a{display:block;padding:10px;border-radius:9px;border:1px solid transparent;color:#bfd4df;font-size:11px;overflow-wrap:anywhere}
.command-mission-list a:hover,.command-mission-list a.selected{background:#1c3445;border-color:#3a6270;color:#f4fbff}
.command-mission-list small{display:block;color:#819daf;margin-top:4px}
.command-detail-toggle{border:1px solid #34546a;border-radius:13px;background:#101e30;margin-bottom:12px;overflow:hidden;scroll-margin-top:95px}
.command-detail-toggle summary{list-style:none;cursor:pointer;display:flex;align-items:center;justify-content:space-between;gap:15px;padding:15px 20px;color:#dceaf1;font-weight:760;font-size:13px}
.command-detail-toggle summary::-webkit-details-marker{display:none}
.command-detail-toggle summary:after{content:"+";font-size:18px;color:#95d8d3}
.command-detail-toggle[open] summary:after{content:"−"}
.command-detail-toggle[open] summary{border-bottom:1px solid #2b495e}
.command-detail-content{padding:16px 19px}
.command-detail-content h2{font-size:14px;margin:0 0 12px}
.command-detail-content .office-intro{display:none}
.command-detail-content .office-layout{grid-template-columns:minmax(0,1.5fr) minmax(200px,.7fr)}
.command-detail-content .office-panel{padding:12px}
.command-detail-content .office-task-list{max-height:310px}
.command-detail-content .office-scene{background:#0b1726}
.command-form-grid{display:grid;grid-template-columns:1fr 1fr;gap:11px}
.command-form-grid label{margin:0}
.command-form-grid input,.command-form-grid select{margin-top:7px}
.command-form-textarea{margin:12px 0}
.command-form-textarea label{margin:0 0 7px}
.command-form-textarea textarea{min-height:117px}
.command-submit{margin:6px 0 0;max-width:270px}
.command-footer-note{font-size:10px;color:#87a0b3;line-height:1.8;margin-top:9px}
.command-audit{border-top:1px solid #294155;margin-top:13px;padding-top:12px;font-size:11px;color:#90b0c4}
.command-detail-page{max-width:1060px;margin:0 auto}
.command-detail-page .task-headline{margin:12px 0 15px}
.command-detail-page .stage-section{border-color:#294b62;background:#101e30}
.command-detail-page .approval-detail{margin:16px 0}
.command-detail-page .detail-block{background:#111f31}
.command-detail-page .command-detail-toggle pre{max-height:370px}
.command-detail-page .command-detail-toggle .action{max-width:400px}
.command-detail-page .command-detail-toggle .panel{border:none;box-shadow:none;background:transparent;padding:8px}
.command-detail-page .command-detail-toggle .panel h3{font-size:14px}
.command-detail-page .command-detail-toggle .panel-head{margin-bottom:8px}
.command-detail-page .command-detail-toggle .hint{margin-top:4px}
.command-detail-page .command-detail-toggle form{margin-bottom:11px}
.command-quick-status{display:flex;gap:9px;align-items:center;flex-wrap:wrap}
.command-connect{color:#98b3c2;font-size:10px}
.command-separator{width:1px;height:14px;background:#355267}
.command-screenreader{position:absolute;clip-path:inset(50%);width:1px;height:1px;overflow:hidden}
@media(min-width:1500px){.command-grid{grid-template-columns:190px minmax(0,1fr) 282px;gap:20px}.command-working-grid{grid-template-columns:minmax(0,1.3fr) minmax(280px,.7fr)}}
@media(max-width:1200px){.command-grid{grid-template-columns:142px minmax(0,1fr)}.command-inspector{grid-column:2;position:static;grid-template-columns:1fr 1fr}.command-working-grid{grid-template-columns:1fr 1fr}}
@media(max-width:930px){.command-grid{grid-template-columns:1fr}.command-rail{position:static;display:flex;overflow-x:auto;white-space:nowrap;gap:4px}.command-rail .rail-caption,.command-rail .rail-divider{display:none}.command-rail a{flex:none;padding:8px 10px}.command-inspector{grid-column:1}.command-intro{padding-top:18px}.command-detail-content .office-layout{grid-template-columns:1fr}.command-rail{scrollbar-width:thin}}
@media(max-width:720px){.shell{padding-inline:13px}.topbar{height:68px;min-height:68px}.topright .pill:not(.online){display:none}.command-working-grid{grid-template-columns:1fr}.command-metrics{gap:7px}.command-metric{padding:11px}.command-metric span{font-size:10px}.command-metric strong{font-size:20px}.command-inspector{grid-template-columns:1fr}.command-card{padding:15px}.command-intro{align-items:start;flex-direction:column}.command-form-grid{grid-template-columns:1fr}.command-headline h1{font-size:26px}.command-preview-screen iframe{height:260px}.command-quick-status{display:none}}
/* Command Deck 2500 — high-contrast architectural redesign.
   Visual details are CSS-native; no external textures, fonts, or GPU-heavy effects. */
body{background:#060a12;color:#e6f3f7}
body::selection{background:#275e64;color:#fff}
.shell{max-width:1800px;min-height:100vh}
.topbar{border:1px solid #204558;border-top:0;border-radius:0 0 18px 18px;background:linear-gradient(115deg,rgba(11,26,40,.98),rgba(8,14,27,.98));box-shadow:0 16px 30px rgba(0,0,0,.16)}
.brand .mark{filter:drop-shadow(0 0 8px rgba(84,239,218,.58))}
.brand-text small{color:#5be6d7;letter-spacing:1.9px;font-weight:850}
.command-intro{position:relative;isolation:isolate;min-height:268px;display:grid;grid-template-columns:minmax(0,1fr) 240px auto;align-items:center;gap:22px;border:1px solid #2e6070;border-radius:23px;padding:36px 31px;margin:25px 0 2px;overflow:hidden;background:radial-gradient(circle at 73% 49%,rgba(43,136,145,.20),transparent 30%),linear-gradient(120deg,#112b3b 0%,#0b1828 53%,#101b32 100%);box-shadow:inset 0 0 0 1px rgba(176,255,237,.04),0 25px 65px rgba(0,0,0,.27)}
.command-intro:before{content:"";position:absolute;inset:0;pointer-events:none;z-index:-1;opacity:.28;background:linear-gradient(90deg,transparent 98%,rgba(96,216,214,.18) 99%),linear-gradient(transparent 98%,rgba(96,216,214,.18) 99%);background-size:38px 38px;mask-image:linear-gradient(90deg,transparent 8%,#000 90%)}
.command-intro:after{content:"2500";position:absolute;font-size:190px;font-weight:900;letter-spacing:-18px;line-height:1;left:2%;bottom:-49px;opacity:.036;color:#a9fff1;pointer-events:none}
.command-headline{z-index:1;min-width:0}
.command-kicker{display:flex;align-items:center;gap:9px;color:#8bdfd7;font:800 10px/1.6 Consolas,monospace;letter-spacing:2px;text-transform:uppercase}
.command-signal{width:7px;height:7px;border-radius:100%;background:#a5fae7;box-shadow:0 0 0 4px rgba(108,238,211,.08),0 0 15px rgba(108,238,211,.7);flex:none}
.command-headline h1{font-weight:830;letter-spacing:-1.7px;line-height:1.2;font-size:clamp(30px,3.3vw,48px);margin:18px 0 11px}
.command-headline h1 em{font-style:normal;background:linear-gradient(100deg,#9cfff0,#8ebfff);-webkit-background-clip:text;background-clip:text;color:transparent}
.command-headline p{font-size:13px;color:#b3cdd8;max-width:660px;margin:0;line-height:1.85}
.command-hero-meta{display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin-top:20px}
.command-hero-meta span{font:700 9px/1.5 Consolas,monospace;letter-spacing:1px;color:#8eabbc;padding:5px 8px;border:1px solid rgba(117,201,207,.18);border-radius:6px;background:rgba(7,23,34,.3)}
.command-new-btn{position:relative;z-index:2;background:linear-gradient(110deg,#afffed,#81d6ef);color:#07222c!important;font-weight:850;border:none;border-radius:12px;padding:13px 19px;box-shadow:0 8px 22px rgba(47,155,156,.16);text-align:center}
.command-new-btn:hover{background:#d9fff7;color:#041923!important;transform:translateY(-1px)}
.command-hero-orbit{position:relative;height:206px;width:206px;justify-self:center;border-radius:100%;background:radial-gradient(circle,rgba(83,226,210,.09) 0%,rgba(83,226,210,.05) 37%,transparent 67%);filter:drop-shadow(0 0 17px rgba(28,185,195,.13))}
.command-orbit-ring{position:absolute;inset:8px;border-radius:50%;border:1px solid rgba(123,236,224,.3)}
.command-orbit-ring.outer{border-top:3px solid #9cf7e7;border-left:1px dashed rgba(142,239,238,.3);animation:command-orbit 38s linear infinite}
.command-orbit-ring.outer:before{content:"";position:absolute;left:28px;top:17px;width:8px;height:8px;border-radius:100%;background:#d9fff7;box-shadow:0 0 13px #76e9dc}
.command-orbit-ring.inner{inset:28px;border-color:#4f9dab;border-right:2px solid #96c7ff;animation:command-orbit 52s linear infinite reverse}
.command-orbit-core{position:absolute;inset:53px;border-radius:50%;display:flex;align-items:center;justify-content:center;flex-direction:column;background:radial-gradient(circle at 45% 35%,#2a777c,#0a2d3d 70%);border:1px solid #73bfc5;box-shadow:inset 0 0 25px rgba(130,245,225,.12),0 0 25px rgba(103,222,213,.14)}
.command-orbit-core b{font:900 33px/1 Consolas,monospace;letter-spacing:-2px;color:#dbfff7}
.command-orbit-core small{font:700 9px/1.5 Consolas,monospace;letter-spacing:1px;color:#81d9d3}
.command-orbit-beam{position:absolute;inset:0;border-radius:50%;border:1px dotted rgba(112,218,229,.3)}
@keyframes command-orbit{to{transform:rotate(360deg)}}
.command-grid{gap:16px;padding-top:17px}
.command-rail{background:linear-gradient(180deg,#0e2031,#0a1423);border:1px solid #2a5363;box-shadow:inset 3px 0 rgba(79,192,185,.1)}
.command-rail .rail-caption{color:#68b0c0}
.command-rail a{font-weight:650}
.command-rail a.rail-active{border:1px solid #36767a;background:linear-gradient(90deg,#153f47,#102c3f);box-shadow:inset 3px 0 #8de8d6;color:#c6fff3}
.command-card{position:relative;background:linear-gradient(145deg,#112335,#0d1929);border-color:#294d60;box-shadow:inset 0 1px rgba(202,255,241,.035)}
.command-card::before{content:"";position:absolute;inset:12px auto auto 12px;width:21px;height:21px;border-left:1px solid rgba(126,236,220,.25);border-top:1px solid rgba(126,236,220,.25);pointer-events:none}
.command-card-header{border-bottom:1px solid #264153;padding-bottom:12px}
.command-card-header h2{letter-spacing:.1px}
.command-metric{background:linear-gradient(115deg,#122c3b,#0d1d2e);border-color:#2b5867;padding:17px 18px;min-height:83px}
.command-metric strong{font:800 30px/1 Consolas,monospace;color:#c8f7ed}
.command-metric.priority{background:linear-gradient(115deg,#362c2a,#171b2b);border-color:#745f4c}
.command-focus-heading{border-inline-start:3px solid #76e9d4;padding-inline-start:16px}
.command-focus-heading a{font-size:21px}
.command-inspector .command-card:first-child{border-top:2px solid #58b8b5}
.command-preview-screen{border-radius:11px;border-color:#386b77;background:#0b1e29}
.command-preview-placeholder{background:radial-gradient(circle at center,#193e4a,#0e1b2b 63%)}
.command-detail-toggle{border-color:#294d61;background:#0d1b2b}
.command-detail-toggle[open] summary{background:#132e3a}
.command-approval-item{background:linear-gradient(110deg,#2d282a,#1c1e29)}
@media(max-width:1490px){.command-intro{grid-template-columns:minmax(0,1fr) 170px auto}.command-hero-orbit{transform:scale(.82);width:170px;height:170px}.command-new-btn{padding-inline:13px}}
@media(max-width:1130px){.command-intro{grid-template-columns:minmax(0,1fr) 180px}.command-intro>.command-new-btn{grid-column:1/-1;justify-self:start}.command-hero-orbit{grid-column:2;grid-row:1;transform:scale(.86)}}
@media(max-width:700px){.command-intro{display:block;padding:25px 19px;min-height:0;border-radius:17px}.command-hero-orbit{display:none}.command-headline h1{font-size:29px;letter-spacing:-1px}.command-hero-meta{margin-bottom:16px}.command-new-btn{display:inline-block}.command-metric{min-height:65px;padding:12px 10px}.command-metric strong{font-size:22px}.command-hero-meta span:nth-child(n+3){display:none}}

@media(prefers-reduced-motion:reduce){*,*:before,*:after{animation:none!important;transition:none!important;scroll-behavior:auto!important}}
"""

COMMAND_JS = r"""'use strict';
(() => {
  // Workspace navigation always works, including when no task exists yet.
  document.querySelectorAll('a[href="#mission-intake"],a[href="#agents"]').forEach((a) => {
    a.addEventListener('click', () => {
      const id = a.getAttribute('href').slice(1);
      const panel = document.getElementById(id);
      if (panel && panel.tagName === 'DETAILS') panel.open = true;
    });
  });
  if (location.hash === '#agents' || location.hash === '#mission-intake') {
    const panel = document.getElementById(location.hash.slice(1));
    if (panel && panel.tagName === 'DETAILS') panel.open = true;
  }
  const root = document.querySelector('[data-command-task]');
  const selected = root ? root.getAttribute('data-command-task') : '';
  const taskId = /^[0-9a-f]{12}$/.test(selected) ? selected : '';
  const byId = (id) => document.getElementById(id);
  let inflight = false;
  let approvalSignature = null;

  function displayApprovals(items) {
    const list = byId('command-approval-list');
    if (!list || !Array.isArray(items)) return;
    const safeItems = items.filter(x => x && /^[0-9a-f]{12}$/.test(x.id)).slice(0,50);
    const signature = JSON.stringify(safeItems);
    if (signature === approvalSignature) return;
    approvalSignature = signature;
    list.replaceChildren();
    if (!safeItems.length) {
      const empty = document.createElement('div');
      empty.className = 'command-approval-empty';
      empty.textContent = '✓ لا توجد موافقات معلّقة الآن.';
      list.appendChild(empty);
      return;
    }
    safeItems.forEach((x) => {
      const article = document.createElement('article');
      article.className = 'command-approval-item';
      const name = document.createElement('strong');
      name.textContent = String(x.title || 'مهمة');
      const stage = document.createElement('p');
      stage.textContent = String(x.stage || '—') + ' · مراجعة إلزامية';
      const action = document.createElement('a');
      action.href = '/ideas/' + x.id + '#task-approval';
      action.textContent = 'افتح القرار والتقارير ←';
      article.append(name, stage, action);
      list.appendChild(article);
    });
  }
  function setText(id, value) {
    const el = byId(id);
    if (el) el.textContent = String(value ?? '—');
  }

  const update = async () => {
    if (inflight || document.hidden) return;
    inflight = true;
    try {
      const endpoint = '/command/state' + (taskId ? '?task=' + taskId : '');
      const r = await fetch(endpoint, {cache:'no-store'});
      if (!r.ok) throw Error('State unavailable');
      const d = await r.json();
      if (!d || !d.metrics || !Array.isArray(d.approvals)) throw Error('Invalid response');
      const m = d.metrics;
      setText('command-total', m.total);
      setText('command-running', m.running);
      setText('command-pending', m.approvals);
      setText('command-approval-count', String(m.approvals) + ' معلّقة');
      setText('command-health-worker', d.worker);
      setText('command-health-verdict', d.verification?.verdict || 'NOT VERIFIED');
      setText('command-health-stage', d.verification?.stage || '—');
      setText('command-health-sha', d.verification?.sha || '—');
      setText('command-health-failures', m.needs_work);
      const verdict = byId('command-health-verdict');
      if (verdict) verdict.className = d.accepted_final ? 'ok' : 'warn';
      displayApprovals(d.approvals);
      if (taskId && d.task?.id === taskId) {
        const status = byId('command-task-state');
        const stage = byId('command-task-stage');
        const rawStatus = String(d.task.status || 'UNKNOWN');
        if (status) {
          status.dataset.state = rawStatus === 'DONE' && !d.accepted_final ? 'LEGACY_DONE' : rawStatus;
          status.textContent = rawStatus === 'DONE' && !d.accepted_final
            ? 'DONE · غير متحقق' : rawStatus;
        }
        if (stage) stage.textContent = String(d.task.stage || '—');
      }
      setText('command-connection', 'متصل · بيانات النظام');
    } catch (_) {
      setText('command-connection', 'الاتصال متوقف · آخر حالة محفوظة');
    } finally {
      inflight = false;
    }
  };
  update();
  setInterval(update, 5000);
  document.addEventListener('visibilitychange', () => { if (!document.hidden) update(); });
})();
"""


def _pick_task(records: list[dict], requested: str | None) -> dict | None:
    if requested and TASK_ID.fullmatch(requested):
        for r in records:
            if r["id"] == requested:
                return r
    for status in ("RUNNING", "NEEDS_WORK", "BLOCKED", "WAITING_APPROVAL",
                   "INTERRUPTED", "PENDING"):
        for r in records:
            if r["status"] == status:
                return r
    return records[0] if records else None


def _verification(task_id: str) -> dict:
    """Never manufacture a PASS if the v3.1 Acceptance Gate isn't available."""
    if not TASK_ID.fullmatch(task_id):
        return {"verdict": "UNKNOWN", "stage": "—", "sha": ""}
    try:
        with cli.managed_readonly_connect() as db:
            last = db.execute(
                "SELECT stage, verdict, commit_sha FROM acceptance_stage_results "
                "WHERE task_id=? ORDER BY updated_at DESC LIMIT 1", (task_id,)
            ).fetchone()
            if last is None:
                return {"verdict": "NOT VERIFIED", "stage": "—", "sha": ""}
            return {"verdict": str(last["verdict"])[:40],
                    "stage": str(last["stage"])[:40],
                    "sha": str(last["commit_sha"])[:12]}
    except (sqlite3.Error, ValueError, OSError):
        return {"verdict": "NOT VERIFIED", "stage": "—", "sha": ""}



def command_snapshot(focus: str | None = None) -> dict:
    """Bounded, read-only snapshot for the dashboard, without goals or code.

    Last worker and acceptance states are recorded evidence, not a claim that
    a currently running agent passed checks or that an app was deployed.
    """
    from factory.intake import list_ideas

    records = list_ideas(limit=50)
    active = _pick_task(records, focus)
    verdict = (_verification(active["id"]) if active else
               {"verdict": "NOT VERIFIED", "stage": "—", "sha": ""})
    approved_final = bool(active and active["status"] == "DONE" and
                          verdict["verdict"] == "ACCEPTED" and
                          verdict["stage"] == "final")
    return {
        "task": ({
            "id": active["id"],
            "status": active["status"][:40],
            "stage": active["stage"][:40],
        } if active else None),
        "metrics": {
            "total": len(records),
            "running": sum(r["status"] == "RUNNING" for r in records),
            "approvals": sum(r["status"] == "WAITING_APPROVAL" for r in records),
            "needs_work": sum(r["status"] in ("NEEDS_WORK", "BLOCKED", "FAILED")
                              for r in records),
        },
        "approvals": [
            {"id": r["id"], "title": r["title"][:100], "stage": r["stage"][:40]}
            for r in records
            if r["status"] == "WAITING_APPROVAL" and TASK_ID.fullmatch(r["id"])
        ],
        "verification": verdict,
        "accepted_final": approved_final,
        "worker": worker_state()[:40],
    }


def home_html(csrf: str, records: list[dict], *, focus: str | None = None) -> tuple[str, int | None]:
    """Return HTML and explicitly configured iframe port for a restricted CSP."""
    active = _pick_task(records, focus)
    waiting = [r for r in records if r["status"] == "WAITING_APPROVAL"]
    running = sum(r["status"] == "RUNNING" for r in records)
    failures = sum(r["status"] in ("NEEDS_WORK", "BLOCKED", "FAILED") for r in records)
    port = None
    if active:
        try:
            port = preview_port(active["id"])
        except (OSError, ValueError, TypeError):
            port = None
    verification = _verification(active["id"]) if active else {"verdict": "—", "stage": "—", "sha": ""}
    accepted_final = bool(active and active["status"] == "DONE" and
                          verification["verdict"] == "ACCEPTED" and
                          verification["stage"] == "final")
    worker = worker_state()
    result = (
        '<section class="command-intro" id="workspace" aria-label="مركز القيادة">'
        '<div class="command-headline">'
        '<div class="command-kicker"><span class="command-signal" aria-hidden="true"></span>'
        'UNIFIED OPERATIONS · COMMAND DECK 2500</div>'
        '<h1>مركز قيادة <em>جيل المستقبل.</em></h1>'
        '<p>مهمتك، فريق الـAI، الموافقات والتحقق — كل قرار في مكان واحد.</p>'
        '<div class="command-hero-meta"><span>01 / MISSION CONTROL</span>'
        '<span>LOCAL FIRST</span><span>READ-ONLY TELEMETRY</span></div></div>'
        '<div class="command-hero-orbit" aria-hidden="true">'
        '<div class="command-orbit-ring outer"></div>'
        '<div class="command-orbit-ring inner"></div>'
        '<div class="command-orbit-core"><b>ISA</b><small>AI / OS</small></div>'
        '<div class="command-orbit-beam"></div></div>'
        '<a class="command-new-btn" href="#mission-intake">＋ إطلاق مهمة</a>'
        '</section>'
        '<div class="command-grid"><nav class="command-rail" aria-label="أقسام مركز القيادة">'
        '<span class="rail-caption">NAVIGATION</span>'
        '<a class="rail-active" href="#workspace"><span class="rail-icon">◈</span> القيادة</a>'
        '<a href="#missions"><span class="rail-icon">▤</span> المهام</a>'
        '<a href="#approvals"><span class="rail-icon">◇</span> الموافقات</a>'
        '<a href="#live"><span class="rail-icon">▣</span> المعاينة</a>'
        '<a href="#agents"><span class="rail-icon">⌘</span> الوكلاء</a>'
        '<span class="rail-divider"></span>'
        '<a href="#mission-intake"><span class="rail-icon">＋</span> إنشاء مشروع</a>'
        '</nav><div class="command-main">'
        '<section class="command-metrics" aria-label="ملخص المهام">'
        '<div class="command-metric"><span>إجمالي المهام</span><strong id="command-total">'
        + str(len(records)) + '</strong></div>'
        '<div class="command-metric"><span>تنفيذ جارٍ</span><strong id="command-running">'
        + str(running) + '</strong></div>'
        '<div class="command-metric priority"><span>تحتاج قرارك</span><strong id="command-pending">'
        + str(len(waiting)) + '</strong></div></section>'
        '<section class="command-card" id="focus" aria-labelledby="focus-title">'
        '<div class="command-card-header"><h2 id="focus-title">المهمة الحالية</h2>'
        '<span class="command-connect" id="command-connection">حالة محفوظة</span></div>'
    )
    if active:
        tid = escape(active["id"], quote=True)
        result += (
            '<div data-command-task="' + tid + '" data-accepted="'
            + ('true' if accepted_final else 'false') + '">'
            '<div class="command-focus-heading"><a href="/ideas/' + tid + '">'
            + escape(active["title"]) + '</a>'
            '<span id="command-task-state" class="command-badge" data-state="'
            + ('LEGACY_DONE' if active["status"] == "DONE" and not accepted_final
               else escape(active["status"], quote=True))
            + '">' + ('DONE · غير متحقق' if active["status"] == "DONE" and not accepted_final
                     else escape(active["status"])) + '</span></div>'
            '<div class="command-focus-meta">'
            '<span class="command-chip">المرحلة: <strong id="command-task-stage">'
            + escape(active["stage"]) + '</strong></span>'
            '<span class="command-chip">ID: ' + tid + '</span>'
            '<span class="command-chip">التحقق: <strong>'
            + escape(verification["verdict"]) + '</strong></span></div>'
            '<p class="command-focus-note">' + escape(active["goal_preview"]) + '</p>'
            '<div class="command-focus-links">'
            '<a class="command-link" href="/ideas/' + tid + '">مراجعة المهمة والتقارير</a>'
            '<a class="command-link secondary" href="/studio/' + tid + '">Live Studio</a>'
            '</div></div>'
        )
        if active["status"] in ("BLOCKED", "NEEDS_WORK", "FAILED"):
            result += ('<div class="command-issue" role="status">'
                       'المهمة تحتاج معالجة. راجع تقرير القبول قبل محاولة المتابعة.</div>')
    else:
        result += (
            '<div class="command-preview-placeholder">'
            '<strong>لا توجد مهام بعد</strong>'
            '<p>ابدأ مشروعاً جديداً وسيظهر هنا مع حالته الفعلية.</p>'
            '<a class="command-link" href="#mission-intake">إنشاء أول مهمة</a></div>'
        )
    result += '</section><div class="command-working-grid">'
    result += (
        '<section class="command-card" id="live">'
        '<div class="command-card-header"><h2>المعاينة الحية</h2>'
        '<small>LOCAL DEVELOPMENT ONLY</small></div>'
        '<div class="command-preview-screen">'
    )
    if active and port is not None:
        url = "http://127.0.0.1:" + str(port) + "/"
        result += (
            '<iframe title="معاينة المشروع المحلية" src="' + escape(url, quote=True)
            + '" loading="lazy" referrerpolicy="no-referrer" '
            'sandbox="allow-scripts allow-same-origin allow-forms"></iframe>'
        )
    else:
        result += (
            '<div class="command-preview-placeholder">'
            '<span class="preview-icon" aria-hidden="true">▣</span>'
            '<strong>المعاينة غير متصلة</strong>'
            '<p>شغّل سيرفر تطوير المشروع وحدد منفذه من Live Studio. '
            'لن يتم تشغيل أي أمر تلقائياً.</p></div>'
        )
    result += '</div><div class="command-preview-actions">'
    if active:
        result += '<a class="command-link secondary" href="/studio/' + escape(active["id"],quote=True) + '">إعداد المعاينة</a>'
    else:
        result += '<a class="command-link secondary" href="#mission-intake">ابدأ مشروعك</a>'
    result += '<small>لا يوجد نشر تلقائي أو تشغيل خفي للسيرفر</small></div></section>'
    result += (
        '<section class="command-card" id="approvals" aria-labelledby="approval-center-title">'
        '<div class="command-card-header"><h2 id="approval-center-title">◈ مركز القرارات</h2>'
        '<span class="command-badge" data-state="WAITING_APPROVAL" id="command-approval-count">'
        + str(len(waiting)) + ' معلّقة</span></div>'
        '<div class="command-approval-stack" id="command-approval-list" aria-live="polite">'
    )
    if not waiting:
        result += (
            '<div class="command-approval-empty">✓ لا توجد موافقات معلّقة الآن.</div>'
        )
    else:
        for r in waiting:
            tid = escape(r["id"], quote=True)
            result += (
                '<article class="command-approval-item"><strong>' + escape(r["title"])
                + '</strong><p>' + escape(r["stage"])
                + ' · مراجعة إلزامية قبل المتابعة</p>'
                '<a href="/ideas/' + tid + '#task-approval">افتح القرار والتقارير ←</a></article>'
            )
    result += (
        '</div><p class="command-approval-help">لا تُنفّذ الموافقة من هذه القائمة. '
        'افحص التقارير أولاً، ثم اعتمد من صفحة المهمة.</p></section></div>'
    )
    # Keep the original Pixel Office scene, but reveal it on demand to reduce clutter.
    result += (
        '<details class="command-detail-toggle" id="agents">'
        '<summary>⌘ مكتب الـAgents — عرض مصغّر قابل للتوسيع</summary>'
        '<div class="command-detail-content"><section id="departments" aria-label="الأقسام">'
        + office_html() + '</section></div></details>'
    )
    result += (
        '<details class="command-detail-toggle" id="mission-intake">'
        '<summary>＋ إنشاء مهمة أو مشروع جديد</summary>'
        '<div class="command-detail-content"><form method="post" action="/ideas">'
        '<input type="hidden" name="csrf" value="' + escape(csrf,quote=True) + '">'
        '<div class="command-form-grid"><label for="title">اسم المشروع'
        '<input id="title" name="title" maxlength="100" placeholder="مثال: Nova Systems">'
        '</label><label for="methodology">منهجية العمل'
        '<select id="methodology" name="methodology">'
        '<option value="hybrid">Hybrid</option><option value="agile">Agile</option>'
        '<option value="traditional">Traditional</option></select></label></div>'
        '<div class="command-form-textarea"><label for="idea">وصف المهمة</label>'
        '<textarea id="idea" name="idea" required maxlength="4000" '
        'placeholder="صف الهدف والحدود، وضع المواصفات التفصيلية داخل مستودع المشروع...">'
        '</textarea></div>'
        '<button type="submit" class="action command-submit">إنشاء المشروع والمهمة</button>'
        '<p class="command-footer-note">إنشاء المهمة يضيفها للطابور؛ قد يبدأ الـWorker تلقائياً إذا كان Auto-run مفعّلاً. '
        'Acceptance Contract مطلوب قبل البناء وفق محرك v3.1.</p></form></div></details>'
        '</div><aside class="command-inspector">'
        '<section class="command-card"><div class="command-card-header"><h2>صحة التنفيذ</h2>'
        '<small>REAL EVIDENCE</small></div>'
        '<div class="command-health">'
        '<div class="command-health-line"><span>آخر Worker state</span><strong id="command-health-worker">'
        + escape(worker[:40]) + '</strong></div>'
        '<div class="command-health-line"><span>آخر نتيجة قبول</span><strong id="command-health-verdict"'
        + (' class="ok"' if accepted_final else ' class="warn"')
        + '>' + escape(verification["verdict"]) + '</strong></div>'
        '<div class="command-health-line"><span>مرحلة التحقق</span><strong id="command-health-stage">'
        + escape(verification["stage"]) + '</strong></div>'
        '<div class="command-health-line"><span>Commit متحقق</span><strong id="command-health-sha">'
        + escape(verification["sha"] or "—") + '</strong></div>'
        '<div class="command-health-line"><span>تحتاج إصلاح</span><strong id="command-health-failures">'
        + str(failures) + '</strong></div></div>'
        '<p class="command-footer-note">غياب دليل تحقق يُعرض NOT VERIFIED، '
        'ولا يُعتبر اختباراً ناجحاً. Worker state هي آخر حالة مُسجلة فقط.</p>'
        '</section>'
        '<section class="command-card" id="missions">'
        '<div class="command-card-header"><h2>المشاريع والمهام</h2>'
        '<small>' + str(len(records)) + ' TASKS</small></div>'
        '<div class="command-mission-list">'
    )
    if not records:
        result += '<p class="command-card-sub">لا توجد مشاريع مسجلة.</p>'
    for r in records:
        tid = escape(r["id"],quote=True)
        selected = ' selected' if active and active["id"] == r["id"] else ''
        result += (
            '<a class="' + selected.strip() + '" href="/?task=' + tid + '#focus">'
            + escape(r["title"]) + '<small>' + escape(r["status"]) + ' · '
            + escape(r["stage"]) + '</small></a>'
        )
    result += (
        '</div></section>'
        '<section class="command-card"><h2>الإجراء التالي</h2>'
        '<p>راجع الموافقات والقبول أولاً. لا تدمج أو تنشر من لوحة المراقبة.</p>'
        '<a class="command-link secondary" href="/office">فتح المكتب بكامل الشاشة</a>'
        '</section></aside></div>'
        '<script src="/command.js" defer></script>'
    )
    return result, port


def detail_html(csrf: str, r: dict) -> str:
    """Keep current approval routes intact, group verbose tools, outputs, audit."""
    tid = escape(r["id"], quote=True)
    status = escape(r["status"], quote=True)
    result = (
        '<div class="command-detail-page">'
        '<div class="command-intro"><div class="command-headline">'
        '<p class="eyebrow">UNIFIED COMMAND / MISSION DETAIL</p>'
        '<h1>قرارات المهمة <em>ومخرجاتها</em></h1>'
        '<p>مراجعة التقارير أولاً، ثم اعتماد الخطوة المطلوبة.</p>'
        '</div><a class="command-new-btn" href="/">مركز القيادة</a></div>'
        + task_hero(r) + stage_track(r) + approval_panel(csrf, r)
        + '<div class="command-focus-links"><a class="command-link" href="/studio/' + tid
        + '">فتح Live Studio</a>'
        '<a class="command-link secondary" href="/#approvals">مركز الموافقات</a></div>'
        '<section class="command-card" style="margin-top:15px">'
        '<div class="command-card-header"><h2>ملخص المهمة</h2>'
        '<span class="command-badge" data-state="' + status + '">' + status + '</span></div>'
        '<p class="command-subline">المرحلة التالية: <strong>' + escape(r["next_stage"]) + '</strong></p>'
        '<p class="command-subline">المستودع المحلي: <code>' + escape(r["project"]) + '</code></p>'
        '<details class="command-detail-toggle" style="margin-top:12px">'
        '<summary>وصف المهمة الكامل</summary><div class="command-detail-content">'
        '<pre>' + escape(r["goal"]) + '</pre></div></details>'
    )
    if r["error"]:
        result += '<div class="command-issue" role="status">' + escape(r["error"]) + '</div>'
    result += '</section>'
    result += (
        '<h2 id="reports" style="font-size:16px;margin:25px 0 10px">التقارير والتحقق</h2>'
    )
    if not r["outputs"]:
        result += (
            '<section class="command-card"><p class="command-card-sub">'
            'لم تُسجّل تقارير مراحل بعد. غياب التقرير ليس نجاحاً.</p></section>'
        )
    for item in r["outputs"]:
        result += (
            '<details class="command-detail-toggle"><summary>مرحلة: '
            + escape(item["stage"]) + '</summary>'
            '<div class="command-detail-content"><pre>'
            + escape(item["content"]) + '</pre></div></details>'
        )
    result += (
        '<details class="command-detail-toggle" id="project-tools">'
        '<summary>أدوات إضافية — بحث وتسويق وفحص GitHub</summary>'
        '<div class="command-detail-content">'
        '<section class="panel"><div class="panel-head"><h3>أدوات المشروع</h3>'
        '<span class="tag">OPTIONAL</span></div>'
        '<p class="hint">أدوات مساعدة؛ لا تنشر ولا تعتمد النتائج تلقائياً.</p>'
        '<form method="post" action="/ideas/' + tid + '/research">'
        '<input type="hidden" name="csrf" value="' + escape(csrf,quote=True) + '">'
        '<label for="research-query">بحث GitHub Open Source</label>'
        '<input id="research-query" name="query" maxlength="150" '
        'placeholder="e.g. booking open source">'
        '<button class="action" type="submit">بحث الرخص والمشاريع</button></form>'
        '<form method="post" action="/ideas/' + tid + '/marketing">'
        '<input type="hidden" name="csrf" value="' + escape(csrf,quote=True) + '">'
        '<button class="action" type="submit">تجهيز مسودة تسويق</button></form>'
        '<form method="post" action="/ideas/' + tid + '/github-preflight">'
        '<input type="hidden" name="csrf" value="' + escape(csrf,quote=True) + '">'
        '<button class="action" type="submit">فحص جاهزية GitHub PR</button></form>'
        '</section></div></details>'
        '<details class="command-detail-toggle" id="audit-events">'
        '<summary>سجل الأحداث (Audit Log)</summary>'
        '<div class="command-detail-content"><pre>'
    )
    for item in r["events"]:
        result += escape(item["ts"] + "  " + item["event"] + "  "
                         + item["info"][:180]) + "\n"
    return result + '</pre></div></details></div>'
