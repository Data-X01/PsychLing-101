#!/usr/bin/env python3
"""Prepare event-level data. Default: validate in memory; --write creates new files."""
import argparse
import csv
from collections import Counter, defaultdict
from datetime import datetime
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import re

CONFIG = {'experiment': 'goecke2024_expressional_fluency',
 'task_type': 'expressional_fluency',
 'tasks': {'long_base': {'time_condition': 'long',
                         'variant': 'base',
                         'limit': 240000,
                         'cap': 36,
                         'items': {'FS1_long': 'Nennen Sie ein Synomym zu dem Begriff:\nEINSAM'},
                         'block_order': ['instruct', 'FS1_long'],
                         'initial_instruction': 'InstructionsSyn_long.htm',
                         'pre_instruction': {'instruct': 'InstructionsSyn_long.htm'},
                         'post_instruction': {'FS1_long': 'InstructionsEnd.htm'}},
           'short_base': {'time_condition': 'short',
                          'variant': 'base',
                          'limit': 90000,
                          'cap': 24,
                          'items': {'FS1_base': 'Nennen Sie ein Synonym zu dem Begriff:\n'
                                                'ENTSPANNEN',
                                    'FS2_base': 'Nennen Sie ein Synonym zu dem Begriff:\nSAUBER'},
                          'block_order': ['instruct', 'FS1_base', 'instruct2', 'FS2_base'],
                          'initial_instruction': 'InstructionsSyn.htm',
                          'pre_instruction': {'instruct': 'InstructionsSyn.htm',
                                              'instruct2': 'InstructionsSynBetween.htm'},
                          'post_instruction': {'FS2_base': 'InstructionsEnd.htm'}}},
 'sources': [{'path': 'task_materials/synonym_base_long.iqx',
              'kind': 'material',
              'sha256': 'e12acff84450f24a260ae6b18d1d4cfc49557a3e893c9f61331dd0659bcb16e9',
              'encoding': 'utf-8-sig'},
             {'path': 'task_materials/InstructionsEnd.htm',
              'kind': 'material',
              'sha256': 'b0a09f12189054d9cd6af015b99c58c9e92e31e0d7150ae2559316a572f552b6',
              'encoding': 'cp1252'},
             {'path': 'task_materials/InstructionsSyn_long.htm',
              'kind': 'material',
              'sha256': 'fbff26fdc92f27869923dce02fa6c702b0e67bd296e760a8bbc69aea110150e3',
              'encoding': 'utf-8-sig'},
             {'path': 'raw/wilhelm_retrieval_version2_synonym_base_long_raw_2206030851.csv',
              'kind': 'raw',
              'sha256': '691300d2fc695b53517a48245a1125116d03fc9e15819bdb9d4102a83c7b488e',
              'encoding': 'utf-8-sig',
              'delimiter': ',',
              'rows': 3598,
              'task': 'long_base'},
             {'path': 'task_materials/synonym_base_short.iqx',
              'kind': 'material',
              'sha256': 'd80ec6ee26aa7300181224f0ac035299eaa115582f82991b40477de9521c1df5',
              'encoding': 'utf-8-sig'},
             {'path': 'task_materials/InstructionsSyn.htm',
              'kind': 'material',
              'sha256': 'c067ffb36bba2988e5324016606001ab4028b420e10575c0daf2f77258990ebd',
              'encoding': 'utf-8-sig'},
             {'path': 'raw/wilhelm_retrieval_version2_synonym_base_short_raw_2206030842.csv',
              'kind': 'raw',
              'sha256': 'd605e9f9cea8fce783aed09fa39798417f4328ae5e4cb107e3912750499eafe1',
              'encoding': 'utf-8-sig',
              'delimiter': ',',
              'rows': 6170,
              'task': 'short_base'},
             {'path': 'analysis_scripts/23_SynomeLong.R',
              'kind': 'reference',
              'sha256': '75784cffd273bf9f82c747bb19bb342d8eac86ff1c32505885acbc6cf850cd78',
              'encoding': 'utf-8-sig'},
             {'path': 'scored/synonym_base_long_JL1_19-04-2022_copy.csv',
              'kind': 'scored',
              'sha256': '41f75a78f1ceeed2b75f4397a9fa72b1210fd17849d4e9dd4c9c4ac8fc67af5f',
              'encoding': 'utf-8-sig',
              'delimiter': ';',
              'rows': 2209,
              'rater': 'JL'},
             {'path': 'scored/synonym_long_JL_full_03-06-2022_snippet2.csv',
              'kind': 'scored',
              'sha256': 'ccbd2d8f8ba01cc0b3762115b5881f93f301e33889266d7d2bf4a46e343fe62a',
              'encoding': 'cp1252',
              'delimiter': ';',
              'rows': 1389,
              'rater': 'JL'},
             {'path': 'scored/synonym_base_long_KH1_19-04-2022.csv',
              'kind': 'scored',
              'sha256': 'c7ae5b59742c44bc190fac0e4040a5628724e9c305a088982843bd2ea99b33f1',
              'encoding': 'utf-8-sig',
              'delimiter': ';',
              'rows': 2209,
              'rater': 'KH'},
             {'path': 'scored/synonym_long_kh_full_03-06-2022_snippet2.csv',
              'kind': 'scored',
              'sha256': '5f44e6c37529ced571b9d3bf5e81f5b22019d3f1d402480955001e7220792541',
              'encoding': 'utf-8-sig',
              'delimiter': ';',
              'rows': 1389,
              'rater': 'KH'},
             {'path': 'analysis_scripts/24_SynonymeShort.R',
              'kind': 'reference',
              'sha256': 'cc7b7b56755ac5318d369900b97b5a7249f4bde0c5537fa77875ea05acbcf7f7',
              'encoding': 'utf-8-sig'},
             {'path': 'scored/synonym_base_short_VS1_19-04-2022_copy.csv',
              'kind': 'scored',
              'sha256': '10fe40cd2c99084b6f0250a861d74f8ec23f1226f8327cf528c374c1500f198b',
              'encoding': 'utf-8-sig',
              'delimiter': ';',
              'rows': 3700,
              'rater': 'VS'},
             {'path': 'scored/synonym_short_VS_full_03-06-2022_snippet2.csv',
              'kind': 'scored',
              'sha256': '995ac488bd4080b1fc653af851de062f82f58d929c012ab7a91c8d4b8e8a4bc2',
              'encoding': 'utf-8-sig',
              'delimiter': ';',
              'rows': 2470,
              'rater': 'VS'},
             {'path': 'scored/synonym_base_short_KH1_19-04-2022_copy.csv',
              'kind': 'scored',
              'sha256': '296c85ba348c205bb9def77eafeaacfe1e56a2c94c97465fc177e0b6207fb92b',
              'encoding': 'utf-8-sig',
              'delimiter': ';',
              'rows': 3700,
              'rater': 'KH'},
             {'path': 'scored/synonym_short_kh_full_03-06-2022_snippet2.csv',
              'kind': 'scored',
              'sha256': '64457b417d3da2a67ed80d3b79a5535ea15ca47eff67561e4b33cae2b4ac4588',
              'encoding': 'utf-8-sig',
              'delimiter': ';',
              'rows': 2470,
              'rater': 'KH'},
             {'path': 'analysis_scripts/README_VPCODES.txt',
              'kind': 'reference',
              'sha256': 'f653bac49641b67c008f2fc6bc75d6767401be77d863938a13bdd2f0ea1dc4b6',
              'encoding': 'utf-8-sig'}]}
