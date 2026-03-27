from collections import deque

FARMER, CABBAGE, GOAT, WOLF = 1, 2, 4, 8
ROLES = "FCGW"

initial_state = FARMER | CABBAGE | GOAT | WOLF, 0
final_state = 0, FARMER | CABBAGE | GOAT | WOLF


def valid(state: tuple[int, int]) -> bool:
    def check(side: int) -> bool:
        if (side & CABBAGE) and (side & GOAT):
            return False
        if (side & GOAT) and (side & WOLF):
            return False
        return True

    l, r = state
    return check(r) if l & FARMER else check(l)


def state_to_str(state: tuple[int, int]) -> str:
    def foo(side: int):
        return "".join(ROLES[i] for i in range(4) if (side & (1 << i)) != 0)

    l, r = state
    return f"{foo(l):<4} | {foo(r)}"


def bfs():
    # path of states
    q = deque([[initial_state]])

    vis = {initial_state: 0}

    solutions = []
    step = 1

    while q:
        print(f"=== step {step} queue ===")
        for path in q:
            print("  " + state_to_str(path[-1]))
        print()

        level_size = len(q)
        for _ in range(level_size):
            path = q.popleft()
            current_state = path[-1]
            current_depth = len(path) - 1

            if current_state == final_state:
                solutions.append(path)
                continue

            l, r = current_state
            for i in range(4):
                next_state = None
                if (l & FARMER) and (l & (1 << i)):
                    next_state = (l ^ (FARMER | (1 << i)), r ^ (FARMER | (1 << i)))
                elif (r & FARMER) and (r & (1 << i)):
                    next_state = (l ^ (FARMER | (1 << i)), r ^ (FARMER | (1 << i)))

                if next_state is not None and valid(next_state):
                    if next_state not in vis:
                        vis[next_state] = current_depth + 1
                        q.append(path + [next_state])
                    elif vis[next_state] == current_depth + 1:
                        q.append(path + [next_state])
        if solutions:
            break

        step += 1

    print("-" * 30)
    print(f"find {len(solutions)} best solutions：\n")
    for idx, sol in enumerate(solutions, 1):
        print(f"solution {idx}")
        for s in sol:
            print("  " + state_to_str(s))
        print()


if __name__ == "__main__":
    bfs()
