import sys,glob,os,numpy as np,soundfile as sf
d=sys.argv[1]; secs=[(0,11.2),(11.2,58.8),(58.8,61.6),(61.6,100.8),(100.8,128.8),(128.8,173.6)]
print("stem      "+' '.join(f"{a:>5.0f}-{b:<5.0f}" for a,b in secs))
for f in sorted(glob.glob(d+'/*.wav')):
    y,sr=sf.read(f); y=y.mean(1) if y.ndim>1 else y
    print(f"{os.path.basename(f):10s}"+' '.join(f"{20*np.log10(np.sqrt(np.mean(y[int(a*sr):int(b*sr)]**2))+1e-9):11.1f}" for a,b in secs))
    if 'drums' in f: print("  len",len(y)/sr)
