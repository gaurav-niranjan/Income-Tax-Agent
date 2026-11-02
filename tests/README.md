# Tests: what they check and why

There are 120 tests. They run in about 5 seconds, with no API key, no internet and no model
download.

```bash
uv run pytest -q                     # run everything
uv run pytest tests/test_clean.py -v # run one stage, with test names
uv run pytest -k rerank -v           # run every test with "rerank" in its name
```

## How the tests work (no real PDF, no real AI)

The real PDF is 118 MB, and real AI calls are slow and cost quota. So the tests use small
stand-ins:

- **Real snippets, tiny inputs.** Tests paste in a few real lines from the Act, such as the
  Section 202 tax-slab table from page 244. `make_page()` in [helpers.py](helpers.py) wraps
  them in the real page header and footer, so they look like pages from the PDF.
- **Fake models.** `FakeEmbeddings`, `FakeLLM` and `FakeReranker` stand in for the real
  embedding model, Gemini and the reranker. They give simple, predictable answers.
  `FakeLLM`'s answer always contains "Fake answer".
- **A tiny real index in a temp folder.** pytest's `tmp_path` gives each test an empty folder
  that is deleted afterwards. Many tests build a real search index there from 3 or 4
  sentences, then search it.
- **Trap fakes.** Some fakes exist to prove that something did *not* happen. For example,
  `ExplodingLLM` raises an error if it is called at all.
- **The app without a browser.** Streamlit's `AppTest` runs the real app script. Tests type
  a question and read what appears on the page.

## The map

The app is a pipeline. Each stage has its own test file.

```
PDF pages ─► 1. clean ─► 2. find sections ─► 3. chunk + index ─► 4. search ─► 5. answer ─► 6. app
                                                                                 │
                                                       7. eval tools (score the answers)
```

| Stage | File | Tests |
|---|---|---|
| 1. Cleaning | [test_clean.py](test_clean.py) | 9 |
| 2. Finding sections | [test_sections.py](test_sections.py) | 8 |
| 3. Chunking and the index | [test_chunk_index.py](test_chunk_index.py), [test_structured.py](test_structured.py) | 6 + 10 |
| 4. Search | [test_retrieval.py](test_retrieval.py) | 22 |
| 5. Answering | [test_graph.py](test_graph.py) | 31 |
| 6. The app | [test_app.py](test_app.py), [test_limits.py](test_limits.py) | 13 + 3 |
| 7. Eval tools | [test_metrics.py](test_metrics.py), [test_judge.py](test_judge.py), [test_runs.py](test_runs.py) | 4 + 8 + 6 |

Some counts are bigger than the number of test functions. A test marked
`@pytest.mark.parametrize` runs once per example input, and each run counts as one test.

Below, each test is listed with **the bug it would catch**.

---

## 1. Cleaning ([test_clean.py](test_clean.py))

**What this stage does:** removes junk from each PDF page before anything else sees it.

**Why it matters:** the PDF has a header and footer on every page. It also has footnotes that
quote the **old, repealed law**. If those footnotes stay in, the app may answer with law that
no longer applies.

- `test_strips_header_footer_and_page_counter`: "Income Tax Department", the download date
  and "Page 1 of 1" would end up in the search text.
- `test_removes_footnote_with_old_text_and_its_omitted_marker`: the old wording of a deleted
  rule would stay in, and the app could quote it as current law. The deleted item must show
  as `[omitted]`.
- `test_ablation_flag_keeps_footnotes`: the switch that keeps footnotes (used to measure how
  much cleaning helps) would stop working.
- `test_inserted_text_keeps_words_but_loses_marker`: `85[(7) ...]` marks text added by an
  amendment. The marker must go but the words must stay. A bug here deletes real law.
- `test_marker_matching_handles_nested_brackets_and_page_breaks`: a marker whose text
  contains its own brackets, or runs onto the next page, would be cut in the wrong place.
- `test_one_footnote_can_have_several_markers`: when one amendment touched three places, only
  the first place would be cleaned.
