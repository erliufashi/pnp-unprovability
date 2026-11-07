import itertools,json
checks=0
for m in range(1,13):
    for x in itertools.product((0,1),repeat=m):
        for j in range(m):
            # Query arrives after complete payload consumption; no payload cache.
            position=0
            for bit in iter(x):
                if position==j:
                    answer=bit
                    break
                position+=1
            assert answer==x[j]
            assert position+1==j+1<=m
            # Separately charged external storage implementation.
            disk=bytearray(x)  # one byte/bit in probe, m logical payload bits
            assert disk[j]==x[j] and len(disk)==m
            checks+=1
print(json.dumps({'scope':'finite implementation check, not all-m proof or physical RAM claim','m_range':[1,12],'cases':checks,'passed':True,'sequential_postquery_payload_reads':'j+1','random_access_postquery_payload_reads':1,'external_log_logical_payload_bits':'m','probe_external_log_host_bytes':'m'},indent=2))
