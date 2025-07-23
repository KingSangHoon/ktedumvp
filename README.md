# Git 커밋 이력 기반 LLM 코드 분석 및 컴파일 예측 시스템

## 📋 프로젝트 개요
**과제명**: Git 커밋 이력 기반 LLM 코드 분석 및 컴파일 예측 시스템 개발  
**목적**: 커밋 이력 패턴 분석을 통한 코드 품질 예측 및 컴파일 성공률 향상  
**목표**: 과거 커밋 데이터 학습으로 컴파일 실패 사전 예측, 코드 변경 위험도 평가, 개발 효율성 극대화

## 🚨 현재 문제점 및 예상 효과

### 현재 문제점
- **반복적 컴파일 실패**: 유사한 패턴의 코드 변경으로 인한 반복적 빌드 실패
- **커밋 이력 미활용**: 풍부한 Git 히스토리 데이터의 분석적 활용 부족
- **패턴 인식 한계**: 개발자의 경험에만 의존한 위험 코드 식별
- **리소스 낭비**: 예측 가능한 컴파일 실패로 인한 CI/CD 리소스 낭비

### 예상 효과
- **예측 정확도**: 커밋 패턴 분석을 통한 컴파일 성공률 80% 이상 예측
- **리소스 최적화**: 불필요한 빌드 프로세스 사전 차단으로 30% 리소스 절약
- **개발 생산성**: 코드 변경 위험도 사전 알림으로 개발 속도 향상
- **지식 축적**: 팀 전체의 코딩 패턴 학습 및 베스트 프랙티스 도출

## 🔍 분석 범위

### 분석 대상
**히스토리 기반 위험 평가**
- 과거 실패한 커밋과의 유사도 분석
- 특정 파일/디렉토리의 변경 위험도
- 동시 수정 파일 조합별 실패 확률

### 컴파일 예측 모델
**성공률 예측**
- 현재 커밋의 컴파일 성공 확률 (0-100%)
- 위험도 등급별 분류 (Safe, Caution, High Risk, Critical)
- 예상 실패 원인 및 해결 방안 제시

## 📊 시스템 아키텍처

### 프론트엔드 레이어 (Streamlit)
```
사용자 인터페이스 → GitHub API 직접 호출 → 커밋 데이터 조회
       ↓
백엔드 API 호출 → LLM 분석 요청 → 결과 시각화
```

### 백엔드 API 레이어
```
REST API 엔드포인트:
- /analyze: 코드 diff 직접 분석
- /analyze-real-commit: GitHub 커밋 실시간 분석  
- /analyze-commit: 특정 커밋 SHA 분석
- /health: 서버 상태 확인

AI Agent 통합:
- 다중 LLM 프로바이더 지원 (Azure OpenAI, OpenAI, Claude)
- 동적 프롬프트 생성 및 최적화
- 분석 결과 후처리 및 검증

RAG 데이터 연동:
- MS 인덱서를 통한 도메인별 히스토리 데이터 검색
- 컨텍스트 기반 특화된 분석 제공
```

## 🛠️ 기술 스택

**프론트엔드**
- Streamlit 웹 애플리케이션
- GitHub API 직접 연동
- 실시간 분석 결과 시각화
- 반응형 UI 및 다이얼로그 팝업

**백엔드 API & AI Agent**
- Spring Boot 기반 REST API 서버
- `/analyze`, `/analyze-real-commit` 엔드포인트
- **통합 AI Agent**: 다중 LLM 모델 지원 (Azure OpenAI, OpenAI, Claude)
- GitHub API 연동 및 코드 diff 분석
- 지능형 프롬프트 엔지니어링 및 결과 최적화
- **RAG 시스템**: MS 인덱서 기반 도메인별 히스토리 데이터 활용

## 🎯 주요 기능

### 실시간 커밋 분석
- **다양한 조회 방식**: 최근 커밋, 특정 커밋 SHA, 기간별 커밋 조회
- **파일 타입 필터링**: .py, .js, .ts, .java, .cpp 등 언어별 선택 분석
- **즉시 분석**: 커밋 선택 후 즉시 AI 분석 실행
- **실시간 연동**: GitHub API를 통한 최신 커밋 데이터 실시간 조회

### AI Agent 기반 다각도 분석
- **코드 품질 평가**: 코딩 스타일, 복잡도, 가독성 분석
- **보안 취약점 탐지**: SQL Injection, XSS, 하드코딩된 민감정보 검사
- **성능 최적화**: 비효율적 알고리즘, 메모리 누수, 리소스 관리 문제 식별
- **버그 탐지**: Null Pointer, 인덱스 초과, 논리적 오류 사전 발견
- **리팩토링 제안**: 코드 구조 개선 및 모범 사례 추천
- **지능형 분석**: AI Agent를 통한 컨텍스트 기반 정확한 분석
- **도메인 특화 분석**: RAG를 통한 프로젝트별 히스토리 패턴 반영

### 유연한 분석 환경
- **다중 LLM 지원**: Azure OpenAI, OpenAI, Claude 모델 선택
- **테스트/실제 모드**: 더미 데이터로 테스트 또는 실제 GitHub 연동
- **직접 SHA 분석**: Repository 정보와 커밋 SHA로 즉시 분석
- **배치 분석**: 여러 커밋 동시 분석 및 비교

### 사용자 친화적 인터페이스
- **직관적 웹 UI**: Streamlit 기반 반응형 인터페이스
- **팝업 분석**: 상세 분석 결과를 다이얼로그로 표시
- **실시간 상태**: API 서버 연결 상태 및 진행 상황 표시
- **설정 관리**: 사이드바를 통한 모든 분석 옵션 중앙 관리

## 💻 구현 현황

### 현재 구현된 기능
**Streamlit 웹 애플리케이션**
- GitHub API 연동을 통한 실시간 커밋 조회
- 다양한 조회 방식 (최근/특정/기간별 커밋)
- 파일 타입별 필터링 및 코드 diff 표시
- AI 분석 결과 실시간 표시

**백엔드 API 서버 + AI Agent**
- REST API 엔드포인트 구현 (`/analyze`, `/analyze-real-commit`)
- **통합 AI Agent**: 다중 LLM 모델 지원 (Azure OpenAI, OpenAI, Claude)
- GitHub API 연동 및 코드 분석 로직
- 지능형 프롬프트 생성 및 결과 후처리
- **RAG 시스템**: MS 인덱서를 통한 도메인별 커밋 히스토리 활용
- 에러 핸들링 및 상태 모니터링

**분석 기능**
- 코드 품질, 보안, 성능, 버그 탐지 분석
- 커밋별 상세 분석 및 결과 시각화
- 테스트용 더미 데이터 및 실제 GitHub 연동
- 실시간 분석 상태 표시

### 주요 코드 구조
```python
# GitHub API 연동
def get_commits(owner, repo, token=None, since=None, until=None, per_page=10)
def get_commit_detail(owner, repo, sha, token=None)

# AI Agent 통합 분석 API 호출
def analyze_code_with_ai(code_diff, filename, commit_message, provider, model, analysis_types)
def analyze_real_commit(repo_owner, repo_name, commit_sha, analysis_types, github_token=None)

# UI 구성 요소
- 사이드바: 설정 및 직접 분석 기능
- 메인 화면: 커밋 목록 및 조회 버튼
- 팝업 다이얼로그: 상세 분석 결과 표시
```
