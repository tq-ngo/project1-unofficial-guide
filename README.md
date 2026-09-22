# The Unofficial Guide

**Quang Ngo - `campus_life` corpus**

> **This file is your submission.** Fill it in as you go — most sections get
> written during the milestone that produces them, not at the end.
>
> How the starter works, and every command you'll need, is in `RUNNING.md`.
> Leave that file alone.
>
> **Paste everything as text.** No screenshots, no video. A typed table gets
> full credit; a picture of the same table gets none.
>
> Delete these instruction blocks as you replace them. The `<!-- -->` comments
> are notes to you and don't show up when the page renders — you can leave them
> or remove them.

---

# Unit 1

## What This Does

<!-- Three or four sentences. Which corpus you picked, and the kinds of
     questions your system answers. Write it for someone who has never seen
     this repo.

     Milestone 5. -->

A RAG system built on the `campus_life` corpus - 88 short posts covering housing, dining, course reviews, administrative deadlines, and campus services at a university. Ask a question in English and the system finds relevant passages, checks whether they're close enough to actually answer from, and then sends them to Gemini with strict grounding instructions so the answer cites its source document. If nothing in the corpus is relevant, the system refuses rather than guessing. It handles questions like "When is the add/drop deadline?" or "What food does Verrill Street Grill serve?" - practical campus logistics where the answer lives in one or two specific documents.

## Chunking Strategy

**Chunk size:** 380 characters &nbsp;|&nbsp; **Overlap:** 70 characters &nbsp;|&nbsp; **Minimum chunk:** 80 characters

The `campus_life` documents are short, self-contained posts averaging about 300 characters each — most are a title line followed by two or three sentences covering a single topic (one dining hall, one admin deadline, one housing review). The starter's 800-character window never split anything because almost no post is that long, which means each post was already one chunk. After reading the documents, I chose 380 characters because it keeps most posts as a single chunk (they're already below 380) while splitting the handful of longer ones (like `housing_old_brewhouse.txt` at 554 characters or `housing_innisfree_hall.txt` at 519 characters) into pieces that still contain complete sentences. The sentence-boundary splitter avoids mid-sentence cuts, and the 70-character overlap carries about one sentence of context into the next chunk so no thought is orphaned at a boundary. The 80-character minimum merges tiny trailing fragments back into the previous chunk — anything under 80 characters in this corpus was just a heading with no content worth embedding on its own.

<!-- What about YOUR documents made you pick these numbers? Short posts and
     long sectioned guides don't want the same chunking, and "800 seemed
     reasonable" earns nothing. Point at something you noticed when you read
     the documents in Milestone 1.

     If you changed your mind partway through, say so and say why. That's worth
     more than pretending you got it right first time.

     Milestone 3. -->

## Sample Chunks

<!-- Five chunks, pasted as text. Label each one and name the file it came from
     AND the function that produced it — the grader checks your code against
     what you claim here.

     `python app.py chunks -n 5` prints all three for you. Copy them straight
     across.

     Milestone 3. -->

**Chunk 1** — source: `admin_add_drop_deadline.txt` — produced by: `chunker.py::split_documents`

```
On the add/drop deadline

You can add a course through the end of the second week. Dropping is a longer window — through the end of week six — but a drop after week two shows as a W on your transcript. Nothing anywhere on the registrar's site says this plainly, and students find out from each other.
```

**Chunk 2** — source: `course_biol_160_workload.txt` — produced by: `chunker.py::split_documents`

```
Workload for BIOL 160 Cell Biology

People keep asking so: 9 to 11 hours a week, the heaviest first-year course by reputation. That's real time, not optimistic time.

It's front-loaded — the first month is heavier than the rest, partly because you're learning the format.
```

**Chunk 3** — source: `course_math_220_exams.txt` — produced by: `chunker.py::split_documents`

```
MATH 220 Linear Algebra — assessment

Two midterms and a cumulative final. Curved to a b- median.

The problem sets are the course; the lectures make sense afterwards rather than during.
```

