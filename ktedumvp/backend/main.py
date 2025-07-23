# backend/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import time
from services.llm_service import AzureOpenAIService

app = FastAPI(title="GitHub Commit Analyzer API")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발용, 프로덕션에서는 구체적인 도메인 설정
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# LLM 서비스 초기화
llm_service = AzureOpenAIService()

# 요청 모델
class AIAnalysisRequest(BaseModel):
    code_diff: str
    filename: str
    commit_message: str
    provider: str
    model: str
    analysis_types: List[str]

# 응답 모델
class AIAnalysisResponse(BaseModel):
    success: bool
    result: str
    error: str = None



@app.post("/analyze", response_model=AIAnalysisResponse)
async def analyze_code(request: AIAnalysisRequest):
    """
    AI 코드 분석 엔드포인트 - 실제 Azure OpenAI 연동
    """
    try:
        # 실제 Azure OpenAI로 분석
        analysis_result = llm_service.analyze_code(
            code_diff=request.code_diff,
            commit_message=request.commit_message,
            filename=request.filename,
            analysis_types=request.analysis_types
        )
        
        return AIAnalysisResponse(
            success=True,
            result=analysis_result
        )
        
    except Exception as e:
        return AIAnalysisResponse(
            success=False,
            result="",
            error=f"분석 중 오류가 발생했습니다: {str(e)}"
        )

@app.get("/")
async def root():
    return {"message": "GitHub Commit Analyzer API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": time.time()}

# 새로운 요청 모델
class CommitAnalysisRequest(BaseModel):
    commit_sha: str
    analysis_types: List[str]

class RealCommitAnalysisRequest(BaseModel):
    repo_owner: str
    repo_name: str
    commit_sha: str
    analysis_types: List[str]
    github_token: str = None

DUMMY_COMMITS = {
    "abc123": {
        "sha": "abc123def456789",
        "commit": {
            "message": "feat: 사용자 인증 시스템 개선\n\n- JWT 토큰 만료 시간 조정\n- 비밀번호 해싱 알고리즘 업그레이드",
            "author": {"name": "김개발", "date": "2025-07-22T14:30:00Z"}
        },
        "files": [
            {
                "filename": "auth/jwt_handler.py",
                "status": "modified",
                "additions": 15,
                "deletions": 8,
                "patch": "@@ -12,8 +12,15 @@ class JWTHandler:\n-    TOKEN_EXPIRE_TIME = 30  # 30분\n+    TOKEN_EXPIRE_TIME = 60 * 24  # 24시간\n+    \n+    def validate_token_strength(self, token):\n+        # 토큰 강도 검증 로직 추가\n+        return len(token) > 32"
            },
            {
                "filename": "auth/password_utils.py", 
                "status": "modified",
                "additions": 20,
                "deletions": 12,
                "patch": "@@ -5,12 +5,20 @@ import hashlib\n-def hash_password(password):\n-    return hashlib.md5(password.encode()).hexdigest()\n+def hash_password(password):\n+    import bcrypt\n+    salt = bcrypt.gensalt()\n+    return bcrypt.hashpw(password.encode('utf-8'), salt)"
            }
        ]
    },
    "def456": {
        "sha": "def456ghi789abc", 
        "commit": {
            "message": "perf: 데이터베이스 쿼리 최적화\n\n- N+1 쿼리 문제 해결\n- 인덱스 추가로 조회 성능 50% 향상",
            "author": {"name": "박DB", "date": "2025-07-22T13:15:00Z"}
        },
        "files": [
            {
                "filename": "models/user_model.py",
                "status": "modified", 
                "additions": 8,
                "deletions": 25,
                "patch": "@@ -18,25 +18,8 @@ class User(db.Model):\n-    def get_posts(self):\n-        posts = []\n-        for post_id in self.post_ids:\n-            post = Post.query.get(post_id)  # N+1 쿼리 발생\n-            posts.append(post)\n-        return posts\n+    posts = db.relationship('Post', lazy='select', backref='user')"
            }
        ]
    },
    "ghi789": {
        "sha": "ghi789abc123def",
        "commit": {
            "message": "security: XSS 취약점 수정\n\n- 사용자 입력값 이스케이프 처리\n- CSRF 토큰 검증 강화", 
            "author": {"name": "이보안", "date": "2025-07-22T12:00:00Z"}
        },
        "files": [
            {
                "filename": "templates/user_profile.html",
                "status": "modified",
                "additions": 12,
                "deletions": 5,
                "patch": "@@ -23,5 +23,12 @@\n-<div>사용자명: {{ user.name }}</div>\n+<div>사용자명: {{ user.name|e }}</div>\n+{% csrf_token %}\n+<script>\n+    // XSS 방지를 위한 입력값 검증\n+    function sanitizeInput(input) {\n+        return input.replace(/[<>\"']/g, '');\n+    }\n+</script>"
            }
        ]
    }
}


