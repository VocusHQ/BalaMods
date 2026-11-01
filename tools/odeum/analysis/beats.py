import sys, numpy as np, pretty_midi
NN=['C','Db','D','Eb','E','F','Gb','G','Ab','A','Bb','B']
pm=pretty_midi.PrettyMIDI(sys.argv[1]); B=0.4; S16=0.1
notes=[n for i in pm.instruments for n in i.notes]
on=np.array([n.start for n in notes]); w=np.array([n.velocity for n in notes],float)
ph=(np.angle(np.sum(w*np.exp(2j*np.pi*on/S16)))/(2*np.pi))*S16
print("16th phase offset s:",round(ph,3))
nb=int((pm.get_end_time())/B)+1
# per-beat lowest sustained note (bass) and top note (melody)
rows=[]
for b in range(nb):
    t=ph+b*B
    act=[n for n in notes if n.start<t+0.3 and n.end>t+0.05]
    bass=[n for n in act if n.pitch<52]; mel=[n for n in act if n.pitch>=60]
    bp=min(bass,key=lambda n:(n.pitch)).pitch if bass else None
    # melody: loudest-ish highest among notes starting near this beat
    st=[n for n in notes if t-0.05<=n.start<t+0.35 and n.pitch>=60]
    rows.append((b,bp,st))
stride=int(sys.argv[2]) if len(sys.argv)>2 else 28
for b0 in range(0,nb,stride):
    line=[]
    for b in range(b0,min(b0+stride,nb)):
        bp=rows[b][1]; line.append(NN[bp%12] if bp else '.')
    print(f"{ph+b0*B:6.1f}s |"+' '.join(f"{x:>2}" for x in line))