**Chunk 4** — source: `dining_the_ridgeway_cafe.txt` — produced by: `chunker.py::split_documents`

```
The Ridgeway Café

Second-year here. Wait times: 10 to 15 minutes at 12:30, none after 2:00. The thing worth going for is the onlyplace on campus with real espresso. The thing to know is that seating is tight; about 40 seats for a building of 900.

Hours are 7:00am to 4:00pm weekdays only. Costs declining balance only, no meal swipes.
```

**Chunk 5** — source: `housing_innisfree_hall_noise.txt` — produced by: `chunker.py::split_documents`

```
Noise levels in Innisfree Hall

Asked about this a lot so writing it down. Moderate; the building is l-shaped and the short wing is much quieter.

If you're someone who needs quiet to work, the library is open until 2am during term and that's what most people in this building end up doing.
```

## Sample Answer

<!-- One complete question and answer, pasted as text, with the source line
     visible. Milestone 4. -->

**Question:** When is the deadline to add or drop a course without a W on your transcript?

**Answer:**

```
The deadline to add a course is the end of the second week, which is also the deadline to drop a course without receiving a W on your transcript (since a drop after week two shows as a W).

Source: admin_add_drop_deadline.txt
```

**My relevance cutoff:** `0.58`

<!-- The number you set in config.py, and how you got there.

     You ran five questions your corpus covers and the five in OUT_OF_SCOPE
     that it clearly doesn't, and wrote down the best distance for each. What
     did those two groups look like? Where was the gap? Put the actual numbers
     here — the table below wants all ten rows.

     Milestone 4. -->

The in-corpus group topped out at 0.4798 and the out-of-scope group bottomed out at 0.8246, a gap of about 0.34. I set the cutoff at 0.58, which is in the middle of that gap. This means the system won't refuse any of the five test questions and will refuse all five out-of-scope questions.

| Question                                                                     | In corpus? | Best distance |
| ---------------------------------------------------------------------------- | ---------- | ------------- |
| When is the deadline to add or drop a course without a W on your transcript? | Yes        | 0.1550        |
| What are the closing hours for the main library on weekend nights?           | Yes        | 0.3627        |
| How much printing credit do undergraduate students receive each semester?    | Yes        | 0.4029        |
| What type of food is served at Verrill Street Grill?                         | Yes        | 0.4096        |
| Does the student health center require an appointment for urgent care?       | Yes        | 0.4798        |
| What is the capital of Mongolia?                                             | No         | 0.8246        |
| What is the recommended dosage of ibuprofen for a headache?                  | No         | 0.8442        |
| Who won the 1994 World Cup?                                                  | No         | 0.8859        |
| How do I write a for loop in Rust?                                           | No         | 0.8960        |
| How do I change the oil in a diesel engine?                                  | No         | 0.9340        |

## How I Used AI

**1.** I asked Claude to write a chunker that wouldn't cut mid-sentence, given my notes about campus_life documents being short posts (200–500 characters each) where each post is usually one complete thought. Claude returned a function that split on sentence endings and grouped sentences into chunks, but it didn't handle overlap: it just moved to the next batch of sentences with no shared context between neighboring chunks. I added the overlap logic myself by walking backwards through the current sentences to carry the last ~70 characters of context into the next chunk, and added the MIN_CHUNK_SIZE that merges tiny trailing fragments back into the previous chunk.

**2.** I asked Claude to help me write the 2 custom acceptance criteria in `criteria.md`. It suggested a criterion about "answer accuracy" measured by exact-match against expected keywords, which wouldn't work because the model paraphrases freely. I rewrote criterion 4 to be about chunk sizing and criterion 5 to be about answer conciseness, which I chose because the campus_life documents are short factual posts and long answers would signal the model is hallucinating.

<!-- ── Stretch features ─────────────────────────────────────────────────────
     Doing one? Say so here BEFORE you start. A feature this README never
     claims earns nothing.
     ───────────────────────────────────────────────────────────────────────── -->

