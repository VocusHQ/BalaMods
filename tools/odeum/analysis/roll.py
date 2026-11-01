import sys,numpy as np,pretty_midi,matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
NN=['C','Db','D','Eb','E','F','Gb','G','Ab','A','Bb','B']
mid,b0,b1,out=sys.argv[1],int(sys.argv[2]),int(sys.argv[3]),sys.argv[4]
BAR=2.8; t0=(b0-1)*BAR; t1=b1*BAR
pm=pretty_midi.PrettyMIDI(mid); ns=[n for i in pm.instruments for n in i.notes if n.end>t0 and n.start<t1 and n.pitch>=int(sys.argv[5] if len(sys.argv)>5 else 0)]
lo=min(n.pitch for n in ns)-1; hi=max(n.pitch for n in ns)+1
fig,ax=plt.subplots(figsize=(22,10),dpi=80)
for n in ns: ax.add_patch(plt.Rectangle((n.start,n.pitch-0.4),n.end-n.start,0.8,color=plt.cm.viridis(n.velocity/127)))
for b in range(b0,b1+2):
    x=(b-1)*BAR; ax.axvline(x,color='r',lw=1.5); ax.text(x+0.05,hi,str(b),color='r')
    for k in range(1,7): ax.axvline(x+k*0.4,color='#ccc',lw=0.5)
ax.set_xlim(t0,t1); ax.set_ylim(lo,hi+1)
ax.set_yticks(range(lo,hi+1)); ax.set_yticklabels([NN[p%12]+str(p//12-1) for p in range(lo,hi+1)],fontsize=7)
for p in range(lo,hi+1):
    if p%12 in (1,3,6,8,10): ax.axhspan(p-0.5,p+0.5,color='#f2f2f2',zorder=0)
plt.tight_layout(); plt.savefig(out)
