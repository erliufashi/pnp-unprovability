#!/usr/bin/env python3
"""Structural mask/shape counterexample; not an actual softmax/GPU claim."""
import argparse
import hashlib
import json
from pathlib import Path


def add(a,b): return max(-4,min(4,a+b))


def midpoint_tree(values):
    if len(values)==1: return values[0]
    split=len(values)//2
    return add(midpoint_tree(values[:split]),midpoint_tree(values[split:]))


def run(path):
    original=[0,4,4,-4]; extended=original+[0,0]
    old=midpoint_tree(original); new=midpoint_tree(extended)
    assert old==4 and new==0 and old!=new
    assert all(add(0,x)==x and add(x,0)==x for x in range(-4,5))
    assert extended[:len(original)]==original and extended[-2:]==[0,0]
    explicit_old=add(add(0,4),add(4,-4))
    explicit_new=add(add(0,add(4,4)),add(-4,add(0,0)))
    assert old==explicit_old and new==explicit_new
    report={'passed':True,'word_codes':list(range(-4,5)),
            'original_leaves':original,'masked_extended_leaves':extended,
            'original_code':old,'recomputed_code':new,'zero_is_strict_identity':True,
            'future_content_exposed':False,'changed_feature':'global-length-dependent parentheses',
            'scope':'generic masked reduction; not measured softmax/GPU/200B',
            'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'passed':True,'old_code':old,'new_code':new,'report':str(path)},ensure_ascii=False))
    return 0


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report',type=Path,default=Path(__file__).resolve().parents[1]/'reports/causal-contract-tests-v1.json')
    raise SystemExit(run(parser.parse_args().report))
