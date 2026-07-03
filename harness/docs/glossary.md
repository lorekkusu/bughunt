# Glossary

One-line definitions of the terms used in the reports.

| Term | Meaning |
|------|---------|
| **Recall** | Of the planted bugs (12 in `python-basic`), the fraction the tool actually found. |
| **Precision** | Of the issues the tool reported, the fraction that were real (higher = fewer false alarms). |
| **False positive (FP)** | The tool flagged safe/correct code as a bug — i.e. it stepped on one of the planted "noise" items. |
| **Bonus** | A genuine bug the tool found that is *not* in our planted list (an unplanned extra catch). |
| **n/m stability** | Found in n of m runs. ✅ = every run · ⚠️ = some runs · ❌ = never. Captures run-to-run variance. |
| **Effort** | How hard the model "thinks" (low → max). Higher = slower and more expensive. |
| **Cost (API-equivalent)** | What this run's tokens *would* cost on the API — **not** your actual subscription/plan spend. |
| **Speed** | Wall-clock seconds for one review. |
| **Judge** | An LLM (Claude opus) that scores "tool output vs answer key" automatically. |
| **Planted bug** | A deliberately introduced defect at a known location (12 in `python-basic`). |
| **Noise / red herring** | Code written to *look* suspicious but that is actually safe — used to measure false positives. |
| **prompt_id** | Which review prompt ran: `standard-v1` for automated tools; `native` = the tool used its own prompt. |
| **code_hash** | Fingerprint of the reviewed project's source — decides whether code changed and a re-run is needed. |
| **manual** | A human-triggered tool (e.g. Cursor Bugbot) scored via `bench judge`; cost/speed/tokens are not captured. |

See `../REFERENCES.md` for where each parameter/price/flag comes from.
