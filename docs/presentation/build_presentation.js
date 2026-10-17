const pptxgen = require('pptxgenjs');
const { applyTheme } = require('/root/.claude/skills/synced/0677fbc7-bdde-4233-96ea-70cbf1e5cdf2_0ce747ea-87ed-4ac0-bf85-d4e84a6e643a/pptx/scripts/apply_theme.js');
const OUT = '/home/user/reflica/docs/presentation/Reflica_Proposal_Presentation_1.pptx';
const THEME = { name: 'Reflica India', headFontFace: 'Cambria', bodyFontFace: 'Calibri',
  colors: { dk1:'1A2238', lt1:'FFFFFF', dk2:'3E4A61', lt2:'EEF2F7',
    accent1:'1A2238', accent2:'E07A2F', accent3:'138A72', accent4:'5B6B8C', accent5:'C9D3E3', accent6:'B33A3A',
    hlink:'138A72', folHlink:'5B6B8C' } };
const HEX = { navy:'1A2238', saffron:'E07A2F', green:'138A72', slate:'5B6B8C', grid:'D5DCE6' };
const pres = new pptxgen();
pres.layout = 'LAYOUT_WIDE';
pres.title = 'IndiaEconForecast / Reflica India – Proposal Presentation';
pres.author = 'Sundram Awasthi';
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
const C = pres.SchemeColor;
const W = 13.333;

pres.defineSlideMaster({ title: 'DARK', background: { color: C.text1 },
  objects: [{ placeholder: { options: { name: 'title', type: 'title', x: 0.8, y: 1.7, w: 11.7, h: 2.0, fontSize: 40, bold: true, color: C.background1, valign: 'bottom' }, text: '' } }] });
pres.defineSlideMaster({ title: 'CONTENT', background: { color: C.background1 },
  margin: [0.5, 0.6, 0.6, 0.6],
  objects: [
    { placeholder: { options: { name: 'title', type: 'title', x: 0.6, y: 0.35, w: 12.1, h: 0.85, fontSize: 32, bold: true, color: C.text1, valign: 'middle', margin: 0 }, text: '' } },
    { text: { text: 'Reflica India · Minor Project 1 · GLA University', options: { x: 0.6, y: 7.0, w: 8, h: 0.3, fontSize: 10, color: C.accent4, margin: 0 } } },
  ],
  slideNumber: { x: 12.2, y: 7.0, w: 0.5, h: 0.3, fontSize: 10, color: C.accent4, align: 'right' } });

let n = 0;
function content(title, section) {
  const s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: section });
  s.addText(title, { placeholder: 'title' });
  return s;
}
const tb = (o) => Object.assign({ isTextBox: true, margin: 0, fontSize: 14, color: C.text2, valign: 'top' }, o);
function card(s, x, y, w, h, fill, name) {
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.08, fill: { color: fill || C.background2 }, line: { type: 'none' }, objectName: name });
}
function badge(s, x, y, label, fill, d) {
  d = d || 0.55;
  s.addShape(pres.shapes.OVAL, { x, y, w: d, h: d, fill: { color: fill }, line: { type: 'none' } });
  s.addText(label, tb({ x, y, w: d, h: d, align: 'center', valign: 'middle', fontSize: 16, bold: true, color: C.background1 }));
}
function bullets(items, size) {
  return items.map((t, i) => {
    const runs = typeof t === 'string' ? { text: t } : t;
    return { text: runs.text, options: { bullet: true, breakLine: i < items.length - 1, bold: runs.bold, paraSpaceAfter: 6, fontSize: size || 14 } };
  });
}

// 1 Title
pres.addSection({ title: 'Opening' });
let s = pres.addSlide({ masterName: 'DARK', sectionTitle: 'Opening' });
s.addText('IndiaEconForecast / Reflica India', tb({ x: 0.8, y: 0.8, w: 11, h: 0.5, fontSize: 18, color: C.accent2, bold: true }));
s.addText('Hybrid AI Forecasting of Indian Economic and Policy Outcomes', { placeholder: 'title' });
s.addText('Minor Project 1 · First (Proposal) Presentation', tb({ x: 0.8, y: 3.9, w: 11, h: 0.4, fontSize: 18, color: C.accent5 }));
s.addText([
  { text: 'Sundram Awasthi', options: { bold: true, breakLine: true, color: C.background1 } },
  { text: 'M.Tech CSE (2026–28) · GLA University, Mathura', options: { breakLine: true } },
  { text: 'Guide: [add guide name]', options: {} },
], tb({ x: 0.8, y: 5.2, w: 8, h: 1.2, fontSize: 16, color: C.accent5 }));
s.addText('Field: Predictive AI for India\'s Economy and Public Policy', tb({ x: 0.8, y: 6.6, w: 11, h: 0.35, fontSize: 12, color: C.accent4, italic: true }));
s.addNotes('Introduce yourself and the title. One line: "My project forecasts India\'s CPI inflation with a numerical model and uses dated official evidence from RBI and the government, through a fixed bounded rule, to decide whether the forecast should change." Mention it has two parts: Part A, an LLM benchmark on Indian yes/no events, and Part B, CPI forecasting with evidence-aware revision.');