- `test_unknown_marker_numbers_are_left_alone`: real references like `section 2(77)[a]` would
  be mistaken for markers and damaged.
- `test_omitted_section_line_is_not_mistaken_for_a_footnote`: the line `447. [***]` (a whole
  section was deleted) would be removed as if it were a footnote.
- `test_table_columns_are_kept_but_padding_is_shrunk`: table rows would lose their column
  gaps, or keep 30 spaces of padding that wastes chunk space.

## 2. Finding sections ([test_sections.py](test_sections.py))

**What this stage does:** works out which section (e.g. "Section 202") each piece of text
belongs to. Citations and the eval both depend on this.

**Why it matters:** the PDF is messy. Numbers are spaced oddly (`3 .`, `2.(1)`). Table rows
also start with numbers (`1.`, `3.`). At the end of the Act, the **Schedules** (appendix
tables) number their items 1, 2, 3 again.

- `test_detects_sections_with_odd_spacing_and_skips_table_rows`: `3 .` would be missed, or a
  table row `3.` would be mistaken for Section 3.
- `test_section_without_text_after_number`: a deleted section, which is just `447.` after
  cleaning, would be skipped.
- `test_schedule_items_are_not_sections`: item 3 of Schedule I would be treated as Section 3.
- `test_schedule_title_skips_part_heading`: a Schedule would get "PART A" as its title instead
  of its real name.
- `test_sections_record_chapter_part_and_sub_part`: the Act is grouped into chapters and
  parts. Sections would get the wrong chapter or part, or keep an old part after a new
  chapter starts.
- `test_headings_belong_to_the_section_they_introduce`: a chapter heading would be glued to
  the end of the section *before* it.
- `test_schedule_parts_are_not_chapter_parts`: "A.—Life insurance" inside a Schedule would be
  taken as a part of the Act.
- `test_lookup_by_offset_lists_both_sections_at_a_boundary`: text that runs from one section
  into the next would report only one section, or the wrong pages.

## 3. Chunking and the index

**What this stage does:** cuts the Act into **chunks** (pieces of about 1,000 to 1,500
characters) and stores them in a search **index** on disk.

**Why it matters:** every chunk must record which sections it covers. The eval checks search
results by section number.

### Fixed-size chunks ([test_chunk_index.py](test_chunk_index.py))

The baseline chunker: cut every N characters, with some overlap.

- `test_chunks_cover_text_with_overlap_and_whole_words`: chunks would cut words in half, skip
  text, be too long, or stop overlapping.
- `test_chunk_crossing_a_section_boundary_lists_both`: a chunk with the end of Section 1 and
  the start of Section 2 would list only one of them. The eval would then miscount hits.
- `test_header_chunker_keeps_text_and_adds_search_prefix`: the "header" option adds
  "Section 2: Definitions." to the *searched* text. This catches the header leaking into the
  text the AI reads, or going missing.
