import sys, numpy as np, librosa
y,sr=librosa.load(sys.argv[1],sr=22050,mono=True)
oenv=librosa.onset.onset_strength(y=y,sr=sr,hop_length=256)
fps=sr/256
ac=librosa.autocorrelate(oenv-oenv.mean(),max_size=int(fps*4))
lags=np.arange(len(ac))/fps
cand=[(ac[i],60/lags[i]) for i in range(int(fps*0.25),len(ac)-1) if ac[i]>ac[i-1] and ac[i]>ac[i+1]]
cand.sort(reverse=True)
print("autocorr peaks (strength, bpm):",[(round(a/ac[0],3),round(b,2)) for a,b in cand[:10]])
# fine tempo search: comb strength over bpm grid
best=[]
for bpm in np.arange(60,200,0.05):
    period=fps*60/bpm
    idx=np.arange(0,len(oenv)-1,period)
    # best phase
    sc=max(oenv[(idx+ph).astype(int).clip(0,len(oenv)-1)].mean() for ph in np.linspace(0,period,16,endpoint=False))
    best.append((sc,bpm))
best.sort(reverse=True); print("comb best:",[(round(a,3),round(b,2)) for a,b in best[:8]])