// 2 Introduction
pres.addSection({ title: 'Problem' });
s = content('Introduction', 'Problem');
s.addText(bullets([
  'Consumer Price Index (CPI) inflation measures how fast household prices rise. The RBI targets 4% (±2%).',
  'CPI drives RBI repo-rate decisions, loan EMIs, wages, pensions and government price measures.',
  'Between two monthly CPI releases, many official signals arrive: RBI policy statements, government stock limits, export rules.',
  'AI and LLM tools now claim to forecast the economy, but few are tested fairly on Indian data.',
], 15), tb({ x: 0.6, y: 1.45, w: 6.4, h: 4.2 }));
const stats = [['4.82%', 'CPI inflation, Aug 2026\n(first release)', C.accent2], ['0.25%', 'CPI inflation, Oct 2025\n(lowest in our data)', C.accent3], ['2012 → 2024', 'CPI base year changed\nfrom the Jan 2026 data', C.accent1]];
stats.forEach((st, i) => {
  const y = 1.45 + i * 1.75;
  card(s, 7.6, y, 5.1, 1.5, C.background2, 'stat' + i);
  s.addText(st[0], tb({ x: 7.9, y: y + 0.2, w: 2.6, h: 1.1, fontSize: 32, bold: true, color: st[2], valign: 'middle', fontFace: 'Cambria' }));
  s.addText(st[1], tb({ x: 10.5, y: y + 0.2, w: 2.1, h: 1.1, fontSize: 13, valign: 'middle' }));
});
s.addText('Inflation swung from 6.21% (Oct 2024) to 0.25% (Oct 2025) and back to 4.82% (Aug 2026). Forecasting it well matters.', tb({ x: 0.6, y: 5.9, w: 6.4, h: 0.8, fontSize: 14, italic: true, color: C.accent3 }));
s.addNotes('Explain CPI simply: the average price of what households buy. Headline CPI inflation y-o-y is the price rise compared with the same month last year. It matters because the RBI sets the repo rate to keep CPI near 4%. Point at the numbers: inflation moved a lot in two years, so forecasting is hard and useful. Also note the base-year change to 2024 in Feb 2026; it creates a series break we must handle.');

// 3 Problem statement
s = content('Problem Statement', 'Problem');
card(s, 0.6, 1.45, 12.1, 1.75, C.text1, 'rq');
s.addText('Can dated, source-linked claims from official documents, combined with a fixed bounded revision rule, improve India\'s headline CPI forecasts beyond strong numerical models, using only information available at each forecast date?',
  tb({ x: 0.95, y: 1.6, w: 11.4, h: 1.45, fontSize: 18, color: C.background1, valign: 'middle', italic: true, fontFace: 'Cambria' }));
const probs = [
  ['1', 'No fair testing', 'Many studies use revised data or information published after the forecast date (look-ahead leakage). Results look better than reality.'],
  ['2', 'No explanation', 'Forecasts change without saying which evidence caused it. Users cannot audit them.'],
  ['3', 'Overreaction to news', 'Forecasters often overreact to news (Bordalo et al. 2020). Free-form LLM updates have no limit on how far they move.'],
];
probs.forEach((p, i) => {
  const x = 0.6 + i * 4.1;
  card(s, x, 3.55, 3.9, 2.9, C.background2, 'prob' + i);
  badge(s, x + 0.3, 3.8, p[0], C.accent2);
  s.addText(p[1], tb({ x: x + 1.0, y: 3.8, w: 2.7, h: 0.55, fontSize: 17, bold: true, color: C.text1, valign: 'middle' }));
  s.addText(p[2], tb({ x: x + 0.3, y: 4.55, w: 3.35, h: 1.8, fontSize: 14 }));
});
s.addText('Companion question (Part A): how accurate and well-calibrated are LLMs on Indian economic and policy yes/no events?', tb({ x: 0.6, y: 6.55, w: 12.1, h: 0.35, fontSize: 13, italic: true, color: C.accent4 }));
s.addNotes('Read the question slowly. Then explain the three sub-problems. Leakage: if you test with values that were revised later, or documents published after the forecast date, the model looks better than it really is. Explanation: we want every forecast change linked to a dated source. Overreaction: research shows forecasters overreact to news, so we limit the size of any change.');

