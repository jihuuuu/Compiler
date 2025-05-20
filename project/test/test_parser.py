# tests/test_parser.py

import pytest
from parser import parser

def load_tokens(path):
    with open(path, 'r') as f:
        toks = f.read().split()
    toks.append('$')
    return toks

# 정상 케이스
@pytest.mark.parametrize("tokfile", [
    "tests/valid1.tok",
    # "tests/valid2.tok",
])
def test_valid(tokfile):
    tokens = load_tokens(tokfile)
    result = parser(tokens)
    # 파스 트리 형태 확인 (예: 튜플)
    assert isinstance(result, tuple)

# 오류 케이스
@pytest.mark.parametrize("tokfile", [
    "tests/invalid1.tok",
    # "tests/invalid2.tok",
])
def test_invalid(tokfile):
    tokens = load_tokens(tokfile)
    result = parser(tokens)
    assert isinstance(result, dict) and "error" in result
