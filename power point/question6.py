import sys
import math
from collections import defaultdict, deque

EPS = 1e-9

def cross(ax, ay, bx, by):
    return ax * by - ay * bx

def seg_intersection(p1, p2, q1, q2):
    # returns list of intersection points (0,1 or 2 points for collinear overlap endpoints)
    x1,y1 = p1; x2,y2 = p2
    x3,y3 = q1; x4,y4 = q2
    rx = x2 - x1; ry = y2 - y1
    sx = x4 - x3; sy = y4 - y3
    rxs = cross(rx, ry, sx, sy)
    qpx = x3 - x1; qpy = y3 - y1
    qpxr = cross(qpx, qpy, rx, ry)

    if abs(rxs) < EPS:
        # parallel or collinear
        if abs(qpxr) < EPS:
            # collinear: compute overlap interval along parameter t on p: p1 + t * r
            def proj_t(px, py):
                if abs(rx) >= abs(ry):
                    if abs(rx) < EPS:
                        return 0.0
                    return (px - x1) / rx
                else:
                    return (py - y1) / ry
            t0 = proj_t(x1,y1); t1 = proj_t(x2,y2)
            u0 = proj_t(x3,y3); u1 = proj_t(x4,y4)
            a0,a1 = min(t0,t1), max(t0,t1)
            b0,b1 = min(u0,u1), max(u0,u1)
            lo = max(a0,b0); hi = min(a1,b1)
            if hi + EPS < lo:
                return []
            # clamp to [0,1] for segment p
            lo_cl = max(0.0, lo); hi_cl = min(1.0, hi)
            p_lo = (x1 + lo_cl * rx, y1 + lo_cl * ry)
            p_hi = (x1 + hi_cl * rx, y1 + hi_cl * ry)
            if math.hypot(p_lo[0]-p_hi[0], p_lo[1]-p_hi[1]) < EPS:
                return [p_lo]
            else:
                return [p_lo, p_hi]
        else:
            return []
    else:
        t = cross(qpx, qpy, sx, sy) / rxs
        u = cross(qpx, qpy, rx, ry) / rxs
        if -EPS <= t <= 1+EPS and -EPS <= u <= 1+EPS:
            px = x1 + t * rx
            py = y1 + t * ry
            return [(px, py)]
        else:
            return []

def round_pt(p):
    return (round(p[0],8), round(p[1],8))

def length(a,b):
    return math.hypot(a[0]-b[0], a[1]-b[1])

def polygon_area(points):
    n = len(points)
    if n < 3:
        return 0.0
    s = 0.0
    for i in range(n):
        x1,y1 = points[i]
        x2,y2 = points[(i+1) % n]
        s += x1 * y2 - x2 * y1
    return s / 2.0

def find_cycle_iterative(adj, coords):
    n = len(coords)
    visited = [False]*n
    in_stack = [False]*n
    parent = [-1]*n

    for start in range(n):
        if visited[start]:
            continue
        stack = [(start, None, iter(adj[start]))]  # (node, parent, neighbor-iterator)
        parent[start] = -1
        while stack:
            node, par, neigh_it = stack[-1]
            if not visited[node]:
                visited[node] = True
                in_stack[node] = True
            try:
                nei = next(neigh_it)
                if nei == par:
                    continue
                if not visited[nei]:
                    parent[nei] = node
                    stack.append((nei, node, iter(adj[nei])))
                    continue
                else:
                    if in_stack[nei]:
                        # found back-edge. reconstruct cycle from node back to nei
                        cycle = []
                        cur = node
                        cycle.append(nei)  # ensure start at nei
                        while True:
                            cycle.append(cur)
                            if cur == nei:
                                break
                            cur = parent[cur]
                            if cur == -1:
                                break
                        # cycle currently has nei,...,node,nei ; remove duplicate ending and reverse to get proper order
                        # create unique cycle list in order
                        if len(cycle) >= 4:  # includes repeated start at end
                            # remove last element (duplicate)
                            cycle = cycle[:-1]
                            cycle.reverse()
                            # ensure at least 3 distinct nodes and non-zero area
                            uniq = []
                            for v in cycle:
                                if not uniq or uniq[-1] != v:
                                    uniq.append(v)
                            if len(uniq) >= 3:
                                poly = [coords[i] for i in uniq]
                                if abs(polygon_area(poly)) > EPS:
                                    return uniq
                        # else continue searching
                    # else already visited but not in stack -> cross edge, ignore
            except StopIteration:
                # all neighbours processed
                stack.pop()
                in_stack[node] = False
    return None

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    it = iter(data)
    try:
        N = int(next(it))
    except StopIteration:
        return

    segs = []
    total_original_length = 0.0
    for _ in range(N):
        x1 = float(next(it)); y1 = float(next(it)); x2 = float(next(it)); y2 = float(next(it))
        segs.append(((x1,y1),(x2,y2)))
        total_original_length += length((x1,y1),(x2,y2))

    # For each segment collect intersection points and endpoints
    pts_on_seg = []
    for i in range(N):
        pts_on_seg.append([segs[i][0], segs[i][1]])

    for i in range(N):
        for j in range(i+1, N):
            pts = seg_intersection(segs[i][0], segs[i][1], segs[j][0], segs[j][1])
            for p in pts:
                pts_on_seg[i].append(p)
                pts_on_seg[j].append(p)

    # Build unique points map and split segments
    point_id = {}
    id_coords = []

    def get_id(pt):
        rpt = round_pt(pt)
        if rpt in point_id:
            return point_id[rpt]
        idx = len(id_coords)
        point_id[rpt] = idx
        id_coords.append((rpt[0], rpt[1]))
        return idx

    edges = {}  # key: (a,b) with a<b -> length

    for i in range(N):
        p1, p2 = segs[i]
        pts = pts_on_seg[i]
        # deduplicate by rounded coords but preserve original for sorting
        uniq = {}
        ordered_pts = []
        for p in pts:
            rp = round_pt(p)
            if rp not in uniq:
                uniq[rp] = p
                ordered_pts.append(p)
        # param t along segment
        x1,y1 = p1; x2,y2 = p2
        dx = x2 - x1; dy = y2 - y1
        def t_of(p):
            if abs(dx) >= abs(dy):
                if abs(dx) < EPS:
                    return 0.0
                return (p[0] - x1) / dx
            else:
                return (p[1] - y1) / dy
        ordered_pts.sort(key=lambda q: t_of(q))
        for k in range(len(ordered_pts)-1):
            a = ordered_pts[k]; b = ordered_pts[k+1]
            ida = get_id(a); idb = get_id(b)
            if ida == idb:
                continue
            key = (ida, idb) if ida < idb else (idb, ida)
            if key not in edges:
                seglen = length(a,b)
                if seglen > EPS:
                    edges[key] = seglen

    if not edges:
        print("No")
        return

    # adjacency
    adj = defaultdict(list)
    for (a,b), L in edges.items():
        adj[a].append(b)
        adj[b].append(a)

    coords = id_coords
    # find a simple cycle using iterative DFS
    cycle = find_cycle_iterative(adj, coords)
    if not cycle:
        print("No")
        return

    poly = [coords[i] for i in cycle]
    area = abs(polygon_area(poly))
    perim = 0.0
    for i in range(len(poly)):
        perim += length(poly[i], poly[(i+1) % len(poly)])

    leftover = total_original_length - perim
    can_arjun = (leftover + 1e-6 >= perim)

    print("Yes")
    print("Yes" if can_arjun else "No")
    print("{:.2f}".format(area))

if __name__ == "__main__":
    main()
