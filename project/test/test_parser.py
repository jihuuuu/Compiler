import pytest
import sys, os
# project 폴더(=parser.py가 있는 곳)를 PYTHONPATH에 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from parser import parser, ErrorReport, ParseTree

def load_tokens(path):
    with open(path, 'r') as f:
        txts = f.read().split()
    txts.append('$')
    return txts

# sample_input 케이스
@pytest.mark.parametrize("textfile", ["test/sample_input.txt"])
def test_sample(textfile):
    tokens = load_tokens(textfile)
    ok, tree = parser(tokens)
    assert ok, "파싱에 실패했습니다"
    assert isinstance(tree, ParseTree)

# 정상 케이스
@pytest.mark.parametrize("textfile", ["test/valid1.txt"])
def test_valid(textfile):
    tokens = load_tokens(textfile)
    result = parser(tokens)
    ok, tree = parser(tokens)
    assert ok, "파싱에 실패했습니다"
    assert isinstance(tree, ParseTree)

# 오류 케이스
@pytest.mark.parametrize("textfile", ["test/invalid1.txt"])
def test_invalid(textfile):
    tokens = load_tokens(textfile)
    ok, err = parser(tokens)
    assert not ok, "오류 케이스인데 True로 나왔습니다"
    assert isinstance(err, ErrorReport)
