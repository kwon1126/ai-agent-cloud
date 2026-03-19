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

```bash
# Homebrew를 이용한 설치
brew install ollama

# 또는 공식 사이트에서 직접 다운로드
# https://ollama.com/download
```

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

## 권장 모델

| 모델 | 크기 | 용도 |
|------|------|------|
| `llama3.2:1b` | ~1.3GB | 가벼운 테스트, 저사양 PC |
| `llama3.2:3b` | ~2GB | 범용 대화 |
| `gemma3:4b` | ~3GB | 범용 대화 |
| `qwen2.5-coder:7b` | ~4.7GB | 코드 생성/분석 |
| `llama3.3:70b` | ~43GB | 고성능 (RAM 64GB 이상 권장) |

> **참고**: 모델 크기가 클수록 성능이 좋지만, 그만큼 RAM과 디스크 공간이 필요하다. Apple Silicon Mac에서는 통합 메모리 덕분에 비교적 큰 모델도 원활하게 실행 가능하다.
