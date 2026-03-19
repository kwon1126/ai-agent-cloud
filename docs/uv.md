# uv (Python 패키지 매니저)

## uv란?

**uv**는 Rust로 작성된 초고속 Python 패키지 매니저이다. 기존 `pip`, `pip-tools`, `virtualenv`, `pyenv` 등을 하나로 통합한 도구로, 기존 도구 대비 **10~100배 빠른 속도**를 제공한다.

주요 특징:

- pip 대비 극적으로 빠른 패키지 설치 속도
- Python 버전 관리 내장 (`pyenv` 대체)
- 가상환경 관리 내장 (`virtualenv` 대체)
- `pyproject.toml` 기반의 프로젝트 관리
- lock 파일을 통한 재현 가능한 환경 구성

## 설치

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Homebrew (macOS)
brew install uv
```

## 설치 확인

```bash
uv --version
```

## 기본 사용법

### Python 버전 관리

```bash
# 사용 가능한 Python 버전 목록
uv python list

# 특정 Python 버전 설치
uv python install 3.12

# 특정 버전을 현재 프로젝트에 고정
uv python pin 3.12
```

### 프로젝트 초기화 및 관리

```bash
# 새 프로젝트 생성
uv init my-project
cd my-project

# 기존 디렉토리에서 프로젝트 초기화
uv init
```

### 패키지 설치 및 관리

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

### 가상환경

```bash
# 가상환경 생성 (.venv 디렉토리)
uv venv

# 특정 Python 버전으로 가상환경 생성
uv venv --python 3.12
```

### 스크립트 실행

```bash
# 프로젝트 스크립트 실행 (가상환경 자동 활성화)
uv run python main.py
uv run pytest
```

### pip 호환 명령어

```bash
# 기존 pip 명령어 스타일로도 사용 가능
uv pip install requests
uv pip install -r requirements.txt
uv pip freeze
```
