import sys, numpy as np, pretty_midi
NN=['C','Db','D','Eb','E','F','Gb','G','Ab','A','Bb','B']
pm=pretty_midi.PrettyMIDI(sys.argv[1]); BAR=2.8; ph=float(sys.argv[2]) if len(sys.argv)>2 else 0.0
notes=[n for i in pm.instruments for n in i.notes]
tmpl={}
for r in range(12):
    for q,iv in (('',(0,4,7)),('m',(0,3,7)),('7',(0,4,7,10)),('m7',(0,3,7,10)),('maj7',(0,4,7,11)),('dim',(0,3,6)),('sus4',(0,5,7))):
        v=np.zeros(12); v[[ (r+i)%12 for i in iv]]=1; tmpl[NN[r]+q]=v/np.linalg.norm(v)
nbar=int(pm.get_end_time()/BAR)+1
for b in range(nbar):
    out=[]
    for h in (0,1):
        t0=ph+b*BAR+h*BAR/2; t1=t0+BAR/2
        pc=np.zeros(12); bass=np.zeros(12)
        for n in notes:
            ov=min(n.end,t1)-max(n.start,t0)
            if ov>0:
                pc[n.pitch%12]+=ov*n.velocity
                if n.pitch<52: bass[n.pitch%12]+=ov*n.velocity
        if pc.sum()==0: out.append('   --   '); continue
        v=pc/np.linalg.norm(pc)
        best=max(tmpl,key=lambda k:tmpl[k]@v - (0.03 if len(k)>3 else 0))
        bn=NN[int(np.argmax(bass))] if bass.sum() else '?'
        top=' '.join(NN[i] for i in np.argsort(pc)[::-1][:4])
        out.append(f"{best:>6}/{bn:<2} [{top}]")
    print(f"bar{b+1:3d} {ph+b*BAR:6.1f}s  "+'   |   '.join(out))
