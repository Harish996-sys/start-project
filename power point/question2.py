import sys

def main():
    lines = sys.stdin.read().strip().splitlines()
    balance = int(lines[0].strip())
    n = int(lines[1].strip())
    ops = lines[2:]

    transactions = []  # (type, amount, active, committed)
    commits = []       # snapshots: (balance, txn_count)
    output = []

    for op in ops:
        parts = op.split()
        cmd = parts[0]

        if cmd == "read":
            output.append(str(balance))

        elif cmd == "credit":
            amt = int(parts[1])
            transactions.append(["credit", amt, True, False])
            balance += amt

        elif cmd == "debit":
            amt = int(parts[1])
            transactions.append(["debit", amt, True, False])
            balance -= amt

        elif cmd == "abort":
            tno = int(parts[1]) - 1
            if 0 <= tno < len(transactions):
                t = transactions[tno]
                if t[2] and not t[3]:  # active and not committed
                    if t[0] == "credit":
                        balance -= t[1]
                    else:
                        balance += t[1]
                    t[2] = False  # deactivate

        elif cmd == "commit":
            # take snapshot
            commits.append((balance, len(transactions)))
            # mark all active as committed
            for t in transactions:
                if t[2]:
                    t[3] = True

        elif cmd == "rollback":
            cno = int(parts[1]) - 1
            if 0 <= cno < len(commits):
                snap_balance, snap_txn_count = commits[cno]
                balance = snap_balance
                # discard later transactions
                transactions = transactions[:snap_txn_count]
                # discard later commits
                commits = commits[:cno + 1]

    sys.stdout.write("\n".join(output))

if __name__ == "__main__":
    main()
