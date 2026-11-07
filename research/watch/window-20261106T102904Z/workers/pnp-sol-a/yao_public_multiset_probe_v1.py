"""Research-only executable counterexample to one proposed Yao distribution.
Input access is ordinary rereadable word RAM, not an opaque comparator.
No claim to solve unrestricted element distinctness or real-task coverage.
"""
from itertools import permutations
from math import isqrt
from pathlib import Path
import hashlib
import json
from bounded_vm_v1 import Envelope, canonical, run

# Difference between observed sum and sum(0,...,n-1), computed without DIV.
# Return 1 iff the difference is nonzero modulo 2^w (COLLISION promise).
SUM_DIFF = [
    ["CONST",0,0], ["INPUT",1,0], ["CONST",2,1],
    ["CONST",3,0], ["CONST",4,0], ["LT",5,3,1],
    ["JZ",5,14], ["ADD",6,3,2], ["INPUT",7,6],
    ["SUB",8,7,3], ["ADD",4,4,8], ["ADD",3,3,2],
    ["JMP",5], ["HALT"], ["LT",5,0,4], ["OUT",5], ["HALT"]
]


def execute(values):
    n = len(values)
    w = max(5, (n*n+1).bit_length())  # true profile without floor for n>=128
    m = isqrt(n)
    fuel = 32*n+512
    reserve = 16+m+n+1
    out = run(SUM_DIFF, [n,*values], Envelope(fuel-reserve,m,4096,1,w))
    assert out['status'] == 'halt', out
    assert out['stats']['steps'] == 8*n+10
    assert out['stats']['description_bytes'] == len(canonical(SUM_DIFF)) <= 4096
    total_steps = reserve+out['stats']['steps']
    assert total_steps <= fuel
    # Raw acquisition, init, source fetch, arithmetic are separate charged entries.
    total_bit_charge = out['stats']['bit_charge'] + out['stats']['init_write_bits'] + (n+1)*w
    cap = (16+m)*w + fuel*(8*4096+8*w+w*w)
    assert total_bit_charge <= cap
    assert out['stats']['input_reads'] == n+1
    assert out['stats']['data_reads'] == 0
    return out, {'word_bits':w, 'register_bits':16*w, 'array_bits':m*w,
                 'source_bytes':len(canonical(SUM_DIFF)), 'random_bits':0,
                 'reserved_init_and_acquisition_steps':reserve,
                 'total_word_steps':total_steps, 'fuel_cap':fuel,
                 'total_bit_charge':total_bit_charge, 'bit_cap':cap,
                 'charged_input_reads':2*(n+1)}


def main():
    permutations_checked = 0
    replacements_checked = 0
    for n in range(2,6):
        for p in permutations(range(n)):
            out,_ = execute(p)
            assert out['output'] == [0]
            permutations_checked += 1
            for source in range(n):
                for target in range(n):
                    if source == target:
                        continue
                    x = list(p)
                    x[target] = p[source]
                    out,_ = execute(x)
                    assert out['output'] == [1], (n,p,source,target,out)
                    assert len(set(x)) == n-1
                    replacements_checked += 1
    fullscale = []
    for n in (128,255,256,1024,4095):
        base = list(range(n))
        for x in (base, list(reversed(base))):
            assert execute(x)[0]['output'] == [0]
        duplicate = base[:]
        duplicate[-1] = 0
        out,ledger = execute(duplicate)
        assert out['output'] == [1]
        # Out-of-promise single duplicate plus a compensating fresh value.
        balanced = base[:]
        balanced[1] = 0
        balanced[-1] = n
        assert len(set(balanced)) == n-1
        assert sum(balanced) == sum(base)
        assert execute(balanced)[0]['output'] == [0]
        fullscale.append({'n':n, 'ledger':ledger,
                          'outside_promise_single_collision_is_missed':True})
    return {'status':'pass', 'permutations_checked':permutations_checked,
            'single_replacements_checked':replacements_checked,
            'all_promised_inputs_classified_exactly':True,
            'worst_case_ED_solved':False,'real_coverage_claim':False,
            'program_code_bytes':len(canonical(SUM_DIFF)),
            'program_sha256':hashlib.sha256(canonical(SUM_DIFF)).hexdigest(),
            'vm_sha256':hashlib.sha256(Path(__file__).with_name('bounded_vm_v1.py').read_bytes()).hexdigest(),
            'fullscale':fullscale}


if __name__ == '__main__':
    print(json.dumps(main(),indent=2))
