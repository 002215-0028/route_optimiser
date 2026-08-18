import math
import random
from typing import List, Tuple

Point = Tuple[float, float]  # (lat, lng)


def _project(points: List[Point]) -> List[Point]:
    """Scale longitude by cos(mean latitude) so degrees are comparable."""
    mean_lat = sum(p[0] for p in points) / len(points)
    k = math.cos(math.radians(mean_lat))
    return [(lat, lng * k) for lat, lng in points]


def _sq_dist(a: Point, b: Point) -> float:
    return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2


def kmeans(points: List[Point], k: int, max_iters: int = 100, seed: int = 42) -> List[int]:
    """Cluster points into k groups. Returns a cluster index per point."""
    if k >= len(points):
        return list(range(len(points)))  # more clusters than points: one each

    rng = random.Random(seed)
    pts = _project(points)

    # --- farthest-point seeding ---
    centroids = [pts[rng.randrange(len(pts))]]
    while len(centroids) < k:
        farthest = max(pts, key=lambda p: min(_sq_dist(p, c) for c in centroids))
        centroids.append(farthest)

    assignments = [-1] * len(pts)
    for _ in range(max_iters):
        # (2) every point joins its nearest centroid
        new_assignments = [
            min(range(k), key=lambda ci: _sq_dist(p, centroids[ci])) for p in pts
        ]
        if new_assignments == assignments:
            break  # nobody changed their mind: converged
        assignments = new_assignments

        # (3) move each centroid to the mean of its members
        for ci in range(k):
            members = [pts[i] for i, a in enumerate(assignments) if a == ci]
            if members:
                centroids[ci] = (
                    sum(m[0] for m in members) / len(members),
                    sum(m[1] for m in members) / len(members),
                )

    return assignments