// 4 Motivation and applications
s = content('Motivation and Applications', 'Problem');
s.addText('Why this research', tb({ x: 0.6, y: 1.45, w: 5.6, h: 0.45, fontSize: 20, bold: true, color: C.text1 }));
s.addText(bullets([
  'Indian evidence on whether news text helps CPI forecasts is mixed: sometimes it helped, sometimes it hurt (Pratap 2021; Das & Das 2024).',
  'In a live test, LLM agents were weakest on inflation (LiveMacroEval 2026). So the LLM should read evidence, not forecast directly.',
  'Official RBI and PIB documents are dated, public and linkable, which makes fair, point-in-time testing possible.',
]), tb({ x: 0.6, y: 2.05, w: 5.6, h: 4.5 }));
s.addText('Who can use it', tb({ x: 6.8, y: 1.45, w: 5.9, h: 0.45, fontSize: 20, bold: true, color: C.text1 }));
const apps = [['Researchers', 'A public point-in-time dataset of Indian CPI and official evidence'], ['Analysts and students', 'Inflation monitoring with forecasts that show their sources'], ['Policy readers', 'See which RBI or government action moved the forecast'], ['AI evaluators', 'A fair benchmark of LLMs on Indian events (Part A)']];
apps.forEach((a, i) => {
  const x = 6.8 + (i % 2) * 3.0, y = 2.05 + Math.floor(i / 2) * 2.3;
  card(s, x, y, 2.85, 2.1, i % 3 === 0 ? 'FBEBDD' : 'E3F2EE', 'app' + i);
  s.addText(a[0], tb({ x: x + 0.2, y: y + 0.2, w: 2.45, h: 0.4, fontSize: 16, bold: true, color: C.text1 }));
  s.addText(a[1], tb({ x: x + 0.2, y: y + 0.7, w: 2.45, h: 1.3, fontSize: 13 }));
});
s.addText('Not a replacement for RBI or official statistics; no trading or policy advice.', tb({ x: 0.6, y: 6.55, w: 12.1, h: 0.35, fontSize: 12, italic: true, color: C.accent4 }));
s.addNotes('Motivation: earlier Indian studies give mixed results, and LLMs on their own are weak at inflation. That is why our design uses the LLM only to extract claims and a numerical model to forecast. Applications: researchers get a clean dataset; analysts get explainable forecasts; policy readers can trace effects; Part A gives an Indian LLM benchmark.');

// 5 Lit review numerical
pres.addSection({ title: 'Literature' });
s = content('Literature Review: Numerical CPI Forecasting', 'Literature');
const hdr = (t) => ({ text: t, options: { bold: true, color: 'FFFFFF', fill: { color: HEX.navy }, fontSize: 14 } });
const row = (arr, shade) => arr.map((t, j) => ({ text: t, options: { fontSize: 13, fill: { color: shade ? 'EEF2F7' : 'FFFFFF' }, bold: j === 0, color: '1A2238' } }));
s.addTable([
  [hdr('Model / study'), hdr('How it works'), hdr('Strength'), hdr('Limitation for us')],
  row(['Naive / random walk', 'Next month = this month', 'Hard to beat in the short term', 'Uses no new information'], false),
  row(['SARIMA', 'Statistical model of trend and seasons', 'Strong on Indian CPI in past studies', 'Numbers only; cannot read news'], true),
  row(['XGBoost / ML', 'Boosted decision trees on lags and features', 'Captures non-linear patterns', 'Overfits on short samples'], false),
  row(['Mohan et al. 2025 (RBI)', 'Combines 216 models for CPI', 'Best accuracy; about 70% below a random walk', 'No text evidence; no revision rule'], true),
], { x: 0.6, y: 1.45, w: 12.1, colW: [2.6, 3.3, 3.1, 3.1], border: { type: 'solid', pt: 0.75, color: HEX.grid }, rowH: 0.6, valign: 'middle' });
card(s, 0.6, 5.25, 12.1, 1.35, 'E3F2EE', 'take5');
s.addText([{ text: 'Takeaway: ', options: { bold: true, color: C.accent3 } }, { text: 'numerical models are strong and must be our baselines. But they only use past numbers, so they react late to policy news such as an RBI rate cut or a wheat stock limit.' }],
  tb({ x: 0.9, y: 5.4, w: 11.5, h: 1.05, fontSize: 15, valign: 'middle' }));
s.addNotes('Explain each model in one line. Naive: assume nothing changes. SARIMA: classic time-series model with seasonality. XGBoost: machine learning with trees. Mohan et al. at RBI combined 216 models and beat a random walk by about 70%. These are strong, so any new method must beat them; that is why they are our baselines. Their gap: they ignore text evidence.');

// 6 Lit review text / LLM
s = content('Literature Review: Text and LLM-Based Forecasting', 'Literature');
s.addTable([
  [hdr('Study'), hdr('What it does'), hdr('Limitation for our problem')],
  row(['Pratap et al. 2021 (RBI)', 'News sentiment index for Indian food inflation', 'Mixed results; aggregate index; no significance tests'], false),
  row(['Das & Das 2024', 'Newspaper headline words + ML for Indian inflation', 'Text hurt 2 of 3 models; look-ahead risk'], true),
  row(['Fan et al. 2025 (LLM-CPI)', 'LLM text signals added to a CPI model, with intervals', 'China and social media; no revision policy'], false),
  row(['LiveMacroEval 2026', 'Live LLM nowcasts of US indicators', 'No fixed update rule; weakest on CPI; US only'], true),
  row(['Forecast-Dojo 2026', 'LLM agents with an evidence ledger', 'Event questions, not CPI; no bounded rule'], false),
  row(['Modugno 2013 / Thorsrud 2016', 'News-driven nowcast updating', 'Numeric or topic level; not claim level'], true),
], { x: 0.6, y: 1.45, w: 12.1, colW: [3.0, 4.6, 4.5], border: { type: 'solid', pt: 0.75, color: HEX.grid }, rowH: 0.58, valign: 'middle' });
card(s, 0.6, 5.75, 12.1, 0.95, 'FBEBDD', 'take6');
s.addText([{ text: 'Takeaway: ', options: { bold: true, color: C.accent2 } }, { text: 'text can help, but results are mixed, and no reviewed work limits how much news may move the forecast.' }],
  tb({ x: 0.9, y: 5.85, w: 11.5, h: 0.75, fontSize: 15, valign: 'middle' }));
