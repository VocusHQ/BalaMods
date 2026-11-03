"""Shared "live band" post-processing for the Odeum pack modules (Vesper, Basilicus).

  - humanize: small timing and velocity wobble, seeded per track (reproducible), so parts breathe
  - key change: shift chosen spans up a semitone (pitched tracks only, drums untouched)
  - break: everything stops after a unison hit, only a pickup (late notes) leads back in
Notes are lmmsgen tuples (tick, key, length, velocity).
"""
import random

from lmmsgen import BEAT


class Live:
    def __init__(self, lead_in, span):
        self.lead_in, self.span = lead_in, span

    def where(self, tick):
        """(span, beat in span) of a tick."""
        b = tick / BEAT - self.lead_in
        s = int(b // self.span)
        return s, b - s * self.span

    def humanize(self, notes, seed, t=1.5, v=6):
        rng = random.Random(seed)
        return [(max(0, tick + int(round(rng.uniform(-t, t)))), key, ln, max(1, min(127, int(vel + rng.uniform(-v, v)))))
                for tick, key, ln, vel in notes]

    def shift(self, notes, spans, semis=1):
        return [(tick, key + semis if self.where(tick)[0] in spans else key, ln, vel) for tick, key, ln, vel in notes]

    def cut(self, notes, span, hit=4.0, ring=.6, back=7.0):
        """Break in `span`: notes up to the hit stay (cut off `ring` beats after it), nothing between, then the pickup."""
        out = []
        for tick, key, ln, vel in notes:
            s, b = self.where(tick)
            if s == span and hit + .05 < b < back - .01:
                continue
            end_ticks = (hit + ring - b) * BEAT
            if s == span and b <= hit + .05 and ln > end_ticks:
                ln = max(8, int(end_ticks))
            if s == span - 1 and ln > (self.span - b + hit + ring) * BEAT:  # a note held over from the span before
                ln = max(8, int((self.span - b + hit + ring) * BEAT))
            out.append((tick, key, ln, vel))
        return out
