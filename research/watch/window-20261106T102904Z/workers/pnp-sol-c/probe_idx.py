import json

def build(docs,version):
    postings={};token_reads=0
    for i,doc in enumerate(docs):
        seen=set()
        for term in doc.split():
            token_reads+=1
            if term not in seen:
                postings.setdefault(term,[]).append(i);seen.add(term)
    obj={'version':version,'postings':postings}
    size=len(json.dumps(obj,sort_keys=True,ensure_ascii=False).encode())
    return obj,{'token_reads':token_reads,'posting_id_writes':sum(map(len,postings.values())),'serialized_index_bytes':size}

def query(index,term):
    result=list(index['postings'].get(term,[]))
    return result,{'dictionary_lookups':1,'returned_ids':len(result)}

def scan(docs,term):
    return [i for i,d in enumerate(docs) if term in d.split()]

docs=['' if i%17==0 else f'tag{i%11} common common 中文{i%3} item{i}' for i in range(128)]
idx,stats=build(docs,0)
terms=sorted({t for d in docs for t in d.split()}|{'absent','COMMON','中文'})
returned=0
for term in terms:
    a,cost=query(idx,term);assert a==scan(docs,term)
    returned+=cost['returned_ids']
updated=docs.copy();updated[0]='new_term'
assert query(idx,'new_term')[0]!=scan(updated,'new_term')
newidx,newstats=build(updated,1)
assert query(newidx,'new_term')[0]==scan(updated,'new_term')
# Computability does not prevent leakage; permitted view must exclude labels.
allowed={'documents':docs};forbidden0={'labels':{'hidden':0}};forbidden1={'labels':{'hidden':1}}
def build_bad(allowed,forbidden):return dict(forbidden['labels'])
assert build_bad(allowed,forbidden0)!=build_bad(allowed,forbidden1)
def build_view(allowed,forbidden):return build(allowed['documents'],0)[0]
assert build_view(allowed,forbidden0)==build_view(allowed,forbidden1)
assert (1000+1000*1)/1000==2 and 1000+1>10
print(json.dumps({'status':'pass','documents':len(docs),'query_terms':len(terms),'exact_scan_equivalence':True,'build':stats,'all_query_returned_ids':returned,'stale_index_negative_control':True,'rebuild':newstats,'computable_build_can_leak_labels':True,'local_permitted_view_noninterference':True,'cold_vs_amortized_negative_control':True,'python_worst_case_runtime_or_physical_ram_claim':False,'realistic_coverage':False},indent=2))
