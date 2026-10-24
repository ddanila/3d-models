"""Circular 3D lead fillets with explicit radius and tessellation error bounds."""
import math


def fillet(points, radius, chord_error):
    """Return a sampled centerline and bend descriptors; never shrink a bend to fit.

    Radius is measured at the wire centerline. Coincident consecutive points are
    removed. Endpoints are preserved; reversals and overlapping bends are invalid.
    The chord-error bound covers centerline approximation, not forming tolerance.
    """
    if not (math.isfinite(radius) and radius > 0 and
            math.isfinite(chord_error) and 0 < chord_error < radius):
        raise ValueError('Require positive radius and chord error smaller than radius')
    clean = []
    for p in points:
        if len(p) != 3 or not all(math.isfinite(x) for x in p):
            raise ValueError('Invalid lead point')
        if not clean or math.dist(p, clean[-1]) > 1e-12:
            clean.append(list(p))
    if len(clean) < 2:
        raise ValueError('Lead requires two distinct points')
    lengths = [math.dist(a, b) for a, b in zip(clean, clean[1:])]
    bends = {}
    for i in range(1, len(clean)-1):
        a, b, c = clean[i-1:i+2]
        u = [(b[k]-a[k])/lengths[i-1] for k in range(3)]
        v = [(c[k]-b[k])/lengths[i] for k in range(3)]
        cosine = max(-1., min(1., sum(x*y for x, y in zip(u, v))))
        angle = math.acos(cosine)
        if angle < 1e-8:
            continue
        if math.pi-angle < 1e-8:
            raise ValueError('Lead reverses direction')
        offset = radius*math.tan(angle/2)
        start = [b[k]-offset*u[k] for k in range(3)]
        end = [b[k]+offset*v[k] for k in range(3)]
        normal = [(v[k]-cosine*u[k])/math.sin(angle) for k in range(3)]
        center = [start[k]+radius*normal[k] for k in range(3)]
        count = max(1, math.ceil(angle/(2*math.acos(1-chord_error/radius))))
        arc = [start]
        for j in range(1, count):
            phi = angle*j/count
            arc.append([center[k]+(start[k]-center[k])*math.cos(phi)+radius*u[k]*math.sin(phi) for k in range(3)])
        arc.append(end)
        bends[i] = {'vertexIndex': i, 'radiusMm': radius, 'centerMm': center,
                    'angleRadians': angle, 'tangentOffsetMm': offset,
                    'maximumChordErrorMm': radius*(1-math.cos(angle/count/2)),
                    'points': arc}
    for i, length in enumerate(lengths):
        used = sum(bends[j]['tangentOffsetMm'] for j in (i, i+1) if j in bends)
        if used > length+1e-10:
            raise ValueError(f'Bends require {used:.6g} mm on segment {i} of length {length:.6g} mm')
    output = [clean[0]]
    for i in range(1, len(clean)-1):
        candidates = bends[i]['points'] if i in bends else [clean[i]]
        for p in candidates:
            if math.dist(output[-1], p) > 1e-12:
                output.append(p)
    if math.dist(output[-1], clean[-1]) > 1e-12:
        output.append(clean[-1])
    return output, [{k: v for k, v in bend.items() if k != 'points'} for bend in bends.values()]
