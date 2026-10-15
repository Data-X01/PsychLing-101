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

CONFIG = {'experiment': 'goecke2024_word_fluency',
 'task_type': 'word_fluency',
 'tasks': {'long_base': {'time_condition': 'long',
                         'variant': 'base',
                         'limit': 480000,
                         'cap': 300,
                         'items': {'WL1_base_l': 'Nennen Sie Worte, die als ERSTEN Buchstaben ein '
                                                 "'S' haben",
                                   'WL2_base_l': 'Nennen Sie Worte, die als LETZTEN Buchstaben ein '
                                                 "'N' haben"},
                         'block_order': ['instruct_WL1_base_1', 'WL1_base_l', 'WL2_base_l'],
                         'initial_instruction': 'InstructionsWL_long.htm',
                         'pre_instruction': {'instruct_WL1_base_1': 'InstructionsWL_long.htm'},
                         'post_instruction': {'WL1_base_l': 'InstructionsWeiterWL1.htm',
                                              'WL2_base_l': 'InstructionsEnd.htm'}},
           'short_base': {'time_condition': 'short',
                          'variant': 'base',
                          'limit': 90000,
                          'cap': 100,
                          'items': {'WL1_base_s': 'Nennen Sie Worte, die als ERSTEN Buchstaben ein '
                                                  "'D' haben",
                                    'WL2_base_s': 'Nennen Sie Worte, die als LETZTEN Buchstaben '
                                                  "ein 'R' haben",
                                    'WL3_base_s': 'Nennen Sie Worte, die aus 4 Buchstaben '
                                                  'bestehen'},
                          'block_order': ['instruct_WL1_base_s',
                                          'WL1_base_s',
                                          'WL2_base_s',
                                          'WL3_base_s'],
                          'initial_instruction': 'InstructionsWL.htm',
                          'pre_instruction': {'instruct_WL1_base_s': 'InstructionsWL.htm'},
                          'post_instruction': {'WL1_base_s': 'InstructionsWeiterWL1.htm',
                                               'WL2_base_s': 'InstructionsWeiterWL1.htm',
                                               'WL3_base_s': 'InstructionsEnd.htm'}},
           'short_hard': {'time_condition': 'short',
                          'variant': 'hard',
                          'limit': 120000,
                          'cap': 100,
                          'items': {'WL1_base_hard_s': 'Nennen Sie Worte mit als ERSTEN Buchstaben '
                                                       "ein 'Q' haben",
                                    'WL2_base_hard_s': 'Nennen Sie Worte, die als ZWEITEN '
                                                       "Buchstaben ein 'V' haben"},
                          'block_order': ['instruct_WL1_base_hard_s',
                                          'WL1_base_hard_s',
                                          'WL2_base_hard_s'],
                          'initial_instruction': 'InstructionsWL_hard.htm',
                          'pre_instruction': {'instruct_WL1_base_hard_s': 'InstructionsWL_hard.htm'},
                          'post_instruction': {'WL1_base_hard_s': 'InstructionsWeiterWL1.htm',
                                               'WL2_base_hard_s': 'InstructionsEnd.htm'}}},
 'sources': [{'path': 'task_materials/wordlist_base_long_ges.iqx',
              'kind': 'material',
              'sha256': 'cd9531f9c268a96e4c23f83c0fdc7b0334b08e47002427256a5bec8ff435dec9',
              'encoding': 'utf-8-sig'},
             {'path': 'task_materials/InstructionsEnd.htm',
              'kind': 'material',
              'sha256': 'b0a09f12189054d9cd6af015b99c58c9e92e31e0d7150ae2559316a572f552b6',
              'encoding': 'cp1252'},
             {'path': 'task_materials/InstructionsWeiterWL1.htm',
              'kind': 'material',
              'sha256': '4ce67f88679bf7a3994542d56644e2bc955a3b7f18c30bc72306db9d86efaf45',
              'encoding': 'cp1252'},
             {'path': 'task_materials/InstructionsWL_long.htm',
              'kind': 'material',
              'sha256': '1e09fa3d0cc26d7d49b0b0f3ae9e236e55c7ed711f5690bde21ab536c084dbb2',
              'encoding': 'cp1252'},
             {'path': 'raw/wilhelm_retrieval_version2_wordlist_base_long_ges_raw_2206030858.csv',
              'kind': 'raw',
              'sha256': '7fe36f3e6f421e91136342dda8a88b6e539034533203998bc47572f0e86ab2cd',
              'encoding': 'utf-8-sig',
              'delimiter': ',',
              'rows': 50791,
              'task': 'long_base'},
             {'path': 'task_materials/wordlist_base_short_ges.iqx',
              'kind': 'material',
              'sha256': 'eff9c3b157714a581299836d1b0c988c0a082d93573207abae1743fdf4c0eb9d',
              'encoding': 'utf-8-sig'},
             {'path': 'task_materials/InstructionsWL.htm',
              'kind': 'material',
              'sha256': 'c85eb89c2ff8e0318f6691ba855b346c090fef323bf47a8b1a4e2a40f5948415',
              'encoding': 'cp1252'},
             {'path': 'raw/wilhelm_retrieval_version2_wordlist_base_short_ges_raw_2206030847.csv',
              'kind': 'raw',
              'sha256': '0370eb354a457fc9240cde463e945890e304af9f64d5c66d167d90117c313a4e',
              'encoding': 'utf-8-sig',
              'delimiter': ',',
              'rows': 17756,
              'task': 'short_base'},
             {'path': 'task_materials/wordlist_base_short_hard_ges.iqx',
              'kind': 'material',
              'sha256': '4aab1e0f8f86256e2317cbed74fa51a61ce5b0ce74e3341adb7410caa153ded8',
              'encoding': 'utf-8-sig'},
             {'path': 'task_materials/InstructionsWL_hard.htm',
              'kind': 'material',
              'sha256': '1e31cf54afb045a9a20ac29201bba607d8d73e9896e28d427282f0e554d45113',
              'encoding': 'cp1252'},
             {'path': 'raw/wilhelm_retrieval_version2_wordlist_base_short_hard_ges_raw_2206030903.csv',
              'kind': 'raw',
              'sha256': '5225f4c68cdba9a7f7934fe9100324f67feec89290553f5b7b8327a936925c95',
              'encoding': 'utf-8-sig',
              'delimiter': ',',
              'rows': 6626,
              'task': 'short_hard'},
             {'path': 'analysis_scripts/20_WordListLong.R',
              'kind': 'reference',
              'sha256': 'daa042e50e44fd32708566d262f2d236fb8ea87cfb8e3a6489ac7fb3781a9d3c',
              'encoding': 'utf-8-sig'},
             {'path': 'scored/wordlist_base_long_JL1_19-04-2022_copy.csv',
              'kind': 'scored',
              'sha256': '1d92917dfac991cee1312f9b1a9e85e92560c1d557dd372460942a50c61e283b',
              'encoding': 'utf-8-sig',
              'delimiter': ';',
              'rows': 31060,
              'rater': 'JL'},
             {'path': 'scored/wordlist_base_long_ges_JL_full_03-06-2022_snippet2.csv',
              'kind': 'scored',
              'sha256': '42a8968b76b32f6ef78a7c873b783e9361dc1dfc11394ec104563d9b9116a50a',
              'encoding': 'cp1252',
              'delimiter': ';',
              'rows': 19731,
              'rater': 'JL'},
             {'path': 'scored/wordlist_base_long_VS1_19-04-2022_copy.csv',
              'kind': 'scored',
              'sha256': 'd879ef4a4150ef4dbcfab86a0bf8c5086a4f7e62e836b5620f13cb0ebb346cc3',
              'encoding': 'cp1252',
              'delimiter': ';',
              'rows': 31060,
              'rater': 'VS'},
             {'path': 'scored/wordlist_base_long_ges_VS_full_03-06-2022_snippet2.csv',
              'kind': 'scored',
              'sha256': 'c2a00dbce52a6c46edb0409d0b68fd4f198104248e1f13e5e4bcfc90d5221f2d',
              'encoding': 'utf-8-sig',
              'delimiter': ';',
              'rows': 19731,
              'rater': 'VS'},
             {'path': 'scored/wordlist_base_long_KH1_19-04-2022_copy.csv',
              'kind': 'scored',
              'sha256': '8a2bf0d7e67e59a3185140cbf60f5306cec19aabc6b88de93df6118d5d5fb220',
              'encoding': 'utf-8-sig',
              'delimiter': ';',
              'rows': 31060,
              'rater': 'KH'},
             {'path': 'analysis_scripts/21_WordListShort.R',
              'kind': 'reference',
              'sha256': 'a7aa3aa7a5f153f7dc125a865f86ba77b3426114072900c874bcad25a67ad69e',
              'encoding': 'utf-8-sig'},
             {'path': 'scored/wordlist_base_short_JL_19-04-2022.csv',
              'kind': 'scored',
              'sha256': 'f22e19f566daa28c8d3b5d88422b41bc67ab5341e2cb9f9bfc0815eea0851b69',
              'encoding': 'cp1252',
              'delimiter': ';',
              'rows': 10630,
              'rater': 'JL'},
             {'path': 'scored/wordlist_base_short_VS_19-04-2022.csv',
              'kind': 'scored',
              'sha256': '003e84aa4eaa489332d0ca6367cfbcfdab0ec6fc421a2b7baf596bba844c852d',
              'encoding': 'cp1252',
              'delimiter': ';',
              'rows': 10630,
              'rater': 'VS'},
             {'path': 'scored/wordlist_base_short_VS_full_03-06-2022_snippet2.csv',
              'kind': 'scored',
              'sha256': 'fac3b96abfd0be6aa7ae00d4a80cd5652ecd33a74c8239a5a6717f2df6575544',
              'encoding': 'utf-8-sig',
              'delimiter': ';',
              'rows': 7126,
              'rater': 'VS'},
             {'path': 'scored/wordlist_base_short_KH_19-04-2022.csv',
              'kind': 'scored',
              'sha256': '465e5294cc3ffd43aeabb43280243b485047dfdd1e9afe320addc695d0539786',
              'encoding': 'cp1252',
              'delimiter': ';',
              'rows': 10630,
              'rater': 'KH'},
             {'path': 'scored/wordlist_base_short_kh_full_03-06-2022_snippet2.csv',
              'kind': 'scored',
              'sha256': '829554c94360ffc9a2fe2fe91fcc44f3e612e0f3391dc338bc11f48810b803de',
              'encoding': 'utf-8-sig',
              'delimiter': ';',
              'rows': 7126,
              'rater': 'KH'},
             {'path': 'analysis_scripts/33_WordListHard.R',
              'kind': 'reference',
              'sha256': '06f6cd0067d2b1c3b76204eeb2d07b7f163106f3b8c134d2b26d5d112852fc04',
              'encoding': 'utf-8-sig'},
             {'path': 'scored/wordlist_base_short_hard_nb_full_03-06-2022.csv',
              'kind': 'scored',
              'sha256': '82de21a41307c3a951113fc50b8fca7f625215072bc71b51700a0697f8c23812',
              'encoding': 'utf-8-sig',
              'delimiter': ';',
              'rows': 6626,
              'rater': 'NB'},
             {'path': 'scored/wordlist_base_short_hard_az_full_03-06-2022.csv',
              'kind': 'scored',
              'sha256': 'af8a20bf6519c8647b0622de7db4784efe64a911b4c8e3ef1d48053ef9ae0786',
              'encoding': 'utf-8-sig',
              'delimiter': ';',
              'rows': 6626,
              'rater': 'AZ'},
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
