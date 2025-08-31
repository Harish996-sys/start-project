import sys

def parse_time(t):
    h_s, m_s = t.strip().split(':')
    return int(h_s) % 12, int(m_s)

def mod360(x):
    return x % 360

def main():
    data = sys.stdin.read().strip().splitlines()
    if not data:
        return

    lines = [ln.strip() for ln in data if ln.strip() != ""]
    idx = 0

    hour, minute = parse_time(lines[idx]); idx += 1
    Q = int(lines[idx]); idx += 1
    A, B, X, Y = map(int, lines[idx].split()); idx += 1
    queries = []
    for _ in range(Q):
        queries.append(int(lines[idx])); idx += 1

    # initial angles (degrees clockwise from 12)
    H = (hour % 12) * 30
    M = minute * 6
    total_cost = 0

    for target in queries:
        D = mod360(M - H)  # cw angle from hour to minute in [0,359]
        finals = [mod360(target), mod360(360 - target)]
        best_cost = None
        best_move = None  # tuple (h_deg, h_dir, m_deg, m_dir), dirs: +1 cw, -1 ccw, 0 no move

        # try each desired final cw delta
        for f in finals:
            if f == D:
                # no move needed
                if best_cost is None or 0 < best_cost:
                    best_cost = 0
                    best_move = (0, 0, 0, 0)
                continue

            if f > D:
                # need to increase cw delta by total_increase = f - D
                total_inc = f - D

                # minute-only cw
                m = total_inc
                # minute-only cw allowed if it does not wrap past hour: m <= 360 - D (true for f>D)
                cost = m * Y * A
                if best_cost is None or cost < best_cost:
                    best_cost = cost
                    best_move = (0, 0, m, +1)

                # hour-only ccw (hour moves ccw increases D)
                h = total_inc
                if h % 30 == 0 and h <= 360 - D:
                    cost = h * X * B
                    if best_cost is None or cost < best_cost:
                        best_cost = cost
                        best_move = (h, -1, 0, 0)

                # both: hour ccw (h) + minute cw (m), with h multiple of 30
                # h + m = total_inc, and h <= 360 - D (hour ccw limit)
                max_h_mult = (360 - D) // 30
                max_h_by_total = total_inc // 30
                max_k = min(max_h_mult, max_h_by_total)
                for k in range(0, max_k + 1):
                    h = 30 * k
                    m = total_inc - h
                    if m < 0:
                        continue
                    # hour ccw by h, minute cw by m
                    cost = h * X * B + m * Y * A
                    if best_cost is None or cost < best_cost:
                        best_cost = cost
                        best_move = (h, -1, m, +1)

            else:  # f < D
                # need to decrease cw delta by total_reduce = D - f
                total_red = D - f

                # minute-only ccw
                m = total_red
                # allowed if m <= D (true for f < D)
                cost = m * Y * B
                if best_cost is None or cost < best_cost:
                    best_cost = cost
                    best_move = (0, 0, m, -1)

                # hour-only cw (hour moves cw decreases D)
                h = total_red
                if h % 30 == 0 and h <= D:
                    cost = h * X * A
                    if best_cost is None or cost < best_cost:
                        best_cost = cost
                        best_move = (h, +1, 0, 0)

                # both: hour cw (h) + minute ccw (m), with h multiple of 30
                # h + m = total_red, and h <= D (hour cw limit)
                max_h_mult = D // 30
                max_h_by_total = total_red // 30
                max_k = min(max_h_mult, max_h_by_total)
                for k in range(0, max_k + 1):
                    h = 30 * k
                    m = total_red - h
                    if m < 0:
                        continue
                    # hour cw by h, minute ccw by m
                    cost = h * X * A + m * Y * B
                    if best_cost is None or cost < best_cost:
                        best_cost = cost
                        best_move = (h, +1, m, -1)

        # If no valid move found (should not happen per problem), treat cost 0
        if best_cost is None:
            best_cost = 0
            best_move = (0,0,0,0)

        # apply chosen move to update H and M
        h_deg, h_dir, m_deg, m_dir = best_move
        if h_dir == +1:
            H = mod360(H + h_deg)
        elif h_dir == -1:
            H = mod360(H - h_deg)
        # if h_dir == 0, hour unchanged

        if m_dir == +1:
            M = mod360(M + m_deg)
        elif m_dir == -1:
            M = mod360(M - m_deg)
        # else minute unchanged

        total_cost += int(best_cost)

    # print final total cost (single integer, newline)
    sys.stdout.write(str(int(total_cost)) + "\n")


if __name__ == "__main__":
    main()
