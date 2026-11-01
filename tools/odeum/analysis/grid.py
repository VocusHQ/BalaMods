import sys, numpy as np, pretty_midi
pm=pretty_midi.PrettyMIDI(sys.argv[1])
notes=sorted([n for i in pm.instruments for n in i.notes],key=lambda n:n.start)
on=np.array([n.start for n in notes]); w=np.array([n.velocity*(n.end-n.start)**0.5 for n in notes])
print(len(notes),"notes, range",min(n.pitch for n in notes),max(n.pitch for n in notes))
res=[]
for bpm in np.arange(70,170,0.02):
    sub=60/bpm/4  # 16th
    ph=np.angle(np.sum(w*np.exp(2j*np.pi*on/sub)))
    res.append((abs(np.sum(w*np.exp(2j*np.pi*on/sub)))/w.sum(),bpm,ph))
res.sort(reverse=True); print([(round(a,3),round(b,2)) for a,b,_ in res[:8]])
# triplet test
for bpm in (100,150,75):
  for div,name in((2,'8th'),(3,'8th-trip'),(4,'16th'),(6,'16th-trip')):
    sub=60/bpm/div; print(bpm,name,round(abs(np.sum(w*np.exp(2j*np.pi*on/sub)))/w.sum(),3))
