# parser.py

from grammar import GRAMMAR, END_MARKER
from first_follow import compute_first_sets, compute_follow_sets
from slr_table import build_slr_table

def parser(tokens):
    """
    tokens: list of terminal symbols ending with '$'
    RETURN: parse tree (e.g. nested tuples) or {"error": "..."}
    """
    # 1. FIRST, FOLLOW 계산
    first_sets  = compute_first_sets(GRAMMAR)
    follow_sets = compute_follow_sets(GRAMMAR, first_sets)

    # 2. SLR(1) 테이블 생성
    action, goto_tbl = build_slr_table(GRAMMAR, first_sets, follow_sets)

    # 3. 파싱 스택 & 트리 스택 초기화
    stack = [0]
    tree_stack = []
    pointer = 0

    # 4. Shift-Reduce 파싱 루프
    while True:
        state = stack[-1]
        a = tokens[pointer]

        if (state, a) not in action:
            return {"error": f"Unexpected token '{a}' at position {pointer}"}

        act = action[(state, a)]
        if act[0] == "shift":
            _, s = act
            stack.append(s)
            tree_stack.append(a)
            pointer += 1

        elif act[0] == "reduce":
            _, (A, beta) = act
            # beta: list of symbols on RHS
            children = []
            for _ in beta:
                stack.pop()
                children.insert(0, tree_stack.pop())
            # 새 노드
            tree_stack.append((A, children))
            # GOTO
            new_state = goto_tbl[(stack[-1], A)]
            stack.append(new_state)

        else:  # accept
            return tree_stack[0]
