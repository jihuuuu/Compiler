# main.py 
import sys
from parser import parser

def main():
    if len(sys.argv) != 2:
        print("Usage: python main.py <token_file>")
        sys.exit(1)
    token_file = sys.argv[1]
    # 토큰 파일에서 심볼(터미널)들을 읽어 리스트로 만듭니다.
    tokens = []
    with open(token_file, 'r') as f:
        for line in f:
            tokens.extend(line.strip().split())
    # 입력 심볼의 끝에 end-marker '$'를 추가
    tokens.append('$')
    result = parser(tokens)
    # 파스 트리 또는 에러 리포트 출력
    print(result)

if __name__ == "__main__":
    main()
