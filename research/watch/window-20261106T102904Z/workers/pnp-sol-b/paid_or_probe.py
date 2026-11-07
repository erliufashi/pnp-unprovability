"""B55 research VM: raw-bit indexed input, paid index construction, finite program."""
import json
from dataclasses import dataclass
import unittest

@dataclass
class Trace:
    accept:bool
    steps:int
    input_reads:int
    index_bits:int

def nd_program(m):
    # GUESS_BIT is exactly two write-bit successors; no answer-bearing instruction.
    return [{'op':'GUESS_BIT','next':i+1} for i in range(m)]+[
        {'op':'SEEK','next':m+1},
        {'op':'READ_BRANCH','if0':m+3,'if1':m+2},
        {'op':'ACCEPT'}, {'op':'REJECT'}]

def encode_program(m):
    return json.dumps(nd_program(m),sort_keys=True,separators=(',',':')).encode()

def run_nd_branch(bits,m,address):
    if len(bits)!=1<<m or not 0<=address<len(bits): raise ValueError('invalid fixed-shape input')
    index=[]; steps=0
    for i in range(m-1,-1,-1):
        index.append((address>>i)&1); steps+=1
    # One index-tape SEEK primitive is part of the frozen model, not a free oracle.
    head=0
    for b in index: head=2*head+b
    steps+=1
    answer=bool(bits[head]); steps+=1 # READ_BRANCH observes one raw bit
    steps+=1 # ACCEPT or REJECT
    return Trace(answer,steps,1,len(index))

class ORTests(unittest.TestCase):
    def test_exhaustive_all_small_inputs_and_branches(self):
        m=3; N=1<<m
        for x in range(1<<N):
            bits=[(x>>i)&1 for i in range(N)]
            accepted=any(run_nd_branch(bits,m,j).accept for j in range(N))
            self.assertEqual(accepted,any(bits))
    def test_all_singletons_and_zero(self):
        m=8; N=1<<m
        zeros=bytearray(N)
        self.assertFalse(any(run_nd_branch(zeros,m,j).accept for j in range(N)))
        for i in range(N):
            x=bytearray(N); x[i]=1
            self.assertTrue(run_nd_branch(x,m,i).accept)
            self.assertEqual(run_nd_branch(x,m,i).steps,11)
    def test_frozen_profile(self):
        # N=65536 raw input bits, common total step clock 16384.
        m=16; N=1<<m; T=16384
        x=bytearray(N); x[-1]=1
        trace=run_nd_branch(x,m,N-1)
        self.assertEqual(trace,Trace(True,19,1,16))
        self.assertLessEqual(len(encode_program(m)),8192)
        self.assertLess(T,N/3)
    def test_adversarial_deterministic_transcript(self):
        N=32; q=12
        queried=list(range(q))
        x0=[0]*N; x1=[0]*N; x1[q]=1
        self.assertEqual([x0[i] for i in queried],[x1[i] for i in queried])
        self.assertNotEqual(any(x0),any(x1))
    def test_randomized_coverage_mass(self):
        # Each random seed can inspect at most q distinct positions on all-zero input.
        N=12; q=3
        seeds=[set((s+i)%N for i in range(q)) for s in range(N)]
        probs=[sum(i in ss for ss in seeds)/len(seeds) for i in range(N)]
        self.assertAlmostEqual(sum(probs),q)
        self.assertLess(min(probs),1/3)

if __name__=='__main__':
    unittest.main(verbosity=2)
