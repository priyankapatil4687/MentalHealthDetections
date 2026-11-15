import numpy as np
from scipy import stats


def wilson_ci(k, n, z=1.96):
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return (float(max(0.0, centre - half)), float(min(1.0, centre + half)))


def chi_square_test(ct):
    """Chi-square test of independence on a contingency table (DataFrame)."""
    ct = ct.loc[ct.sum(axis=1) > 0, ct.sum(axis=0) > 0]
    if ct.shape[0] < 2 or ct.shape[1] < 2:
        return None
    chi2, p, dof, expected = stats.chi2_contingency(ct.values)
    n = float(ct.values.sum())
    k = min(ct.shape) - 1
    return {
        "chi2": float(chi2),
        "p_value": float(p),
        "dof": int(dof),
        "n": n,
        "cramers_v": float(np.sqrt(chi2 / (n * k))),
        "share_cells_expected_lt5": float((expected < 5).mean()),
    }


def kruskal_test(groups, min_n=30):
    """Kruskal-Wallis across groups (dict name -> values). Returns None if not testable."""
    kept = {k: np.asarray(v, float) for k, v in groups.items() if len(v) >= min_n}
    if len(kept) < 2:
        return None
    try:
        h, p = stats.kruskal(*kept.values())
    except ValueError:
        return None
    n = sum(len(v) for v in kept.values())
    return {
        "H": float(h),
        "p_value": float(p),
        "n": int(n),
        "groups": len(kept),
        "epsilon_squared": float(h * (n + 1) / (n * n - 1)),
    }


def benjamini_hochberg(pvals):
    p = np.asarray(pvals, float)
    n = len(p)
    if n == 0:
        return p
    order = np.argsort(p)
    ranked = p[order] * n / np.arange(1, n + 1)
    adj = np.minimum.accumulate(ranked[::-1])[::-1]
    out = np.empty(n)
    out[order] = np.minimum(adj, 1.0)
    return out
