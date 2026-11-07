"""Exact integer checks for a huge mathematical dimension, not execution on that input."""
import json

def ceil_log2(x):
    assert x>0
    return (x-1).bit_length()

k=38
Q0=(1<<40)*k**8
r=Q0**(5*k*k)
D=4*Q0**(7*k*k)
d=ceil_log2(D)
E=4*(d+100)
n=1<<E
M=1<<(E//2)
w=2*E+1
B=4096
F=32*n+512
I=16+M
Qbits=I*w+F*(8*B+8*w+w*w)
S_cap=(M+32)*w+(1<<20)+4*ceil_log2(F+1)+2*ceil_log2(n+M+32)+2*ceil_log2(Qbits+1)
S_simple=64*E*M
checks={
 'k_at_least_8':k>=8,
 'q_bound_exact_Q0':Q0==(1<<40)*k**8,
 'r_corollary_54':r==Q0**(5*k*k),
 'r_implies_theorem_53':r>=200*k*k*Q0**(4*k*k),
 'n_at_least_r':n>=r,
 'foot_lower_bound_at_least_8':n>=16*Q0**(2*k*k),
 'sqrt_q_at_most_quarter':Q0>=16,
 'full_time_below_k_minus_2_n':F<=(k-2)*n,
 'exact_word_width':(n*n+1).bit_length()==w,
 'complete_bp_space_below_simple_bound':S_cap<=S_simple,
 'source_required_space_exceeds_complete_cap':S_cap*D<n,
 'source_required_space_exceeds_simple_bound':S_simple*D<n,
 'paid_nd_fits':12*w+21+I+n+1<=F,
 'paid_sum_fits':7*n+9+I+n+1<=F,
 'bytecode_and_address_fit':B>=512 and w>=6,
}
assert all(checks.values()),checks
print(json.dumps({'status':'pass','k':k,'Q0_decimal':Q0,'r_bit_length':r.bit_length(),'D_bit_length':D.bit_length(),'d':d,'E':E,'dimension':'n=2^E','mutable_words':'M=2^(E/2)','word_bits':w,'fuel':'F=32*2^E+512','description_bytes':B,'complete_state_formula':'(M+32)*w+2^20+4*ceil_log2(F+1)+2*ceil_log2(n+M+32)+2*ceil_log2(Qbits+1)','simple_space_cap':'64*E*2^(E/2)','checks':checks,'scope':'exact arithmetic on compact integers; no array of length n, no physical feasibility or coverage claim'},indent=2))
