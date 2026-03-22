# AI Agent Cloud

이 프로젝트는 Ollama를 사용하여 로컬에서 동작하는 AI 코딩 어시스턴트를 구현합니다.

## 필수 요구사항 (Ollama 모델 설치)

이 프로젝트(`main.py`)를 기본 설정으로 실행하려면 **`qwen2.5-coder:7b`** 모델이 필요합니다. 
터미널에서 아래 명령어를 실행하여 해당 모델을 다운로드(설치)해 주세요.

```bash
ollama pull qwen2.5-coder:7b
```

> **참고:** `main.py` 내부의 `execute_llm_call` 함수에서 `model="qwen2.5-coder:7b"` 부분을 수정하면 `llama3.2` 등 다른 모델도 사용할 수 있습니다. 변경 시에는 사용할 모델을 사전에 `ollama pull <모델명>`으로 설치해 두어야 합니다.

## 실행 방법

이 프로젝트는 `uv` 패키지 관리자를 사용합니다. 터미널에서 다음 명령어를 입력하여 AI 에이전트를 실행할 수 있습니다.

```bash
uv run main.py
```
