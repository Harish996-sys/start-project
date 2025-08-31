import sys
from collections import deque

def solve():
    data = sys.stdin.read().strip().splitlines()
    if not data:
        return
    # parse M N
    parts = data[0].strip().split()
    if len(parts) < 2:
        return
    M, N = map(int, parts)
    grid = [data[i+1].strip().split() for i in range(M)]

    starts = []
    dests = []
    for r in range(M):
        for c in range(N):
            if grid[r][c] == 's':
                starts.append((r,c))
            elif grid[r][c] == 'S':
                dests.append((r,c))

    if len(starts) != 2 or len(dests) != 2:
        print("Impossible")
        return

    dest_set = set(dests)

    # determine orientation and anchor (left/top cell)
    sr0, sc0 = starts[0]; sr1, sc1 = starts[1]
    if sr0 == sr1:  # same row -> horizontal
        # choose leftmost as anchor
        if sc0 < sc1:
            start_anchor = (sr0, sc0)
        else:
            start_anchor = (sr0, sc1)
        start_dir = 0  # 0 horizontal
    else:  # vertical
        # choose topmost as anchor
        if sr0 < sr1:
            start_anchor = (sr0, sc0)
        else:
            start_anchor = (sr1, sc1)
        start_dir = 1  # 1 vertical

    # helper to check a cell is free (not H) and in bounds
    def is_free_cell(r, c):
        if r < 0 or r >= M or c < 0 or c >= N:
            return False
        return grid[r][c] != 'H'

    # helper to check list of cells
    def cells_free(cells):
        for (r,c) in cells:
            if not is_free_cell(r,c):
                return False
        return True

    # produce occupied cells for a state
    def sofa_cells(r, c, dir):
        if dir == 0:  # H uses (r,c),(r,c+1)
            return [(r,c), (r,c+1)]
        else:         # V uses (r,c),(r+1,c)
            return [(r,c), (r+1,c)]

    # initial validity: ensure starting cells not blocked
    sr, sc = start_anchor
    if not cells_free(sofa_cells(sr, sc, start_dir)):
        print("Impossible")
        return

    # BFS
    q = deque()
    q.append((sr, sc, start_dir, 0))
    visited = set()
    visited.add((sr, sc, start_dir))

    while q:
        r, c, dir, steps = q.popleft()

        occ = sofa_cells(r, c, dir)
        if set(occ) == dest_set:
            print(steps)
            return

        # Moves and rotations
        if dir == 0:  # horizontal: occupies (r,c),(r,c+1)
            # move left
            if c-1 >= 0:
                new_cells = [(r, c-1), (r, c)]
                if cells_free(new_cells):
                    s = (r, c-1, 0)
                    if s not in visited:
                        visited.add(s)
                        q.append((r, c-1, 0, steps+1))
            # move right
            if c+2 < N:
                new_cells = [(r, c+1), (r, c+2)]
                if cells_free(new_cells):
                    s = (r, c+1, 0)
                    if s not in visited:
                        visited.add(s)
                        q.append((r, c+1, 0, steps+1))
            # move up
            if r-1 >= 0:
                new_cells = [(r-1, c), (r-1, c+1)]
                if cells_free(new_cells):
                    s = (r-1, c, 0)
                    if s not in visited:
                        visited.add(s)
                        q.append((r-1, c, 0, steps+1))
            # move down
            if r+1 < M:
                new_cells = [(r+1, c), (r+1, c+1)]
                if cells_free(new_cells):
                    s = (r+1, c, 0)
                    if s not in visited:
                        visited.add(s)
                        q.append((r+1, c, 0, steps+1))

            # rotations: two possible 2x2 blocks that include the horizontal sofa
            # Top block: rows (r-1, r), cols (c, c+1)  => new vertical anchors at (r-1,c) and (r-1,c+1)
            if r-1 >= 0 and c+1 < N:
                block = [(r-1, c), (r-1, c+1), (r, c), (r, c+1)]
                if cells_free(block):
                    # vertical anchors (top row of block)
                    for new_anchor in [(r-1, c), (r-1, c+1)]:
                        nr, nc = new_anchor
                        s = (nr, nc, 1)
                        if s not in visited:
                            visited.add(s)
                            q.append((nr, nc, 1, steps+1))
            # Bottom block: rows (r, r+1), cols (c, c+1) => new vertical anchors at (r, c) and (r, c+1)
            if r+1 < M and c+1 < N:
                block = [(r, c), (r, c+1), (r+1, c), (r+1, c+1)]
                if cells_free(block):
                    for new_anchor in [(r, c), (r, c+1)]:
                        nr, nc = new_anchor
                        s = (nr, nc, 1)
                        if s not in visited:
                            visited.add(s)
                            q.append((nr, nc, 1, steps+1))

        else:  # vertical: occupies (r,c),(r+1,c)
            # move up
            if r-1 >= 0:
                new_cells = [(r-1, c), (r, c)]
                if cells_free(new_cells):
                    s = (r-1, c, 1)
                    if s not in visited:
                        visited.add(s)
                        q.append((r-1, c, 1, steps+1))
            # move down
            if r+2 < M:
                new_cells = [(r+1, c), (r+2, c)]
                if cells_free(new_cells):
                    s = (r+1, c, 1)
                    if s not in visited:
                        visited.add(s)
                        q.append((r+1, c, 1, steps+1))
            # move left
            if c-1 >= 0:
                new_cells = [(r, c-1), (r+1, c-1)]
                if cells_free(new_cells):
                    s = (r, c-1, 1)
                    if s not in visited:
                        visited.add(s)
                        q.append((r, c-1, 1, steps+1))
            # move right
            if c+1 < N:
                new_cells = [(r, c+1), (r+1, c+1)]
                if cells_free(new_cells):
                    s = (r, c+1, 1)
                    if s not in visited:
                        visited.add(s)
                        q.append((r, c+1, 1, steps+1))

            # rotations: two possible 2x2 blocks that include the vertical sofa
            # Left block: cols (c-1, c), rows (r, r+1) => horizontal anchors at (r, c-1) and (r+1, c-1)
            if c-1 >= 0 and r+1 < M:
                block = [(r, c-1), (r+1, c-1), (r, c), (r+1, c)]
                if cells_free(block):
                    for new_anchor in [(r, c-1), (r+1, c-1)]:
                        nr, nc = new_anchor
                        s = (nr, nc, 0)
                        if s not in visited:
                            visited.add(s)
                            q.append((nr, nc, 0, steps+1))
            # Right block: cols (c, c+1), rows (r, r+1) => horizontal anchors at (r, c) and (r+1, c)
            if c+1 < N and r+1 < M:
                block = [(r, c), (r+1, c), (r, c+1), (r+1, c+1)]
                if cells_free(block):
                    for new_anchor in [(r, c), (r+1, c)]:
                        nr, nc = new_anchor
                        s = (nr, nc, 0)
                        if s not in visited:
                            visited.add(s)
                            q.append((nr, nc, 0, steps+1))

    # BFS exhausted
    print("Impossible")


if __name__ == "__main__":
    solve()
