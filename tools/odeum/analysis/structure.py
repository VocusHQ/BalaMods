import sys, numpy as np, librosa
y,sr=librosa.load(sys.argv[1],sr=22050,mono=True)
hop=256; fps=sr/hop
oenv=librosa.onset.onset_strength(y=y,sr=sr,hop_length=hop)
pulse=0.2  # 300/min common grid
P=fps*pulse
# best phase
phs=np.linspace(0,P,40,endpoint=False)
sc=[oenv[(np.arange(0,len(oenv)-P,P)+ph).astype(int)].mean() for ph in phs]
ph=phs[int(np.argmax(sc))]; print("grid phase s:",ph/fps)
idx=(np.arange(0,len(oenv)-P,P)+ph).astype(int)
acc=oenv[idx]
# accent pattern folded by 3,4,5,6,12
for m in (2,3,4,5,6,8,12,15,24):
    f=[acc[i::m].mean() for i in range(m)]
    print(m,' '.join(f"{v:.2f}" for v in f))
C=librosa.feature.chroma_cqt(y=y,sr=sr,hop_length=hop)
Cs=np.stack([C[:,i:i+int(P)].mean(1) for i in idx]).T
Cs=Cs/ (np.linalg.norm(Cs,axis=0)+1e-9)
n=Cs.shape[1]
rep=[(np.mean(np.sum(Cs[:,:n-L]*Cs[:,L:],axis=0)),L) for L in range(6,n//2)]
rep.sort(reverse=True); print("repeat lags (pulses, s):",[(round(a,3),L,round(L*pulse,1)) for a,L in rep[:12]])
