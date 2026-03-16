# AI Agent Cloud

개발 환경 설정 가이드

---

## 목차

1. [Git 설치](#1-git-설치)
2. [GitHub Desktop 설치](#2-github-desktop-설치)
3. [Node.js 설치](#3-nodejs-설치)
4. [Python 설치](#4-python-설치)
5. [uv (Python 패키지 매니저)](#5-uv-python-패키지-매니저)
6. [VS Code 확장 프로그램](#6-vs-code-확장-프로그램)

---

## 1. Git 설치

### macOS

```bash
# Homebrew를 이용한 설치
brew install git

# 또는 Xcode Command Line Tools 설치 시 자동 포함
xcode-select --install
```

### Windows

1. [https://git-scm.com/downloads/win](https://git-scm.com/downloads/win) 에서 설치 파일 다운로드
2. 설치 프로그램 실행 후 기본 옵션으로 설치
3. 설치 중 **"Git Bash Here"** 옵션 체크 권장

### 설치 확인

```bash
git --version
```

### 초기 설정

```bash
git config --global user.name "이름"
git config --global user.email "이메일@example.com"
```

---

## 2. GitHub Desktop 설치

GitHub Desktop은 Git을 GUI로 쉽게 사용할 수 있는 도구이다.

### macOS

```bash
# Homebrew를 이용한 설치
brew install --cask github
```

또는 [https://desktop.github.com](https://desktop.github.com) 에서 직접 다운로드

### Windows

1. [https://desktop.github.com](https://desktop.github.com) 에서 설치 파일 다운로드
2. 설치 프로그램 실행
3. GitHub 계정으로 로그인

### 기본 사용법

1. **Clone Repository** — 원격 저장소를 로컬로 복제
2. **Create Branch** — 새 브랜치 생성
3. **Commit** — 변경사항 커밋 (좌측 하단에서 메시지 작성 후 커밋)
4. **Push** — 원격 저장소에 반영
5. **Pull** — 원격 저장소의 변경사항 가져오기

---

## 3. Node.js 설치

### macOS

```bash
# Homebrew를 이용한 설치
brew install node

# 또는 nvm(Node Version Manager)을 이용한 설치 (권장)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash

# 터미널 재시작 후
nvm install --lts
nvm use --lts
```

### Windows

1. [https://nodejs.org](https://nodejs.org) 에서 **LTS 버전** 다운로드
2. 설치 프로그램 실행 후 기본 옵션으로 설치

### 설치 확인

```bash
node --version
npm --version
```

---

## 4. Python 설치

### macOS

```bash
# Homebrew를 이용한 설치
brew install python
```

### Windows

1. [https://www.python.org/downloads](https://www.python.org/downloads) 에서 최신 버전 다운로드
2. 설치 시 **"Add Python to PATH"** 반드시 체크
3. 설치 프로그램 실행

### 설치 확인

```bash
python3 --version
pip3 --version
```

---

## 5. uv (Python 패키지 매니저)

### uv란?

**uv**는 Rust로 작성된 초고속 Python 패키지 매니저이다. 기존 `pip`, `pip-tools`, `virtualenv`, `pyenv` 등을 하나로 통합한 도구로, 기존 도구 대비 **10~100배 빠른 속도**를 제공한다.

주요 특징:

- pip 대비 극적으로 빠른 패키지 설치 속도
- Python 버전 관리 내장 (`pyenv` 대체)
- 가상환경 관리 내장 (`virtualenv` 대체)
- `pyproject.toml` 기반의 프로젝트 관리
- lock 파일을 통한 재현 가능한 환경 구성

### 설치

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Homebrew (macOS)
brew install uv
```

### 설치 확인

```bash
uv --version
```

### 기본 사용법

#### Python 버전 관리

```bash
# 사용 가능한 Python 버전 목록
uv python list

# 특정 Python 버전 설치
uv python install 3.12

# 특정 버전을 현재 프로젝트에 고정
uv python pin 3.12
```

#### 프로젝트 초기화 및 관리

```bash
# 새 프로젝트 생성
uv init my-project
cd my-project

# 기존 디렉토리에서 프로젝트 초기화
uv init
```

#### 패키지 설치 및 관리

```bash
# 패키지 추가 (pyproject.toml에 자동 반영)
uv add requests
uv add flask sqlalchemy

# 개발용 패키지 추가
uv add --dev pytest ruff

# 패키지 제거
uv remove requests

# 의존성 동기화 (lock 파일 기반)
uv sync
```

#### 가상환경

```bash
# 가상환경 생성 (.venv 디렉토리)
uv venv

# 특정 Python 버전으로 가상환경 생성
uv venv --python 3.12
```

#### 스크립트 실행

```bash
# 프로젝트 스크립트 실행 (가상환경 자동 활성화)
uv run python main.py
uv run pytest
```

#### pip 호환 명령어

```bash
# 기존 pip 명령어 스타일로도 사용 가능
uv pip install requests
uv pip install -r requirements.txt
uv pip freeze
```

---

## 6. VS Code 확장 프로그램

VS Code에서 `Ctrl+Shift+X` (macOS: `Cmd+Shift+X`)를 눌러 확장 프로그램 마켓플레이스를 연다.

### Prettier - Code Formatter

코드 자동 포맷팅 도구. JavaScript, TypeScript, JSON, CSS, HTML 등을 지원한다.

- **마켓플레이스 검색**: `Prettier - Code formatter`
- **게시자**: Prettier
- **설치 ID**: `esbenp.prettier-vscode`

```bash
# 터미널에서 설치
code --install-extension esbenp.prettier-vscode
```

설치 후 설정 (`settings.json`):

```json
{
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "editor.formatOnSave": true
}
```

### Material Icon Theme

파일/폴더 아이콘을 Material Design 스타일로 변경해주는 테마.

- **마켓플레이스 검색**: `Material Icon Theme`
- **게시자**: Philipp Kief
- **설치 ID**: `PKief.material-icon-theme`

```bash
# 터미널에서 설치
code --install-extension PKief.material-icon-theme
```

설치 후 `Cmd+Shift+P` → `Material Icons: Activate Icon Theme` 선택

### EditorConfig for VS Code

`.editorconfig` 파일을 통해 에디터 설정을 프로젝트 단위로 통일해주는 도구.

- **마켓플레이스 검색**: `EditorConfig for VS Code`
- **게시자**: EditorConfig
- **설치 ID**: `EditorConfig.EditorConfig`

```bash
# 터미널에서 설치
code --install-extension EditorConfig.EditorConfig
```

### Python 관련 확장 프로그램

#### Python

Python 개발의 핵심 확장. IntelliSense, 디버깅, 린팅, 포맷팅 등을 지원한다.

- **마켓플레이스 검색**: `Python`
- **게시자**: Microsoft
- **설치 ID**: `ms-python.python`

```bash
code --install-extension ms-python.python
```

#### Pylance

Python 언어 서버. 빠른 자동완성, 타입 체크, import 자동 정리 등을 제공한다.

- **마켓플레이스 검색**: `Pylance`
- **게시자**: Microsoft
- **설치 ID**: `ms-python.vscode-pylance`

```bash
code --install-extension ms-python.vscode-pylance
```

#### Ruff

초고속 Python 린터 겸 포맷터. `flake8`, `isort`, `black` 등을 대체한다.

- **마켓플레이스 검색**: `Ruff`
- **게시자**: Astral Software
- **설치 ID**: `charliermarsh.ruff`

```bash
code --install-extension charliermarsh.ruff
```

#### Python Debugger

Python 디버깅 전용 확장.

- **마켓플레이스 검색**: `Python Debugger`
- **게시자**: Microsoft
- **설치 ID**: `ms-python.debugpy`

```bash
code --install-extension ms-python.debugpy
```

### 한번에 모든 확장 프로그램 설치 (터미널)

```bash
code --install-extension esbenp.prettier-vscode
code --install-extension PKief.material-icon-theme
code --install-extension EditorConfig.EditorConfig
code --install-extension ms-python.python
code --install-extension ms-python.vscode-pylance
code --install-extension charliermarsh.ruff
code --install-extension ms-python.debugpy
```
