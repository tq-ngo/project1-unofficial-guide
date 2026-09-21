"""
Stage 2 of the pipeline: splitting documents into chunks.

⚠️ THIS IS THE FILE YOU CHANGE IN MILESTONE 3.

`split_documents` below is deliberately plain. It cuts every document into
fixed-size pieces with a fixed overlap and pays no attention to where sentences
or paragraphs end. It works, and it is not good.

On a corpus of short posts it may not cut anything at all: `campus_life` comes
out as 88 documents and 88 chunks, because almost nothing in it reaches 800
characters. That is the baseline, not a bug — Milestone 3 is where you decide
whether one post should stay one chunk.

Your job in Milestone 3 is to replace the *body* of `split_documents` with a
strategy that fits the documents you actually read in Milestone 1. Keep the
name and the shape of what it returns — the rest of the pipeline calls it, and
your README has to name the function that produced your chunks.

If you get stuck for 30 minutes, `fallback_split` is the original. Switch back
to it, write down what you saw, and move on. That's a real observation about
your pipeline, not giving up.
"""

from dataclasses import dataclass
import re

import config
from ingest import Document


@dataclass
class Chunk:
    """One piece of one document."""

    text: str
    source: str        # which file it came from
    index: int         # which chunk within that file, starting at 0
    produced_by: str   # the function that made it — cite this in your README

    @property
    def label(self) -> str:
        return f"{self.source}#{self.index}"


def fallback_split(
    documents: list[Document],
    chunk_size: int | None = None,
    overlap: int | None = None,
) -> list[Chunk]:
    """
    The starter's original chunker. Fixed-size character windows with overlap.

    Keep this function. Milestone 3's stop rule points back at it, and having
    something to compare your own strategy against is useful in unit 2.
    """
    chunk_size = chunk_size or config.CHUNK_SIZE
    overlap = overlap or config.CHUNK_OVERLAP

    if overlap >= chunk_size:
        raise ValueError("overlap has to be smaller than chunk_size")

    chunks: list[Chunk] = []
    for doc in documents:
        start = 0
        index = 0
        while start < len(doc.text):
            piece = doc.text[start : start + chunk_size].strip()
            if piece:
                chunks.append(
                    Chunk(
                        text=piece,
                        source=doc.source,
                        index=index,
                        produced_by="chunker.py::fallback_split",
                    )
                )
                index += 1
            start += chunk_size - overlap

    return chunks

def _split_into_sentences(text: str) -> list[str]:
    """Split raw text into clean, standalone sentences preserving terminal punctuation."""
    raw_sentences = re.split(r"(?<=[.!?])\s+|\n{2,}", text.strip())
    sentences = [s.strip() for s in raw_sentences if s.strip()]
    return sentences if sentences else [text.strip()]


def _chunk_text_semantically(
    text: str,
    chunk_size: int,
    overlap_size: int,
    min_chunk_size: int,
) -> list[str]:
    """
    Group sentences into self-contained semantic units based on chunk size and overlap.

    Ensures no mid-sentence cuts and eliminates tiny trailing fragments.
    """
    cleaned = text.strip()
    if not cleaned:
        return []

    if len(cleaned) <= chunk_size + 40:
        return [cleaned]

    sentences = _split_into_sentences(cleaned)
    chunks: list[str] = []
    current_sentences: list[str] = []
    current_len = 0

    for sentence in sentences:
        sentence_len = len(sentence)

        if current_sentences and (current_len + 1 + sentence_len > chunk_size):
            chunk_str = " ".join(current_sentences).strip()
            chunks.append(chunk_str)

            overlap_sentences: list[str] = []
            acc_overlap = 0
            for s in reversed(current_sentences):
                if acc_overlap + len(s) <= overlap_size or not overlap_sentences:
                    overlap_sentences.insert(0, s)
                    acc_overlap += len(s) + 1
                else:
                    break

            current_sentences = list(overlap_sentences)
            current_len = sum(len(s) for s in current_sentences) + max(
                0, len(current_sentences) - 1
            )

        current_sentences.append(sentence)
        current_len += sentence_len + (1 if len(current_sentences) > 1 else 0)

    if current_sentences:
        final_chunk = " ".join(current_sentences).strip()
        if chunks and len(final_chunk) < min_chunk_size:
            chunks[-1] = (chunks[-1] + " " + final_chunk).strip()
        else:
            chunks.append(final_chunk)

    return chunks


def split_documents(documents: list[Document]) -> list[Chunk]:
    """
    Split documents into chunks. ⚠️ REPLACE THE BODY OF THIS IN MILESTONE 3.

    Right now it just calls the fallback. That is the plain, generic behaviour
    the brief is talking about.

    When you write your own strategy, set `produced_by` to
    "chunker.py::split_documents" so your README's Sample Chunks section names
    the right function. `app.py chunks` prints that string for you.

    Things worth thinking about before you write any code:
      - Are your documents short posts or long guides?
      - Is the useful information in one sentence, or spread over a paragraph?
      - Would splitting on paragraph breaks keep more thoughts intact than
        splitting on a character count?
    """
    chunks: list[Chunk] = []
    chunk_size = config.CHUNK_SIZE
    overlap_size = config.CHUNK_OVERLAP
    min_chunk_size = config.MIN_CHUNK_SIZE


    for doc in documents:
        text_slices = _chunk_text_semantically(
            text=doc.text,
            chunk_size=chunk_size,
            overlap_size=overlap_size,
            min_chunk_size=min_chunk_size,
        )

        for index, slice_text in enumerate(text_slices):
            chunks.append(
                Chunk(
                    text=slice_text,
                    source=doc.source,
                    index=index,
                    produced_by="chunker.py::split_documents",
                )
            )

    return chunks


def describe(chunks: list[Chunk]) -> str:
    """A one-line summary, printed after indexing."""
    if not chunks:
        return "0 chunks"
    lengths = [len(c.text) for c in chunks]
    return (
        f"{len(chunks)} chunks, "
        f"{sum(lengths) // len(lengths)} characters on average "
        f"(shortest {min(lengths)}, longest {max(lengths)}), "
        f"produced by {chunks[0].produced_by}"
    )


if __name__ == "__main__":
    from ingest import load_documents

    chunks = split_documents(load_documents())
    print(describe(chunks))
