"""Research-only charged ND collision witness on the frozen abstract BRAM."""
import sys,itertools,json,math,hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'a57-review'))
from bounded_vm_nd_v1 import run,Envelope,canonical,SUM

def append_guess(code,target=9):
    b=len(code)
    code += [['CONST',target,0],['CONST',10,1],['CONST',11,2],
             ['GUESSBIT',12],['MUL',target,target,11],['ADD',target,target,12],
             ['MUL',10,10,11],['JZ',10,b+9],['JMP',b+3]]

ND_COLLISION=[]
append_guess(ND_COLLISION)
ND_COLLISION.append(['MOV',14,9])
append_guess(ND_COLLISION)
b=len(ND_COLLISION)
ND_COLLISION += [
 ['CONST',0,0],['INPUT',1,0],['LT',3,14,1],['JZ',3,b+17],
 ['LT',3,9,1],['JZ',3,b+17],['EQ',3,14,9],['JZ',3,b+9],['JMP',b+17],
 ['CONST',2,1],['ADD',4,14,2],['INPUT',5,4],['ADD',4,9,2],['INPUT',6,4],
 ['EQ',7,5,6],['OUT',7],['HALT'],['OUT',0],['HALT']]

def profile(n,small_test=False):
    w=(n*n+1).bit_length()
    if small_test:w=max(6,w)
    return Envelope(32*n+512,math.isqrt(n),4096,1,w)

def paid_run(code,inputs,e,choices=()):
    # Reserve zero initialization AND one full raw-input acquisition pass.
    # These are declared abstract word-work charges, not host CPU measurements.
    initialization=16+e.memory_words
    acquisition=len(inputs)
    execution=Envelope(e.steps-initialization-acquisition,e.memory_words,e.description_bytes,e.output_words,e.word_bits)
    return run(code,inputs,execution,choices=choices)

def branch(xs,i,j,small=False):
    n=len(xs);e=profile(n,small);w=e.word_bits
    choices=[(v>>b)&1 for v in (i,j) for b in range(w-1,-1,-1)]
    r=paid_run(ND_COLLISION,[n,*xs],e,choices=choices)
    expected=(i<n and j<n and i!=j and xs[i]==xs[j])
    assert (r['status']=='halt' and r['output']==[1])==expected,(n,i,j,r)
    assert r['stats']['choice_bits']==2*w
    if i<n and j<n and i!=j:assert r['stats']['steps']==12*w+21,r
    init_words=16+e.memory_words
    assert r['stats']['steps']+init_words+n+1<=e.steps
    bit_bound=init_words*w+e.steps*(8*e.description_bytes+8*w+w*w)
    assert r['stats']['init_write_bits']+r['stats']['bit_charge']+(n+1)*w<=bit_bound
    return expected

def test():
    checks=0;arrays=0
    for n in range(2,5):
        e=profile(n,True);addresses=list(range(n))+[n,(1<<e.word_bits)-1]
        for xs in itertools.product(range(3),repeat=n):
            accepted=False
            for i,j in itertools.product(addresses,repeat=2):
                accepted=branch(xs,i,j,True) or accepted;checks+=1
            assert accepted==(len(set(xs))<n)
            arrays+=1
    big=[]
    for n in (128,129,255,256,1024):
        e=profile(n);mask=(1<<e.word_bits)-1
        distinct=list(range(n));last_duplicate=distinct.copy();last_duplicate[-1]=0
        all_same=[0]*n
        addresses=sorted(set([0,1,n//2,n-1,n,mask]))
        for xs in (distinct,last_duplicate,all_same):
            for i,j in itertools.product(addresses,repeat=2):
                branch(xs,i,j);checks+=1
            r=paid_run(SUM,[n,*xs],e)
            assert r['status']=='halt' and r['output']==[sum(xs)&mask]
            assert r['stats']['steps']==7*n+9
            assert r['stats']['steps']+16+e.memory_words+n+1<=e.steps
            arrays+=1
        big.append({'n':n,'w':e.word_bits,'memory_words':e.memory_words,'fuel':e.steps,'valid_nd_steps':12*e.word_bits+21,'sum_steps':7*n+9})
    return {'status':'pass','arrays':arrays,'branch_runs':checks,'nd_code_bytes':len(canonical(ND_COLLISION)),'nd_instruction_count':len(ND_COLLISION),'nd_code_sha256':hashlib.sha256(canonical(ND_COLLISION)).hexdigest(),'fullscan_SUM_same_profile':True,'initialization_reserved_in_total_fuel':True,'full_input_acquisition_pass_reserved':True,'small_test_width_floor_6_not_asymptotic_claim':True,'large_profiles':big,'coverage_certified':False}

if __name__=='__main__':print(json.dumps(test(),indent=2))
