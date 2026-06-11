#!/usr/bin/env python3
# /// script
# dependencies = ["networkx", "numpy", "scipy"]
# ///
"""
Structural analysis for knowledge-highlight-v2.

Splits a markdown document into paragraphs and scores each by:
  - TF-IDF information density
  - Structural position (post-header paragraphs tend to carry key claims)
  - TextRank graph centrality (paragraphs that many others are similar to)

No LLM calls — this is purely computational, used to supplement Claude's
own semantic analysis of claims, evidence, and insight.

Usage:
    python3 analyze.py <file.md> [--vault-root PATH] [--no-graph]

Output (stdout): JSON object with paragraph texts and scores.
"""

import argparse
import json
import math
import re
import sys
from collections import defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Optional

import networkx as nx
import numpy as np


# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------

@dataclass
class ParaScore:
    index: int
    text: str
    is_header: bool
    tfidf: float
    position: float
    graph: float
    combined: float


# ---------------------------------------------------------------------------
# Frontmatter / parsing
# ---------------------------------------------------------------------------

def strip_frontmatter(content: str) -> str:
    if not content.startswith("---"):
        return content
    end = re.search(r"\n---\s*\n", content[3:])
    if not end:
        return content
    return content[3 + end.end():]


def split_paragraphs(body: str) -> List[dict]:
    """
    Split body into paragraph units.

    Handles the common pattern where a markdown heading line (### Foo)
    is immediately followed by content with no blank line — in that case
    the heading and content are split so the content is analysable.
    """
    paras = []
    chunks = re.split(r"\n\s*\n", body)

    for chunk in chunks:
        text = chunk.strip()
        if len(text) < 15:
            continue

        first_line, _, rest = text.partition("\n")
        first_line = first_line.strip()
        rest = rest.strip()

        if re.match(r"^#{1,6}\s", first_line):
            # Header line — add as header
            paras.append({"text": first_line, "is_header": True})
            # If there's body content in the same chunk, add it separately
            if rest:
                paras.append({"text": rest, "is_header": False})
        else:
            paras.append({"text": text, "is_header": False})

    # Assign indices
    for i, p in enumerate(paras):
        p["index"] = i

    return paras


# ---------------------------------------------------------------------------
# NLP
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
    "all", "both", "few", "any", "just", "very", "much", "one", "two", "three",
})

_STRIP_MD = re.compile(r"\*\*|==|\*|_|`|^#{1,6}\s+", re.MULTILINE)
_PUNCT = re.compile(r"[^\w\s]")


def tokenize(text: str) -> List[str]:
    cleaned = _STRIP_MD.sub(" ", text).lower()
    return [w for w in _PUNCT.sub("", cleaned).split()
            if w not in STOPWORDS and len(w) > 2]


def build_df(paras: List[dict]) -> Dict[str, int]:
    df: Dict[str, int] = defaultdict(int)
    for p in paras:
        if not p["is_header"]:
            for term in set(tokenize(p["text"])):
                df[term] += 1
    return df


def tfidf_score(text: str, df: Dict[str, int], n_docs: int) -> float:
    words = tokenize(text)
    if not words or n_docs == 0:
        return 0.0
    tf: Dict[str, int] = defaultdict(int)
    for w in words:
        tf[w] += 1
    n = len(words)
    score = sum(
        (count / n) * math.log(n_docs / df[term])
        for term, count in tf.items()
        if df.get(term, 0) > 0
    )
    return score / len(tf) if tf else 0.0


def position_score(idx: int, all_paras: List[dict]) -> float:
    """Structural heuristic — paragraphs after a header, or at doc boundaries, often carry key claims."""
    score = 0.0
    n = len(all_paras)
    if idx == 0:
        score += 0.4
    if idx > 0 and all_paras[idx - 1]["is_header"]:
        score += 0.9  # first paragraph under a section heading
    if idx == n - 1:
        score += 0.3
    if idx == n - 2:
        score += 0.2
    return min(score, 1.0)


def tfidf_vector(text: str, vocab: List[str], vocab_idx: Dict[str, int],
                 df: Dict[str, int], n_docs: int) -> np.ndarray:
    vec = np.zeros(len(vocab))
    words = tokenize(text)
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