s.addNotes('About 59 papers checked and 22 read in full. Key point: text and LLM methods exist, but either the Indian results are mixed (Pratap, Das & Das), the work is outside India (Fan, LiveMacroEval), or updating has no fixed rule. LiveMacroEval found LLM agents were weakest on inflation. This sets up our gap.');

// 7 Comparative analysis
s = content('Comparative Analysis', 'Literature');
const Y = '✓', N = '✗', P = '~';
const mk = (t, j, shade, ours) => ({ text: t, options: { fontSize: 14, align: j === 0 ? 'left' : 'center', bold: j === 0 || ours, fill: { color: ours ? 'E3F2EE' : (shade ? 'EEF2F7' : 'FFFFFF') }, color: t === Y ? HEX.green : (t === N ? 'B33A3A' : (t === P ? HEX.saffron : '1A2238')) } });
const crow = (a, i, ours) => a.map((t, j) => mk(t, j, i % 2, ours));
s.addTable([
  [hdr('Work'), hdr('Indian CPI'), hdr('Uses text'), hdr('Claim-level, source-linked'), hdr('Fixed bounded rule'), hdr('Compares update policies')].map((h, j) => (j ? Object.assign(h, { options: Object.assign(h.options, { align: 'center' }) }) : h)),
  crow(['Mohan et al. 2025', Y, N, N, N, N], 0),
  crow(['Pratap et al. 2021', P, Y, N, N, N], 1),
  crow(['Das & Das 2024', Y, Y, N, N, N], 2),
  crow(['Fan et al. 2025', N, Y, N, N, N], 3),
  crow(['LiveMacroEval 2026', N, Y, N, N, N], 4),
  crow(['Forecast-Dojo 2026', N, Y, P, N, N], 5),
  crow(['Modugno / Thorsrud', N, P, N, P, N], 6),
  crow(['Reflica India (proposed)', Y, Y, Y, Y, Y], 7, true),
], { x: 0.6, y: 1.45, w: 12.1, colW: [3.1, 1.6, 1.6, 2.1, 1.8, 1.9], border: { type: 'solid', pt: 0.75, color: HEX.grid }, rowH: 0.52, valign: 'middle' });
s.addText('✓ yes   ~ partly (food inflation only / evidence ledger / news-driven updates)   ✗ no   ·   Based on our reading of each paper. "Proposed" = planned, not yet tested.',
  tb({ x: 0.6, y: 6.35, w: 12.1, h: 0.45, fontSize: 12, color: C.accent4 }));
s.addNotes('Walk through the columns. Most works have one or two pieces, but none combines all five for Indian CPI. Be careful with wording: say "among the works I reviewed", never "first" or "novel". The last row is what we plan to test, not a result.');

// 8 Research gap
s = content('Research Gap', 'Literature');
card(s, 0.6, 1.45, 12.1, 1.9, C.text1, 'gap');
s.addText([{ text: 'Main gap (G2, medium confidence)\n', options: { bold: true, color: C.accent2, fontSize: 15 } },
  { text: 'Among the works reviewed, none tests claim-level, source-linked evidence with a fixed bounded revision rule on Indian headline CPI, compared with never-update and always-update policies, under strict point-in-time testing.', options: { color: C.background1, fontSize: 17 } }],
  tb({ x: 0.95, y: 1.6, w: 11.4, h: 1.6, valign: 'middle', fontFace: 'Cambria' }));
const gaps = [['G1', 'No India-specific prospective LLM forecasting benchmark found', 'Low–medium', C.accent4], ['G2', 'Claim-level evidence + bounded revision rule for Indian CPI', 'Medium', C.accent2], ['G3', 'Whether text helps Indian CPI is still an open question', 'Medium–high', C.accent3]];
gaps.forEach((g, i) => {
  const x = 0.6 + i * 4.1;
  card(s, x, 3.7, 3.9, 2.55, C.background2, 'g' + i);
  badge(s, x + 0.3, 3.95, g[0], g[3], 0.7);
  s.addText('Confidence: ' + g[2], tb({ x: x + 1.2, y: 4.05, w: 2.5, h: 0.5, fontSize: 13, bold: true, color: g[3], valign: 'middle' }));
  s.addText(g[1], tb({ x: x + 0.3, y: 4.85, w: 3.3, h: 1.3, fontSize: 15, color: C.text1 }));
});
s.addText('We claim no novelty. The gap is stated only for the works reviewed (about 59 papers).', tb({ x: 0.6, y: 6.5, w: 12.1, h: 0.35, fontSize: 12, italic: true, color: C.accent4 }));
s.addNotes('G2 is our main gap and the focus of Part B. G1 motivates Part A. G3 means our result is useful either way: if text does not help, that is also a finding. Confidence levels are honest estimates from the review.');

