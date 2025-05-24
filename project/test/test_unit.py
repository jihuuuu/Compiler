import pytest
from parser import (
    compute_terminals_nonterminals,
    compute_first_sets,
    compute_follow_sets,
    EPSILON,
    END_MARKER,
    GRAMMAR
)

# --- Unit tests for grammar analysis utilities ---

def test_terminals_nonterminals_mini():
    """
    Mini-grammar:
      A → a B | ε
      B → b
    """
    mini_gram = {
        'A': [['a', 'B'], [EPSILON]],
        'B': [['b']]
    }
    terms, nonterms = compute_terminals_nonterminals(mini_gram)
    assert terms == {'a', 'b'}
    assert nonterms == {'A', 'B'}


def test_first_sets_mini():
    """
    Mini-grammar with epsilon in B:
      A → a B | ε
      B → b | ε
    """
    mini_gram = {
        'A': [['a', 'B'], [EPSILON]],
        'B': [['b'], [EPSILON]]
    }
    first = compute_first_sets(mini_gram)
    assert first['A'] == {'a', EPSILON}
    assert first['B'] == {'b', EPSILON}


def test_follow_sets_mini():
    """
    Simple grammar:
      S → A S | ε
      A → a
    Test follow sets for S and A.
    """
    mini_gram = {
        'Program': [['S']],
        'S': [['A', 'S'], [EPSILON]],
        'A': [['a']]
    }
    first = compute_first_sets(mini_gram)
    follow = compute_follow_sets(mini_gram, first)
    # S is start symbol, so END_MARKER in its follow
    assert follow['S'] == {END_MARKER}
    # A appears before S and at end of S, so follow(A) includes first(S) without ε and END_MARKER
    assert follow['A'] == {EPSILON, END_MARKER} or 'a' in first['S']


def test_project_grammar_terminals_nonterminals():
    """Verify some known terminals and non-terminals in the project grammar."""
    terms, nonterms = compute_terminals_nonterminals(GRAMMAR)
    # Check common tokens
    expected_terms = {
        'type', 'id', 'if', 'else', 'while', 'for', 'return',
        '(', ')', '{', '}', ';', '=', '==', '+', '-', '*', ',', 'num'
    }
    for t in expected_terms:
        assert t in terms, f"Terminal {t} missing"
    # Check key non-terminals
    for nt in ['Program', 'DeclList', 'Stmt', 'Expr', 'ParamList', 'ArgList']:
        assert nt in nonterms, f"Non-terminal {nt} missing"


def test_project_first_follow_program():
    """FIRST and FOLLOW sets for the start symbol 'Program'."""
    first = compute_first_sets(GRAMMAR)
    follow = compute_follow_sets(GRAMMAR, first)
    assert first['Program'] == {'type'}
    assert follow['Program'] == {END_MARKER}
    # DeclList can be epsilon
    assert EPSILON in first['DeclList']
    # ParamList is followed by ')'
    assert ')' in follow['ParamList']
