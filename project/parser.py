from typing import List, Tuple, Union, Dict, Set
from collections import defaultdict

# You may define ParseTree and ErrorReport in any way that fits your implementation.
# The below is a placeholder and should be modified.

# 0. Special symbols
EPSILON = 'ε'
END_MARKER = '$'
START_SYMBOL = 'Program'
AUG_START = START_SYMBOL + "'"

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



class ParseTree:
    def __init__(self, symbol: str, children=None, token: str = None):
        self.symbol = symbol
        self.children = children or []
        self.token = token
    def __repr__(self):
        # Leaf token
        if self.token:
            return f"{self.symbol}('{self.token}')"

        # If this is the top Program node, flatten all DeclList children
        if self.symbol == START_SYMBOL:
            # find the DeclList child
            decl_list = None
            for c in self.children:
                if c.symbol == 'DeclList':
                    decl_list = c
                    break
            if decl_list:
                decls = extract_decls(decl_list)
                return '\n'.join(repr(d) for d in decls)
            # fallback to default

        # Default: show symbol and children
        return f"{self.symbol}({', '.join(repr(c) for c in self.children)})"
    
def extract_decls(dl: ParseTree) -> List[ParseTree]:
    """
    Recursively collect all direct Decl nodes from a DeclList.
    """
    result = []
    # empty list case
    if not dl.children:
        return result
    # non-empty: children = [Decl_node, rest]
    first_decl, rest = dl.children
    result.append(first_decl)
    result.extend(extract_decls(rest))
    return result


class ErrorReport:
    def __init__(self, position: int, message: str):
        self.position = position
        self.message = message
    def __repr__(self):
        return f"Error at {self.position}: {self.message}"



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

# 1. LR(0) 아이템 & 상태집합
Item = Tuple[str, Tuple[str, ...], int]  # (lhs, production, dot_pos)

def closure(items: Set[Item], grammar: Dict[str, List[List[str]]]) -> Set[Item]:
    closure_set = set(items)
    added = True
    while added:
        added = False
        for lhs, prod, dot in list(closure_set):
            if dot < len(prod):
                sym = prod[dot]
                if sym in grammar:
                    for p in grammar[sym]:
                        new_item = (sym, tuple(p), 0)
                        if new_item not in closure_set:
                            closure_set.add(new_item)
                            added = True
    return closure_set

def goto(items: Set[Item], symbol: str, grammar: Dict[str, List[List[str]]]) -> Set[Item]:
    moved = set()
    for lhs, prod, dot in items:
        if dot < len(prod) and prod[dot] == symbol:
            moved.add((lhs, prod, dot+1))
    return closure(moved, grammar)


def build_states(grammar: Dict[str, List[List[str]]]) -> List[Set[Item]]:
    # augment grammar
    aug_grammar = {AUG_START: [[START_SYMBOL]]}
    aug_grammar.update(grammar)
    # initial state
    start_item = (AUG_START, tuple(aug_grammar[AUG_START][0]), 0)
    C = []
    C.append(closure({start_item}, aug_grammar))
    symbols = set()
    for prods in aug_grammar.values():
        for p in prods:
            symbols |= set(p)
    symbols |= set(aug_grammar.keys())
    added = True
    while added:
        added = False
        for I in C:
            for X in symbols:
                J = goto(I, X, aug_grammar)
                if J and J not in C:
                    C.append(J)
                    added = True
    return C, aug_grammar

def build_slr_table(
    grammar: Dict[str, List[List[str]]],
    first: Dict[str, Set[str]],
    follow: Dict[str, Set[str]]
) -> Tuple[Dict[int, Dict[str, Union[str, Tuple[str,int]]]], Dict[int, Dict[str, int]]]:
    C, aug_grammar = build_states(grammar)
    action = defaultdict(dict)
    goto_tbl = defaultdict(dict)
    for i, I in enumerate(C):
        for lhs, prod, dot in I:
            # Shift
            if dot < len(prod):
                a = prod[dot]
                if a not in grammar:
                    J = goto(I, a, aug_grammar)
                    j = C.index(J)
                    action[i][a] = ('shift', j)
            else:
                # Reduce or accept
                if lhs == AUG_START:
                    action[i][END_MARKER] = ('accept',)
                else:
                    prod_list = list(prod)
                    for a in follow[lhs]:
                        action[i][a] = ('reduce', lhs, prod_list)
        # GOTO entries for non-terminals
        for A in grammar:
            J = goto(I, A, aug_grammar)
            if J:
                goto_tbl[i][A] = C.index(J)
    return action, goto_tbl


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
    print("===== DEBUG: tokens =====")
    for i, tok in enumerate(tokens):
        print(f"{i:>3}: '{tok}'")
    print("==========================")

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



    action, goto_tbl = build_slr_table(GRAMMAR, first, follow)

    states = [0]
    symbols = []  # for building parse tree
    idx = 0
    while True:
        st = states[-1]
        tok = tokens[idx]
        if tok == END_MARKER:
           return True, symbols[0]
        if tok not in action[st]:
            return False, ErrorReport(idx, f"unexpected token '{tok}'")
        act = action[st][tok]
        if act[0] == 'shift':
            states.append(act[1])
            symbols.append(ParseTree(tok, token=tok))
            idx += 1
        elif act[0] == 'reduce':
            _, lhs, prod = act
            if prod != [EPSILON]:
                children = []
                for _ in prod:
                    states.pop()
                    children.append(symbols.pop())
                children.reverse()
                node = ParseTree(lhs, children)
            else:
                node = ParseTree(lhs)
            symbols.append(node)
            goto_state = goto_tbl[states[-1]][lhs]
            states.append(goto_state)
        else:  # accept
            # on accept, find Program node in symbols
            for n in reversed(symbols):
                if n.symbol == START_SYMBOL:
                    return True, n
            return True, symbols[-1]

    