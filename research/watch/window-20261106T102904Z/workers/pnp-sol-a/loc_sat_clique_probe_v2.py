"""Explicit 3CNF occurrence-graph reduction; no complexity lower-bound claim."""
from itertools import combinations, combinations_with_replacement, product
import json


def sat(formula, nv):
    return any(all(any(a[abs(l)-1] == (l > 0) for l in c) for c in formula)
               for a in product((False,True), repeat=nv))


def occurrence_graph(formula):
    occurrences = [(ci,l) for ci,c in enumerate(formula) for l in c]
    graph = [[int(ci != cj and li != -lj)
              for cj,lj in occurrences] for ci,li in occurrences]
    return graph


def local_witness(formula, graph):
    # One literal occurrence chosen from each clause, rather than free assignment tape.
    for chosen in product(range(3),repeat=len(formula)):
        ids = [3*i+j for i,j in enumerate(chosen)]
        if all(graph[u][v] for u,v in combinations(ids,2)):
            return True
    return False


counts = {}
for nv,maxclauses in [(2,3),(3,2)]:
    literals = tuple(range(1,nv+1))+tuple(range(-nv,0))
    clauses = tuple(combinations_with_replacement(literals,3))
    count = 0
    for m in range(1,maxclauses+1):
        for formula in product(clauses,repeat=m):
            graph = occurrence_graph(formula)
            assert len(graph) == 3*m
            assert sum(map(len,graph)) == 9*m*m
            assert local_witness(formula,graph) == sat(formula,nv), formula
            count += 1
    counts[f'{nv}-variables'] = count
print(json.dumps({'status':'pass','formula_counts':counts,
                  'total_formulas':sum(counts.values()),
                  'graph_vertices':'3m', 'explicit_adjacency_cells':'9m^2',
                  'required_clique_size':'m, not a fixed constant',
                  'claimed_SAT_or_clique_lower_bound':False,
                  'claimed_reality_coverage':False},indent=2))
