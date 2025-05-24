from typing import List, Tuple, Union, Dict, Set

# You may define ParseTree and ErrorReport in any way that fits your implementation.
# The below is a placeholder and should be modified.

# 0. Special symbols
EPSILON = 'ε'
END_MARKER = '$'
START_SYMBOL = 'Program'

# 1. CFG 규칙 정의
# The following CFG defines a C-like language with declarations, control flow,
# expressions, and function calls. It is intentionally ambiguous.
GRAMMAR: Dict[str, List[List[str]]] = {
    'Program': [['DeclList']],  # 1
    'DeclList': [['Decl', 'DeclList'], [EPSILON]],  # 2
    'Decl': [['VarDecl'], ['FuncDecl']],  # 3
    'VarDecl': [['type', 'id', ';'],  # 4
                ['type', 'id', '=', 'Expr', ';']],  # 5
    'FuncDecl': [['type', 'id', '(', 'ParamList', ')', 'Block']],  # 6
    'ParamList': [[EPSILON], ['Param', ',', 'ParamList'], ['Param']],  # 7
    'Param': [['type', 'id']],  # 8
    'Block': [['{', 'StmtList', '}']],  # 9
    'StmtList': [[EPSILON], ['Stmt', 'StmtList']],  # 10
    'Stmt': [
        ['if', '(', 'Expr', ')', 'Stmt'],                             # 11
        ['if', '(', 'Expr', ')', 'Stmt', 'else', 'Stmt'],             # 12
        ['while', '(', 'Expr', ')', 'Stmt'],                          # 13
        ['for', '(', 'Expr', ';', 'Expr', ';', 'Expr', ')', 'Stmt'],  # 14
        ['return', 'Expr', ';'],                                      # 15
        ['VarDecl'],                                                  # 16
        ['ExprStmt'],                                                 # 17
        ['Block']],                                                   # 18
    'ExprStmt': [['id', '=', 'Expr', ';']],  # 19
    'Expr': [
        ['Expr', '==', 'Expr'],       # 20
        ['Expr', '+', 'Expr'],        # 21
        ['Expr', '*', 'Expr'],        # 22
        ['-', 'Expr'],                # 23
        ['id', '(', 'ArgList', ')'],  # 24
        ['id'],                       # 25
        ['num'],                      # 26
        ['(', 'Expr', ')'],           # 27
    ],
    'ArgList': [[EPSILON], ['Expr', ',', 'ArgList'], ['Expr']]  # 28
}



class ParseTree:  # TODO
    pass

class ErrorReport:  # TODO
    def __init__(self, position: int, message: str):
        self.position = position
        self.message = message



def compute_terminals_nonterminals(
    grammar: Dict[str, List[List[str]]]
) -> Tuple[Set[str], Set[str]]:
    terminals: Set[str] = set()
    non_terminals: Set[str] = set(grammar.keys())
    for lhs, prods in grammar.items():
        for prod in prods:
            for sym in prod:
                if sym not in grammar and sym != EPSILON:
                    terminals.add(sym)
    return terminals, non_terminals

# 2. FIRST 집합 계산
def compute_first_sets(
    grammar: Dict[str, List[List[str]]]
) -> Dict[str, Set[str]]:
    first: Dict[str, Set[str]] = {nt: set() for nt in grammar}
    changed = True
    while changed:
        changed = False
        for nt, prods in grammar.items():
            for prod in prods:
                # ε 프로덕션
                if prod == [EPSILON]:
                    if EPSILON not in first[nt]:
                        first[nt].add(EPSILON)
                        changed = True
                    continue
                for sym in prod:
                    if sym in grammar:
                        # 비터미널
                        before = len(first[nt])
                        first[nt] |= (first[sym] - {EPSILON})
                        if EPSILON in first[sym]:
                            continue
                        after = len(first[nt])
                        if after > before:
                            changed = True
                        break
                    else:
                        # 터미널
                        if sym not in first[nt]:
                            first[nt].add(sym)
                            changed = True
                        break
    return first

# 3. FOLLOW 집합 계산
def compute_follow_sets(
    grammar: Dict[str, List[List[str]]],
    first: Dict[str, Set[str]]
) -> Dict[str, Set[str]]:
    follow: Dict[str, Set[str]] = {nt: set() for nt in grammar}
    follow[START_SYMBOL].add(END_MARKER)
    changed = True
    while changed:
        changed = False
        for lhs, prods in grammar.items():
            for prod in prods:
                trailer = follow[lhs].copy()
                for sym in reversed(prod):
                    if sym in grammar:
                        before = len(follow[sym])
                        follow[sym] |= trailer
                        after = len(follow[sym])
                        if after > before:
                            changed = True
                        if EPSILON in first[sym]:
                            trailer |= (first[sym] - {EPSILON})
                        else:
                            trailer = first[sym].copy()
                    else:
                        trailer = {sym}
    return follow

# Debugging utility
def pretty_print_sets(sets: Dict[str, Set[str]]):
    for sym, vals in sets.items():
        print(f"{sym:15}: {{ {', '.join(sorted(vals))} }}")


def parser(tokens: List[str]) -> Tuple[bool, Union[ParseTree, ErrorReport]]:
    """
    Returns (True, parse_tree) on success or (False, ErrorReport) on failure.
    Example:
        return True, ParseTree(...)
        return False, ErrorReport(3, "unexpected token 'else'")
    """
    # TODO: implement your SLR(1) parser using a parsing table and stack
    # This is just a placeholder structure


    # 문법 파트 구현 확인을 위한 임시 디버깅 (전체 구현 후 삭제 예정)
    # 토큰 끝에 END_MARKER 붙이기
    if tokens[-1] != END_MARKER:
        tokens = tokens + [END_MARKER]

    # 문법 부분 디버깅
    terms, nonterms = compute_terminals_nonterminals(GRAMMAR)
    print("[DEBUG] TERMINALS   :", terms)
    print("[DEBUG] NONTERMS    :", nonterms)
    print(f"[DEBUG] #TERMS={len(terms)}, #NONTERMS={len(nonterms)}")

    first = compute_first_sets(GRAMMAR)
    print("\n[DEBUG] FIRST SETS:")
    pretty_print_sets(first)

    follow = compute_follow_sets(GRAMMAR, first)
    print("\n[DEBUG] FOLLOW SETS:")
    pretty_print_sets(follow)



    # 아직 SLR 파서 구현 전임을 알리는 에러 리포트
    return False, ErrorReport(0, "SLR parser not yet implemented")