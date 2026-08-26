import sys,time,json
from OCP.STEPControl import STEPControl_Reader
from OCP.IFSelect import IFSelect_RetDone
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_SOLID, TopAbs_COMPOUND, TopAbs_COMPSOLID, TopAbs_SHELL
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp
p=sys.argv[1]
t=time.time();r=STEPControl_Reader(); status=r.ReadFile(p); print('readstatus',int(status),time.time()-t,flush=True)
if status!=IFSelect_RetDone: raise SystemExit(2)
t=time.time(); n=r.TransferRoots(); print('transfer',n,time.time()-t,flush=True)
sh=r.OneShape(); print('oneshape',time.time()-t,flush=True)
exp=TopExp_Explorer(sh,TopAbs_SOLID); count=0; valid=0; vols=0.0
while exp.More():
 s=exp.Current();count+=1
 if BRepCheck_Analyzer(s).IsValid(): valid+=1
 gp=GProp_GProps();BRepGProp.VolumeProperties_s(s,gp);vols+=gp.Mass()
 exp.Next()
b=Bnd_Box();BRepBndLib.Add_s(sh,b); xmin,ymin,zmin,xmax,ymax,zmax=b.Get()
print(json.dumps({'solid_count':count,'valid_solids':valid,'volume_mm3':vols,'bbox':[xmin,ymin,zmin,xmax,ymax,zmax],'elapsed':time.time()-t},indent=2),flush=True)
