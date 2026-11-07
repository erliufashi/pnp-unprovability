#!/usr/bin/env python3
"""Finite-state capacity sanity. Python host memory is NOT the declared model."""
import argparse
import hashlib
import itertools
import json
import math
from pathlib import Path
import time

HERE=Path(__file__).resolve().parent


def bits(value,width):
    return tuple((value>>shift)&1 for shift in reversed(range(width)))


def nd_branch(stream,m,guess):
    """One branch of a specified bounded-register transducer, only next(input).

    The harness supplies nondeterministic choice bits before payload. No expected
    answer or original payload array is available to this logical machine.
    """
    b=m.bit_length(); mask=(1<<b)-1
    assert m>=1 and 0<=guess<=mask
    regs=[0]*8  # I,J,Q,L,cursor_lo,cursor_hi,scratch0,scratch1
    phase=0; value=0; bad=0; eof=0; incoming=0
    transitions=0; max_encoded_bits=0; digest=hashlib.sha256()
    def audit():
        nonlocal transitions,max_encoded_bits
        assert all(0<=word<=mask for word in regs)
        assert 0<=phase<8 and value in (0,1) and bad in (0,1) and eof in (0,1)
        control=phase | (value<<4) | (bad<<5) | (eof<<6) | (incoming<<7)
        assert control<(1<<64)
        encoded=sum(word<<(i*b) for i,word in enumerate(regs)) | (control<<(8*b))
        assert encoded<(1<<(8*b+64))
        assert [((encoded>>(i*b))&mask) for i in range(8)]==regs
        assert encoded>>(8*b)==control
        max_encoded_bits=max(max_encoded_bits,encoded.bit_length()); transitions+=1
        digest.update(encoded.to_bytes((8*b+64+7)//8,'big'))
    def advance_cursor():
        cursor=regs[4]+(regs[5]<<b)+1
        assert cursor<=m+b+1 and cursor<(1<<(2*b))
        regs[4]=cursor&mask; regs[5]=cursor>>b
    # Simulation of b binary nondeterministic transitions, not an input answer.
    audit()
    for choice in bits(guess,b):
        regs[1]=(regs[1]<<1)|choice; regs[3]+=1; incoming=choice; audit()
    assert regs[1]==guess
    regs[3]=0; phase=1; audit()
    for token in stream:
        assert token in (0,1)
        incoming=token; advance_cursor()
        if phase==1:
            if regs[0]==regs[1]: value=token
            regs[0]+=1
            if regs[0]==m: phase=2
        elif phase==2:
            regs[2]=(regs[2]<<1)|token; regs[3]+=1
            if regs[3]==b: phase=3
        else:
            # Invalid extension: bounded early rejection; no further reads.
            bad=1; phase=5; audit()
            return {'accepted':False,'transitions':transitions,'max_encoded_bits':max_encoded_bits,
                    'declared_bits':8*b+64,'digest':digest.hexdigest(),'early_invalid':True}
        audit()
    advance_cursor(); eof=1; phase=6
    accepted=(regs[0]==m and regs[3]==b and regs[1]<m and regs[2]==regs[1] and value==1 and not bad)
    audit()
    return {'accepted':bool(accepted),'transitions':transitions,'max_encoded_bits':max_encoded_bits,
            'declared_bits':8*b+64,'digest':digest.hexdigest(),'early_invalid':False}


def nd_exhaustive():
    tasks=0; valid=0; invalid_query=0; branches=0; transitions=0; digest=hashlib.sha256()
    rows=[]
    for m in range(1,7):
        b=m.bit_length(); local_tasks=0; local_branches=0; max_encoded=0
        for code in range(1<<m):
            payload=bits(code,m)
            for query in range(1<<b):
                accepted=False
                for guess in range(1<<b):
                    result=nd_branch(iter(payload+bits(query,b)),m,guess)
                    accepted=accepted or result['accepted']
                    max_encoded=max(max_encoded,result['max_encoded_bits'])
                    transitions+=result['transitions']; branches+=1; local_branches+=1
                    digest.update(result['digest'].encode())
                expected=query<m and payload[query]==1
                assert accepted==expected
                tasks+=1; local_tasks+=1
                if query<m: valid+=1
                else: invalid_query+=1
        rows.append({'m':m,'b':b,'tasks':local_tasks,'branches':local_branches,
                     'declared_state_bits':8*b+64,'largest_observed_encoding_bits':max_encoded})
    malformed=0
    for m in (1,3,6):
        b=m.bit_length()
        positive=(1,)*m+bits(0,b)
        for tape in [(),(1,)*(m-1),positive[:-1],positive+(0,),positive+(0,1)]:
            for guess in range(1<<b):
                assert not nd_branch(iter(tape),m,guess)['accepted']; malformed+=1
    return {'tasks':tasks,'valid_tasks':valid,'invalid_query_guard_tasks':invalid_query,
            'branches':branches,'logical_transitions_checked':transitions,'malformed_branches':malformed,
            'rows':rows,'digest':digest.hexdigest(),'passed':True}


def exhaustive_encoders():
    rows=[]; total=0; digest=hashlib.sha256()
    for m,s in [(2,1),(3,1),(3,2),(4,1)]:
        population=1<<m; states=1<<s; count=0; example=None
        for mapping in itertools.product(range(states),repeat=population):
            first={}; witness=None
            for x,state in enumerate(mapping):
                if state in first:
                    y=first[state]; j=m-(x^y).bit_length()
                    assert 0<=j<m and ((x>>(m-1-j))&1)!=((y>>(m-1-j))&1)
                    witness=(y,x,j,state); break
                first[state]=x
            assert witness is not None
            digest.update(bytes(witness)); count+=1
            if example is None: example=witness
        assert count==states**population
        rows.append({'m':m,'s':s,'all_prefix_maps_checked':count,'example_collision':example})
        total+=count
    return {'rows':rows,'total_prefix_maps':total,'digest':digest.hexdigest(),'passed':True,
            'scope':'all functions only at listed small (m,s); general theorem remains pigeonhole proof'}


def threshold_ledger():
    budgets=[]
    for s in (64,128,256,1024,1<<20):
        row={'s_retained_bits':s}
        for name,m in [('exact',s+1),('random_safe_gamma_1_3',16*s+1)]:
            b=m.bit_length(); nd_bound=8*b+64
            row[name]={'m_payload_bits':m,'query_bits':b,'protocol_data_bits':m+b,
                       'EOF':'separate protocol sentinel, not included in data-bit count',
                       'ND_declared_bits':nd_bound,'ND_same_budget_certificate':nd_bound<=s,
                       'payload_range_results':[{'C_payload_bits':C,'m_within_C':m<=C,
                                            'separation_in_payload_range':m<=C and nd_bound<=s}
                                           for C in (128,129,136,137,256,4096,65536,1<<20)],
                       'wire_capacity_results':[{'C_data_bit_symbols':C,'full_protocol_data_fit':m+b<=C,
                                                'separation_with_data_fit':m+b<=C and nd_bound<=s}
                                               for C in (128,129,136,137,256,4096,65536,1<<20)],
                       'warning_if_not_fit':'failure of this sufficient certificate is not a proof of easiness or ND impossibility'}
        budgets.append(row)
    a=3**48; b=2**77; assert a<b
    c=5/3-math.log2(3)
    return {'budgets':budgets,'exact_integer_coefficient_certificate':{'power3':str(a),'power2':str(b),
               'strict_less':a<b,'consequence':'1-h2(1/3)>1/16; m=16s+1 is rigorous'},
            'floating_diagnostic_only':{'c_approx':c,'inverse_approx':1/c},
            'state_units':'logical retained configuration bits; not measured RAM',
            'context_units':'payload range C_x differs from full data-bit capacity C_wire; query b and transport framing must be paid, neither is real model tokens'}


def run(path):
    assert not path.exists(),'immutable report exists; choose fresh run directory'
    started=time.perf_counter()
    nd=nd_exhaustive(); maps=exhaustive_encoders(); ledger=threshold_ledger()
    result={'passed':True,'scope':'bounded finite-state U_m; no standard P/NP/physical/human claim',
            'ND_protocol':nd,'deterministic_encoders':maps,'thresholds':ledger,
            'protocol':'m payload bits, b=ceil(log2(m+1)) late query bits, EOF; public m fixed before x/j',
            'model':'8 b-bit registers plus 64 control bits, all retained logical state encoded; static bounded-word transitions',
            'invalid_extension':'may reject on first extra symbol after m+b bits; valid U_m answers wait for EOF',
            'host_caveat':'Python iterators, nondeterministic path enumeration, digest/state audit and expected payload are passive simulation harness, not declared device RAM or writable answer aids.',
            'seconds':time.perf_counter()-started,'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'not_claimed':['minimal ND budget','exact finite witnesses at actual 200B context','real RAM capacity','human adequacy','standard P/NP','changed T3']}
    path.parent.mkdir(parents=True,exist_ok=True); path.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'passed':True,'ND_tasks':nd['tasks'],'ND_branches':nd['branches'],
                      'prefix_maps':maps['total_prefix_maps'],'seconds':result['seconds']},ensure_ascii=False))
    return 0


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report',type=Path,default=HERE.parent/'reports/finite-budget-tests-v1.json')
    raise SystemExit(run(parser.parse_args().report))
