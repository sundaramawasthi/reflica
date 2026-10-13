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

// Plans
await check('P1 owner creates own plan', 'allow', () => setDoc(doc(alice, 'users/alice/plans/p1'), plan('p1', 'alice')));
await check('P2 owner reads own plan', 'allow', () => getDoc(doc(alice, 'users/alice/plans/p1')));
await check('P3 owner lists own plans (orderBy updatedAt)', 'allow', () => getDocs(query(collection(alice, 'users/alice/plans'), orderBy('updatedAt', 'desc'))));
await check('P4 owner overwrites own plan (set)', 'allow', () => setDoc(doc(alice, 'users/alice/plans/p1'), plan('p1', 'alice', { title: 'T2' })));
await check('P5 stage-1 plan with graph field', 'allow', () => setDoc(doc(alice, 'users/alice/plans/p2'), plan('p2', 'alice', { graph: { version: 'graph@1', nodes: [], edges: [] } })));
await check('P6 owner changes ownerId to bob', 'deny', () => setDoc(doc(alice, 'users/alice/plans/p1'), plan('p1', 'bob')));
await check('P7 id field does not match document id', 'deny', () => setDoc(doc(alice, 'users/alice/plans/p3'), plan('other', 'alice')));
await check('P8 missing title', 'deny', () => setDoc(doc(alice, 'users/alice/plans/p4'), { id: 'p4', ownerId: 'alice' }));
await check('P9 other user reads plan', 'deny', () => getDoc(doc(bob, 'users/alice/plans/p1')));
await check('P10 other user lists plans', 'deny', () => getDocs(collection(bob, 'users/alice/plans')));
await check('P11 other user writes plan', 'deny', () => setDoc(doc(bob, 'users/alice/plans/p9'), plan('p9', 'alice')));
await check('P12 signed-out read', 'deny', () => getDoc(doc(anon, 'users/alice/plans/p1')));
await check('P13 signed-out write to users/demo', 'deny', () => setDoc(doc(anon, 'users/demo/plans/d1'), plan('d1', 'demo')));
await check('P14 signed-in user writes to users/demo', 'deny', () => setDoc(doc(alice, 'users/demo/plans/d1'), plan('d1', 'demo')));

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

// Events (stage-1)
await check('E1 owner appends event with serverTimestamp', 'allow', () => setDoc(doc(alice, 'users/alice/plans/p1/events/e1'), event('e1', 'alice', serverTimestamp())));
await check('E2 event with client-chosen time', 'deny', () => setDoc(doc(alice, 'users/alice/plans/p1/events/e2'), event('e2', 'alice', Timestamp.fromDate(new Date('2020-01-01')))));
await check('E3 actor_uid of another user', 'deny', () => setDoc(doc(alice, 'users/alice/plans/p1/events/e3'), event('e3', 'bob', serverTimestamp())));
await check('E4 owner edits an event', 'deny', () => updateDoc(doc(alice, 'users/alice/plans/p1/events/e1'), { type: 'changed' }));
await check('E5 owner reads events', 'allow', () => getDocs(collection(alice, 'users/alice/plans/p1/events')));
await check('E6 other user reads events', 'deny', () => getDocs(collection(bob, 'users/alice/plans/p1/events')));
await check('E7 owner deletes an event (open decision)', 'allow', () => deleteDoc(doc(alice, 'users/alice/plans/p1/events/e1')));

// Everything else
await check('O1 owner reads users/{uid} document itself', 'deny', () => getDoc(doc(alice, 'users/alice')));
await check('O2 owner writes users/{uid} document itself', 'deny', () => setDoc(doc(alice, 'users/alice'), { a: 1 }));
await check('O3 signed-out reads forecasts collection', 'deny', () => getDocs(collection(anon, 'forecasts')));
await check('O4 signed-in writes questions collection', 'deny', () => setDoc(doc(alice, 'questions/q1'), { a: 1 }));
await check('O5 unknown path under the user', 'deny', () => setDoc(doc(alice, 'users/alice/other/x'), { a: 1 }));
await check('P15 owner deletes own plan', 'allow', () => deleteDoc(doc(alice, 'users/alice/plans/p2')));

await env.cleanup();
for (const r of results) console.log(r.join('  '));
const fails = results.filter(r => r[0] === 'FAIL').length;
console.log(`\n${results.length - fails}/${results.length} passed`);
process.exit(fails ? 1 : 0);