// 9 Objectives and RQs
pres.addSection({ title: 'Proposed work' });
s = content('Objectives and Research Questions', 'Proposed work');
s.addText('Objectives', tb({ x: 0.6, y: 1.45, w: 6.2, h: 0.45, fontSize: 20, bold: true, color: C.text1 }));
const objs = ['Build a point-in-time dataset of CPI first releases and dated official documents', 'Build numerical baselines: naive, SARIMA, XGBoost', 'Extract dated, source-linked claims from RBI and PIB documents', 'Design a bounded revision rule and compare it with other update policies', 'Evaluate fairly with a walk-forward test; benchmark LLMs on Indian yes/no events (Part A)'];
objs.forEach((o, i) => {
  const y = 2.05 + i * 0.9;
  badge(s, 0.6, y, String(i + 1), C.accent1, 0.5);
  s.addText(o, tb({ x: 1.3, y: y - 0.05, w: 5.4, h: 0.8, fontSize: 14, valign: 'middle' }));
});
s.addText('Research questions (Part B)', tb({ x: 7.2, y: 1.45, w: 5.5, h: 0.45, fontSize: 20, bold: true, color: C.text1 }));
const rqs = [['RQ1', 'Does evidence-aware bounded revision reduce error (MAE, RMSE) compared with never-update and always-update?'], ['RQ2', 'Does it reduce harmful revisions while keeping interval coverage near its target?'], ['RQ3', 'Which evidence properties (novelty, reliability, relevance, strength) matter most?']];
rqs.forEach((r, i) => {
  const y = 2.05 + i * 1.5;
  card(s, 7.2, y, 5.5, 1.3, i === 0 ? 'FBEBDD' : C.background2, 'rq' + i);
  s.addText(r[0], tb({ x: 7.4, y: y + 0.15, w: 0.9, h: 1.0, fontSize: 18, bold: true, color: C.accent2, valign: 'middle' }));
  s.addText(r[1], tb({ x: 8.3, y: y + 0.1, w: 4.25, h: 1.1, fontSize: 14, valign: 'middle' }));
});
s.addText('Scope: All-India headline CPI-C, year-on-year · official sources (MoSPI, RBI, PIB, MoF) · 2013–2026', tb({ x: 7.2, y: 6.6, w: 5.5, h: 0.3, fontSize: 11, italic: true, color: C.accent4 }));
s.addNotes('Five objectives map to the pipeline: data, models, claims, revision rule, evaluation. RQ1 is about accuracy, RQ2 about avoiding bad changes, RQ3 about which evidence matters. Out of scope for Minor 1: question-answering agents, abstention (Minor 2), trading advice.');

// 10 Architecture
s = content('Proposed System Architecture', 'Proposed work');
function box(x, y, w, h, title, sub, fill, txt, name) {
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.08, fill: { color: fill }, line: { type: 'none' }, objectName: name });
  s.addText([{ text: title, options: { bold: true, fontSize: 14, breakLine: true } }, { text: sub, options: { fontSize: 11 } }], tb({ x: x + 0.12, y, w: w - 0.24, h, align: 'center', valign: 'middle', color: txt }));
}
function arrow(x1, y1, x2, y2) { s.addShape(pres.shapes.LINE, { x: Math.min(x1, x2), y: Math.min(y1, y2), w: Math.abs(x2 - x1) || 0.001, h: Math.abs(y2 - y1) || 0.001, flipV: y2 < y1 && x2 > x1, line: { color: HEX.slate, width: 1.75, endArrowType: 'triangle' } }); }
const L1 = 'FFFFFF';
// Layer 1 sources
box(0.6, 1.45, 2.3, 1.05, 'Official sources', 'MoSPI CPI · RBI · PIB · MoF', C.accent4, L1, 'src');
// Layer 2 store
box(3.4, 1.45, 2.6, 1.05, 'Timestamped store', 'every item keeps its publication time', C.accent1, L1, 'store');
arrow(2.9, 1.97, 3.4, 1.97);
// branches
box(6.6, 1.45, 2.8, 1.05, 'Numerical engine', 'naive · SARIMA · XGBoost → base forecast + interval', C.accent3, L1, 'num');
box(6.6, 3.1, 2.8, 1.05, 'Claim extraction (LLM)', 'quote · topic · direction · date · source', C.accent2, L1, 'claims');
arrow(6.0, 1.97, 6.6, 1.97);
arrow(6.0, 2.2, 6.6, 3.5);
// revision rule
box(10.0, 2.2, 2.7, 1.3, 'Bounded revision rule', 'keep, or adjust within ±limit, with a logged reason', C.text1, L1, 'rule');
arrow(9.4, 1.97, 10.0, 2.6);
arrow(9.4, 3.6, 10.0, 3.1);
// bottom row
box(10.0, 4.4, 2.7, 1.0, 'Forecast log', 'forecast · change · evidence IDs', C.accent4, L1, 'log');
arrow(11.35, 3.5, 11.35, 4.4);
box(6.6, 4.4, 2.8, 1.0, 'Walk-forward evaluation', 'MAE · RMSE · DM test · coverage', C.accent3, L1, 'eval');
arrow(10.0, 4.9, 9.4, 4.9);
box(3.4, 4.4, 2.6, 1.0, 'Research dashboard', 'Flutter + Firebase', C.accent1, L1, 'dash');
arrow(6.6, 4.9, 6.0, 4.9);
// Part A lane
card(s, 0.6, 5.8, 12.1, 0.85, 'FBEBDD', 'partA');
s.addText([{ text: 'Part A (separate evaluation): ', options: { bold: true, color: C.accent2 } }, { text: 'Indian yes/no questions → LLM answers a probability before the deadline → resolved from official sources → Brier score and calibration.' }], tb({ x: 0.9, y: 5.8, w: 11.5, h: 0.85, fontSize: 14, valign: 'middle' }));
s.addText([{ text: 'Key rule: ', options: { bold: true, color: C.text1 } }, { text: 'the LLM never forecasts CPI. It only turns documents into structured claims; the numbers come from the numerical engine.' }], tb({ x: 0.6, y: 2.75, w: 5.4, h: 1.3, fontSize: 13 }));
s.addNotes('Walk left to right. 1) Official sources. 2) Everything is stored with its publication time, so the system can rebuild exactly what was known on any date. 3a) The numerical engine makes the base forecast. 3b) The LLM extracts claims: the exact quote, topic (food, fuel, policy), direction (up or down pressure), date and link. 4) The bounded revision rule decides to keep or adjust the forecast, but never by more than a fixed limit, and logs why. 5) The log feeds walk-forward evaluation and the dashboard. Part A runs separately and is scored with the Brier score.');

