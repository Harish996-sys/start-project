import sys

def read_lines():
    data = sys.stdin.read().splitlines()
    # keep non-empty lines trimmed
    return [ln.rstrip("\n") for ln in data if ln is not None]

def solve():
    lines = [ln for ln in read_lines() if ln.strip() != ""]
    if not lines:
        return

    # first non-empty line should be S
    try:
        S = int(lines[0].strip())
    except:
        # malformed input
        return

    if len(lines) < 1 + S:
        # not enough rows
        return

    grid = [list(lines[1 + i].rstrip()) for i in range(S)]

    pos1 = set()
    pos2 = set()
    for r in range(S):
        row = grid[r]
        for c in range(len(row)):
            ch = row[c]
            if ch == '1':
                pos1.add((r,c))
            elif ch == '2':
                pos2.add((r,c))

    overlaps = set()
    top_chars = set()

    # helper to check membership safely
    def has1(r,c):
        return (r,c) in pos1
    def has2(r,c):
        return (r,c) in pos2

    for r in range(S):
        for c in range(S):
            ch = grid[r][c]
            if ch not in ('1', '2'):
                continue
            # determine the other band set
            if ch == '1':
                other_has = has2
            else:
                other_has = has1

            # check horizontal pass of the other band (left & right)
            hor = False
            if c-1 >= 0 and c+1 < S:
                if other_has(r, c-1) and other_has(r, c+1):
                    hor = True

            # check vertical pass of the other band (up & down)
            ver = False
            if r-1 >= 0 and r+1 < S:
                if other_has(r-1, c) and other_has(r+1, c):
                    ver = True

            if hor or ver:
                overlaps.add((r,c))
                top_chars.add(ch)

    # Output according to problem statement:
    # If no overlaps -> print 0
    # Else if all overlaps have same top char -> print number of overlaps
    # Else -> print "Impossible"
    if len(overlaps) == 0:
        print(0)
        return

    if len(top_chars) == 1:
        print(len(overlaps))
    else:
        print("Impossible")

if __name__ == "__main__":
    solve()
