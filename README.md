# LLM 기반 정적 코드 분석 및 에러 예방 시스템

## 📋 프로젝트 개요

**과제명**: LLM 기반 정적 코드 분석 및 에러 예방 시스템 개발

**목적**: DevPilot 연동을 통한 커밋 코드 실시간 분석 및 에러 사전 탐지로 빌드 안정성 확보

**목표**: 빌드 실패율 감소, 코드 품질 향상, 즉시 알림을 통한 신속한 에러 수정

**수행기간**: 2025년 8월 ~ 11월 (4개월)

## 🚨 현재 문제점 및 예상 효과

### 1.1 현재 문제점
- **빌드 실패**: 커밋 후 빌드 단계에서 에러 발견으로 인한 시간 손실
- **수동 코드 검토**: 사람에 의한 코드 리뷰의 한계와 일관성 부족
- **보안 취약점**: 개발 단계에서 보안 문제 미발견

### 1.2 예상 효과
- **빌드 안정성**: 빌드 실패율 감소
- **즉시 피드백**: 커밋 즉시 에러 탐지 및 알림
- **BSS 차세대 프로젝트 대비**: 대규모 프로젝트 안정성 확보
- **보안 강화**: 개발 단계 보안 취약점 사전 차단
- **확장성**: Git 사용 모든 프로젝트에 적용 가능

### 1.3 향후 확장 방향
- 의존성 관련 에러 분석
- 비즈니스 로직 검증
- 동시성/성능 문제 분석
- SVN 지원 (Git 안정화 후 추가)

## 🔍 코드 분석 범위

### 3.1 감지 가능한 에러 (현재 시스템)

**문법/구조적 에러**
- Syntax Error
- 괄호 누락
- 변수명 오타 등

**명백한 코딩 실수**
- Null Pointer 위험
- 인덱스 초과
- 리소스 누수 등

**보안 취약점**
- SQL Injection
- 하드코딩된 민감정보
- XSS 위험 등

### 3.2 알림 시스템
- **즉시 알림**: 커밋 후 분석 완료 및 알림
- **다중 채널**: 문자(SMS) + 이메일 동시 발송
- **심각도별 구분**: Critical, High, Medium, Low 등급

## 🤖 LLM 선택 및 근거

### Ollama 선택 이유
**외부망으로의 데이터 유출을 방지하고, 완전 로컬에서 실행되는 "Ollama" 사용**

| 구분 | GPT/Claude(온라인) | Ollama(오프라인) |
|------|-------------------|------------------|
| **보안** | 외부 서버 전송 (부적합) | 완전 로컬 처리 (적합) |
| **비용** | 높음 (사용량에 따른 비용 증가) | 온라인에 비해 적음 (초기 인프라 비용만 발생) |
| **성능** | 최고 | 우수 (실용적) |

## 📅 수행방안 (단독)

**수행 환경**: K-ICIS SIT환경에서 진행하며, 개발/운영 환경에 영향도 없음

**사전 준비**: 사전 인프라 리소스 점검 실시

### 단계별 계획

| 단계 | 기간 | 주요 기능 |
|------|------|-----------|
| **1단계** | 8월 | 인프라 리소스 점검, Ollama 환경 구축, Git 커밋 수집 |
| **2단계** | 9월 | 커밋메시지 분석 엔진, 코드 diff 분석, 하이브리드 로직 |
| **3단계** | 10월 | 파일별 특화 분석, 문서 출력 기능, 성능 최적화 |
| **4단계** | 11월 | 성능 최적화, 에러처리, 파일럿 테스트 |

## 🛠️ 기술 스택

### 5.1 기술 스택
- **LLM 프레임워크**: LangChain4j
- **LLM 엔진**: Ollama (미정)
- **알림 시스템**: DevPilot-Common (DevPilot, Neone 알림 서비스)

### 핵심 기술
```java
// LangChain4j 기반 Ollama 연동 예시
OllamaEmbeddingModel embeddingModel = OllamaEmbeddingModel.builder()
    .baseUrl("http://localhost:11434")
    .modelName("codellama")
    .build();

OllamaChatModel chatModel = OllamaChatModel.builder()
    .baseUrl("http://localhost:11434")
    .modelName("codellama")
    .build();
```

## 🏗️ 시스템 아키텍처

### 데이터 플로우
```
Git Repository → Commit Hook → Code Analysis Engine → LLM Processing → 
Error Detection → Notification System → Developer Alert
```

### 주요 컴포넌트
- **Git Hook Listener**: 실시간 커밋 감지
- **Code Diff Analyzer**: 변경사항 분석
- **LLM Analysis Engine**: Ollama 기반 코드 분석
- **Notification Service**: DevPilot-Common 연동 알림

## 📋 요청사항

### 6.1 테스트 협조
- **K-ICIS Cluster (SIT환경) 사용 요청**
- **DevPilot-Common 사용 요청**

## 📁 프로젝트 구조
```
src/
├── main/java/
│   ├── analyzer/          # 코드 분석 엔진
│   ├── git/              # Git 연동 모듈
│   ├── llm/              # LLM 인터페이스
│   ├── notification/     # 알림 시스템
│   └── config/           # 설정 관리
├── main/resources/
│   ├── prompts/          # LLM 프롬프트 템플릿
│   └── application.yml   # 설정 파일
└── test/                 # 테스트 코드
```

## 🚀 설치 및 실행

### 사전 요구사항
```bash
- Java 17+
- Ollama 서버
- Git 연동 권한
- K-ICIS SIT 환경 접근
```

### 실행 방법
```bash
# Ollama 모델 다운로드
ollama pull codellama

# 애플리케이션 실행
mvn spring-boot:run
```

## 📊 성과 지표
- 빌드 실패율 감소 목표: 30% 이상
- 에러 탐지 시간 단축: 커밋 후 5분 이내
- 보안 취약점 사전 차단률: 80% 이상

## 🔮 향후 계획
- BSS 차세대 프로젝트 적용
- 추가 언어 지원 확장
- AI 모델 성능 개선
- 기업 전체 Git 프로젝트 확산
