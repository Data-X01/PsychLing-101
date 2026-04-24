# Chen et al. (2026) - Semantic Transparency Ratings for Chinese Compounds

## Citation

Chen, J., Chersoni, E., Marelli, M., & Huang, C.-R. (2026). The multidimensional nature of semantic transparency in a cross-linguistic perspective: Evidence from human intuitions, computational estimates, and processing data for Chinese compounds. *Cognitive Science*, *50*, e70194. https://doi.org/10.1111/cogs.70194

## Data Source

Data collected via Microsoft Surveys in November 2024. Participants were native Mandarin Chinese speakers.

## Task Description

Participants rated the semantic transparency of Chinese compound words. For each compound, they answered three questions on a 0–5 integer scale.

### Instructions

**Chinese (original):**

“请你对复合词的语义透明度进行打分：
    "（1）复合词各组成成分对复合词整体语义的贡献程度；"
    "（2）复合词整体语义的可推测性（即能否从各组成成分的意义推断出复合词的意义）。"
    "打分范围为0到5，其中0表示\u201c完全没有贡献\u201d或\u201c非常难以推测\u201d，5表示\u201c贡献非常大\u201d或\u201c非常容易推测\u201d。"
    "注：如果某个词或者汉字有多种意义，请根据第一反应进行打分。\n\n"

**English (translation):**

"You are asked to rate the semantic transparency of compound words:
(1) The degree of contribution of each component of the compound word to the overall meaning of the compound word;
(2) The inferability of the overall meaning of the compound word (i.e., whether the meaning of the compound word can be inferred from the meanings of its components).

The rating scale ranges from 0 to 5, where 0 indicates 'no contribution at all' or 'very difficult to infer,' and 5 indicates 'very significant contribution' or 'very easy to infer.'

Note: If a word or character has multiple meanings, please rate based on your first instinct."


### Prompt template

Each JSONL line represents one participant's session segment (3 segments per participant). The `text` field follows this structure:

```
1：
1. "{constituent_1}"为"{stimulus}"这个词的整体语义贡献了多少？请用0-5之间的整数来回答。\n<<{constituent_1_contribution}>>\n
2. "{constituent_2}"为"{stimulus}"这个词的整体语义贡献了多少？请用0-5之间的整数来回答。\n<<{constituent_2_contribution}>>\n
3. "{stimulus}"的意思能从"{constituent_1}"和"{constituent_2}"的语义上推测出来吗？请用0-5之间的整数来回答。\n<<{predictability}>>\n

2：
1. "{constituent_1}"为"{stimulus}"这个词的整体语义贡献了多少？请用0-5之间的整数来回答。<<{constituent_1_contribution}>>
...


```

**Note**: Each participant's 2,675 trials are split into 3 segments (approximately 890 trials per segment) to comply with token limits. All trials for a participant use the same instructions but are distributed across 3 separate JSONL entries with participant IDs: `{original_id}_part1`, `{original_id}_part2`, `{original_id}_part3`. Trial numbers are **global and never reset** across segments. JSONL fields: `"text"`, `"experiment"`, `"participant"`, `"trial_id_start"`, `"trial_id_end"`.

### JSONL Fields

- `text`: Full prompt with instructions and all trial-by-trial data for this segment
- `experiment`: Experiment identifier (`chen2026transparency`)
- `participant`: Participant ID with segment indicator (e.g., `anonymized_1409_part1`)
- `trial_id_start`: Global trial ID at the start of this segment (e.g., 1)
- `trial_id_end`: Global trial ID at the end of this segment (e.g., 892). Note that trial IDs are continuous across all 3 segments per participant and do not reset.

## Dataset Details

- **Total compounds**: 2,675 Chinese compound words
- **Lists**: 108 (compounds distributed across lists, ~25 items per list)
- **Total participants**: 20
- **Language**: Mandarin Chinese

## Files

- `original_data/`: Raw data files adapted from Microsoft Surveys to keep metadata in English
  - `list_NN.csv` (108 files): One file per experimental list in long format. Each row is one participant × one stimulus observation, with columns: `participant_id`, `start_time`, `completion_time`, `stimulus`, `query_c1`, `c1_contribution`, `query_c2`, `c2_contribution`, `query_comp`, `comp`.
  - `item-set.csv`: Stimulus inventory. One row per unique compound, with columns: `stimulus`, `constituent_1`, `constituent_2`, `list_id`.
- `processed_data/exp1.csv`: Cleaned trial-level data in long format. One row per participant × stimulus observation, with columns: `participant_id`, `trial_id`, `stimulus`, `constituent_1`, `constituent_2`, `constituent_1_contribution`, `constituent_2_contribution`, `predictability`.
- `preprocess_data.py`: Script to process raw data into long format
- `generate_prompts.py`: Script to generate LLM prompts (splits each participant's trials into 3 segments)
- `prompts.jsonl.zip`: Zipped JSONL file with 60 prompt segments (20 participants × 3 segments each)
- `CODEBOOK.csv`: Variable descriptions
