import sys, numpy as np, librosa
NOTES=['C','C#','D','Eb','E','F','F#','G','Ab','A','Bb','B']
maj=np.array([6.35,2.23,3.48,2.33,4.38,4.09,2.52,5.19,2.39,3.66,2.29,2.88]); mnr=np.array([6.33,2.68,3.52,5.38,2.60,3.53,2.54,4.75,3.98,2.69,3.34,3.17])
for p in sys.argv[1:]:
    y,sr=librosa.load(p,sr=22050,mono=True)
    dur=len(y)/sr
    tempo,beats=librosa.beat.beat_track(y=y,sr=sr)
    ch=librosa.feature.chroma_cqt(y=y,sr=sr).mean(1)
    best=max(((np.corrcoef(np.roll(t,k),ch)[0,1],NOTES[k]+q) for t,q in((maj,' major'),(mnr,' minor')) for k in range(12)))
    rms=librosa.feature.rms(y=y)[0]; cent=librosa.feature.spectral_centroid(y=y,sr=sr)[0]
    print(f"{p.split('/')[-1]}: {dur:.2f}s tempo~{float(np.atleast_1d(tempo)[0]):.1f} key~{best[1]} ({best[0]:.2f}) rms={rms.mean():.3f} centroid={cent.mean():.0f}Hz")
    print("  chroma:", ' '.join(f"{NOTES[i]}:{ch[i]/ch.max():.2f}" for i in range(12)))
