# Reference

Futrell, R., Gibson, E., Tily, H. J., Blank, I., Vishnevetsky, A., Piantadosi, S. T., & Fedorenko, E. (2021). The Natural Stories corpus: a reading-time corpus of English texts containing rare syntactic constructions. *Language Resources and Evaluation*, 55, 63–77.

# Data source

https://doi.org/10.1007/s10579-020-09503-7

# Description

The Natural Stories corpus collected self-paced reading times for 10 naturalistic English stories containing rare syntactic constructions. Data were collected from 180 participants via Amazon Mechanical Turk. Each participant read 5 stories.

After each story, participants answered 6 comprehension questions (2-choice format). The `comprehension_correct` column records the number of correct answers per participant per story. The original data does not record which individual questions were answered correctly — only the per-story total is available.

## exp1.csv — Self-Paced Reading

180 participants each read 5 of the 10 stories (~1,000 words per story). Participants pressed SPACE to reveal each word one at a time.

# Prompts

`prompts.jsonl.zip` contains one JSON line per participant × story (899 entries total).

Each entry covers one story read by one participant:

- Instruction explains the SPR procedure; reaction times are noted to be recorded
- Each word is shown as: `Word N: 'word' <<RT>> ms`

Comprehension question responses are not included in the prompt text. Although participants answered 6 questions after each story, the original data provides only the per-story total correct count — which individual questions were answered correctly is not recorded. The total (`comprehension_correct`) is retained as a JSON metadata field only.

The `item` field records the story number (1–10). The `rt` field contains the list of reading times in word order.
