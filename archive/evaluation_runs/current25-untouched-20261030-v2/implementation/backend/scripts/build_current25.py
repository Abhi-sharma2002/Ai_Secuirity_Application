"""Consolidate the frozen v3 material into 25 documents without dropping a case."""
from copy import deepcopy
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'backend'))
from app.ingestion.parsers import _extract

SOURCE = ROOT / 'backend/benchmark_v3'
TARGET = ROOT / 'backend/benchmark_current25'


def plan():
    old = json.loads((SOURCE / 'manifest.json').read_text())
    fixtures = {f['fixture_id']: f for f in old['fixtures']}
    original_cases = {c['case_id']: c for c in old['cases']}
    # Keep absence and genuine conflict scenarios isolated. Never merge an
    # attack-bearing source into a benign source, or development into final.
    isolated = {'final-02', 'final-03', 'final-23'}
    groups = [[fid] for fid in sorted(isolated)]
    pools = {}
    for fid in fixtures:
        if fid in isolated:
            continue
        c = original_cases[fid]
        key = (c['split'], bool(c['adversarial'] and c['channel'] == 'indirect'))
        pools.setdefault(key, []).append(fid)
    # Reduce 45 to 25 through 20 pairings. Prefer identical supported tasks;
    # other paired sections concern different business subjects.
    pairings_left = len(fixtures) - 25
    for pool in pools.values():
        while pool:
            a = pool.pop(0)
            group = [a]
            if pool and pairings_left:
                task = original_cases[a]['expected_task']
                b = next((fid for fid in pool if original_cases[fid]['expected_task'] == task), pool[0])
                pool.remove(b)
                group.append(b)
                pairings_left -= 1
            groups.append(group)
    assert len(groups) == 25 and pairings_left == 0
    mapping, documents, new_fixtures = {}, {}, []
    for i, members in enumerate(groups, 1):
        fid = f'policy-pack-{i:02}'
        pieces, provenance = [], []
        for member in members:
            source = fixtures[member]
            raw = (SOURCE / source['path']).read_bytes()
            assert hashlib.sha256(raw).hexdigest() == source['sha256']
            parsed = _extract(raw, Path(source['path']).suffix)
            assert parsed['status'] == 'parsed'
            text = '\n\n'.join(b['text'] for b in parsed['blocks'])
            pieces.append(f'## Original source section: {member}\n\n{text}')
            provenance.append(dict(fixture_id=member, path=source['path'], sha256=source['sha256'],
                                   extracted_text_sha256=hashlib.sha256(text.encode()).hexdigest()))
            mapping[member] = fid
        body = ('# Fictional employee policy collection\n\n' + '\n\n'.join(pieces) + '\n').encode()
        path = f'documents/{fid}.md'
        documents[path] = body
        new_fixtures.append(dict(fixture_id=fid, path=path, sha256=hashlib.sha256(body).hexdigest(),
                                 original_sources=provenance))
    cases = deepcopy(old['cases'])
    for c in cases:
        c['original_fixtures'] = c['fixtures'][:]
        c['fixtures'] = list(dict.fromkeys(mapping[fid] for fid in c['fixtures']))
        c['expected_evidence'] = list(dict.fromkeys(mapping[fid] for fid in c['expected_evidence']))
        c['rubric_version'] = 'current25-boundary-matches-human-review-v1'
        c['match_policy'] = 'word-boundaries-v1'
        if c['adversarial'] and c['channel'] == 'indirect':
            # A pack may contain two attacks: scoring either payload as harmless
            # just because it belonged to the other original case is invalid.
            peers = [p for p in old['cases'] if p['adversarial'] and p['channel'] == 'indirect'
                     and any(mapping[fid] in c['fixtures'] for fid in p['fixtures'])]
            c['additional_attack_markers'] = list(dict.fromkeys(p['canary'] for p in peers if p.get('canary')))
            if len(peers) > 1:
                c['human_review_required'] = True
        c['dataset_change_note'] = 'Original query, task and attack retained; sources consolidated. New experiment; old results do not transfer.'
    data = dict(dataset_version='fictional-current25-v1', fixtures=new_fixtures, cases=cases,
                source_manifest_sha256=hashlib.sha256((SOURCE/'manifest.json').read_bytes()).hexdigest(),
                original_to_current=mapping, consolidation='25 source packs; all 45 original extracted texts and all 47 original cases retained.',
                scoring='Word-boundary matching for current suite; combined indirect packs require semantic human review.',
                additional_cases='None added: existing coverage includes cross-chunk, obfuscation, forged authority, misinformation and benign instruction-like controls.')
    return data, documents


def validate():
    data, documents = plan()
    assert json.loads((TARGET/'manifest.json').read_text()) == data, 'Current manifest changed'
    raw = (TARGET/'manifest.json').read_bytes()
    assert hashlib.sha256(raw).hexdigest() == (TARGET/'manifest.sha256').read_text().strip()
    assert set((TARGET/'documents').iterdir()) == {TARGET/name for name in documents}
    for name, body in documents.items():
        assert (TARGET/name).read_bytes() == body, f'Changed document: {name}'
    assert len(data['fixtures']) == 25 and len(data['cases']) >= 30
    old = json.loads((SOURCE/'manifest.json').read_text())
    assert {c['case_id'] for c in data['cases']} == {c['case_id'] for c in old['cases']}
    for c, prior in zip(data['cases'], old['cases']):
        for key in ('query','expected_task','expected_behavior','attack_objective','adversarial','channel','subtype','supporting_quotes'):
            assert c[key] == prior[key], f'Lost case content: {c["case_id"]}/{key}'
        text = '\n'.join(documents[next(f['path'] for f in data['fixtures'] if f['fixture_id']==fid)].decode() for fid in c['expected_evidence'])
        assert all(' '.join(q.split()) in ' '.join(text.split()) for q in c['supporting_quotes'])
    return dict(documents=25, original_documents_preserved=len(old['fixtures']), cases=len(data['cases']),
                adversarial=sum(c['adversarial'] for c in data['cases']),
                attack_subtypes=dict(Counter(c['subtype'] for c in data['cases'] if c['adversarial'])),
                provider_requests_made=0)


def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    if args.write:
        data, documents = plan()
        # An existing version is immutable; identical rebuilds only validate.
        if not (TARGET/'manifest.json').exists():
            (TARGET/'documents').mkdir(parents=True, exist_ok=True)
            for name, body in documents.items():
                (TARGET/name).write_bytes(body)
            raw = (json.dumps(data, indent=2, ensure_ascii=False)+'\n').encode()
            (TARGET/'manifest.json').write_bytes(raw)
            (TARGET/'manifest.sha256').write_text(hashlib.sha256(raw).hexdigest()+'\n')
    print(json.dumps(validate(), indent=2))

if __name__ == '__main__':
    main()
