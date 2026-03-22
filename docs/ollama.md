# Ollama 설치

## Ollama란?

**Ollama**는 로컬 환경에서 LLM(대규모 언어 모델)을 쉽게 실행할 수 있는 도구이다. 별도의 클라우드 서비스 없이 자신의 컴퓨터에서 다양한 오픈소스 모델을 실행할 수 있다.

주요 특징:

- 로컬에서 LLM 실행 (인터넷 불필요)
- 간단한 CLI 인터페이스
- Llama 3, Gemma, Mistral, Phi 등 다양한 모델 지원
- REST API 제공 (기본 포트: `11434`)
- GPU 가속 지원 (Apple Silicon, NVIDIA)

## 설치

### macOS

macOS에서는 다음 세 가지 방법 중 하나를 선택해 설치할 수 있습니다.

**방법 1: 터미널 명령어 (공식 설치 스크립트)**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**방법 2: Homebrew 이용**
Homebrew가 설치되어 있지 않다면 먼저 터미널에서 아래 명령어로 설치합니다.
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```
이후 아래 명령어로 Ollama를 설치합니다.
```bash
brew install ollama
```

**방법 3: 직접 다운로드**
[https://ollama.com/download](https://ollama.com/download) 에서 패키지를 받아 직접 설치합니다.

### Windows

1. [https://ollama.com/download](https://ollama.com/download) 에서 설치 파일 다운로드
2. 설치 프로그램 실행

### Linux

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

## 설치 확인

```bash
ollama --version
```

## 기본 사용법

### 모델 다운로드 및 실행

```bash
# 모델 다운로드 및 대화 시작
ollama run llama3.2

# 특정 크기의 모델 실행
ollama run llama3.2:1b
ollama run llama3.2:3b

# 경량 모델 (코딩용)
ollama run qwen2.5-coder:7b

# 경량 모델 (범용)
ollama run gemma3:4b
```

### 모델 관리

```bash
# 다운로드된 모델 목록 확인
ollama list

# 모델 미리 다운로드 (실행 없이)
ollama pull llama3.2

# 모델 삭제
ollama rm llama3.2
```

### 서버 실행

```bash
# Ollama 서버 시작 (백그라운드)
ollama serve
```

서버가 실행되면 `http://localhost:11434` 에서 REST API를 사용할 수 있다.

### API 호출 예시

```bash
# curl을 이용한 API 호출
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.2",
  "prompt": "안녕하세요",
  "stream": false
}'
```

### Python에서 사용

```bash
# ollama 파이썬 패키지 설치
uv add ollama
```

```python
import ollama

response = ollama.chat(model="llama3.2", messages=[
    {"role": "user", "content": "안녕하세요"}
])
print(response["message"]["content"])
```

## 모델 검색

전체 모델 목록은 [ollama.com/library](https://ollama.com/library) 에서 확인할 수 있다.

```bash
# CLI에서 모델 검색
ollama search llama
```

## 주요 모델 목록

| 모델 | 다운로드 명령어 | 크기 | 특징 |
|------|-----------------|------|------|
| Llama 3.2 | `ollama pull llama3.2` | ~2GB | Meta, 범용 경량 |
| Llama 3.3 | `ollama pull llama3.3` | ~43GB | Meta, 고성능 |
| DeepSeek R1 | `ollama pull deepseek-r1` | ~4.7GB | 추론/사고 특화 |
| Gemma 3 | `ollama pull gemma3` | ~3GB | Google, 범용 |
| Qwen 2.5 Coder | `ollama pull qwen2.5-coder` | ~4.7GB | 코딩 특화 |
| Mistral | `ollama pull mistral` | ~4.1GB | 범용 |
| Phi-4 | `ollama pull phi4` | ~9.1GB | Microsoft, 추론 |
| CodeLlama | `ollama pull codellama` | ~3.8GB | 코드 생성 |

크기는 기본(default) 태그 기준이며, `:1b`, `:7b`, `:70b` 같은 태그로 다른 크기도 선택 가능하다.

> **참고**: 모델 크기가 클수록 성능이 좋지만, 그만큼 RAM과 디스크 공간이 필요하다. Apple Silicon Mac에서는 통합 메모리 덕분에 비교적 큰 모델도 원활하게 실행 가능하다.

## AI Agent 실습용 추천 모델

AI Agent는 **코드 생성 + 함수 호출(tool use) + JSON 형식 응답** 능력이 중요하다. 노트북 RAM에 맞춰 모델을 선택한다.

### RAM별 추천

| RAM | 모델 | 명령어 | 용도 |
|-----|------|--------|------|
| 8GB | `llama3.2:3b` | `ollama pull llama3.2` | 범용 경량 |
| 16GB | `qwen2.5-coder:7b` | `ollama pull qwen2.5-coder:7b` | 코딩/Agent |
| 16GB | `deepseek-r1:8b` | `ollama pull deepseek-r1:8b` | 추론/사고 |
| 32GB+ | `qwen2.5-coder:14b` | `ollama pull qwen2.5-coder:14b` | 코딩/Agent 고성능 |

### RAM 확인 방법

```bash
# macOS
sysctl -n hw.memorysize | awk '{print $1/1024/1024/1024 "GB"}'

# Windows (PowerShell)
(Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory / 1GB
```

### 실습용 추천 조합

7b~14b 모델이면 기본적인 Agent 실습에 충분하다. 두 가지를 받아두면 용도별로 활용할 수 있다.

```bash
# 코딩/Agent용
ollama pull qwen2.5-coder:7b

# 범용 대화/추론용
ollama pull llama3.2
```

## 모델 저장 경로

Ollama 앱과 모델 파일은 별도로 저장된다. 앱을 삭제해도 모델은 남아있다.

- **macOS**: `~/.ollama/models/`
- **Linux**: `~/.ollama/models/`
- **Windows**: `C:\Users\<사용자>\.ollama\models\`

모델을 포함해 전부 삭제하려면:

```bash
rm -rf ~/.ollama
```
