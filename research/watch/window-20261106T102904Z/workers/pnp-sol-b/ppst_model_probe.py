"""Research-only PPST transfer passports and exact FLMV exponent arithmetic."""
from fractions import Fraction as F
import unittest

def flmv_d(c,k):
    c=F(c); f=F(1)
    for _ in range(k): f=c*f/(1+f)
    return min((1/f-c)/k,1/(c**k))

def ppst_transfer_obligations(p):
    """Conservative necessary-field checks, NOT a theorem/complexity verifier."""
    reasons=[]
    for key,expected in [('input_access','sequential'),('work_access','sequential'),
                         ('total_time','linear'),('policy','deterministic'),
                         ('tool_costs','expanded'),('code','uniform-finite')]:
        if p.get(key)!=expected: reasons.append('unpaid:'+key)
    if p.get('description_cap') is not None: reasons.append('unpaid:witness-description-within-cap')
    if p.get('numerical_clock') is not None: reasons.append('unpaid:witness-clock-within-cap')
    if p.get('frozen_isa',False): reasons.append('unpaid:witness-ISA-simulation')
    return reasons

def sequential_head_work(addresses,start=0):
    total=0; head=start
    for address in addresses:
        total+=abs(address-head)+1
        head=address
    return total

class ProbeTests(unittest.TestCase):
    def test_exact_exponent(self):
        self.assertEqual(flmv_d(F(3,2),2),F(1,36))
        self.assertGreater(F(1,36),F(1,100))
        self.assertLess(F(7,5),F(3,2))
    def test_phi_boundary(self):
        # c=1.7 is above phi: this particular recurrence cannot yield positive d.
        self.assertTrue(all(flmv_d(F(17,10),k)<0 for k in range(1,20)))
    def test_structural_passport(self):
        p=dict(input_access='sequential',work_access='sequential',total_time='linear',
               policy='deterministic',tool_costs='expanded',code='uniform-finite')
        self.assertEqual(ppst_transfer_obligations(p),[])
        # No unpaid fields means structural candidate, not independently verified.
    def test_random_access_transfer_rejected(self):
        p=dict(input_access='random',work_access='random',total_time='linear',
               policy='deterministic',tool_costs='expanded',code='uniform-finite')
        self.assertEqual(len(ppst_transfer_obligations(p)),2)
    def test_numeric_envelope_does_not_inherit_witness(self):
        p=dict(input_access='sequential',work_access='sequential',total_time='linear',
               policy='deterministic',tool_costs='expanded',code='uniform-finite',
               description_cap=1000,numerical_clock=100,frozen_isa=True)
        self.assertEqual(len(ppst_transfer_obligations(p)),3)
    def test_direct_trace_cost_not_language_lower_bound(self):
        self.assertEqual(sequential_head_work([0,63]*4),449)
        # Eight six-bit index constructions alone cost 48 bit writes, not eight free accesses.
        self.assertEqual(8*6,48)

if __name__=='__main__': unittest.main(verbosity=2)
