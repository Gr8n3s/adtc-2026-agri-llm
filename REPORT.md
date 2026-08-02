# Technical Report — AgriPadi

**Team ID:** TBD-register-on-adtf-portal
**Domain:** agriculture
**Model:** Llama-3.2-3B-Instruct-Q4_K_M

---

## Problem

Farmers and extension officers in Nigeria (and West Africa more broadly) need help with crop and livestock problems all the time — pest and disease symptoms, basic husbandry, when and where to sell. Extension officers are stretched thin, and cloud AI tools assume things a lot of rural areas don't have: steady electricity, fiber internet, a card to pay per API call. I wanted something that just works on a cheap laptop with none of that. AgriPadi is that: ask it a farming question in plain language, get an answer, no connection required after the model is downloaded once.

---

## Design Decisions

I went with **Llama 3.2 3B Instruct** rather than the 1B version because it follows multi-part diagnostic questions ("my leaves are yellow AND curling AND it's rainy season") noticeably better. I stayed away from bigger 7B-class models because a Q4_K_M quant of those barely fits the 7GB RAM ceiling once you add context and any retrieval index — 3B at Q4_K_M (~2GB) leaves real headroom.

**Quantization:** Q4_K_M — the usual sweet spot. It keeps the embedding/output layers at higher precision than the rest of the network, which seems to matter for getting facts right rather than just sounding fluent.

**Retrieval:** I'm using a small offline corpus of public agricultural extension material (IITA, FAO, RAB), searched with plain SQLite full-text search instead of a neural embedding model. An embedding model is another chunk of RAM I don't want to spend, and lexical search gets the job done for this kind of content.

**What I considered and didn't use:** Qwen2.5 3B as a backup if Llama 3.2 underperformed on agriculture questions (didn't need it so far). Also looked at a proper embedding-based retriever, but decided the RAM cost wasn't worth it given the budget constraint.

---

## Constraints

- Target hardware: 8GB RAM, integrated GPU only, Ubuntu 22.04 (the ADTC standard laptop profile)
- CPU-only inference via llama.cpp, no GPU
- Has to be 100% offline after the model download — this isn't optional, it's the whole point given the target users
- Peak RAM can't cross 7GB — that's an automatic disqualification per the rules, not just a lower score

---

## Benchmarks

<!-- Phase 0 smoke-test numbers, --skip-accuracy, no RAG/app layer yet. Re-run after Phase 2-3. -->

| Metric | Value |
|---|---|
| Machine | Intel i3-1215U, WSL2 (5.3 GB allocated), Ubuntu 22.04.5 |
| RAM at peak | 3436 MB (3.4 GB) |
| Generation speed | 7.49 tok/s |
| Thermal throttling | None observed (CPU p99 51.7%) |
| Params verified | 3.21B, matches claimed estimate |

These numbers are from an early smoke test (`adtc-profiler run --mode participant --skip-accuracy`) — enough to confirm the pipeline actually works end to end and stays well under the RAM ceiling, but from before the retrieval layer and app UI were built. I'll re-run with accuracy scoring once the agriculture corpus is wired in. Official scores come from the ADTC profiler on their own evaluation machine, not these.