EVENT_COLUMNS = ['participant_id', 'session_id', 'task_run_id', 'trial_id',
    'trial_order', 'fluency_list_id', 'response_order', 'task_type',
    'time_condition', 'task_variant', 'round_time_limit', 'stimulus', 'response',
    'rt', 'event_type', 'source_file', 'source_row', 'source_trialnum',
    'source_blockcode', 'source_trialcode']
RATING_COLUMNS = ['participant_id', 'trial_id', 'rater_id', 'scored_response',
    'fluency_score_raw', 'fluency_score', 'fluency_score_status',
    'repetition_score_raw', 'repetition_score', 'repetition_score_status',
    'response_differs', 'source_extra_fields', 'rating_source_file', 'rating_source_row']
AUDIT_COLUMNS = ['source_file', 'source_row', 'participant_id', 'reason', 'detail']

@lru_cache(maxsize=None)
def iso_date(value):
    for fmt in ('%Y-%m-%d', '%d.%m.%Y', '%d.%m.%y'):
        try:
            return datetime.strptime(value, fmt).date().isoformat()
        except ValueError:
            pass
    raise ValueError('Unrecognized source date: ' + repr(value))

def event_key(row):
    return (iso_date(row['date']), row['time'], row['subject'],
            row['vpcode_hd1'], row['blockcode'], row['trialnum'])

