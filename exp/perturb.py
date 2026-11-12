import numpy as np, cv2
def make_perturber(kind, n, seed):
    rng = np.random.default_rng(seed)
    if kind == 'clean': return lambda t, f: f
    if kind == 'illum':
        # sudden global gain steps (lights switching / auto-exposure) every 4-10 s at ~12 fps + slow drift
        gains = np.ones(n); t = 0; g = 1.0
        while t < n:
            L = int(rng.integers(48, 120)); gains[t:t+L] = g; t += L; g = float(rng.uniform(0.6, 1.4))
        drift = 1 + 0.1*np.sin(np.arange(n)*2*np.pi/300.0)
        G = gains*drift
        return lambda t, f: np.clip(f.astype(np.float32)*G[t], 0, 255).astype(np.uint8)
    if kind == 'jitter':
        d = rng.uniform(-4, 4, size=(n, 2))
        def p(t, f):
            M = np.float32([[1, 0, d[t,0]], [0, 1, d[t,1]]])
            return cv2.warpAffine(f, M, (f.shape[1], f.shape[0]), borderMode=cv2.BORDER_REFLECT)
        return p
    if kind == 'noise':
        def p(t, f):
            r = np.random.default_rng(seed*100003 + t)
            return np.clip(f.astype(np.float32) + r.normal(0, 10, f.shape), 0, 255).astype(np.uint8)
        return p
    raise ValueError(kind)
