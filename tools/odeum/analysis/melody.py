import sys, numpy as np, pretty_midi
NN=['C','Db','D','Eb','E','F','Gb','G','Ab','A','Bb','B']
pm=pretty_midi.PrettyMIDI(sys.argv[1]); BAR=2.8; E=0.2
notes=[n for i in pm.instruments for n in i.notes if n.pitch>=62 and n.end-n.start>=0.12 and n.velocity>=int(sys.argv[3] if len(sys.argv)>3 else 40)]
bars=[int(x) for x in sys.argv[2].split(',')]
for b in range(bars[0],bars[1]+1):
    cells=[]
    for k in range(14):
        t=(b-1)*BAR+k*E
        st=[n for n in notes if t-0.06<=n.start<t+E-0.06]
        if st:
            n=max(st,key=lambda n:n.pitch); cells.append(f"{NN[n.pitch%12]}{n.pitch//12-1}")
        else:
            hold=[n for n in notes if n.start<t and n.end>t+0.1]
            cells.append(' ~ ' if hold else ' . ')
    print(f"bar{b:3d} |"+' '.join(f"{c:>3}" for c in cells))