# 새로운 엔드포인트
@app.post("/analyze-commit", response_model=AIAnalysisResponse)
async def analyze_specific_commit(request: CommitAnalysisRequest):
    """
    특정 커밋 SHA로 코드 분석
    """
    try:
        # 더미 커밋 데이터에서 검색
        commit_data = None
        for dummy_sha, data in DUMMY_COMMITS.items():
            if request.commit_sha.lower().startswith(dummy_sha.lower()):
                commit_data = data
                break
        
        if not commit_data:
            return AIAnalysisResponse(
                success=False,
                result="",
                error=f"커밋 SHA '{request.commit_sha}'를 찾을 수 없습니다. 사용 가능한 SHA: abc123, def456, ghi789"
            )
        
        # 파일들을 하나의 diff로 합치기
        all_patches = []
        for file in commit_data["files"]:
            if file.get("patch"):
                all_patches.append(f"=== {file.get('filename')} ===\n{file.get('patch')}")
        
        combined_diff = "\n\n".join(all_patches)
        filename_summary = f"{len(commit_data['files'])}개 파일"
        
        # LLM 분석 호출
        analysis_result = llm_service.analyze_code_for_critical_issues(
            code_diff=combined_diff,
            commit_message=commit_data["commit"]["message"],
            filename=filename_summary,
            analysis_types=request.analysis_types
        )
        
        return AIAnalysisResponse(
            success=True,
            result=analysis_result
        )
        
    except Exception as e:
        return AIAnalysisResponse(
            success=False,
            result="",
            error=f"분석 중 오류가 발생했습니다: {str(e)}"
        )
    

@app.post("/analyze-real-commit", response_model=AIAnalysisResponse)
async def analyze_real_commit(request: RealCommitAnalysisRequest):
    """
    실제 GitHub API로 특정 커밋 분석
    """
    try:
        # GitHub API로 커밋 상세 정보 조회
        url = f"https://api.github.com/repos/{request.repo_owner}/{request.repo_name}/commits/{request.commit_sha}"
        headers = {}
        if request.github_token:
            headers["Authorization"] = f"token {request.github_token}"
        
        import requests as req  # 이름 충돌 방지
        response = req.get(url, headers=headers, timeout=10)
        
        if response.status_code == 404:
            return AIAnalysisResponse(
                success=False,
                result="",
                error=f"커밋을 찾을 수 없습니다. Repository: {request.repo_owner}/{request.repo_name}, SHA: {request.commit_sha}"
            )
        elif response.status_code != 200:
            return AIAnalysisResponse(
                success=False,
                result="",
                error=f"GitHub API 오류: HTTP {response.status_code}"
            )
        
        commit_data = response.json()
        
        # 파일들을 하나의 diff로 합치기
        files = commit_data.get("files", [])
        if not files:
            return AIAnalysisResponse(
                success=False,
                result="",
                error="분석할 파일 변경사항이 없습니다."
            )
        
        all_patches = []
        for file in files:
            if file.get("patch"):
                all_patches.append(f"=== {file.get('filename')} ===\n{file.get('patch')}")
        
        if not all_patches:
            return AIAnalysisResponse(
                success=False,
                result="",
                error="분석할 코드 변경사항이 없습니다."
            )
        
        combined_diff = "\n\n".join(all_patches)
        filename_summary = f"{len(files)}개 파일"
        
        # LLM 분석 호출
        analysis_result = llm_service.analyze_code_for_critical_issues(
            code_diff=combined_diff,
            commit_message=commit_data["commit"]["message"],
            filename=filename_summary,
            analysis_types=request.analysis_types
        )
        
        return AIAnalysisResponse(
            success=True,
            result=analysis_result
        )
        
    except req.exceptions.Timeout:
        return AIAnalysisResponse(
            success=False,
            result="",
            error="GitHub API 요청 시간이 초과되었습니다."
        )
    except req.exceptions.ConnectionError:
        return AIAnalysisResponse(
            success=False,
            result="",
            error="GitHub API에 연결할 수 없습니다."
        )
    except Exception as e:
        return AIAnalysisResponse(
            success=False,
            result="",
            error=f"분석 중 오류가 발생했습니다: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)