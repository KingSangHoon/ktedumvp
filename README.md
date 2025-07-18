#  LLM 기반 에러 사전 탐지 시스템
## 📋 프로젝트 개요
**과제명**:  LLM 기반 에러 사전 탐지 시스템 개발  
**목적**: 커밋 코드 실시간 분석 및 에러 사전 탐지로 빌드 안정성 확보  
**목표**: 빌드 실패율 감소, 코드 품질 향상, 즉시 알림을 통한 신속한 에러 수정
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
## 📅 수행방안 (단독)
**사전 준비**: 사전 인프라 리소스 점검 실시
## 🛠️ 기술 스택
- **LLM 프레임워크**: LangChain4j
- **LLM 엔진**: Azure AI 서비스 (GPT-4)
- **알림 시스템**: 자체 알림 서비스
## 🏗️ 시스템 아키텍처
### 데이터 플로우
![시스템 아키텍처 다이어그램](https://github.com/KingSangHoon/ktedumvp/blob/main/%EB%8B%A4%EC%9D%B4%EC%96%B4%EA%B7%B8%EB%9E%A8.png)
### 주요 컴포넌트
- **Git Hook Listener**: 실시간 커밋 감지
- **Code Diff Analyzer**: 변경사항 분석
- **LLM Analysis Engine**: Azure AI 기반 코드 분석
- **Notification Service**: 통합 알림 서비스
## 🔮 향후 확장 계획
- **분석 범위 확대**: 의존성 관련 에러 분석, 비즈니스 로직 검증, 동시성/성능 문제 분석
- **성능 최적화**: 코드 성능 최적화 제안 및 개선점 자동 탐지
- **개발 지원**: 개발 가이드 자동생성, 릴리즈 노트 자동 작성
- **라이선스 관리**: 오픈소스 라이선스 충돌 검사 및 호환성 검증
- **플랫폼 확장**: SVN 지원 (Git 안정화 후 추가)
- **프로젝트 적용**: BSS 차세대 프로젝트 적용
- **기술 향상**: 추가 언어 지원 확장, AI 모델 성능 개선