// 11 Methodology
s = content('Methodology', 'Proposed work');
const steps = [['Collect', 'Official data with exact publication time'], ['Build CPI series', 'Revised values to train; first releases to test'], ['Baselines', 'Naive, SARIMA, XGBoost; text indices'], ['Extract claims', 'LLM + quote check against the source'], ['Revise', 'Bounded rule; limits tuned on validation only'], ['Walk-forward test', 'Only data available before each forecast'], ['Compare', 'Never · always · small-step · text-always · ours']];
const sw = 1.62, gap = 0.12;
steps.forEach((st, i) => {
  const x = 0.6 + i * (sw + gap);
  card(s, x, 1.5, sw, 2.3, i < 1 ? 'E3F2EE' : C.background2, 'step' + i);
  badge(s, x + (sw - 0.55) / 2, 1.65, String(i + 1), i < 1 ? C.accent3 : C.accent1);
  s.addText(st[0], tb({ x: x + 0.1, y: 2.3, w: sw - 0.2, h: 0.5, fontSize: 14, bold: true, color: C.text1, align: 'center' }));
  s.addText(st[1], tb({ x: x + 0.1, y: 2.8, w: sw - 0.2, h: 0.95, fontSize: 12, align: 'center' }));
});
card(s, 0.6, 4.15, 6.9, 2.5, C.text1, 'rulebox');
s.addText([
  { text: 'Bounded revision rule (idea)', options: { bold: true, color: C.accent2, fontSize: 16, breakLine: true } },
  { text: 'revised = base + clip( k × evidence score, −B, +B )', options: { fontFace: 'Courier New', color: C.background1, fontSize: 13, breakLine: true } },
  { text: 'evidence score = combined direction and strength of new claims since the last forecast. k (step size) and B (limit) are fixed on validation data before testing; exact form frozen in the protocol.', options: { color: C.accent5, fontSize: 13 } },
], tb({ x: 0.9, y: 4.3, w: 6.3, h: 2.2, paraSpaceAfter: 8 }));
card(s, 7.8, 4.15, 4.9, 2.5, C.background2, 'metrics');
s.addText([
  { text: 'How we measure', options: { bold: true, color: C.text1, fontSize: 16, breakLine: true } },
  { text: 'MAE, RMSE: size of the error', options: { bullet: true, breakLine: true } },
  { text: 'Diebold–Mariano (HLN) test: is the gain real?', options: { bullet: true, breakLine: true } },
  { text: 'Interval coverage; helpful vs harmful revisions', options: { bullet: true, breakLine: true } },
  { text: 'Part A: Brier score, calibration', options: { bullet: true } },
], tb({ x: 8.1, y: 4.3, w: 4.4, h: 2.2, fontSize: 14, paraSpaceAfter: 4 }));
s.addNotes('Step 1 is done. Explain point-in-time: training can use revised history, but testing uses first-release values exactly as published. Walk-forward means train on the past, forecast the next month, move forward one month, repeat. The rule: start from the numerical forecast, add a small step in the direction of the evidence, but clip it to a maximum B. Example: if B is 0.2 points and strong news says food prices will rise, the forecast can move up at most 0.2. We compare against never updating and always following the news. DM test checks the improvement is not luck. CPI is regression, so we do not use accuracy or F1.');

