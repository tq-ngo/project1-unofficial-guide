# Acceptance criteria — The Unofficial Guide

Five criteria that say what "working" means for this system, written in unit 1
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. _"Retrieval works"_ is an opinion. _"For at
least 4 of my 5 test questions, the top results include a chunk containing the
answer"_ is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter or looser one. A reason that says something about your corpus or your
pipeline earns credit; _"80% seemed reasonable"_ does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

---

## 1. Retrieved chunks contain the answer

For at least 4 of my 5 test questions, the retrieved chunks include one that
contains the answer.

**Why this target:**

<!-- e.g. "One of my questions is about a topic only two documents mention, so
     I expect that one to be hard." -->

4 of 5 rather than 5 of 5 because my health-center question ("Does the student health center require an appointment for urgent care?") retrieves at a best distance of 0.4798, which is close to the gate cutoff, since only one document (`health_center.txt`) covers that topic, and the phrasing "urgent care" doesn't appear in the text. That one is the likeliest miss. The other four questions each have a dedicated document whose title nearly matches the query, so 4 of 5 is realistic without being trivially easy.

---

## 2. Every answer names a source

Every answer the system produces names at least one source document.

**Why this target:**

<!-- Why all five and not four? What about your setup makes that achievable —
     or what would have to go wrong for it not to be? -->

All five rather than four because `build_prompt` in `generate.py` tags every chunk with `[from filename.txt]` and the `GROUNDING_INSTRUCTION` explicitly tells the model to "name the document your answer came from." The only way an answer could miss a source is if the model ignores the system instruction entirely, which would be a generation-stage bug worth catching at 5/5 rather than allowing silently at 4/5.

---

## 3. The relevance gate stops out-of-corpus questions

When I ask a question my documents clearly don't cover, the relevance gate
stops it and the system returns "I don't have enough information about that" —
in at least 4 of 5 tries.

<!-- The five questions are the ones in `OUT_OF_SCOPE` at the bottom of
     `questions.py`, and `run_eval.py` puts them through the gate and writes
     what happened into your run log. Swap them for your own if you'd rather —
     just keep five of them, or the "4 of 5" above has nothing to be 4 of. -->

**Why this target:**

<!-- What did your distances look like when you set the cutoff in Milestone 4?
     Was there a clean gap, or did the two groups overlap? -->

My in-corpus distances top out at 0.4798 and my out-of-scope distances start at 0.8246, giving a clean gap of 0.34 with the cutoff at 0.58. Because the gap is wide, all five out-of-scope questions should be refused, so 4 of 5 is conservative. I kept it at 4 rather than 5 in case a future out-of-scope question happens to share vocabulary with campus documents (e.g., "ibuprofen" is the closest at 0.8442, still well above 0.58, but a medical question phrased around "student health" could land closer).

---

## 4. Chunk Sizing

<!-- YOU WRITE THIS ONE.

     How would you know if your chunks were the right size? Name something
     countable or observable.

     Examples of the right shape — don't copy these, they should come from
     what you actually saw in Milestone 3:
       - "At least 4 of 5 sampled chunks read as a complete thought, with no
          sentence cut in half at either end."
       - "No chunk is shorter than 200 characters, since anything below that
          in my corpus turned out to be a heading with no content under it." -->

At least 95% of chunks in the index are between 80 and 420 characters long. No chunk is shorter than 80 characters, since anything below that in the `campus_life` corpus turned out to be a title line or leftover fragment with no answerable content.

**Why this target:**

The `campus_life` documents average about 300 characters each — short, self-contained posts. My `config.py` sets `CHUNK_SIZE = 380` and `MIN_CHUNK_SIZE = 80`, so the chunker targets that range in character counts. The 80-character floor matches `MIN_CHUNK_SIZE` and catches fragments like bare headings ("Noise levels in Innisfree Hall" is 31 characters) that would produce meaningless embeddings. The 420-character ceiling (chunk_size + a small margin for the overlap merge) ensures no chunk grows so large that it mixes two separate topics — which matters because most campus_life posts cover exactly one topic each.

---

## 5. Answer Conciseness

<!-- YOU WRITE THIS ONE TOO.

     Pick something you actually care about getting right. It could be about
     speed, about refusals, about a particular kind of question your corpus
     handles badly, about source attribution being correct rather than merely
     present — anything, as long as it names a number or an observable
     outcome. -->

For all 5 test questions, the generated response is no longer than 60 words and names at least one specific detail (a number, a date, or a name) that appears verbatim in one of the retrieved chunks.

**Why this target:**

The `campus_life` posts are short factual blurbs — most answers live in a single sentence containing a concrete detail ("end of the second week," "$30 of printing," "8am to 11am"). A 60-word cap is checkable by running `len(answer.split())` and ensures the model stays brief rather than padding with its own knowledge. Requiring a verbatim detail from the chunks is checkable by string search (`detail in chunk.text`) and catches answers where the model paraphrases so loosely that it invents a different number or date.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 2 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 1. Retrieved chunks contain the answer

         For at least 4 of my 5 test questions, the retrieved chunks include
         one that contains the answer.

         **Why this target:** ...

         > **Revised in unit 2:** For at least 4 of 5 questions, the top three
         > results contain the answer.
         >
         > **Why revised:** I couldn't judge "the chunks include one that
         > contains the answer" the same way twice — I scored two questions
         > differently on Monday than on Wednesday. The new version is
         > something I can actually check.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "I said 4 of 5 but got 2 of 5, so 2 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.

     The whole reason the originals stay visible is so someone can see what you
     said before you knew the answer.
     ───────────────────────────────────────────────────────────────────────── -->
