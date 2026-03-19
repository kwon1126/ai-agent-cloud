# Git 설치

## macOS

```bash
# Homebrew를 이용한 설치
brew install git

# 또는 Xcode Command Line Tools 설치 시 자동 포함
xcode-select --install
```

## Windows

1. [https://git-scm.com/downloads/win](https://git-scm.com/downloads/win) 에서 설치 파일 다운로드
2. 설치 프로그램 실행 후 기본 옵션으로 설치
3. 설치 중 **"Git Bash Here"** 옵션 체크 권장

## 설치 확인

```bash
git --version
```

## 초기 설정

```bash
git config --global user.name "이름"
git config --global user.email "이메일@example.com"
```
