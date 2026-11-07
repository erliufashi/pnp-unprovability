import itertools,json

def verify_shared(rows,initial,final):
    # Two monotonically increasing index streams over ONE flattened proof.
    w=len(initial);flat=tuple(bit for row in rows for bit in row)
    a=0;b=w
    if rows[0]!=initial:return False
    for _ in range(len(rows)-1):
        for j in range(w):
            if flat[b]!=(1-flat[a]):return False
            a+=1;b+=1
    return rows[-1]==final
checks=0
for w in range(1,5):
    states=list(itertools.product((0,1),repeat=w))
    initial=(0,)*w
    for rows in itertools.product(states,repeat=3):
        expected=(rows[0]==initial and rows[1]==tuple(1-x for x in rows[0]) and rows[2]==tuple(1-x for x in rows[1]))
        assert verify_shared(rows,initial,initial)==expected
        assert not verify_shared(rows,initial,(1,)*w)
        checks+=1
# Impossible two-step 0->1 goal becomes apparently valid with inconsistent middle.
pair1=(0,1);pair2=(0,1)
assert pair1[1]==1-pair1[0] and pair2[1]==1-pair2[0]
assert pair1[1]!=pair2[0]
print(json.dumps({'three_row_proofs_checked':checks,'row_widths':[1,4],'shared_monotone_checker_correct':True,'independent_streams_can_disagree_on_middle_row':True,'scope':'toy consistency sanity check, not an empirical NP characterization proof'},indent=2))
