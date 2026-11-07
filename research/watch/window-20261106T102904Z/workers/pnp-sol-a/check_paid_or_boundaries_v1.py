"""Additional boundary checks; no real-task capability claim."""
import hashlib
import json
from pathlib import Path
from bounded_vm_nd_v1 import Envelope, run
from paid_certificate_or_v1 import ND_OR, OR_SCAN

checks = 0
for n in (16, 31, 32, 63, 64, 127, 128, 255, 256, 1023, 4095):
    w = max(5, (n + 1).bit_length())
    for hit in (None, 0, n // 2, n-1):
        bits = [0] * n
        if hit is not None:
            bits[hit] = 1
        for j in sorted({0, n//2, n-1, n, (1 << w)-1}):
            out = run(ND_OR, [n, *bits], Envelope(6*w+12, 0, 512, 1, w),
                      choices=[(j >> b) & 1 for b in range(w-1,-1,-1)])
            expected = int(j < n and bits[j] == 1)
            assert out['status'] == 'halt' and out['output'] == [expected], (n,hit,j,out)
            assert out['stats']['choice_bits'] == w
            assert out['stats']['steps'] <= 6*w+12
            assert out['stats']['description_bytes'] <= 512
            checks += 1
        scan = run(OR_SCAN, [n, *bits], Envelope(7*n+8, 0, 512, 1, w))
        assert scan['status'] == 'halt' and scan['output'] == [int(hit is not None)]
        if hit is None:
            assert scan['stats']['steps'] == 7*n+8
        checks += 1
    if n >= 128:
        assert n > 6*w+12
print(json.dumps({'status': 'pass', 'boundary_checks': checks,
                  'cwd_independent': True, 'reality_coverage': False,
                  'nd_source_sha256': hashlib.sha256(Path(__file__).with_name('bounded_vm_nd_v1.py').read_bytes()).hexdigest()}, indent=2))
