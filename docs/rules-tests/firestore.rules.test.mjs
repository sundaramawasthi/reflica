// Emulator test matrix for the proposed firestore.rules (scratch, not in repo).
import { readFileSync } from 'node:fs';
import { initializeTestEnvironment, assertSucceeds, assertFails } from '@firebase/rules-unit-testing';
import { doc, setDoc, getDoc, getDocs, updateDoc, deleteDoc, collection, query, where,
         orderBy, limit, writeBatch, serverTimestamp, Timestamp } from 'firebase/firestore';

const env = await initializeTestEnvironment({
  projectId: 'demo-reflica-rules',
  firestore: { rules: readFileSync('firestore.rules', 'utf8'), host: '127.0.0.1', port: 8080 },
});

const alice = env.authenticatedContext('alice').firestore();
const bob = env.authenticatedContext('bob').firestore();
const anon = env.unauthenticatedContext().firestore();

const now = new Date().toISOString();
const plan = (id, owner, extra = {}) => ({ id, ownerId: owner, title: 'T', audience: 'individual',
  inputMode: 'text', rawText: null, artefacts: [], nodes: [], edges: [], status: 'draft',
  createdAt: now, updatedAt: now, ...extra });
const notif = (id, owner) => ({ id, ownerId: owner, kind: 'planCreated', title: 't', body: 'b',
  planId: 'p1', read: false, createdAt: now });
const event = (id, actor, created) => ({ id, type: 'decision', actor_uid: actor,
  graph_before_sha256: null, graph_after_sha256: null, record: {}, created_at: created });

const results = [];
async function check(name, expect, fn) {
  try {
    await (expect === 'allow' ? assertSucceeds(fn()) : assertFails(fn()));
    results.push(['PASS', expect, name]);
  } catch (e) {
    results.push(['FAIL', expect, name + ' :: ' + e.message.split('\n')[0]]);
  }
}

// Old plan paths (plan app removed 2026-10-14): now closed to everyone.
await check('P1 owner creates a plan (old path)', 'deny', () => setDoc(doc(alice, 'users/alice/plans/p1'), plan('p1', 'alice')));
await check('P2 owner reads a plan (old path)', 'deny', () => getDoc(doc(alice, 'users/alice/plans/p1')));
await check('P3 owner lists plans (old path)', 'deny', () => getDocs(query(collection(alice, 'users/alice/plans'), orderBy('updatedAt', 'desc'))));
await check('P4 owner deletes a plan (old path)', 'deny', () => deleteDoc(doc(alice, 'users/alice/plans/p1')));
await check('P5 signed-out write to users/demo/plans', 'deny', () => setDoc(doc(anon, 'users/demo/plans/d1'), plan('d1', 'demo')));

// Notifications
await check('N1 owner creates notification', 'allow', () => setDoc(doc(alice, 'users/alice/notifications/n1'), notif('n1', 'alice')));
try { await setDoc(doc(alice, 'users/alice/notifications/n2'), notif('n2', 'alice')); } catch (e) { results.push(['FAIL', 'allow', 'setup: owner creates notification n2 :: ' + e.code]); }
await check('N2 owner watches latest 50 (orderBy createdAt, limit)', 'allow', () => getDocs(query(collection(alice, 'users/alice/notifications'), orderBy('createdAt', 'desc'), limit(50))));
await check('N3 markRead: update {read: true}', 'allow', () => updateDoc(doc(alice, 'users/alice/notifications/n1'), { read: true }));
await check('N4 markAllRead: query read==false + batch update', 'allow', async () => {
  const snap = await getDocs(query(collection(alice, 'users/alice/notifications'), where('read', '==', false)));
  const b = writeBatch(alice); snap.docs.forEach(d => b.update(d.ref, { read: true })); return b.commit();
});
await check('N5 update changes title', 'deny', () => updateDoc(doc(alice, 'users/alice/notifications/n1'), { title: 'x' }));
await check('N6 read set to non-bool', 'deny', () => updateDoc(doc(alice, 'users/alice/notifications/n1'), { read: 'yes' }));
await check('N7 owner deletes notification', 'allow', () => deleteDoc(doc(alice, 'users/alice/notifications/n2')));
await check('N8 other user reads notifications', 'deny', () => getDocs(collection(bob, 'users/alice/notifications')));
await check('N9 signed-out write to users/demo/notifications', 'deny', () => setDoc(doc(anon, 'users/demo/notifications/x'), notif('x', 'demo')));
await check('N10 create with ownerId of another user', 'deny', () => setDoc(doc(alice, 'users/alice/notifications/n3'), notif('n3', 'bob')));

// Old stage-1 event paths: closed.
await check('E1 owner appends an event (old path)', 'deny', () => setDoc(doc(alice, 'users/alice/plans/p1/events/e1'), event('e1', 'alice', serverTimestamp())));
await check('E2 owner reads events (old path)', 'deny', () => getDocs(collection(alice, 'users/alice/plans/p1/events')));

// Everything else
await check('O1 owner reads users/{uid} document itself', 'deny', () => getDoc(doc(alice, 'users/alice')));
await check('O2 owner writes users/{uid} document itself', 'deny', () => setDoc(doc(alice, 'users/alice'), { a: 1 }));
await check('O3 signed-out reads forecasts collection', 'deny', () => getDocs(collection(anon, 'forecasts')));
await check('O4 signed-in writes questions collection', 'deny', () => setDoc(doc(alice, 'questions/q1'), { a: 1 }));
await check('O5 unknown path under the user', 'deny', () => setDoc(doc(alice, 'users/alice/other/x'), { a: 1 }));

await env.cleanup();
for (const r of results) console.log(r.join('  '));
const fails = results.filter(r => r[0] === 'FAIL').length;
console.log(`\n${results.length - fails}/${results.length} passed`);
process.exit(fails ? 1 : 0);
