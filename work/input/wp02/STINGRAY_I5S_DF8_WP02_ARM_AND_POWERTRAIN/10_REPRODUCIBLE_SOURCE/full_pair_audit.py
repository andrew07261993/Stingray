import importlib.util,sys,itertools,time,csv,json
p='/mnt/data/wp02_work/build_wp02.py';spec=importlib.util.spec_from_file_location('m',p);m=importlib.util.module_from_spec(spec);sys.modules['m']=m;spec.loader.exec_module(m)
parts,_=m.create_parts(m.DEFAULT_DF8_ROOT)

def ov(a,b,tol=1e-7):
 return not(a.xmax < b.xmin+tol or b.xmax < a.xmin+tol or a.ymax < b.ymin+tol or b.ymax < a.ymin+tol or a.zmax < b.zmin+tol or b.zmax < a.zmin+tol)
for st in ('STOWED','DEPLOYED'):
 print('STATE',st,flush=True)
 cache={q.item:[(x,x.BoundingBox()) for x in q.shape(st).Solids()] for q in parts}
 count=0; positive=[]; zero=[]
 for a,b in itertools.combinations(parts,2):
  candidates=[]
  for i,(sa,ba) in enumerate(cache[a.item]):
   for j,(sb,bb) in enumerate(cache[b.item]):
    if ov(ba,bb):candidates.append((i,j,sa,sb))
  if not candidates:continue
  count+=1
  vol=0.0;t=time.time()
  for i,j,sa,sb in candidates:
   try: vol += m.safe_common_volume(sa,sb)
   except Exception as e: print('ERR',st,a.item,b.item,i,j,e,flush=True)
  dt=time.time()-t
  rec=(a.item,b.item,a.name,b.name,len(candidates),vol,dt)
  print('PAIR',*rec,flush=True)
  (positive if vol>1e-6 else zero).append(rec)
 print('SUMMARY',st,'pairs',count,'positive',len(positive),'zero',len(zero),flush=True)
 print('POSITIVES',json.dumps(positive),flush=True)