---

# Unit 2

<!-- These sections get ADDED to what's already above. Don't delete or rewrite
     unit 1 — the point is that someone can see what you said before you knew
     how it went. -->

## Run Log — Before

<!-- Your five criteria, three runs each. `python run_eval.py --label before`
     runs the questions, puts the OUT_OF_SCOPE ones through the gate, and
     writes it all into results/ for you. Targets come from criteria.md; the
     verdict column is your call.

     Criterion 3 is measured in one deterministic pass rather than three, so
     the same number goes in all three run columns. That's correct, not lazy.

     Milestone 1. -->

| Criterion                              | Target | Run 1 | Run 2 | Run 3 | Verdict |
| -------------------------------------- | ------ | ----- | ----- | ----- | ------- |
| 1. Retrieved chunk contains the answer | 4 of 5 |       |       |       |         |
| 2. Every answer names a source         | 5 of 5 |       |       |       |         |
| 3. Gate stops out-of-corpus questions  | 4 of 5 |       |       |       |         |
| 4.                                     |        |       |       |       |         |
| 5.                                     |        |       |       |       |         |

<!-- Underneath, paste the REAL output for each criterion from one of your
     runs — the actual text your system produced, not a description of it.
     Name the file and function that produced it. -->

## Verdicts

<!-- MET or MISSED for each of the five, against the target you wrote last
     unit — not a new one. Plus a sentence on how you decided. That sentence
     matters most where it was close.

     If your target said 4 of 5 and your runs came out 4, 3, 4, that's a MISS.
     The target has to hold, not show up occasionally.

     Milestone 2. -->

| #   | Criterion | Verdict | How I decided |
| --- | --------- | ------- | ------------- |
| 1   |           |         |               |
| 2   |           |         |               |
| 3   |           |         |               |
| 4   |           |         |               |
| 5   |           |         |               |

## Diagnoses

<!-- For each miss: which stage caused it, and how. The stage alone isn't
     enough — you need the mechanism.

     Not a diagnosis: "Question 3 didn't work."
     A diagnosis:     "Question 3 asks about laundry costs. The answer is in
                       one sentence that got split across two chunks, so
                       neither chunk on its own contains it."

     The five stages: loading → chunking → embedding → retrieval → generation.

     Look for a pattern. If three misses all ask about numbers, that's one
     problem, not three.

     Missed nothing? Say so, then say honestly whether your targets were set
     low, and which one you'd tighten and to what.

     Milestone 3. -->

## The Improvement

**What I changed:**

**Why I picked it:**

<!-- Connect it to a specific diagnosis above in one sentence. If you can't,
     you picked a fix because it sounded impressive. -->

### Run Log — After

<!-- Same format, same five criteria, three runs each.
     `python run_eval.py --label after` -->

| Criterion                              | Target | Run 1 | Run 2 | Run 3 | Verdict |
| -------------------------------------- | ------ | ----- | ----- | ----- | ------- |
| 1. Retrieved chunk contains the answer | 4 of 5 |       |       |       |         |
| 2. Every answer names a source         | 5 of 5 |       |       |       |         |
| 3. Gate stops out-of-corpus questions  | 4 of 5 |       |       |       |         |
| 4.                                     |        |       |       |       |         |
| 5.                                     |        |       |       |       |         |

**Did it help?**

<!-- Say plainly whether it did, and how you know. If it made things worse,
     say that — a change that backfired, honestly reported, earns full credit
     and is more interesting than one that worked. What matters is that you can
     tell.

     Milestone 4. -->

## What's Still Broken

<!-- For each criterion still missed after your fix: what you'd do about it,
     and why you stopped where you did.

     "I ran out of time" is fine if it's true. Pretending nothing is left is
     not.

     Milestone 5. -->

## What I'd Do Differently

<!-- Knowing what you know now — which of your five criteria would you write
     differently, and why?

     Milestone 5. -->
