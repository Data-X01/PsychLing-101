#!/usr/bin/env python3
"""German participant prompts. Default: in-memory preview; --write creates a new ZIP."""
import argparse
import csv
import hashlib
from collections import defaultdict
from html.parser import HTMLParser
import json
import re
from pathlib import Path
import zipfile
from preprocess_data import CONFIG, EVENT_COLUMNS

class BodyText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.in_body, self.skip, self.parts = False, 0, []
    def handle_starttag(self, tag, attrs):
        if tag == 'body': self.in_body = True
        if tag in ('script', 'style'): self.skip += 1
        if self.in_body and tag in ('p', 'br', 'div', 'h1', 'h2', 'li'): self.parts.append('\n')
    def handle_endtag(self, tag):
        if tag in ('script', 'style'): self.skip -= 1
        if self.in_body and tag in ('p', 'div', 'h1', 'h2', 'li'): self.parts.append('\n')
        if tag == 'body': self.in_body = False
    def handle_data(self, data):
        if self.in_body and not self.skip: self.parts.append(data)

def instruction(root, filename):
    if filename == 'InstructionsSynBetween.htm':
        # Contributor explicitly approved omission of this unavailable page.
        return ''
    spec = next(s for s in CONFIG['sources'] if s['path'] == 'task_materials/' + filename)
    source_bytes = (root / 'original_data' / spec['path']).read_bytes()
    if hashlib.sha256(source_bytes).hexdigest() != spec['sha256']:
        raise ValueError('Original instruction checksum changed: ' + filename)
    parser = BodyText()
    parser.feed(source_bytes.decode(spec['encoding'], errors='strict'))
    text = '\n'.join(' '.join(line.split()) for line in ''.join(parser.parts).splitlines() if line.strip())
    if not text or '<<' in text or '>>' in text:
        raise ValueError('Missing/invalid original instructions: ' + filename)
    return text

TASK_BY_SOURCE = {s['path']: CONFIG['tasks'][s['task']]
                  for s in CONFIG['sources'] if s['kind'] == 'raw'}

def read_processed_events(root):
    """Read the standardized event CSV without regenerating raw-data preprocessing."""
    path = root / 'processed_data' / 'exp1.csv'
    integer_fields = {'trial_order', 'fluency_list_id', 'response_order',
                      'round_time_limit', 'rt', 'source_row'}
    required_integer_fields = {'trial_order', 'source_row'}
    events, seen_ids = [], set()
    participant_orders, round_orders = defaultdict(int), defaultdict(int)
    with path.open('r', encoding='utf-8', newline='') as handle:
        reader = csv.DictReader(handle, strict=True)
        if reader.fieldnames != EVENT_COLUMNS:
            raise ValueError('Unexpected exp1.csv columns; run reviewed preprocessing first.')
        for record_number, row in enumerate(reader, 2):
            if None in row or any(value is None for value in row.values()):
                raise ValueError(f'Wrong field count in exp1.csv record {record_number}')
            if any('\ufffd' in value for value in row.values()):
                raise ValueError('Replacement character in processed event data')
            for field in integer_fields:
                value = row[field]
                if value == '' and field not in required_integer_fields:
                    continue
                if not value.isascii() or not value.isdigit():
                    raise ValueError(f'Invalid integer {field} in record {record_number}')
                row[field] = int(value)
            participant = row['participant_id']
            if not re.fullmatch(r'[0-9]{2}[A-Za-z]{4}[0-9]{2}', participant):
                raise ValueError('Missing or unresolved processed participant ID')
            if participant in {'99TEST99', '04TEST04', '00TEST00'}:
                raise ValueError('Known test participant in processed events')
            event_key = (participant, row['trial_id'])
            if not row['trial_id'] or event_key in seen_ids:
                raise ValueError('Missing or duplicate processed trial ID')
            seen_ids.add(event_key)
            if row['trial_order'] != participant_orders[participant]:
                raise ValueError('Noncontiguous processed event order')
            participant_orders[participant] += 1
            task = TASK_BY_SOURCE.get(row['source_file'])
            if task is None or row['source_blockcode'] not in task['block_order']:
                raise ValueError('Unknown processed source or block label')
            if (row['task_type'] != CONFIG['task_type'] or
                    row['time_condition'] != task['time_condition'] or
                    row['task_variant'] != task['variant']):
                raise ValueError('Processed task metadata disagrees with administered script')
            expected_stimulus = task['items'].get(row['source_blockcode'], '')
            if row['stimulus'] != expected_stimulus:
                raise ValueError('Processed cue disagrees with administered script')
            expected_type = ('control' if row['response'] in ("Ctrl+'B'", "Ctrl+'Q'")
                             else 'empty' if row['response'] == '' else 'typed')
            if row['event_type'] != expected_type:
                raise ValueError('Processed event type disagrees with response')
            if '<<' in row['response'] or '>>' in row['response']:
                raise ValueError('Reserved prompt symbols in processed response')
            if expected_stimulus:
                round_key = (participant, row['task_run_id'], row['source_blockcode'])
                round_orders[round_key] += 1
                if (row['response_order'] != round_orders[round_key] or
                        row['round_time_limit'] != task['limit'] or
                        row['fluency_list_id'] == ''):
                    raise ValueError('Invalid processed response-round metadata')
            elif any(row[field] != '' for field in ('response_order', 'round_time_limit', 'fluency_list_id')):
                raise ValueError('Instruction event has timed-round metadata')
            events.append(row)
    validation = json.loads((root / 'processed_data' / 'validation.json').read_text(encoding='utf-8'))
    if len(events) != validation['event_rows'] or len(participant_orders) != validation['participants']:
        raise ValueError('Processed event totals disagree with validation.json')
    return events

