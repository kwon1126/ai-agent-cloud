# Node.js 설치

## macOS

```bash
# Homebrew를 이용한 설치
brew install node

# 또는 nvm(Node Version Manager)을 이용한 설치 (권장)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash

# 터미널 재시작 후
nvm install --lts
nvm use --lts
```

## Windows

1. [https://nodejs.org](https://nodejs.org) 에서 **LTS 버전** 다운로드
2. 설치 프로그램 실행 후 기본 옵션으로 설치

## 설치 확인

```bash
node --version
npm --version
```
