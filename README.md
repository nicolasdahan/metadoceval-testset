# MetaDocEval: A Document-Level Contrastive Test Set for MT Metric Evaluation

This repository releases the document-level contrastive test set introduced in *MetaDocEval: A Contrastive Framework for Evaluating Machine Translation Metrics at the Document-Level* (Dahan, Bawden, Yvon — EAMT 2026). The test set lets practitioners diagnose whether MT evaluation metrics are sensitive to discourse-level errors that span multiple sentences, by pairing original system outputs with carefully perturbed counterparts that degrade document-level coherence while preserving sentence-level fluency.

The data covers three language pairs (en→fr, en→es, en→de), two MT systems (Aya23 and Gemini-1.5 Pro), and nine perturbation types (five lexical, four structural). Source documents are drawn from the WMT24++ test sets ([Deutsch et al., 2025](https://arxiv.org/abs/2502.12404)).


## Citation

If you use this test set, please cite:

```bibtex
@inproceedings{dahan-etal-2026-metadoceval,
    title     = {MetaDocEval: A Contrastive Framework for Evaluating Machine Translation Metrics at the Document-Level},
    author    = {Dahan, Nicolas and Bawden, Rachel and Yvon, Fran\c{c}ois},
    booktitle = {Proceedings of the 26th Annual Conference of the European Association for Machine Translation},
    address   = {Tilburg, Netherlands},
    year      = {2026}
}
```

(BibTeX entry will be updated with venue-final fields and DOI once available.)


## Brief summary

Contrastive test sets are used to test MT metrics on their capacity to rank a correct translation higher than a degraded one. Existing contrastive sets target sentence-level phenomena; this dataset extends the contrastive paradigm to **document-level** phenomena that only become visible across multiple sentences (tense alternation, lexical inconsistency, broken discourse connectives, mis-resolved anaphoric pronouns, sentence reordering or removal, etc.).

For each instance we provide:
- the source segment (`src`),
- the original MT output of the segment (`sys`),
- a perturbed version of that output (`sys_perturbed`) that degrades document-level coherence,
- the human reference (`ref`).

A metric that is sensitive to a perturbation should score `sys` higher than `sys_perturbed` on average. The framework is described in detail in the paper.


## Repository structure

```
MetaDocEval/
├── README.md
├── LICENSE
├── CITATION.cff
├── data/
│   ├── en_fr_aya.json
│   ├── en_fr_gemini.json
│   ├── en_es_aya.json
│   ├── en_es_gemini.json
│   ├── en_de_aya.json
│   └── en_de_gemini.json
└── scripts/
    └── load_data.py
```

There is one JSON file per (language pair × system) combination, named `{lang}_{system}.json`.


## Data format

Each JSON file maps **perturbation type** (top-level key) to a **list of contrastive instances**. The top-level keys are:

| Key | Description | Paper notation |
|---|---|---|
| `tense_consistency` | Tense alternation in past-tense verbs | TENSE |
| `lexical_consistency` | Synonym substitution of repeated content words | LEX |
| `conjunction_substitution` | Near-synonym substitution of discourse connectives | CONJ |
| `pronoun_swap_singular` | Gender swap of singular anaphoric pronouns (French *il*/*elle*; Spanish *él*/*ella*; German *er*/*sie*/*es*) | PRO-sg |
| `pronoun_swap_plural` | Gender swap of plural anaphoric pronouns (French *ils*/*elles*; Spanish *ellos*/*ellas*; not applied to German, whose plural pronoun *sie* is gender-neutral) | PRO-pl |
| `sentence_repetition` | Random duplication of ~20% of sentences | (structural) |
| `sentence_removal` | Random deletion of ~20% of sentences | (structural) |
| `sentence_shuffling` | Random shuffling of ~20% of sentences | (structural) |
| `sentence_splitting` | Quality-preserving heuristic split on inner commas | (structural) |

Each list element is a contrastive **instance** with the following fields:

| Field | Type | Description |
|---|---|---|
| `doc_id` | int | Index of the source document within the corresponding WMT24++ subset |
| `seg_ids` | list[int] | Indices of the segment(s) within the document covered by this contrastive instance |
| `src` | str | English source segment |
| `sys` | str | Original MT output of `src` for this system |
| `sys_perturbed` | str | Perturbed counterpart (same surface format as `sys`) |
| `ref` | str | Human reference translation |
| `Levenshtein` | int | Character-level Levenshtein distance between `sys` and `sys_perturbed` (0 = identical, used as a quality-control signal at filtering time) |

Notes:
- Entries with `sys == sys_perturbed` (`Levenshtein == 0`) are intentional, not artefacts: they correspond to segments of a perturbed document whose own surface text is unchanged (a given perturbation typically affects only a subset of a document's segments). They are required as unperturbed context when scoring under sliding windows of size > 1 (see *Reproducing other window sizes* below) and must be kept to reproduce the paper's main analysis. For a purely segment-level evaluation (window size 1) they carry no signal and can be filtered out.
- Metric scores are not bundled with the test set. Users should score `sys` and `sys_perturbed` with their own metric of choice and aggregate the segment- or window-level scores at the document level, as described in the paper.


## Statistics

Number of **contrastive pairs** (entries with `sys ≠ sys_perturbed`, i.e. `Levenshtein > 0`) per perturbation type and (language pair, system):

| Perturbation | en→fr Aya23 | en→fr Gemini | en→es Aya23 | en→es Gemini | en→de Aya23 | en→de Gemini |
|---|---:|---:|---:|---:|---:|---:|
| tense_consistency | 193 | 119 | 118 | 169 | 138 | 160 |
| lexical_consistency | 150 | 150 | 205 | 195 | 122 | 135 |
| conjunction_substitution | 181 | 167 | 270 | 258 | 311 | 346 |
| pronoun_swap_singular | 9 | 5 | — | — | 2 | 5 |
| pronoun_swap_plural | 19 | 11 | — | 1 | — | — |
| sentence_repetition | 334 | 332 | 320 | 318 | 298 | 327 |
| sentence_removal | 334 | 332 | 320 | 318 | 298 | 327 |
| sentence_shuffling | 220 | 224 | 222 | 216 | 192 | 216 |
| sentence_splitting | 27 | 20 | 16 | 24 | 15 | 16 |
| **total** | **1,467** | **1,360** | **1,471** | **1,499** | **1,376** | **1,532** |

Pronoun perturbations are concentrated on en→fr because the gender-of-anaphoric-pronouns phenomenon is most reliably detectable in French (rich morphology and direct gender-marked pronouns *il / elle / ils / elles*). They are excluded from the main evaluation in the paper due to insufficient instances in en→es and en→de.

Documents have an average length of **11.3 segments** after sentence-level alignment with `bertalign`. Across all 6 (language pair, system) files: **8,705 contrastive pairs** in total, drawn from **54,358 segment-level entries** (the remaining entries have `sys == sys_perturbed` and serve as unperturbed context for sliding-window evaluation — see *Data format* note above and *Reproducing other window sizes* below).


## Usage

The included loader is plain Python (stdlib only):

```python
from scripts.load_data import load, iter_entries

data = load("data/en_fr_aya.json")
for entry in iter_entries(data, perturbation="tense_consistency"):
    src = entry["src"]
    sys, pert = entry["sys"], entry["sys_perturbed"]
    ...
```

Or run the loader as a CLI for a quick summary:

```bash
python3 scripts/load_data.py data/en_fr_aya.json
```


## Reproducing other window sizes

Each contrastive instance corresponds to a **single segment** — the SLIDE(1,1) basic unit of [Raunak et al. (2024)](https://aclanthology.org/2024.naacl-short.18/). To reproduce evaluation under larger sliding windows (SLIDE(3,1), SLIDE(6,1), SLIDE(9,1) as reported in the paper), group entries by `doc_id`, form all overlapping *w*-segment windows over consecutive segments with stride 1, concatenate each window's `sys` (respectively `sys_perturbed`) into a single text, and score the concatenation with the target metric. Window-level scores are then averaged within each document to yield a document-level score. The order of segments within a `doc_id` follows their appearance in the original WMT24++ document; the `seg_ids` field of each instance gives that index.


## Source data and license

- **Source documents, human references, and Aya23 / Gemini-1.5 Pro system outputs**: redistributed from WMT24++ ([Deutsch et al., 2025](https://arxiv.org/abs/2502.12404)). The two systems we evaluate are part of the publicly released subset of WMT24++ system outputs (accessible via the `EvalSet` API of the `mt-metrics-eval` package).
- **Perturbations**: contributed by this work. They were generated using `gpt-4o-mini` for the LLM-based ones (tense, lexical, conjunction, pronoun) and a SpaCy-based heuristic for sentence splitting.
- **License of this repository**: MIT (see `LICENSE`).

In addition to the MIT license that applies to the perturbations released here, please cite the WMT24++ paper, since the source/reference/system-output text in `src`, `ref` and `sys` originates from that release:

```bibtex
@misc{wmt24pp,
    title         = {{WMT24++: Expanding the Language Coverage of WMT24 to 55 Languages \& Dialects}},
    author        = {Daniel Deutsch and Eleftheria Briakou and Isaac Caswell and Mara Finkelstein and Rebecca Galor and Juraj Juraska and Geza Kovacs and Alison Lui and Ricardo Rei and Jason Riesa and Shruti Rijhwani and Parker Riley and Elizabeth Salesky and Firas Trabelsi and Stephanie Winkler and Biao Zhang and Markus Freitag},
    year          = {2025},
    eprint        = {2502.12404},
    archivePrefix = {arXiv},
    primaryClass  = {cs.CL},
    url           = {https://arxiv.org/abs/2502.12404}
}
```


## Acknowledgments

This work was supported by the French national research agency (ANR) as part of the MaTOS project (grant number ANR-22-CE23-0033). Rachel Bawden was also partly funded by her chair position in the PRAIRIE institute funded by ANR as part of the *Investissements d'avenir* programme under reference ANR19-P3IA-0001.


## Contact

For questions or issues, please contact `nicolas.dahan@inria.fr` or open an issue once this dataset is hosted publicly.
