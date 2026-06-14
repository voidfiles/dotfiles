#!/usr/bin/env python3
# /// script
# dependencies = ["networkx", "numpy", "scipy", "anyio", "claude_code_sdk"]
# ///
"""
Knowledge-focused progressive summarization (v2).

Three-method pipeline:
  1. LLM multi-pass  — claims, evidence, insight (run in parallel threads)
  2. TextRank graph  — PageRank on paragraph similarity to find backbone ideas
  3. TF-IDF + position — information density and structural position scoring

Passages voted for by multiple methods score higher. Convergence = confidence.

Usage:
    python knowledge_highlight.py <path> [--fast] [--force] [--vault-root PATH] [--verbose]
"""

import argparse
import json
import math
import re
import sys
import threading
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import anyio
from claude_code_sdk import AssistantMessage, ClaudeCodeOptions, TextBlock, query
from claude_code_sdk._errors import MessageParseError
from claude_code_sdk.types import SystemMessage
import networkx as nx
import numpy as np


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class Paragraph:
    text: str
    index: int
    char_start: int
    is_header: bool = False

@dataclass
class LLMPassResult:
    frame: str
    passages: List[str] = field(default_factory=list)
    error: Optional[str] = None

@dataclass
class ScoredPassage:
    text: str
    para_index: int
    llm_votes: int = 0
    llm_frames: List[str] = field(default_factory=list)
    graph_score: float = 0.0
    tfidf_score: float = 0.0
    position_score: float = 0.0
    combined_score: float = 0.0

@dataclass
class ProcessingResult:
    file_path: Path
    success: bool
    bolded_count: int = 0
    highlighted_count: int = 0
    message: str = ""
    error: Optional[str] = None


# ---------------------------------------------------------------------------
# Frontmatter parsing (same schema as existing skill)
# ---------------------------------------------------------------------------

def parse_frontmatter(content: str) -> Tuple[Dict, str]:
    if not content.startswith("---"):
        return {}, content
    end = re.search(r"\n---\s*\n", content[3:])
    if not end:
        return {}, content
    fm_text = content[3:3 + end.start()]
    body = content[3 + end.end():]

    fm: Dict = {}
    lines = fm_text.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]
        if ":" in line and not line.startswith(" "):
            key, _, val = line.partition(":")
            key, val = key.strip(), val.strip()
            if val.lower() == "true":
                fm[key] = True
            elif val.lower() == "false":
                fm[key] = False
            elif val == "[]":
                fm[key] = []
            elif val == "null":
                fm[key] = None
            elif val == "":
                items: List[str] = []
                i += 1
                while i < len(lines) and lines[i].startswith("  - "):
                    items.append(lines[i].strip()[2:])
                    i += 1
                i -= 1
                fm[key] = items
            else:
                fm[key] = val
        i += 1
    return fm, body


def build_frontmatter(fm: Dict) -> str:
    KEY_ORDER = ["type", "tags", "highlighted", "extracted", "processed",
                 "highlighted_date", "extracted_date", "processed_date"]
    ordered = [k for k in KEY_ORDER if k in fm]
    ordered += sorted(k for k in fm if k not in ordered)

    lines = ["---"]
    for k in ordered:
        v = fm[k]
        if isinstance(v, bool):
            lines.append(f"{k}: {str(v).lower()}")
        elif isinstance(v, list):
            if not v:
                lines.append(f"{k}: []")
            else:
                lines.append(f"{k}:")
                lines.extend(f"  - {item}" for item in v)
        elif v is None:
            lines.append(f"{k}: null")
        else:
            lines.append(f"{k}: {v}")
    lines.append("---")
    return "\n".join(lines)


def detect_content_type(path: Path) -> str:
    s = str(path)
    if "Clippings" in s:
        return "article"
    if "daily" in s:
        return "daily"
    if "Meetings" in s:
        return "meeting"
    if "assets" in s:
        return "asset"
    return "unknown"


# ---------------------------------------------------------------------------
# Text segmentation
# ---------------------------------------------------------------------------

