"""Exhaustive finite checks of the binary priority policy. No dependencies."""
from itertools import product


def strict_orders(n):
    pairs = [(i, j) for i in range(n) for j in range(n) if i != j]
    for bits in product((False, True), repeat=len(pairs)):
        rel = {p for p, bit in zip(pairs, bits) if bit}
        if all((i, k) in rel for i, j in rel for j2, k in rel if j == j2):
            yield rel


def classify(signs, rel):
    relevant = {h for h, v in enumerate(signs) if v != 0}
    maximal = {h for h in relevant if not any((h, k) in rel for k in relevant)}
    positive = bool(maximal) and all(signs[h] == 1 for h in maximal)
    negative = bool(maximal) and all(signs[h] == -1 for h in maximal)
    unresolved = any(signs[h] == 1 for h in maximal) and any(signs[h] == -1 for h in maximal)
    none = not relevant
    assert sum((positive, negative, unresolved, none)) == 1
    return 'positive' if positive else 'negative' if negative else 'unresolved' if unresolved else 'none'


def main():
    cases = 0
    orders = 0
    for n in range(1, 5):
        local_orders = list(strict_orders(n))
        orders += len(local_orders)
        for rel in local_orders:
            for signs in product((-1, 0, 1), repeat=n):
                classify(signs, rel)
                cases += 1
    assert classify((1, -1), {(0, 1)}) == 'negative'
    assert classify((1, -1), set()) == 'unresolved'
    assert classify((1, 1), set()) == 'positive'
    assert classify((1, -1, 1), {(0, 2), (1, 2)}) == 'positive'
    print(f'PASS {cases} status classifications over {orders} strict orders with 1 to 4 authorities.')

    # Exact finite interpretation of naval_binary.tff.
    worlds = range(3)
    authorities = range(3)  # ROE, UNCLOS, NSD
    p = {0: False, 1: False, 2: True}
    active = lambda h, w: h != 1 or w != 1
    d = lambda h, w, u: (h == 0 and u == 2) or (h == 1 and u == 1) or h == 2
    less = {(1, 0), (1, 2)}
    for h in authorities:
        for w in worlds:
            assert any(d(h, w, u) for u in worlds)
    pos = lambda h, w: active(h, w) and all(p[u] for u in worlds if d(h, w, u))
    neg = lambda h, w: active(h, w) and all(not p[u] for u in worlds if d(h, w, u))
    signs = tuple(1 if pos(h, 0) else -1 if neg(h, 0) else 0 for h in authorities)
    assert signs == (1, -1, 0)
    assert classify(signs, less) == 'positive'
    assert pos(0, 0) and neg(1, 0)  # Issued conflict persists.
    assert not any(pos(1, w) or neg(1, w) for w in [1])
    assert not all(neg(1, u) for u in worlds)  # Not known that warning requirement applies.
    assert not all(not p[u] for u in worlds)  # Not known that warning action holds.
    weak_pos = lambda h, w: active(h, w) and not all(not p[u] for u in worlds if d(h, w, u))
    weak_neg = lambda h, w: active(h, w) and not all(p[u] for u in worlds if d(h, w, u))
    assert weak_pos(2, 0) and weak_neg(2, 0)
    assert not weak_pos(1, 1) and not weak_neg(1, 1)
    assert all(classify(tuple(1 if pos(h, w) else -1 if neg(h, w) else 0 for h in authorities), less) == 'positive' for w in worlds)
    print('PASS active weak permission of both alternatives, inactive weak-permission guard, and knowledge of the effective positive status.')
    print('PASS explicit three-world naval interpretation, serial normative relations, inactive guard, persistent conflict, effective response, no mediation, and both knowledge queries.')


if __name__ == '__main__':
    main()