def exclusion(row):
    if row['vpcode_hd1'] == '':
        return 'missing_participant_id'
    if row['vpcode_hd1'] in {'99TEST99', '04TEST04', '00TEST00'}:
        return 'R_test_code_exclusion'
    if row['subject'] == '811805689':
        return 'R_subject_exclusion'
    if not re.fullmatch(r'[0-9]{2}[A-Za-z]{4}[0-9]{2}', row['vpcode_hd1']):
        return 'unresolved_participant_id'
    return ''

def read_source(root, spec):
    path = root / 'original_data' / spec['path']
    text = path.read_bytes().decode(spec['encoding'], errors='strict')
    if '\ufffd' in text:
        raise ValueError('Replacement character in ' + spec['path'])
    reader = csv.reader(io_lines(text), delimiter=spec['delimiter'], strict=True)
    header = next(reader)
    required = ['date', 'time', 'subject', 'trialnum', 'blockcode', 'trialcode',
                'latency', 'response', 'vpcode_hd1']
    if spec['kind'] == 'scored':
        required += ['flu', 'rep']
    if any(header.count(name) != 1 for name in required):
        raise ValueError('Missing or duplicate required column in ' + spec['path'])
    extras = [i for i, name in enumerate(header) if name not in required]
    if any(header[i] != '' for i in extras):
        raise ValueError('Unexpected named column in ' + spec['path'])
    seen = set()
    rows = []
    for row_number, values in enumerate(reader, 2):
        if len(values) != len(header):
            raise ValueError(f'Wrong field count: {spec["path"]}, record {row_number}')
        key = tuple(values)
        if key in seen:
            raise ValueError(f'Exact duplicate source record: {spec["path"]}:{row_number}')
        seen.add(key)
        row = {name: values[header.index(name)] for name in required}
        row['_extra'] = [{'column_position': i + 1, 'value': values[i]} for i in extras if values[i] != '']
        row['_row'] = row_number
        rows.append(row)
    if len(rows) != spec['rows']:
        raise ValueError('Source row count changed: ' + spec['path'])
    return rows

def io_lines(text):
    # StringIO preserves quoted newlines; source_row counts CSV records, not lines.
    from io import StringIO
    return StringIO(text, newline='')

def parse_score(raw, field):
    if raw in ('', 'NA'):
        return (0, 'missing_as_zero') if field == 'rep' else ('', 'missing')
    if raw == '-99' and field == 'flu':
        return '', 'sentinel_missing'
    if re.fullmatch(r'-?\d+(?:\.0+)?', raw):
        return int(float(raw)), 'numeric'
    return '', 'unresolved'