def split_paragraphs(body: str) -> List[Paragraph]:
    """Split body into paragraphs, preserving char positions."""
    paras: List[Paragraph] = []
    raw_chunks = re.split(r"\n\s*\n", body)
    pos = 0
    for chunk in raw_chunks:
        text = chunk.strip()
        if len(text) < 15:            # skip tiny fragments
            pos += len(chunk) + 2
            continue
        actual_start = body.find(text, pos)
        if actual_start == -1:
            actual_start = pos
        is_header = bool(re.match(r"^#{1,6}\s", text))
        paras.append(Paragraph(
            text=text,
            index=len(paras),
            char_start=actual_start,
            is_header=is_header,
        ))
        pos = actual_start + len(text)
    return paras


# ---------------------------------------------------------------------------
# NLP: TF-IDF and position scoring
# ---------------------------------------------------------------------------

STOPWORDS = frozenset({
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for", "of",
    "with", "is", "are", "was", "were", "be", "been", "being", "have", "has",
    "had", "do", "does", "did", "will", "would", "could", "should", "may",
    "might", "can", "it", "its", "this", "that", "these", "those", "they",
    "their", "there", "here", "from", "by", "as", "not", "which", "who",
    "what", "when", "where", "how", "if", "then", "than", "more", "most",
    "also", "we", "our", "you", "your", "he", "she", "his", "her", "i", "my",
    "me", "us", "them", "so", "up", "out", "about", "into", "through", "after",
    "over", "such", "no", "only", "same", "other", "between", "each", "while",
    "all", "both", "few", "any", "just", "been", "very", "much",
})

_STRIP_MD = re.compile(r"\*\*|==|\*|_|`")
_PUNCT = re.compile(r"[^\w\s]")


def tokenize(text: str) -> List[str]:
    cleaned = _STRIP_MD.sub("", text).lower()
    return [w for w in _PUNCT.sub("", cleaned).split()
            if w not in STOPWORDS and len(w) > 2]


def build_doc_freq(paras: List[Paragraph]) -> Dict[str, int]:
    df: Dict[str, int] = defaultdict(int)
    for p in paras:
        if not p.is_header:
            for term in set(tokenize(p.text)):
                df[term] += 1
    return df


def para_tfidf_score(para: Paragraph, df: Dict[str, int], n_docs: int) -> float:
    if para.is_header or n_docs == 0:
        return 0.0
    words = tokenize(para.text)
    if not words:
        return 0.0
    tf: Dict[str, int] = defaultdict(int)
    for w in words:
        tf[w] += 1
    n = len(words)
    score = sum(
        (count / n) * math.log(n_docs / df[term])
        for term, count in tf.items()
        if term in df and df[term] > 0
    )
    return score / len(tf) if tf else 0.0


def para_position_score(para: Paragraph, all_paras: List[Paragraph]) -> float:
    """Structural position heuristic — post-header and boundary paragraphs often carry key claims."""
    idx = para.index
    score = 0.0
    if idx == 0:
        score += 0.4
    if idx > 0 and all_paras[idx - 1].is_header:
        score += 0.8
    total = len(all_paras)
    if idx == total - 1:
        score += 0.3
    if idx == total - 2:
        score += 0.2
    return min(score, 1.0)


# ---------------------------------------------------------------------------
# Graph: TextRank-style PageRank on paragraph similarity
# ---------------------------------------------------------------------------

def build_tfidf_vector(para: Paragraph, vocab: List[str], vocab_idx: Dict[str, int],
                       df: Dict[str, int], n_docs: int) -> np.ndarray:
    vec = np.zeros(len(vocab))
    words = tokenize(para.text)
    if not words:
        return vec
    tf: Dict[str, int] = defaultdict(int)
    for w in words:
        tf[w] += 1
    n = len(words)
    for term, count in tf.items():
        if term in vocab_idx and df.get(term, 0) > 0:
            vec[vocab_idx[term]] = (count / n) * math.log(n_docs / df[term])
    return vec


