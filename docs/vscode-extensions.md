# VS Code 확장 프로그램

VS Code에서 `Ctrl+Shift+X` (macOS: `Cmd+Shift+X`)를 눌러 확장 프로그램 마켓플레이스를 연다.

## Prettier - Code Formatter

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

## Material Icon Theme

파일/폴더 아이콘을 Material Design 스타일로 변경해주는 테마.

- **마켓플레이스 검색**: `Material Icon Theme`
- **게시자**: Philipp Kief
- **설치 ID**: `PKief.material-icon-theme`

```bash
# 터미널에서 설치
code --install-extension PKief.material-icon-theme
```

설치 후 `Cmd+Shift+P` → `Material Icons: Activate Icon Theme` 선택

## EditorConfig for VS Code

`.editorconfig` 파일을 통해 에디터 설정을 프로젝트 단위로 통일해주는 도구.

- **마켓플레이스 검색**: `EditorConfig for VS Code`
- **게시자**: EditorConfig
- **설치 ID**: `EditorConfig.EditorConfig`

```bash
# 터미널에서 설치
code --install-extension EditorConfig.EditorConfig
```

## Python 관련 확장 프로그램

### Python

Python 개발의 핵심 확장. IntelliSense, 디버깅, 린팅, 포맷팅 등을 지원한다.

- **마켓플레이스 검색**: `Python`
- **게시자**: Microsoft
- **설치 ID**: `ms-python.python`

```bash
code --install-extension ms-python.python
```

### Pylance

Python 언어 서버. 빠른 자동완성, 타입 체크, import 자동 정리 등을 제공한다.

- **마켓플레이스 검색**: `Pylance`
- **게시자**: Microsoft
- **설치 ID**: `ms-python.vscode-pylance`

```bash
code --install-extension ms-python.vscode-pylance
```

### Ruff

초고속 Python 린터 겸 포맷터. `flake8`, `isort`, `black` 등을 대체한다.

- **마켓플레이스 검색**: `Ruff`
- **게시자**: Astral Software
- **설치 ID**: `charliermarsh.ruff`

```bash
code --install-extension charliermarsh.ruff
```

### Python Debugger

Python 디버깅 전용 확장.

- **마켓플레이스 검색**: `Python Debugger`
- **게시자**: Microsoft
- **설치 ID**: `ms-python.debugpy`

```bash
code --install-extension ms-python.debugpy
```

## 한번에 모든 확장 프로그램 설치 (터미널)

```bash
code --install-extension esbenp.prettier-vscode
code --install-extension PKief.material-icon-theme
code --install-extension EditorConfig.EditorConfig
code --install-extension ms-python.python
code --install-extension ms-python.vscode-pylance
code --install-extension charliermarsh.ruff
code --install-extension ms-python.debugpy
```
