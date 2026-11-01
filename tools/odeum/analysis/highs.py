"""High-frequency check (Locked's hard rule: nothing piercing). Prints band levels relative to each file's
total level, so a draft can be compared with the original Balatro track.
Usage: python highs.py a.mp3 b.ogg ...  [--from S --to S]"""
import sys, subprocess, numpy as np, scipy.signal as ss
args=[a for a in sys.argv[1:] if not a.startswith("--")]
opt=dict(zip(sys.argv[1::1],sys.argv[2::1])); t0=float(opt.get("--from",0)); t1=opt.get("--to")
for f in args:
    raw=subprocess.run(["ffmpeg","-v","error","-i",f,"-f","f32le","-ac","1","-ar","44100","-"],capture_output=True,check=True).stdout
    y=np.frombuffer(raw,np.float32).astype(float); y=y[int(t0*44100):int(float(t1)*44100) if t1 else None]
    tot=20*np.log10(np.sqrt((y**2).mean())+1e-9); r=[]
    for lo,hi in ((2000,4000),(4000,8000),(8000,16000)):
        x=ss.sosfiltfilt(ss.butter(4,[lo,hi],btype='band',fs=44100,output='sos'),y); r.append(20*np.log10(np.sqrt((x**2).mean())+1e-9)-tot)
    print(f"{f.split('/')[-1][:44]:44s} 2-4k {r[0]:6.1f}  4-8k {r[1]:6.1f}  8-16k {r[2]:6.1f}  dB vs total")