// 12 Dataset
s = content('Dataset Collected', 'Proposed work');
const months = ['2024-01','2024-02','2024-03','2024-04','2024-05','2024-06','2024-07','2024-08','2024-09','2024-10','2024-11','2024-12','2025-01','2025-02','2025-03','2025-04','2025-05','2025-06','2025-07','2025-08','2025-09','2025-10','2025-11','2025-12','2026-01','2026-02','2026-03','2026-04','2026-05','2026-06','2026-07','2026-08'];
const vals = [5.10,5.09,4.85,4.83,4.75,5.08,3.54,3.65,5.49,6.21,5.48,5.22,4.31,3.61,3.34,3.16,2.82,2.10,1.55,2.07,1.54,0.25,0.71,1.33,2.75,3.21,3.40,3.48,3.93,4.38,4.45,4.82];
const mn = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
const labels = months.map(m => mn[+m.slice(5) - 1] + ' ' + m.slice(2, 4));
s.addChart(pres.charts.LINE, [{ name: 'Headline CPI inflation (first release, %)', labels, values: vals }], {
  x: 0.6, y: 1.4, w: 7.4, h: 4.3, chartColors: [HEX.saffron], lineSize: 2.5, lineDataSymbol: 'circle', lineDataSymbolSize: 5,
  showTitle: true, title: 'India headline CPI inflation, first release (%)', titleFontSize: 14, titleColor: HEX.navy, titleFontFace: '+mn-lt',
  showLegend: false, catAxisLabelColor: HEX.slate, valAxisLabelColor: HEX.slate, catAxisLabelFontSize: 10, valAxisLabelFontSize: 11,
  catAxisLabelFontFace: '+mn-lt', valAxisLabelFontFace: '+mn-lt', catAxisLabelFrequency: 3, valAxisMinVal: 0, valAxisMaxVal: 7,
  valGridLine: { color: HEX.grid, size: 0.5 }, catGridLine: { style: 'none' }, valAxisLabelFormatCode: '0.0',
});
s.addText('Source: MoSPI CPI press releases, Jan 2024 – Aug 2026 (32 months). Base 2012=100 until Dec 2025; 2024=100 from Jan 2026.', tb({ x: 0.6, y: 5.8, w: 7.4, h: 0.5, fontSize: 11, color: C.accent4 }));
const ds = [['613', 'rows of revised CPI\n2013 – Sep 2026'], ['33', 'first releases with exact\ndate, time and link'], ['81', 'registered official\ndocuments'], ['22', 'RBI MPC resolutions\nApr 2023 – Oct 2026']];
ds.forEach((d, i) => {
  const x = 8.4 + (i % 2) * 2.2, y = 1.4 + Math.floor(i / 2) * 1.75;
  card(s, x, y, 2.05, 1.55, i % 3 === 0 ? 'FBEBDD' : 'E3F2EE', 'ds' + i);
  s.addText(d[0], tb({ x: x + 0.15, y: y + 0.1, w: 1.8, h: 0.75, fontSize: 32, bold: true, color: i % 3 === 0 ? C.accent2 : C.accent3, fontFace: 'Cambria', valign: 'middle' }));
  s.addText(d[1], tb({ x: x + 0.15, y: y + 0.85, w: 1.85, h: 0.65, fontSize: 11 }));
});
s.addText([
  { text: 'Documents: ', options: { bold: true, color: C.text1 } },
  { text: '8 Monetary Policy Reports, 2 MPC minutes, 2 transcripts, 14 PIB price releases (stock limits, export rules), Economic Survey 2025-26.', options: { breakLine: true } },
  { text: 'Every row: ', options: { bold: true, color: C.text1 } },
  { text: 'ID, source, publication time, link, confidence.' },
], tb({ x: 8.4, y: 4.95, w: 4.3, h: 1.6, fontSize: 12 }));
s.addNotes('Explain the chart: these are first-release values, exactly as published, which we use for testing. Inflation fell to 0.25% in Oct 2025 and rose to 4.82% by Aug 2026. Numbers: 613 rows of revised CPI for training, 33 months of first releases, 81 documents including all 22 RBI policy resolutions since April 2023. Data quality: COVID-imputed months (Apr–May 2020) are flagged, the base-year change uses the official linking factor 0.5267, and a release published late (a transcript published 15 Apr 2024 for an 8 Feb meeting) is only used from its publication date. Claims are not extracted yet; that is the next step.');

