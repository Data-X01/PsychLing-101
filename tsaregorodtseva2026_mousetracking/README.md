# Mouse-tracking dataset on spatial associations in language processing
Preprint: Tsaregorodtseva, Oksana and Rinaldi, Luca and Marelli, Marco, Systematic Spatial Association Effects Can Arise from Language Experience (February 02, 2026). Available at SSRN: https://ssrn.com/abstract=5658577 or http://dx.doi.org/10.2139/ssrn.5658577

All scripts and data generated for the experiment are available in the Open Science Framework (OSF) at: https://osf.io/ahbd3/

## Overview

This dataset contains trial-level behavioral data from a mouse-tracking experiment investigating how linguistic experience can give rise to systematic spatial associations.

Participants were presented with words and asked to classify them as abstract or concrete by dragging each word to one of two response areas (top vs. bottom of the screen). Response mappings between semantic categories and spatial locations varied across blocks, allowing us to examine how spatial associations emerge and adapt over time.

The dataset includes:
- trial-level responses (assigned vs. actual response)
- timing measures (movement initiation and completion times)
- stimulus information
- participant demographics
- experimental structure (phases, blocks, and instruction mappings)

## Experimental design

Participants performed a classification task in which they decided whether a word referred to an abstract or a concrete concept.

- Responses were made by dragging words to the top or bottom of the screen.
- The mapping between semantic categories (abstract/concrete) and spatial locations (top/bottom) varied across blocks.
- The experiment consisted of:
  - initial training blocks with feedback
  - main experimental blocks without feedback
  - a change in response mapping followed by retraining
  - additional main blocks under the new mapping

## Data structure

The dataset is organized at the trial level, with each row corresponding to a single trial.

Key variables include:
- `condition`: assigned correct response location (top/bottom)
- `response`: actual response location
- `response_category`: inferred semantic judgment (abstract/concrete)
- `instruction_mapping`: mapping rule active during the trial
- `start_rt`, `end_rt`: movement timing measures

See `CODEBOOK.csv` for full variable descriptions.

## Notes on preprocessing

The data were originally collected using jsPsych and subsequently cleaned and standardized for use within the PsychLing-101 framework.

Preprocessing steps included:
- removal of non-experimental trials (instructions, device checks, etc.)
- standardization of variable names
- reconstruction of semantic responses from motor responses and instruction mappings
- preservation of both assigned and actual responses

## Availability

The full dataset, experimental materials, and analysis scripts are publicly available in an external repository.


## PsychLing-101 formatting

This dataset has been reformatted to comply with the PsychLing-101 data standard, including:
- standardized trial-level CSV files
- participant-level prompt generation for language model evaluation

## License

To be specified upon publication.