def task_for(event):
    # Synonym runs share an 'instruct' label, so resolve by source file.
    return TASK_BY_SOURCE[event['source_file']]

def prompt_records(events, root):
    groups = defaultdict(list)
    for event in events: groups[event['participant_id']].append(event)
    records = []
    for participant, rows in sorted(groups.items()):
        parts, previous_run, previous_block = [], None, None
        runs = set()
        for event in rows:
            task, block = task_for(event), event['source_blockcode']
            new_run = event['task_run_id'] != previous_run
            if new_run:
                parts.append(instruction(root, task['initial_instruction']))
                parts.append(f'Durchgang {int(event["task_run_id"].split("_")[1]) + 1}.')
                previous_block = None
                runs.add(event['task_run_id'])
            if block != previous_block:
                if not new_run and previous_block in task['items']:
                    page = task['post_instruction'].get(previous_block)
                    if page: parts.append(instruction(root, page))
                if block in task['pre_instruction'] and block != task['block_order'][0]:
                    parts.append(instruction(root, task['pre_instruction'][block]))
                if event['stimulus']:
                    parts.append(event['stimulus'])
            value = event['response'] if event['response'] != '' else 'Keine Texteingabe aufgezeichnet'
            if event['rt'] != '': value += f' | Latenz: {event["rt"]} ms'
            label = f'{event["response_order"]}. ' if event['response_order'] != '' else 'Aufgezeichnetes Instruktionsereignis: '
            parts.append(label + '<<' + value + '>>')
            previous_run, previous_block = event['task_run_id'], block
        text = '\n\n'.join(p for p in parts if p)
        # Every event appears once. No human scores or unobserved trials are invented.
        if text.count('<<') != len(rows) or text.count('>>') != len(rows):
            raise ValueError('Prompt event/delimiter count mismatch')
        records.append(dict(text=text, experiment=CONFIG['experiment'], participant_id=participant,
            metadata={'language': 'de', 'task_type': CONFIG['task_type'], 'event_count': len(rows),
                      'task_run_count': len(runs), 'missing_synonym_transition_omitted': any(e['source_blockcode'] in ('instruct2', 'FS2_base') for e in rows)}))
    return records

def check_lengths(records, tokenizer='utf8_byte_bound'):
    encoder = None
    if tokenizer != 'utf8_byte_bound':
        import tiktoken
        # Requires a locally available encoding cache; dependency installation is a separate step.
        encoder = tiktoken.get_encoding(tokenizer)
    counts, exceeded = {}, []
    for record in records:
        text = record['text']
        count = len(encoder.encode(text, disallowed_special=())) if encoder else len(text.encode('utf-8'))
        counts[record['participant_id']] = count
        if count >= 32000: exceeded.append(record['participant_id'])
        record['metadata']['prompt_length_measure'] = tokenizer
        record['metadata']['prompt_length_value'] = count
    return dict(measure=tokenizer, participants=len(records), maximum=max(counts.values(), default=0),
                maximum_participant_ids=[p for p, n in counts.items() if n == max(counts.values(), default=0)],
                at_or_above_32000=exceeded, counts=counts)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='Create prompts.jsonl.zip after all length checks pass.')
    parser.add_argument('--examples', type=int, default=0, help='Print this many complete participant prompts.')
    parser.add_argument('--tokenizer', choices=['utf8_byte_bound', 'cl100k_base', 'o200k_base'], default='utf8_byte_bound')
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    events = read_processed_events(root)
    records = prompt_records(events, root)
    report = check_lengths(records, args.tokenizer)
    print(json.dumps({k: v for k, v in report.items() if k != 'counts'}, ensure_ascii=False, indent=2))
    for record in records[:max(0, args.examples)]:
        print(json.dumps(record, ensure_ascii=False))
    if report['at_or_above_32000']:
        raise ValueError('Length limit unresolved for: ' + ', '.join(report['at_or_above_32000']) + '. No truncation or output.')
    if args.write:
        payload = ''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in records).encode('utf-8')
        info = zipfile.ZipInfo('prompts.jsonl', date_time=(2024, 1, 1, 0, 0, 0))
        info.compress_type = zipfile.ZIP_DEFLATED
        info.external_attr = 0o600 << 16
        with zipfile.ZipFile(root / 'prompts.jsonl.zip', mode='x') as archive:
            archive.writestr(info, payload)
        with zipfile.ZipFile(root / 'prompts.jsonl.zip') as archive:
            if archive.testzip() is not None or archive.read('prompts.jsonl') != payload:
                raise ValueError('ZIP verification failed')

if __name__ == '__main__':
    main()