def textrank_scores(content_paras: List[Paragraph]) -> Dict[int, float]:
    """Return PageRank score keyed by paragraph index."""
    if len(content_paras) < 3:
        return {p.index: 0.5 for p in content_paras}

    df = build_doc_freq(content_paras)
    vocab = list(df.keys())
    vocab_idx = {t: i for i, t in enumerate(vocab)}
    n = len(content_paras)

    vecs = [build_tfidf_vector(p, vocab, vocab_idx, df, n) for p in content_paras]

    # Cosine similarity matrix
    norms = [np.linalg.norm(v) for v in vecs]
    sim = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            if i != j and norms[i] > 0 and norms[j] > 0:
                sim[i][j] = np.dot(vecs[i], vecs[j]) / (norms[i] * norms[j])

    G = nx.DiGraph()
    G.add_nodes_from(range(n))
    threshold = 0.08
    for i in range(n):
        for j in range(n):
            if i != j and sim[i][j] > threshold:
                G.add_edge(i, j, weight=float(sim[i][j]))

    try:
        pr = nx.pagerank(G, weight="weight", max_iter=150)
    except nx.PowerIterationFailedConvergence:
        pr = {i: 1.0 / n for i in range(n)}

    return {p.index: pr.get(i, 1.0 / n) for i, p in enumerate(content_paras)}


# ---------------------------------------------------------------------------
# LLM multi-pass
# ---------------------------------------------------------------------------

CONTENT_TYPE_CONTEXT = {
    "article": "This is an article or web clipping.",
    "meeting": "This is meeting content. Focus on decisions, commitments, and insights.",
    "daily": "This is a personal daily note. Focus on reflections, patterns, commitments.",
    "asset": "This is a book or document summary. Focus on frameworks and core arguments.",
    "unknown": "This is a knowledge document.",
}

LLM_FRAMES = [
    {
        "name": "claims",
        "instruction": (
            "FRAME: Claims and Arguments\n"
            "Find the main **claims, assertions, and arguments** — propositions the author defends "
            "that could in principle be true or false. These form the argumentative skeleton."
        ),
    },
    {
        "name": "evidence",
        "instruction": (
            "FRAME: Evidence and Support\n"
            "Find passages containing **data, studies, statistics, examples, or citations** "
            "used to support claims. These are where the author tries to prove something."
        ),
    },
    {
        "name": "insight",
        "instruction": (
            "FRAME: Insight and Explanation\n"
            "Find passages with **valuable explanations, mental models, or frameworks** — "
            "where the author illuminates WHY something works or offers a conceptual lens "
            "that changes how you'd think about the topic."
        ),
    },
]


def call_claude(prompt: str, model: str) -> Optional[str]:
    async def _run() -> Optional[str]:
        import claude_code_sdk._internal.client as _client
        _orig = _client.parse_message

        def _safe_parse(data):  # noqa: ANN001
            try:
                return _orig(data)
            except MessageParseError:
                return SystemMessage(subtype=data.get("type", "unknown"), data=data)

        _client.parse_message = _safe_parse
        result: Optional[str] = None
        try:
            options = ClaudeCodeOptions(model=model)
            async for message in query(prompt=prompt, options=options):
                if isinstance(message, AssistantMessage) and result is None:
                    for block in message.content:
                        if isinstance(block, TextBlock):
                            result = block.text
                            break
        finally:
            _client.parse_message = _orig
        return result

    return anyio.run(_run)


def extract_json(response: str) -> Optional[dict]:
    if not response:
        return None
    m = re.search(r"\{[\s\S]*\}", response)
    if m:
        try:
            return json.loads(m.group())
        except json.JSONDecodeError:
            pass
    return None


def _run_frame(body: str, content_type: str, frame: dict, model: str,
               out: dict, key: str) -> None:
    """Thread target: run one LLM frame pass and store result in `out[key]`."""
    ctx = CONTENT_TYPE_CONTEXT.get(content_type, CONTENT_TYPE_CONTEXT["unknown"])
    prompt = f"""{ctx}

{frame['instruction']}

Return 5–15 passages as EXACT verbatim quotes from the document (not paraphrased).
Each passage should be 1–4+ sentences — a complete, meaningful unit of knowledge.
Skip text that is already bold (**text**) or highlighted (==text==).

Document:
{body}

Return JSON:
{{
  "passages": [
    "exact verbatim passage 1",
    "exact verbatim passage 2"
  ]
}}"""
    resp = call_claude(prompt, model)
    data = extract_json(resp) if resp else None
    out[key] = data.get("passages", []) if data else []


