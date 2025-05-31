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
GRAMMAR: Dict[str, List[List[str]]] = { #비모호화된 문법
    'Program': [['DeclList']],  # 1
    'DeclList': [['Decl', 'DeclList'], [EPSILON]],  # 2
    'Decl': [['VarDecl'], ['FuncDecl']],  # 3
    'VarDecl': [['type', 'id', ';'],  # 4
                ['type', 'id', '=', 'Expr', ';']],  
    'FuncDecl': [['type', 'id', '(', 'ParamList', ')', 'Block']],   # 5
    'ParamList': [[EPSILON], ['Param', ',', 'ParamList'], ['Param']],  # 6
    'Param': [['type', 'id']],  # 7
    'Block': [['{', 'StmtList', '}']],  # 8
    'StmtList': [[EPSILON], ['Stmt', 'StmtList']],  # 9
    'Stmt': [['MatchedStmt'], ['UnmatchedStmt']],  # 10
    'MatchedStmt': [
        ['if', '(', 'Expr', ')', 'MatchedStmt', 'else', 'MatchedStmt'],  # 11
        ['while', '(', 'Expr', ')', 'MatchedStmt'],                     
        ['for', '(', 'Expr', ';', 'Expr', ';', 'Expr', ')', 'MatchedStmt'],   
        ['return', 'Expr', ';'],                                         
        ['VarDecl'],                                                      
        ['ExprStmt'],                                                     
        ['Block']                                                        
    ],                                                 
    'UnmatchedStmt': [
        ['if', '(', 'Expr', ')', 'Stmt'],                                  # 12
        ['if', '(', 'Expr', ')', 'MatchedStmt', 'else', 'UnmatchedStmt'],  
        ['while', '(', 'Expr', ')', 'UnmatchedStmt'],                      
        ['for', '(', 'Expr', ';', 'Expr', ';', 'Expr', ')', 'UnmatchedStmt']  
    ],
    'ExprStmt': [['id', '=', 'Expr', ';']],  # 13
    'Expr': [['Equality']],  # 14
    'Equality': [['Equality', '==', 'Additive'],  # 15
                 ['Additive']],  
    'Additive': [['Additive', '+', 'Multiplicative'],  # 16
                 ['Additive', '-', 'Multiplicative'],  
                 ['Multiplicative']],  
    'Multiplicative': [['Multiplicative', '*', 'Unary'],  # 17
                       ['Unary']],                               
    'Unary': [['-', 'Unary'],  # 18
              ['Primary']], 
    'Primary': [['id', '(', 'ArgList', ')'],  # 19
                ['id'],  
                ['num'], 
                ['(', 'Expr', ')']], 
    'ArgList': [[EPSILON],  # 20
                ['Expr', ',', 'ArgList'], 
                ['Expr']] 
}



class ParseTree:
    def __init__(self, symbol: str, children=None, token: str = None):
        self.symbol = symbol
        self.children = children or []
        self.token = token
    def __repr__(self):
        if self.token:
            return f"{self.symbol}('{self.token}')"

        if self.symbol == START_SYMBOL:
            decl_list = None
            for c in self.children:
                if c.symbol == 'DeclList':
                    decl_list = c
                    break
            if decl_list:
                decls = extract_decls(decl_list)
                return '\n'.join(repr(d) for d in decls)

        return f"{self.symbol}({', '.join(repr(c) for c in self.children)})"
    
def extract_decls(dl: ParseTree) -> List[ParseTree]:
    result = []
    if not dl.children:
        return result
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
                # ε
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

# Debugging 용
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
                        if p == [EPSILON]:
                            epsilon_item = (sym, tuple(p), 1)
                            if epsilon_item not in closure_set:
                                closure_set.add(epsilon_item)
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

                if a == EPSILON:
                    continue

                if a not in aug_grammar:
                    J = goto(I, a, aug_grammar)
                    if not J:
                        continue
                    j = C.index(J)
                    action[i][a] = ('shift', j)
            else:
                # Reduce or accept
                if lhs == AUG_START:
                    # 현재 상태 i에서 END_MARKER('$')를 만났을 때 accept
                    if END_MARKER in action[i]:
                        print(f"[WARN] Accept 충돌: state={i}, symbol='{END_MARKER}', 기존='{action[i][END_MARKER]}'")
                    action[i][END_MARKER] = ('accept',)
                else:
                    prod_list = list(prod)
                    for a in follow[lhs]:
                        if a == EPSILON:
                            continue
                        if a in action[i]:
                            print(f"[WARN] Shift/Reduce or Reduce/Reduce 충돌: state={i}, symbol='{a}', 기존='{action[i][a]}', 새 REDUCE→({lhs} -> {prod_list})")
                        action[i][a] = ('reduce', lhs, prod_list)
        # GOTO entries for non-terminals
        for A in aug_grammar.keys():
            if A == EPSILON:
                continue
            J = goto(I, A, aug_grammar)
            if not J:
                continue
            j = C.index(J)
            goto_tbl[i][A] = j

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


    # 토큰 끝에 END_MARKER 붙이기
    if tokens[-1] != END_MARKER:
        tokens = tokens + [END_MARKER]


    # 문법 부분 디버깅
    terms, nonterms = compute_terminals_nonterminals(GRAMMAR)
    # print("[DEBUG] TERMINALS   :", terms)
    # print("[DEBUG] NONTERMS    :", nonterms)
    # print(f"[DEBUG] #TERMS={len(terms)}, #NONTERMS={len(nonterms)}")

    first = compute_first_sets(GRAMMAR)
    # print("\n[DEBUG] FIRST SETS:")
    # pretty_print_sets(first)

    follow = compute_follow_sets(GRAMMAR, first)
    # print("\n[DEBUG] FOLLOW SETS:")
    # pretty_print_sets(follow)



    action, goto_tbl = build_slr_table(GRAMMAR, first, follow)

    states = [0]
    symbols = []  # for building parse tree
    idx = 0
    while True:
        st = states[-1]
        tok = tokens[idx]

        # 1) action 테이블 존재 여부 확인
        if tok not in action[st]:
            return False, ErrorReport(idx, f"unexpected token '{tok}'")
        act = action[st][tok]

        # 2) shift, reduce, accept
        if act[0] == 'shift':
            _, next_state = act
            states.append(next_state)
            symbols.append(ParseTree(tok, token=tok))
            idx += 1

        elif act[0] == 'reduce':
            _, lhs, prod = act 

            # 자식 노드 모으기
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

            # GOTO 검사 / 이동
            prev_state = states[-1]
            if lhs not in goto_tbl[prev_state]:
                return False, ErrorReport(idx, f"GOTO 누락: 상태 {prev_state}에서 {lhs}로 이동할 수 없음")
            goto_state = goto_tbl[prev_state][lhs]
            states.append(goto_state)

        else:  # accept
            # parse 완료: 루트 노드 찾기
            for n in reversed(symbols):
                if n.symbol == AUG_START or n.symbol == START_SYMBOL:
                    return True, n
            return True, symbols[-1]
        
    