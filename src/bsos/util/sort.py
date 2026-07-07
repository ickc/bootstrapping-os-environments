from __future__ import annotations

import json
from typing import Any, Callable, Hashable, Iterable, Mapping, TypeVar

K = TypeVar("K", bound=Hashable)
T = TypeVar("T")


def deep_sort(obj: Any) -> Any:
    """Recursively rebuild a nested dict/list/scalar structure in canonical order.

    Dicts are rebuilt with keys sorted; lists are rebuilt with elements
    recursively canonicalized first, then sorted by their JSON-serialized form
    (a total order across the mixed scalar/dict/list elements that parsed
    YAML/JSON produces — dicts have no native ``<``). Scalars pass through
    unchanged. Pure: returns a new structure, never mutates *obj*.

    Intended for normalizing output from tools whose own list/dict ordering
    is not guaranteed stable across runs (e.g. iteration over a Rust
    ``HashMap`` with a randomized per-process seed), so that a second pass
    produces byte-identical results given identical content.
    """
    if isinstance(obj, dict):
        return {k: deep_sort(obj[k]) for k in sorted(obj)}
    if isinstance(obj, list):
        items = [deep_sort(item) for item in obj]
        return sorted(items, key=lambda item: json.dumps(item, sort_keys=True))
    return obj


def toposort_keys(keys: Iterable[K], edges: Mapping[K, Iterable[K]]) -> list[K]:
    """Depth-first topological sort over a graph given as bare keys.

    *keys* gives node identity and also the traversal order: it doubles as the
    tie-break among keys with no ordering relation, and as the order in which
    each key's own predecessors are visited among themselves. ``edges[k]``
    lists the predecessors of ``k`` (keys that must precede it in the
    output); predecessors absent from *keys* are ignored. Every key appears
    exactly once in the output, in dependency-first order.

    Cycles are broken silently at the back edge (the edge that would revisit
    a key already on the current DFS path), so cycle members may emerge in
    either order — this is not an error, just an inherent ambiguity of
    linearizing a cyclic graph.

    Runs in O(V + E): each key is visited once, and each key's edge list is
    scanned once, at the moment that key is visited.
    """
    keys = list(keys)
    key_set = set(keys)
    seen: set[K] = set()
    result: list[K] = []

    def visit(key: K) -> None:
        if key in seen:
            return
        seen.add(key)
        for dep in edges.get(key, ()):
            if dep in key_set:
                visit(dep)
        result.append(key)

    for key in keys:
        visit(key)
    return result


def toposort(iterable: Iterable[T], *, key: Callable[[T], K], depends_on: Callable[[T], Iterable[K]]) -> list[T]:
    """Depth-first topological sort over arbitrary items.

    Mirrors ``sorted(iterable, key=...)``, but replaces the total-order
    comparator with an explicit predecessor relation: *key* gives each item's
    identity, and *depends_on* gives the keys of the items that must precede
    it. See :func:`toposort_keys` for the ordering and cycle-breaking
    semantics.
    """
    items = list(iterable)
    by_key = {key(item): item for item in items}
    edges = {key(item): depends_on(item) for item in items}
    return [by_key[k] for k in toposort_keys(by_key.keys(), edges)]
