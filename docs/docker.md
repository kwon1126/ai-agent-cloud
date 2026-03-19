# Docker Desktop 설치

## Docker란?

**Docker**는 애플리케이션을 컨테이너로 패키징하여 어디서든 동일한 환경에서 실행할 수 있게 해주는 도구이다. **Docker Desktop**은 macOS, Windows에서 Docker를 쉽게 사용할 수 있도록 GUI와 함께 제공되는 데스크탑 애플리케이션이다.

주요 특징:

- 컨테이너 기반 격리 환경 제공
- OS에 관계없이 동일한 실행 환경 보장
- Docker Compose로 멀티 컨테이너 관리
- GUI 대시보드로 컨테이너 모니터링
- Kubernetes 클러스터 내장 (선택적 활성화)

## 설치

### macOS

1. [https://www.docker.com/products/docker-desktop/](https://www.docker.com/products/docker-desktop/) 에서 설치 파일 다운로드
   - Apple Silicon (M1/M2/M3/M4): **Apple Silicon** 버전 선택
   - Intel: **Intel chip** 버전 선택
2. `.dmg` 파일 실행 후 `Docker.app`을 Applications 폴더로 드래그
3. Docker Desktop 앱 실행
4. 초기 설정 완료 (서비스 약관 동의)

또는 Homebrew로 설치:

```bash
brew install --cask docker
```

### Windows

1. [https://www.docker.com/products/docker-desktop/](https://www.docker.com/products/docker-desktop/) 에서 설치 파일 다운로드
2. 설치 프로그램 실행
3. 설치 중 **WSL 2 백엔드 사용** 옵션 체크 (권장)
4. 설치 완료 후 재부팅
5. Docker Desktop 앱 실행

> **참고**: Windows에서는 WSL 2가 필요하다. 설치되어 있지 않으면 Docker Desktop이 설치 과정에서 안내해준다.

```powershell
# WSL 2 수동 설치 (필요한 경우)
wsl --install
```

## 설치 확인

```bash
# Docker 버전 확인
docker --version

# Docker Compose 버전 확인
docker compose version

# 테스트 컨테이너 실행
docker run hello-world
```

`Hello from Docker!` 메시지가 출력되면 정상적으로 설치된 것이다.

## 기본 사용법

### 컨테이너 실행

```bash
# 컨테이너 실행 (포그라운드)
docker run <이미지명>

# 컨테이너 백그라운드 실행
docker run -d <이미지명>

# 포트 매핑 (-p 호스트포트:컨테이너포트)
docker run -d -p 8080:80 nginx

# 이름 지정
docker run -d --name my-nginx -p 8080:80 nginx

# 볼륨 마운트 (-v 호스트경로:컨테이너경로)
docker run -d -v $(pwd)/data:/app/data <이미지명>
```

### 컨테이너 관리

```bash
# 실행 중인 컨테이너 목록
docker ps

# 모든 컨테이너 목록 (중지된 것 포함)
docker ps -a

# 컨테이너 중지
docker stop <컨테이너명>

# 컨테이너 시작
docker start <컨테이너명>

# 컨테이너 재시작
docker restart <컨테이너명>

# 컨테이너 삭제
docker rm <컨테이너명>

# 컨테이너 로그 확인
docker logs <컨테이너명>
docker logs -f <컨테이너명>  # 실시간

# 컨테이너 내부 접속
docker exec -it <컨테이너명> bash
```

### 이미지 관리

```bash
# 이미지 목록
docker images

# 이미지 다운로드
docker pull <이미지명>

# 이미지 삭제
docker rmi <이미지명>

# 사용하지 않는 이미지 정리
docker image prune
```

## Docker Compose

여러 컨테이너를 하나의 파일로 정의하고 관리할 수 있다.

### docker-compose.yml 예시

```yaml
services:
  web:
    image: nginx
    ports:
      - "8080:80"
    volumes:
      - ./html:/usr/share/nginx/html

  db:
    image: postgres:16
    environment:
      POSTGRES_PASSWORD: mysecretpassword
    volumes:
      - db-data:/var/lib/postgresql/data

volumes:
  db-data:
```

### Compose 명령어

```bash
# 실행
docker compose up -d

# 상태 확인
docker compose ps

# 로그 확인
docker compose logs -f

# 중지
docker compose down

# 볼륨까지 삭제
docker compose down -v
```

## Docker Desktop 설정 (권장)

Docker Desktop > Settings에서 리소스를 조정할 수 있다.

### 리소스 할당 (macOS/Windows)

| 항목 | 기본값 | 권장값 |
|------|--------|--------|
| CPUs | 절반 | 필요에 따라 조정 |
| Memory | 2GB | 4GB 이상 |
| Disk | 64GB | 필요에 따라 조정 |

> **참고**: Apple Silicon Mac에서는 리소스가 호스트와 자동으로 공유되므로 별도 설정이 필요 없다.

## Docker로 Ollama 실행

Docker를 사용하면 Ollama를 컨테이너로 실행할 수 있다. 호스트 환경을 오염시키지 않고 깔끔하게 관리할 수 있다.

### CPU만 사용하는 경우

```bash
docker run -d \
  --name ollama \
  -p 11434:11434 \
  -v ollama:/root/.ollama \
  ollama/ollama
```

### NVIDIA GPU 사용하는 경우

```bash
docker run -d \
  --name ollama \
  --gpus all \
  -p 11434:11434 \
  -v ollama:/root/.ollama \
  ollama/ollama
```

> **참고**: GPU 사용을 위해서는 [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)이 설치되어 있어야 한다.

### 컨테이너 안에서 모델 실행

```bash
# 모델 다운로드 및 실행
docker exec -it ollama ollama run llama3.2

# 모델 미리 다운로드
docker exec -it ollama ollama pull qwen2.5-coder:7b

# 다운로드된 모델 목록 확인
docker exec -it ollama ollama list
```

### Docker Compose로 Ollama 실행

```yaml
services:
  ollama:
    image: ollama/ollama
    container_name: ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama:/root/.ollama
    restart: unless-stopped
    # GPU 사용 시 아래 주석 해제
    # deploy:
    #   resources:
    #     reservations:
    #       devices:
    #         - driver: nvidia
    #           count: all
    #           capabilities: [gpu]

volumes:
  ollama:
```

```bash
docker compose up -d
```

## 전체 정리

```bash
# 모든 컨테이너 중지 및 삭제
docker stop $(docker ps -aq)
docker rm $(docker ps -aq)

# 모든 이미지 삭제
docker rmi $(docker images -q)

# Docker 시스템 전체 정리 (미사용 리소스)
docker system prune -a
```

> **주의**: `docker system prune -a`는 사용하지 않는 모든 이미지, 컨테이너, 네트워크를 삭제한다. 필요한 데이터가 없는지 확인 후 실행한다.