- `test_breadcrumb_header_starts_with_chapter_and_part`: the longer header ("Chapter II >
  Part A > Section 1") would be built wrongly.
- `test_short_model_name`: index folders are named from the model, e.g.
  `fixed-1000-150__bge-base`. A change here would rename them, so the app and the eval would
  no longer find the indexes in the repo.
- `test_build_and_load_index`: the index folder (chunks, database, `manifest.json`) would not
  save, or would load back different.

### Structured chunks ([test_structured.py](test_structured.py))

The smarter chunker: it splits by sub-section, definition and table row, never across
sections.

- `test_subsections_skip_wrapped_references_and_allow_gaps`: a line starting "(1) was
  received." (the end of a sentence) would be mistaken for sub-section (1). A gap where (4)
  was deleted would confuse it.
- `test_table_rows_and_the_subsection_after_them`: the tax-slab rows would not each be found,
  or sub-section (2) after the table would be missed.
- `test_paren_numbered_table_rows_are_not_subsections`: table rows numbered `(1)`, `(2)` would
  be mistaken for sub-sections.
- `test_schedule_rows_with_letter_suffix_and_notes`: Schedule row `2A` or the note under a
  table would be lost.
- `test_definitions_stand_alone_and_opening_text_joins_the_first`: Section 2 is a long list of
  definitions. Each must be its own chunk, labelled e.g. "Section 2(10)".
- `test_small_section_is_one_chunk_and_chunks_never_cross_sections`: a chunk would mix two
  sections, or some text would end up in no chunk (or in two).
- `test_breadcrumb_prefix_keeps_label_and_text`: the breadcrumb option would change the text
  or labels instead of only the searched prefix.
- `test_split_table_repeats_its_header`: when a long table is split, the later part would lose
  its column names. "5. From Rs. 1600001 to Rs. 2000000 20%" means little without "Total
  income | Rate of tax".
- `test_small_tail_merges_into_the_chunk_before`: tiny leftover chunks (a few words) would be
  made. They match searches badly.
- `test_build_structured_index`: the structured index would not build, or its manifest would
  be wrong.

## 4. Search ([test_retrieval.py](test_retrieval.py))

**What this stage does:** finds the chunks that best match a question. There are three
modes:

- **dense**: compares meanings, using embeddings.
- **BM25**: matches exact words and numbers.
- **hybrid**: runs both and merges the two ranked lists with **RRF** (Reciprocal Rank
  Fusion). A chunk ranked well by both lists beats one ranked first by only one list.

A **reranker** can then re-score the top results with a slower, more careful model.

- `test_tokenize_keeps_numbers_and_drops_digit_commas`: "Rs. 25,000" would not match "25000".
  Amounts are what people ask about most.
- `test_rrf_rewards_items_ranked_by_both_lists`: the RRF formula would be wrong.
- `test_rrf_lets_agreement_outvote_a_single_top_hit`: documents a known weakness of RRF, using
  a real failed question in miniature. If RRF changes, this shows it.
- `test_best_rank_fusion_keeps_every_lists_top_hit`: the other merge method (used when
  searching with several rewrites of a question) would drop a list's best result.
- `test_bm25_finds_exact_amount`: BM25 would not find a chunk by its exact amount.
- `test_every_mode_returns_ranked_chunks` (runs 3 times: dense, BM25, hybrid): a mode would
  return duplicates, the wrong count, or ranks out of order.
- `test_bm25_searches_the_prefix_but_returns_plain_text`: BM25 would ignore the
  "Section 202: New tax regime" header, or show it to the user.
- `test_retrieve_multi_with_one_query_equals_retrieve`: searching with a list of one query
  would give different results from a plain search.
- `test_retrieve_multi_merges_the_queries`: searching with several queries would drop the
  results of some of them.
- `test_retrieve_multi_returns_nothing_when_no_query_matches`: with no match, search would
  return junk, so the app would answer instead of saying "not found". Checked with and
  without the reranker.
- `test_retrieve_multi_uses_the_configured_fusion` (runs twice: best rank, RRF): with the
  reranker off, the results of several queries would be merged with the wrong method.
- `test_retrieve_multi_rejects_unknown_fusion`: a typo in the merge setting would be ignored
  silently instead of raising an error.
- `test_expand_neighbours_adds_same_section_chunks_once`: the "include surrounding text"
  option would add the wrong chunks, or the same chunk twice.
- `test_expand_neighbours_skips_other_sections`: surrounding text would be pulled in from a
  different section.
- `test_rerank_pools_all_queries_and_scores_against_the_question`: the reranker would score
  results against a rewrite instead of the user's real question.
- `test_rerank_adds_half_the_best_rewrite_score`: the scoring rule (question score + half the
  best rewrite score) would change.
- `test_rerank_also_applies_to_a_single_query`: reranking would be skipped when there is only
  one query.
- `test_rerank_can_be_switched_per_request`: the app's "Rerank results" switch would be
  ignored.
- `test_rerank_on_request_loads_a_reranker_when_settings_have_none`: turning rerank on in the
  app would crash when it is off in the settings.

## 5. Answering ([test_graph.py](test_graph.py))

**What this stage does:** the LangGraph pipeline. It rewrites follow-up questions, searches,
then asks Gemini to answer using only the retrieved text, with citations like
`[Section 202]`.

**Why it matters:** this is where the app could make things up, or burn through the free
Gemini quota.

### Reading the AI's text

- `test_parse_citations` (6 example answers): citations like `[Section 202(1)(a)]`,
  `[Sections 202 and 156]` or `[Schedule XV]` would be misread.
- `test_strip_excerpt_refs` (6 real answers): Gemini sometimes writes `[Excerpt 4]`, which
  means nothing to a user. These must be removed, keeping the section citation.
- `test_parse_expansions` (5 examples): the AI's rewritten search queries would be misread.
  For example, a numbered list mark would be kept, or "1.25 lakh" would be taken as a list
  number.

### The pipeline

- `test_graph_answers_with_citations`: a normal question would not produce an answer with
  valid citations.
- `test_graph_skips_llm_when_nothing_is_retrieved`: with no matching text, the app must say
  "I could not find this in the Act" **without calling the AI**. This uses `ExplodingLLM`.
  Calling the AI here invites a made-up answer.
- `test_graph_without_expand_flag_searches_only_the_question`: the "rewrite my question"
  feature would run (and use quota) when it is switched off.
- `test_graph_expansion_finds_what_the_question_alone_misses`: rewrites like "12 lakh" →
  "Rs. 1200000" would not be searched.
- `test_graph_falls_back_to_the_question_when_expansion_fails`: if the rewrite call fails,
  the whole question would fail instead of searching with the original question.
- `test_graph_stops_when_expansion_quota_is_gone`: when the daily quota is used up, the app
  would carry on and fail later in a confusing way.

### Chat memory

- `test_follow_up_is_rewritten_with_the_chat_history`: "and the limit?" would be searched on
  its own (and find nothing useful) instead of with the earlier question. It also checks that
  two visitors don't share chat memory.
- `test_errors_are_not_left_over_from_the_previous_question`: an error message from question
  1 would still show under question 2.
- `test_chat_continues_after_a_failed_question`: one failed question would break the rest of
  the chat.

### The Gemini client

- `test_llm_calls_are_logged_with_tokens_and_cache_hits`: the dev panel's token counts would
  be wrong.
- `test_llm_cache_avoids_second_call`: the same question would call Gemini twice instead of
  using the saved answer. Re-running the eval would waste quota.
- `test_llm_without_cache_calls_every_time`: the app answers with the cache off, so one bad
  answer can't stick for everyone. With this broken, it would serve saved answers anyway (or
  write a cache it shouldn't).
- `test_llm_stops_at_once_on_daily_quota`: the client would keep retrying after the daily
  quota is gone, which is pointless.
- `test_llm_does_not_retry_permanent_errors`: a bad API key would be retried again and again.

## 6. The app

### The page ([test_app.py](test_app.py))

**What it checks:** the real Streamlit app, run without a browser.

- `test_app_shows_disclaimer_and_privacy_note`: the "Not tax advice" and "questions go to
  Gemini" notes would disappear.
- `test_question_gets_answer_with_sources`: asking a question would not show the answer, its
  sources, or citation tags like `§1`.
- `test_focus_an_earlier_answer_but_follow_up_on_the_latest`: clicking "Sources" under an
  older answer (or using the picker) would not show that answer's sources. Or a follow-up
  question would build on the old answer instead of the latest one.
- `test_answer_survives_a_click_while_it_loads`: clicking something while an answer loads
  would make the finished answer vanish.
- `test_no_index_picker_with_one_index`: the index picker would show when there is nothing to
  choose.
- `test_index_picker_switches_index`: choosing another index would not change which index is
  searched.
- `test_visitor_cap_survives_a_page_reload`: a visitor could get around the question limit by
  reloading the page.
- `test_cap_for_all_visitors`: once all visitors together reach the limit, the question box
  would stay open, or the "Please try again later" note would be missing.
- `test_no_cap_in_dev_mode`: the owner's dev mode would still be limited.
- `test_search_toggles_work`: the "Rerank results" and "Rewrite my question" switches would
  crash the app or be ignored.
- `test_follow_up_uses_the_chat_so_far`: the page would not show what a follow-up was
  searched as.
- `test_dev_panel_only_in_dev_mode` (runs twice: on, off): the dev panel (timings, AI calls)
  would show to normal visitors, or be missing in dev mode.

### Question limits ([test_limits.py](test_limits.py))

The free Gemini quota is shared by everyone. These limits stop strangers from using it up.

- `test_visitor_limit_and_window`: the per-visitor limit would not apply, would affect other
  visitors, or would never reset after 24 hours.
- `test_total_limit_across_visitors`: the limit for all visitors together would not apply.
- `test_free_again_in_without_questions`: "try again in ..." would show a wrong wait for a new
  visitor.

## 7. Eval tools

These score the app. If they are wrong, every number in the README is wrong.

### Search scores ([test_metrics.py](test_metrics.py))

- `test_strict_hit_needs_30_percent_of_the_chunk`: a "strict hit" means the expected section
  fills at least 30% of the chunk, not just a passing mention. Catches the rule drifting.
- `test_first_hit_ranks_per_rule`: the rank of the first correct chunk would be found wrongly.
  It also checks that phrase matching ignores extra spaces and line breaks.
- `test_summarize_hit_at_k_and_mrr`: **hit@k** (was a right chunk in the top k?) or **MRR**
  (on average, how high was the first right chunk?) would be calculated wrongly.
- `test_summarize_by_type_has_all_group_and_per_type_counts`: the breakdown by question type
  (table, definition, lakh, ...) would be wrong.

### The AI judge ([test_judge.py](test_judge.py))

A second AI call grades each answer as correct, partial or incorrect.

- `test_parse_verdict_accepts_fenced_json`: the judge's reply, wrapped in a code block, would
  fail to parse.
- `test_parse_verdict_rejects_bad_replies` (3 bad replies): a broken grade (e.g. "mostly"
  instead of "correct") would be accepted silently.
- `test_judge_prompt_states_scope_and_includes_everything`: the judge would not be given the
  question, reference answer, retrieved text or app answer.
- `test_summarize_answers`: correctness, faithfulness or refusal rates would be counted
  wrongly.
- `test_uses_old_law_matches_only_the_repealed_figure`: on the trap questions
  ([eval/traps.jsonl](../eval/traps.jsonl)), an answer counts as "old law" if it states a figure
  that only the repealed text has. The check would miss "5%", or wrongly flag "25%" or
  "Rs. 500000" as the old "5%" or "Rs. 500".
- `test_summarize_answers_counts_old_law_over_trap_rows_judged_or_not`: the old-law rate would
  count non-trap questions, or skip answers the judge failed to grade (the check needs no
  judge).

### Saving eval runs ([test_runs.py](test_runs.py))

Each eval run is saved in a folder named by its settings, so runs can be compared.

- `test_hash_ignores_bookkeeping_but_not_settings`: two runs with the same settings would get
  different IDs (or different settings the same ID).
- `test_stamp_puts_run_metadata_first`: run details (ID, date, note) would be missing or out
  of order.
- `test_same_config_same_day_replaces_the_run`: re-running the same eval would pile up
  duplicate runs instead of replacing the old one.
- `test_readme_shows_only_key_runs`: the results table would show the wrong runs or wrong
  numbers.
- `test_setup_columns_name_the_reranker_rule`: the results table would describe the reranker
  setup wrongly.
- `test_config_diff_compares_nested_keys`: `compare.py diff` would miss a changed setting.

---

## When a test fails

1. Read the name. It says which promise broke.
2. The file tells you the stage. Look at the code for that stage first.
3. Run only that test: `uv run pytest tests/test_clean.py::test_name -v`.
4. If you changed the behaviour on purpose (e.g. new UI text), update the test. Otherwise,
   fix the code.