// 13 Tools and timeline
pres.addSection({ title: 'Plan' });
s = content('Tools and Timeline', 'Plan');
const tools = [['Research engine', 'Python: pandas, statsmodels, scikit-learn, XGBoost'], ['Claim extraction', 'LLM API, with quote check against the source'], ['Data', 'CSV / JSON with provenance; MoSPI e-Sankhyiki API'], ['App and dashboard', 'Flutter (web, Android)'], ['Backend', 'Firebase Auth + Firestore (free Spark plan)'], ['Version control', 'Git / GitHub']];
tools.forEach((t, i) => {
  const y = 1.45 + i * 0.85;
  card(s, 0.6, y, 4.9, 0.72, C.background2, 'tool' + i);
  s.addText([{ text: t[0] + '  ', options: { bold: true, color: C.text1 } }, { text: t[1] }], tb({ x: 0.8, y, w: 4.6, h: 0.72, fontSize: 13, valign: 'middle' }));
});
const tl = [['Oct 2026', 'Literature, gap, proposal, data collection', true], ['Nov 2026', 'Claim extraction; freeze protocol; guide approval', false], ['Dec 26 – Jan 27', 'Baselines; data pipeline; Part A pilot', false], ['Feb – Mar 2027', 'Text evidence + bounded revision experiments', false], ['Apr 2027', 'Evaluation and robustness checks', false], ['May 2027', 'Dashboard, report, final presentation', false]];
s.addShape(pres.shapes.LINE, { x: 6.35, y: 1.7, w: 0.001, h: 4.85, line: { color: HEX.grid, width: 2 } });
tl.forEach((t, i) => {
  const y = 1.45 + i * 0.85;
  s.addShape(pres.shapes.OVAL, { x: 6.2, y: y + 0.2, w: 0.3, h: 0.3, fill: { color: t[2] ? C.accent3 : C.background1 }, line: { color: t[2] ? HEX.green : HEX.slate, width: 1.5 } });
  s.addText(t[0], tb({ x: 6.8, y: y + 0.05, w: 1.9, h: 0.6, fontSize: 14, bold: true, color: t[2] ? C.accent3 : C.text1, valign: 'middle' }));
  s.addText(t[1] + (t[2] ? '  ✓ done' : ''), tb({ x: 8.7, y: y + 0.05, w: 4.0, h: 0.6, fontSize: 13, valign: 'middle' }));
});
s.addNotes('Tools: Python for all research code, an LLM only for claim extraction, Flutter and Firebase for the dashboard, all on free plans. Timeline: steps 1 to 6 are done (about 50% of Minor 1). Next month: claim extraction and freezing the protocol so the test cannot be tuned after seeing results.');

// 14 Outcomes and references
s = content('Expected Outcomes and References', 'Plan');
s.addText('Expected outcomes', tb({ x: 0.6, y: 1.45, w: 5.6, h: 0.45, fontSize: 20, bold: true, color: C.text1 }));
s.addText(bullets([
  'A public point-in-time dataset: Indian CPI first releases + dated official evidence',
  'A fair comparison of revision policies (never, always, small-step, text-always, bounded)',
  'Explainable forecasts: every change linked to its source claim',
  'An Indian LLM forecasting benchmark (Part A)',
  { text: 'An honest result, including if the method does not help', bold: true },
]), tb({ x: 0.6, y: 2.0, w: 5.6, h: 4.5 }));
s.addText('Key references', tb({ x: 6.8, y: 1.45, w: 5.9, h: 0.45, fontSize: 20, bold: true, color: C.text1 }));
const refs = ['Mohan et al. (2025), RBI Bulletin', 'Pratap, Ranjan, Kishore & Bhoi (2021), RBI Occasional Papers 42(2)', 'Das & Das (2024), IJEF 16(6)', 'Fan, Lv, Sun & Wang (2025), arXiv 2506.09516', 'Zhao et al. (2026), LiveMacroEval, arXiv 2608.30110', 'Ye et al. (2026), Forecast-Dojo, arXiv 2609.28876', 'Modugno (2013), IJF 29(4)', 'Bordalo, Gennaioli, Ma & Shleifer (2020), AER 110(9)'];
s.addText(refs.map((r, i) => ({ text: '[' + (i + 1) + ']  ' + r, options: { breakLine: i < refs.length - 1, paraSpaceAfter: 5 } })), tb({ x: 6.8, y: 2.0, w: 5.9, h: 4.5, fontSize: 13 }));
s.addNotes('Outcomes: dataset, fair comparison, explainable forecasts, Part A benchmark. Stress the honest result: if text evidence does not help beyond strong numbers, that is still a valid research finding. References: the full list of 46 is in the review paper.');

// 15 Thank you
pres.addSection({ title: 'Closing' });
s = pres.addSlide({ masterName: 'DARK', sectionTitle: 'Closing' });
s.addText('Thank You', { placeholder: 'title' });
s.addText('Questions and suggestions are welcome', tb({ x: 0.8, y: 3.9, w: 11, h: 0.5, fontSize: 20, color: C.accent2 }));
s.addText('Sundram Awasthi · M.Tech CSE · GLA University', tb({ x: 0.8, y: 5.6, w: 11, h: 0.4, fontSize: 14, color: C.accent5 }));
s.addNotes('Be ready for: Why not just use an LLM? How do you avoid leakage? What if the method does not help? See docs/PRESENTER_GUIDE.md section 6 for all 12 answers.');

(async () => { await pres.writeFile({ fileName: OUT }); await applyTheme(OUT, THEME); console.log('ok'); })();