def prepare(root=None):
    root = Path(root) if root else Path(__file__).resolve().parent
    expected = {spec['path'] for spec in CONFIG['sources']}
    actual = {p.relative_to(root / 'original_data').as_posix()
              for p in (root / 'original_data').rglob('*') if p.is_file()}
    if actual != expected:
        raise ValueError(f'Source manifest mismatch: missing={expected-actual}, extra={actual-expected}')
    for spec in CONFIG['sources']:
        digest = hashlib.sha256((root / 'original_data' / spec['path']).read_bytes()).hexdigest()
        if digest != spec['sha256']:
            raise ValueError('Source checksum changed: ' + spec['path'])
    audit, raw_index, runs = [], defaultdict(list), defaultdict(list)
    summary = {'experiment': CONFIG['experiment'], 'raw_rows': 0,
               'scored_rows': 0, 'excluded_raw_rows': 0, 'excluded_scored_rows': 0,
               'warnings': [], 'source_sha256': {s['path']: s['sha256'] for s in CONFIG['sources']}}
    for spec in CONFIG['sources']:
        if spec['kind'] != 'raw':
            continue
        rows = read_source(root, spec)
        summary['raw_rows'] += len(rows)
        allowed = CONFIG['tasks'][spec['task']]
        for row in rows:
            key = event_key(row)
            if row['blockcode'] not in allowed['block_order']:
                raise ValueError('Unknown raw block: ' + repr(row['blockcode']))
            reason = exclusion(row)
            if reason:
                summary['excluded_raw_rows'] += 1
                audit.append(dict(source_file=spec['path'], source_row=row['_row'],
                    participant_id=row['vpcode_hd1'], reason=reason, detail=''))
                continue
            datetime.strptime(row['time'], '%H:%M:%S')
            run_key = (row['vpcode_hd1'], key[0], key[1], row['subject'], spec['path'])
            row['_source'] = spec['path']
            row['_task'] = spec['task']
            row['_key'] = key
            runs[run_key].append(row)
    events, participant_runs = [], defaultdict(list)
    for run_key, rows in runs.items():
        participant_runs[run_key[0]].append((run_key, rows))
    for participant, groups in sorted(participant_runs.items()):
        groups.sort(key=lambda g: (g[0][1], g[0][2], g[0][4], g[0][3]))
        dates = {date: i for i, date in enumerate(sorted({g[0][1] for g in groups}))}
        list_number, trial_order = 0, 0
        for run_number, (run_key, rows) in enumerate(groups):
            task = CONFIG['tasks'][rows[0]['_task']]
            run_id = f'run_{run_number:03d}'
            rows.sort(key=lambda r: (task['block_order'].index(r['blockcode']), r['_row']))
            counts, last_numbers, lists = Counter(), {}, {}
            for row in rows:
                block = row['blockcode']
                is_task = block in task['items']
                if is_task:
                    control_without_trial = (row['trialnum'] == '' and row['trialcode'] == ''
                        and row['response'] in ("Ctrl+'B'", "Ctrl+'Q'"))
                    if row['trialcode'] != block + '_txt' and not control_without_trial:
                        raise ValueError('Unexpected task trial label: ' + repr(row['trialcode']))
                    if not control_without_trial:
                        number = int(row['trialnum'])
                        if number <= last_numbers.get(block, 0):
                            raise ValueError('Duplicate or invalid trial order in ' + row['_source'])
                        last_numbers[block] = number
                        if number > task['cap']:
                            raise ValueError('Trial number exceeds task script cap')
                    if block not in lists:
                        lists[block] = list_number
                        list_number += 1
                    counts[block] += 1
                rt = ''
                if row['latency'] != '':
                    if not re.fullmatch(r'\d+', row['latency']):
                        raise ValueError('Invalid latency: ' + repr(row['latency']))
                    rt = int(row['latency'])
                    if is_task and rt > task['limit']:
                        raise ValueError('Single latency exceeds round time limit')
                event_type = ('control' if row['response'] in ("Ctrl+'B'", "Ctrl+'Q'")
                              else 'empty' if row['response'] == '' else 'typed')
                if '<<' in row['response'] or '>>' in row['response']:
                    raise ValueError('Reserved prompt delimiter in raw response')
                event = dict(participant_id=participant, session_id=f'session_{dates[run_key[1]]:03d}',
                    task_run_id=run_id, trial_id=f'event_{trial_order:06d}', trial_order=trial_order,
                    fluency_list_id=lists[block] if is_task else '',
                    response_order=counts[block] if is_task else '', task_type=CONFIG['task_type'],
                    time_condition=task['time_condition'], task_variant=task['variant'],
                    round_time_limit=task['limit'] if is_task else '',
                    stimulus=task['items'][block] if is_task else '', response=row['response'],
                    rt=rt, event_type=event_type, source_file=row['_source'], source_row=row['_row'],
                    source_trialnum=row['trialnum'], source_blockcode=block, source_trialcode=row['trialcode'])
                events.append(event)
                raw_index[row['_key']].append(event)
                trial_order += 1
            for block in lists:
                block_events = [e for e in events[-len(rows):] if e['source_blockcode'] == block]
                if sum(e['rt'] for e in block_events if e['rt'] != '') > task['limit']:
                    summary['warnings'].append(f'{participant}/{run_id}/{block}: summed latencies exceed limit')
    ratings = []
    for spec in CONFIG['sources']:
        if spec['kind'] != 'scored':
            continue
        rows = read_source(root, spec)
        summary['scored_rows'] += len(rows)
        for row in rows:
            reason = exclusion(row)
            if reason:
                summary['excluded_scored_rows'] += 1
                audit.append(dict(source_file=spec['path'], source_row=row['_row'],
                    participant_id=row['vpcode_hd1'], reason=reason, detail=''))
                continue
            matches = raw_index.get(event_key(row), [])
            if len(matches) != 1:
                audit.append(dict(source_file=spec['path'], source_row=row['_row'],
                    participant_id=row['vpcode_hd1'], reason='unmatched_rating' if not matches else 'ambiguous_rating',
                    detail='No guessed match; original rating retained in original_data'))
                continue
            event = matches[0]
            flu, fs = parse_score(row['flu'], 'flu')
            rep, rs = parse_score(row['rep'], 'rep')
            ratings.append(dict(participant_id=event['participant_id'], trial_id=event['trial_id'],
                rater_id=spec['rater'], scored_response=row['response'],
                fluency_score_raw=row['flu'], fluency_score=flu, fluency_score_status=fs,
                repetition_score_raw=row['rep'], repetition_score=rep, repetition_score_status=rs,
                response_differs=int(row['response'] != event['response']),
                source_extra_fields=json.dumps(row['_extra'], ensure_ascii=False) if row['_extra'] else '',
                rating_source_file=spec['path'], rating_source_row=row['_row']))
    if len({(e['participant_id'], e['trial_id']) for e in events}) != len(events):
        raise ValueError('Duplicate output event identifiers')
    by_participant = defaultdict(list)
    for event in events:
        by_participant[event['participant_id']].append(event)
    if any([e['trial_order'] for e in rows] != list(range(len(rows))) for rows in by_participant.values()):
        raise ValueError('Noncontiguous output trial order')
    reasons = Counter(row['reason'] for row in audit)
    summary.update(participants=len(by_participant), event_rows=len(events), rating_rows=len(ratings),
        raw_reconciliation_ok=(len(events) + summary['excluded_raw_rows'] == summary['raw_rows']),
        scored_reconciliation_ok=(len(ratings) + summary['excluded_scored_rows'] +
            reasons['unmatched_rating'] + reasons['ambiguous_rating'] == summary['scored_rows']),
        event_types=dict(Counter(e['event_type'] for e in events)), audit_reasons=dict(reasons),
        response_differences=sum(r['response_differs'] for r in ratings),
        unnamed_annotation_rows=sum(bool(r['source_extra_fields']) for r in ratings),
        unresolved_scores=sum(r['fluency_score_status'] == 'unresolved' or r['repetition_score_status'] == 'unresolved' for r in ratings),
        umlaut_event_rows=sum(any(c in e['response'] for c in 'äöüÄÖÜß') for e in events),
        multiple_run_participants=sum(len(g) > len({row[1][0]['_task'] for row in g}) for g in participant_runs.values()))
    if not summary['raw_reconciliation_ok'] or not summary['scored_reconciliation_ok']:
        raise ValueError('Row reconciliation failed')
    if reasons['unmatched_rating'] or reasons['ambiguous_rating']:
        summary['warnings'].append('Unmatched/ambiguous ratings retained only in sources and audit; review before release.')
    if summary['unnamed_annotation_rows']:
        summary['warnings'].append('Unnamed scoring annotations preserved as positional JSON; meaning unverified.')
    if summary['unresolved_scores']:
        summary['warnings'].append('Unresolved scoring strings preserved; no guessed numeric values.')
    summary['warnings'].append('Consent-withdrawal exclusions and public-sharing permission remain unverified.')
    return events, ratings, audit, summary

def write_csv(path, columns, rows):
    with path.open('x', encoding='utf-8', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='Create new outputs; never overwrite existing files.')
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    events, ratings, audit, summary = prepare(root)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if args.write:
        paths = [root / 'processed_data' / 'exp1.csv', root / 'processed_data' / 'exp2.csv',
                 root / 'processed_data' / 'validation.json', root / 'local_audit.csv']
        if any(path.exists() for path in paths):
            raise FileExistsError('Output exists. Use a separately approved fresh directory; no overwrite option.')
        paths[0].parent.mkdir(exist_ok=True)
        write_csv(paths[0], EVENT_COLUMNS, events)
        write_csv(paths[1], RATING_COLUMNS, ratings)
        with paths[2].open('x', encoding='utf-8') as handle:
            json.dump(summary, handle, ensure_ascii=False, indent=2)
        write_csv(paths[3], AUDIT_COLUMNS, audit)

if __name__ == '__main__':
    main()