def compute_graph_scores(content_paras: List[dict]) -> Dict[int, float]:
    if len(content_paras) < 3:
        return {p["index"]: 0.5 for p in content_paras}

    df = build_df(content_paras)
    vocab = list(df.keys())
    vocab_idx = {t: i for i, t in enumerate(vocab)}
    n = len(content_paras)

    vecs = [tfidf_vector(p["text"], vocab, vocab_idx, df, n) for p in content_paras]
    norms = [np.linalg.norm(v) for v in vecs]

    sim = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            if i != j and norms[i] > 0 and norms[j] > 0:
                sim[i][j] = np.dot(vecs[i], vecs[j]) / (norms[i] * norms[j])

    G = nx.DiGraph()
    G.add_nodes_from(range(n))
    for i in range(n):
        for j in range(n):
            if i != j and sim[i][j] > 0.08:
                G.add_edge(i, j, weight=float(sim[i][j]))

    try:
        pr = nx.pagerank(G, weight="weight", max_iter=150)
    except nx.PowerIterationFailedConvergence:
        pr = {i: 1.0 / n for i in range(n)}

    return {p["index"]: pr.get(i, 1.0 / n) for i, p in enumerate(content_paras)}


def normalize(vals: List[float]) -> List[float]:
    mn, mx = min(vals, default=0.0), max(vals, default=1.0)
    if mx == mn:
        return [0.5] * len(vals)
    return [(v - mn) / (mx - mn) for v in vals]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def analyze(file_path: Path, include_graph: bool = True) -> dict:
    content = file_path.read_text(encoding="utf-8")
    body = strip_frontmatter(content)

    paras = split_paragraphs(body)
    content_paras = [p for p in paras if not p["is_header"]]

    if not content_paras:
        return {"file": str(file_path), "paragraphs": [], "content_para_count": 0}

    df = build_df(content_paras)
    n_docs = len(content_paras)

    # TF-IDF scores
    tfidf_raw = [tfidf_score(p["text"], df, n_docs) for p in content_paras]
    tfidf_norm = normalize(tfidf_raw)

    # Position scores
    pos_raw = [position_score(p["index"], paras) for p in content_paras]

    # Graph scores
    if include_graph and len(content_paras) >= 3:
        graph_raw = compute_graph_scores(content_paras)
        graph_vals = normalize([graph_raw.get(p["index"], 0.0) for p in content_paras])
    else:
        graph_vals = [0.0] * len(content_paras)

    # Combined score (structural only — Claude adds LLM votes on top)
    results = []
    for i, p in enumerate(content_paras):
        tfidf_s = tfidf_norm[i]
        pos_s = pos_raw[i]
        graph_s = graph_vals[i]
        combined = tfidf_s * 0.4 + pos_s * 0.4 + graph_s * 0.2
        results.append({
            "index": p["index"],
            "text": p["text"],
            "is_header": False,
            "tfidf": round(tfidf_s, 4),
            "position": round(pos_s, 4),
            "graph": round(graph_s, 4),
            "combined_structural": round(combined, 4),
        })

    # Sort by structural score for Claude's reference
    results_sorted = sorted(results, key=lambda x: x["combined_structural"], reverse=True)

    return {
        "file": str(file_path),
        "content_para_count": len(content_paras),
        "total_chars": len(body),
        "target_layer1_chars": int(len(body) * 0.15),
        "paragraphs_by_score": results_sorted,
        "all_paragraphs_ordered": results,  # in document order
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Structural analysis for knowledge-highlight-v2")
    parser.add_argument("path", help="Markdown file to analyze")
    parser.add_argument("--vault-root", type=Path, help="Vault root (default: CWD)")
    parser.add_argument("--no-graph", action="store_true", help="Skip TextRank graph scoring")
    args = parser.parse_args()

    vault_root = args.vault_root or Path.cwd()
    file_path = Path(args.path)
    if not file_path.is_absolute():
        file_path = vault_root / file_path

    if not file_path.exists():
        print(json.dumps({"error": f"file not found: {file_path}"}))
        return 1

    result = analyze(file_path, include_graph=not args.no_graph)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
