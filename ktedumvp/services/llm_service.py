# backend/services/llm_service.py
import os
from openai import AzureOpenAI
from dotenv import load_dotenv
from typing import List
from services.azure_rag_service import AzureRAGService

# 환경변수 로드
load_dotenv()

class AzureOpenAIService:
    def __init__(self):
        try:
            self.client = AzureOpenAI(
                azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
                api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                api_version=os.getenv("AZURE_OPENAI_API_VERSION")
            )
            self.deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
            self.rag_service = AzureRAGService()  # RAG 서비스 초기화
            print(f"Azure OpenAI 초기화 성공 - Deployment: {self.deployment}")
        except Exception as e:
            print(f"Azure OpenAI 초기화 실패: {e}")
            raise
    
    def analyze_code(
        self, 
        code_diff: str, 
        commit_message: str, 
        filename: str,
        analysis_types: List[str]
    ) -> str:
        """
        일반적인 코드 분석 (더미 데이터용) + RAG 연동
        """
        try:
            # 1. 외부 API 패턴 감지
            detected_patterns = self.rag_service.detect_external_apis(code_diff)
            print(f"감지된 API 패턴: {detected_patterns}")
            
            # 2. RAG에서 관련 지식 검색
            knowledge_docs = self.rag_service.search_api_knowledge(detected_patterns)
            
            # 3. RAG 지식을 프롬프트용으로 포맷팅
            api_knowledge = self.rag_service.format_knowledge_for_prompt(knowledge_docs)
            has_rag_content = len(api_knowledge.strip()) > 0
            print(f"📝 [LLM] RAG 콘텐츠 포함 여부: {'✅ YES' if has_rag_content else '❌ NO'}")
        
            # 4. RAG 지식이 포함된 프롬프트 생성
            prompt = self._create_analysis_prompt_with_rag(
                code_diff, commit_message, filename, analysis_types, api_knowledge
            )
            
            print(f"Azure OpenAI API 호출 시작 (RAG 강화) - Model: {self.deployment}")
            
            # Azure OpenAI API 호출
            response = self.client.chat.completions.create(
                model=self.deployment,
                messages=[
                    {
                        "role": "system", 
                        "content": "당신은 전문적인 코드 리뷰어입니다. 코드 변경사항을 분석하고 상세한 피드백을 제공합니다. 제공된 API 가이드라인을 참고하여 더 정확한 분석을 제공하세요."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            result = response.choices[0].message.content
            print("Azure OpenAI API 호출 성공 (RAG 강화)")
            return result
            
        except Exception as e:
            print(f"Azure OpenAI API 호출 실패: {e}")
            raise Exception(f"Azure OpenAI API 호출 실패: {str(e)}")
    
    def analyze_code_for_critical_issues(
        self, 
        code_diff: str, 
        commit_message: str, 
        filename: str,
        analysis_types: List[str]
    ) -> str:
        """
        치명적 오류 탐지에 집중한 코드 분석 (실제 GitHub 데이터용, RAG 없음)
        """
        try:
            # 치명적 이슈 중심 프롬프트 생성 (RAG 없음)
            prompt = self._create_critical_analysis_prompt(
                code_diff, commit_message, filename, analysis_types
            )
            
            print(f"Azure OpenAI API 호출 시작 (치명적 이슈 분석) - Model: {self.deployment}")
            
            # Azure OpenAI API 호출
            response = self.client.chat.completions.create(
                model=self.deployment,
                messages=[
                    {
                        "role": "system", 
                        "content": "당신은 시니어 DevOps 엔지니어입니다. 코드 변경사항을 분석하여 빌드 실패, 배포 위험, 런타임 에러 등 치명적인 문제를 찾아내는 것이 주 임무입니다."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                temperature=0.1,  # 더 정확한 분석을 위해 낮춤
                max_tokens=2000
            )
            
            result = response.choices[0].message.content
            print("Azure OpenAI API 호출 성공 (치명적 이슈 분석)")
            return result
            
        except Exception as e:
            print(f"Azure OpenAI API 호출 실패: {e}")
            raise Exception(f"Azure OpenAI API 호출 실패: {str(e)}")
    
    def _summarize_api_knowledge(self, api_knowledge: str, max_length=300) -> str:
        # 최대 max_length 글자까지만 자르고 ... 붙이기
        if len(api_knowledge) > max_length:
            return api_knowledge[:max_length].strip() + "..."
        return api_knowledge
    
    def _create_analysis_prompt_with_rag(
        self, 
        code_diff: str, 
        commit_message: str, 
        filename: str,
        analysis_types: List[str],
        api_knowledge: str
    ) -> str:
        """
        RAG 지식이 포함된 일반 코드 분석용 프롬프트 생성
        """
        analysis_sections = {
            "코드 품질": "코드의 가독성, 복잡도, 구조적 문제점을 분석해주세요.",
            "보안 취약점": "보안상 취약점이나 위험한 패턴을 찾아 지적해주세요.",
            "성능 최적화": "성능 개선 가능한 부분을 찾아 제안해주세요.",
            "버그 탐지": "잠재적인 버그나 오류 가능성을 찾아주세요.",
            "리팩토링 제안": "코드 구조 개선 및 리팩토링 방안을 제안해주세요."
        }
        
        # 선택된 분석 항목만 포함
        selected_analyses = []
        for analysis_type in analysis_types:
            if analysis_type in analysis_sections:
                selected_analyses.append(f"- {analysis_type}: {analysis_sections[analysis_type]}")
        
        analysis_text = "\n".join(selected_analyses)
        
        summarized_knowledge = self._summarize_api_knowledge(api_knowledge, max_length=300)

        print(api_knowledge, "로 포맷팅 완료")

        prompt = f"""다음 코드 변경사항을 분석해주세요:

**파일명:** {filename}
**커밋 메시지:** {commit_message}

**코드 변경사항:**
```diff
{code_diff}
```
**분석 요청 항목:**
{analysis_text}

{api_knowledge}

**위에 제공된 API 가이드라인이 있다면 반드시 참고하여 해당 API 사용 시 주의사항을 중점적으로 분석해주세요.**

**응답 형식:**
다음 마크다운 형식으로 응답해주세요:

## 🔍 코드 분석 결과

##관련 API 가이드라인 요약:
{api_knowledge}

### 📊 전체 요약
- 간단한 변경사항 요약

### 🎯 상세 분석
(요청된 분석 항목들에 대한 상세 내용)

### ⚠️ 발견된 이슈
1. 이슈 1
2. 이슈 2

### 💡 개선 제안
1. 제안 1
2. 제안 2

### 📈 점수 (10점 만점)
- 전체 품질: X/10
- 보안성: X/10
- 성능: X/10

한국어로 전문적이고 구체적으로 분석해주세요."""

        return prompt
    
    def _create_critical_analysis_prompt(
        self, 
        code_diff: str, 
        commit_message: str, 
        filename: str,
        analysis_types: List[str]
    ) -> str:
        """
        치명적 이슈 탐지용 프롬프트 생성 (RAG 없음)
        """
        prompt = f"""다음 커밋 변경사항을 분석하여 **치명적인 오류 가능성**을 찾아주세요:

**파일명:** {filename}
**커밋 메시지:** {commit_message}

**코드 변경사항:**
```diff
{code_diff}
```

**🚨 중점 분석 영역:**
1. **빌드 실패 위험**: 컴파일 에러, 의존성 문제, 설정 오류
2. **런타임 크래시**: NullPointer, 배열 오버플로우, 타입 에러
3. **배포 위험**: 환경 설정, 데이터베이스 스키마, API 호환성
4. **보안 취약점**: SQL 인젝션, XSS, 인증 우회, 개인정보 유출
5. **성능 저하**: 무한루프, 메모리 누수, 대용량 처리 문제

**응답 형식:**
## 🚨 치명적 이슈 분석

### ⚡ 위험도 평가
- **전체 위험도**: 🔴 높음 | 🟡 중간 | 🟢 낮음
- **빌드 성공률**: XX%
- **배포 안전성**: 🔴 위험 | 🟡 주의 | 🟢 안전

### 🔥 발견된 치명적 이슈
1. **[이슈 유형]** 구체적인 문제점
   - 발생 가능성: XX%
   - 영향 범위: 설명
   - 해결 방법: 구체적 수정안

### ✅ 확인된 안전 요소
- 안전하다고 판단되는 변경사항들

### 🎯 즉시 조치 사항
1. **우선순위 1**: 반드시 수정해야 할 사항
2. **우선순위 2**: 배포 전 검토 필요

### 📋 검증 체크리스트
- [ ] 단위 테스트 통과 확인
- [ ] 통합 테스트 실행
- [ ] 스테이징 환경 배포 테스트
- [ ] 성능 테스트 실행

**Jenkins 빌드나 배포에서 문제가 발생할 가능성이 있다면 반드시 명시해주세요.**
**소소한 성능 개선이나 코드 스타일은 무시하고, 오직 시스템을 망가뜨릴 수 있는 치명적 문제에만 집중해주세요.**"""

        return prompt