def run_llm_passes(body: str, content_type: str, model: str) -> Dict[str, List[str]]:
    """Run all three LLM frames in parallel threads."""
    results: Dict[str, List[str]] = {}
    threads = [
        threading.Thread(target=_run_frame, args=(body, content_type, f, model, results, f["name"]))
        for f in LLM_FRAMES
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return results


# ---------------------------------------------------------------------------
# Passage scoring: map LLM passages → paragraphs, combine signals
# ---------------------------------------------------------------------------

def overlap_ratio(passage: str, para_text: str) -> float:
    """Word overlap fraction: how much of `passage` appears in `para_text`."""
    a = set(passage.lower().split())
    b = set(para_text.lower().split())
    return len(a & b) / len(a) if a else 0.0


def find_para_for_passage(passage: str, paras: List[Paragraph]) -> Optional[int]:
    """Return the index of the best-matching paragraph for a passage."""
    # Exact substring match (fastest)
    for p in paras:
        if passage in p.text:
            return p.index
    # After stripping markdown markers
    clean = _STRIP_MD.sub("", passage).strip()
    for p in paras:
        if clean in _STRIP_MD.sub("", p.text):
            return p.index
    # Word overlap fallback
    best_idx, best_score = None, 0.35  # minimum threshold
    for p in paras:
        if p.is_header:
            continue
        s = overlap_ratio(passage, p.text)
        if s > best_score:
            best_score, best_idx = s, p.index
    return best_idx


def normalize_list(vals: List[float]) -> List[float]:
    mn, mx = min(vals, default=0), max(vals, default=1)
    if mx == mn:
        return [0.5] * len(vals)
    return [(v - mn) / (mx - mn) for v in vals]


def build_scored_passages(
    llm_results: Dict[str, List[str]],
    paras: List[Paragraph],
    graph_scores: Dict[int, float],
    tfidf_map: Dict[int, float],
    pos_map: Dict[int, float],
) -> List[ScoredPassage]:
    """
    For every unique LLM passage, tally votes and combine with structural signals.
    Passages are deduplicated: overlapping passages keep the longer one.
    """
    # Collect all passages with their frame votes
    passage_frames: Dict[str, List[str]] = defaultdict(list)
    for frame_name, passages in llm_results.items():
        for p in passages:
            p = p.strip()
            if p:
                passage_frames[p].append(frame_name)

    # Remove passages that are substrings of another passage (keep the longer)
    all_texts = sorted(passage_frames.keys(), key=len, reverse=True)
    keep: List[str] = []
    for candidate in all_texts:
        dominated = any(candidate in longer for longer in keep)
        if not dominated:
            keep.append(candidate)

    # Normalize structural scores
    content_paras = [p for p in paras if not p.is_header]
    graph_vals = normalize_list([graph_scores.get(p.index, 0.0) for p in content_paras])
    tfidf_vals = normalize_list([tfidf_map.get(p.index, 0.0) for p in content_paras])
    para_to_norm_graph = {p.index: graph_vals[i] for i, p in enumerate(content_paras)}
    para_to_norm_tfidf = {p.index: tfidf_vals[i] for i, p in enumerate(content_paras)}

    scored: List[ScoredPassage] = []
    for text in keep:
        para_idx = find_para_for_passage(text, paras)
        frames = passage_frames[text]
        gs = para_to_norm_graph.get(para_idx, 0.0) if para_idx is not None else 0.0
        ts = para_to_norm_tfidf.get(para_idx, 0.0) if para_idx is not None else 0.0
        ps = pos_map.get(para_idx, 0.0) if para_idx is not None else 0.0

        # LLM votes are the dominant signal; structural scores refine the ranking
        combined = len(frames) * 2.0 + gs * 1.0 + ts * 0.5 + ps * 0.5

        scored.append(ScoredPassage(
            text=text,
            para_index=para_idx if para_idx is not None else -1,
            llm_votes=len(frames),
            llm_frames=frames,
            graph_score=gs,
            tfidf_score=ts,
            position_score=ps,
            combined_score=combined,
        ))

    return sorted(scored, key=lambda x: x.combined_score, reverse=True)


def select_layer1(scored: List[ScoredPassage], body: str, target_fraction: float = 0.15) -> List[str]:
    """Pick top passages until ~target_fraction of body length is covered."""
    target = max(int(len(body) * target_fraction), 200)
    selected, total = [], 0
    for sp in scored:
        if total >= target:
            break
        selected.append(sp.text)
        total += len(sp.text)
    return selected


def select_layer2(layer1_passages: List[str], scored: List[ScoredPassage],
                  target_fraction: float = 0.20) -> List[str]:
    """From Layer 1, pick the top-scoring ~20% for highlighting."""
    layer1_set = set(layer1_passages)
    layer1_scored = [sp for sp in scored if sp.text in layer1_set]
    n = max(1, int(len(layer1_scored) * target_fraction))
    return [sp.text for sp in layer1_scored[:n]]


# ---------------------------------------------------------------------------
# Formatting
# ---------------------------------------------------------------------------

# LLMs tend to normalize Unicode typography to ASCII. Map each fancy char to
# its ASCII look-alike so we can match even when the model “cleaned” the text.
# IMPORTANT: every substitution here must be strictly 1 char → 1 char so that
# indices in the normalized string map 1:1 to indices in the original string.
_UNICODE_TO_ASCII: List[Tuple[str, str]] = [
    ("\u2018", "'"),  # left single quotation mark  -> apostrophe
    ("\u2019", "'"),  # right single quotation mark -> apostrophe
    ("\u201c", '"'),  # left double quotation mark  -> double quote
    ("\u201d", '"'),  # right double quotation mark -> double quote
    ("\u2014", "-"),  # em dash                     -> hyphen
    ("\u2013", "-"),  # en dash                     -> hyphen
    ("\u2026", "."),  # horizontal ellipsis         -> period (1->1, lossy but safe)
]


def _normalize_typography(text: str) -> str:
    """Replace curly quotes / dashes with ASCII equivalents for fuzzy matching."""
    for fancy, plain in _UNICODE_TO_ASCII:
        text = text.replace(fancy, plain)
    return text


def _find_span(passage: str, body: str) -> Optional[Tuple[int, int]]:
    """
    Return (start, end) of `passage` in `body`.

    Priority:
      1. Exact substring match (fastest, always preferred)
      2. Typography-normalized match (LLM swapped curly quotes / dashes to ASCII)
      3. Whitespace-normalized match (trailing Markdown double-spaces removed)
    """
    # 1. Exact
    idx = body.find(passage)
    if idx != -1:
        return idx, idx + len(passage)

    # 2. Normalize typography in both; since every substitution is 1:1 in
    #    character length the returned indices are valid for the *original* body.
    norm_passage = _normalize_typography(passage)
    norm_body = _normalize_typography(body)
    idx = norm_body.find(norm_passage)
    if idx != -1:
        return idx, idx + len(norm_passage)

    # 3. Strip trailing spaces from each "line" within the passage (Markdown
    #    source often has "  \n" hard-line-breaks the LLM doesn't reproduce).
    stripped_passage = "\n".join(line.rstrip() for line in passage.split("\n"))
    stripped_body = "\n".join(line.rstrip() for line in body.split("\n"))
    idx = stripped_body.find(stripped_passage)
    if idx != -1:
        return idx, idx + len(stripped_passage)

    # 4. Combined: normalize typography AND strip trailing spaces
    norm_stripped_passage = _normalize_typography(stripped_passage)
    norm_stripped_body = _normalize_typography(stripped_body)
    idx = norm_stripped_body.find(norm_stripped_passage)
    if idx != -1:
        return idx, idx + len(norm_stripped_passage)

    return None


def apply_formatting(body: str, bold_passages: List[str],
                     highlight_passages: List[str]) -> Tuple[str, int, int]:
    modified = body
    bold_count = highlight_count = 0

    # Apply bold (longest first to avoid subset conflicts)
    for passage in sorted(bold_passages, key=len, reverse=True):
        if f"**{passage}**" in modified or f"==**{passage}**==" in modified:
            continue
        span = _find_span(passage, modified)
        if span is None:
            continue
        start, end = span
        original_text = modified[start:end]
        # Wrap the *original* body text (preserves Unicode / trailing spaces).
        # Use the cleaned passage for the bold marker so readers see clean text.
        modified = modified[:start] + f"**{original_text}**" + modified[end:]
        bold_count += 1

    # Upgrade bold → bold+highlight for Layer 2
    for passage in highlight_passages:
        # The original text was already bolded; search for **<anything>** where
        # the content fuzzy-matches `passage`.
        bolded_exact = f"**{passage}**"
        if bolded_exact in modified:
            modified = modified.replace(bolded_exact, f"==**{passage}**==", 1)
            highlight_count += 1
        else:
            # Try to find **<original text>** using the same fuzzy span logic,
            # but on the bolded content.
            norm_passage = _normalize_typography(passage)
            # Find **…** block whose inner text normalizes to norm_passage
            for m in re.finditer(r"\*\*(.+?)\*\*", modified, re.DOTALL):
                if _normalize_typography(m.group(1)) == norm_passage:
                    modified = modified[:m.start()] + f"==**{m.group(1)}**==" + modified[m.end():]
                    highlight_count += 1
                    break

    return modified, bold_count, highlight_count


# ---------------------------------------------------------------------------
# Main per-file processor
# ---------------------------------------------------------------------------

def process_file(
    file_path: Path,
    vault_root: Path,
    force: bool,
    fast: bool,
    model: str,
    verbose: bool,
) -> ProcessingResult:
    def log(msg: str) -> None:
        if verbose:
            print(f"    [{file_path.name}] {msg}", flush=True)

    try:
        raw = file_path.read_text(encoding="utf-8")
        fm, body = parse_frontmatter(raw)

        if fm.get("highlighted") and not force:
            return ProcessingResult(
                file_path=file_path, success=True,
                message=f"skip — already highlighted (--force to redo)",
            )

        content_type = fm.get("type") or detect_content_type(file_path)

        # Assets: process summary.md inside the folder
        if content_type == "asset":
            summary = file_path.parent / "summary.md"
            if summary.exists():
                file_path = summary
                raw = file_path.read_text(encoding="utf-8")
                fm, body = parse_frontmatter(raw)
            else:
                return ProcessingResult(file_path=file_path, success=False, error="no summary.md in asset folder")

        # Segment
        paras = split_paragraphs(body)
        content_paras = [p for p in paras if not p.is_header]
        log(f"{len(content_paras)} content paragraphs, type={content_type}")

        if len(content_paras) < 3:
            return ProcessingResult(file_path=file_path, success=True, message="skip — too short")

        # === Phase 1: LLM multi-pass ===
        log("LLM passes: claims, evidence, insight (parallel)…")
        llm_results = run_llm_passes(body, content_type, model)
        total_llm = sum(len(v) for v in llm_results.values())
        log(f"  → {total_llm} passages across {len(llm_results)} frames")

        # === Phase 2: Structural scoring ===
        if not fast:
            log("building TF-IDF + TextRank graph…")
            df = build_doc_freq(content_paras)
            n_docs = len(content_paras)
            tfidf_map = {p.index: para_tfidf_score(p, df, n_docs) for p in content_paras}
            pos_map = {p.index: para_position_score(p, paras) for p in content_paras}
            graph_scores = textrank_scores(content_paras)
        else:
            log("fast mode — skipping graph/TF-IDF")
            tfidf_map = {p.index: 0.0 for p in content_paras}
            pos_map = {p.index: para_position_score(p, paras) for p in content_paras}
            graph_scores = {p.index: 0.0 for p in content_paras}

        # === Phase 3: Consensus scoring ===
        log("scoring passages…")
        scored = build_scored_passages(llm_results, paras, graph_scores, tfidf_map, pos_map)
        log(f"  → {len(scored)} unique passages scored")

        if not scored:
            fm["highlighted"] = True
            fm["highlighted_date"] = datetime.now().strftime("%Y-%m-%d")
            fm.setdefault("extracted", False)
            fm.setdefault("processed", False)
            file_path.write_text(f"{build_frontmatter(fm)}\n{body}", encoding="utf-8")
            return ProcessingResult(file_path=file_path, success=True, message="no passages found")

        # === Phase 4: Layer selection ===
        layer1 = select_layer1(scored, body, target_fraction=0.15)
        layer2 = select_layer2(layer1, scored, target_fraction=0.20)
        log(f"Layer 1: {len(layer1)} passages | Layer 2: {len(layer2)} passages")

        # === Phase 5: Apply formatting ===
        modified_body, bold_count, highlight_count = apply_formatting(body, layer1, layer2)

        # === Phase 6: Write ===
        fm["type"] = content_type
        fm["highlighted"] = True
        fm["highlighted_date"] = datetime.now().strftime("%Y-%m-%d")
        fm.setdefault("extracted", False)
        fm.setdefault("processed", False)

        file_path.write_text(f"{build_frontmatter(fm)}\n{modified_body}", encoding="utf-8")

        return ProcessingResult(
            file_path=file_path, success=True,
            bolded_count=bold_count, highlighted_count=highlight_count,
            message=f"{bold_count} bolded, {highlight_count} highlighted",
        )

    except Exception as e:
        return ProcessingResult(file_path=file_path, success=False, error=str(e))


# ---------------------------------------------------------------------------
# File discovery
# ---------------------------------------------------------------------------

def find_files(path_arg: str, vault_root: Path) -> List[Path]:
    path = Path(path_arg)
    if not path.is_absolute():
        path = vault_root / path
    if path.is_file() and path.suffix == ".md":
        return [path]
    if path.is_dir():
        return sorted(path.glob("**/*.md"))
    return []


def get_vault_root(arg: Optional[Path]) -> Path:
    if arg:
        return arg
    cwd = Path.cwd()
    # If CWD looks like an Obsidian vault, use it
    if (cwd / ".obsidian").exists() or (cwd / "CLAUDE.md").exists():
        return cwd
    return cwd


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description="Knowledge-focused progressive summarization v2")
    parser.add_argument("path", nargs="?", default="Clippings/", help="File or folder to process")
    parser.add_argument("--force", action="store_true", help="Re-process already-highlighted files")
    parser.add_argument("--fast", action="store_true", help="Skip graph/TF-IDF, LLM passes only")
    parser.add_argument("--model", default="claude-haiku-4-5-20251001", help="Claude model for LLM passes")
    parser.add_argument("--vault-root", type=Path, help="Vault root (default: CWD)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show phase-by-phase progress")
    args = parser.parse_args()

    vault_root = get_vault_root(args.vault_root)
    files = find_files(args.path, vault_root)

    if not files:
        print(f"No markdown files found: {args.path}", file=sys.stderr)
        print(f"  (looked in: {vault_root / args.path})", file=sys.stderr)
        return 1

    mode = "fast (LLM-only)" if args.fast else "full (LLM + TF-IDF + TextRank)"
    print(f"knowledge-highlight v2  [{mode}]")
    print(f"Processing {len(files)} file(s)...\n")

    results: List[ProcessingResult] = []
    for fp in files:
        print(f"  {fp.name} ...", end="", flush=True)
        r = process_file(fp, vault_root, args.force, args.fast, args.model, args.verbose)
        results.append(r)
        if r.success:
            suffix = f" ✓  {r.message}" if r.message else " ✓"
            print(suffix)
        else:
            print(f" ✗  {r.error}")

    processed = [r for r in results if r.success and r.bolded_count > 0]
    skipped = [r for r in results if r.success and r.bolded_count == 0]
    failed = [r for r in results if not r.success]

    print(f"\n{'─'*50}")
    print(f"Processed : {len(processed)}")
    print(f"Skipped   : {len(skipped)}")
    print(f"Failed    : {len(failed)}")
    if processed:
        print(f"Bolded    : {sum(r.bolded_count for r in processed)} passages total")
        print(f"Highlighted: {sum(r.highlighted_count for r in processed)} passages total")

    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
