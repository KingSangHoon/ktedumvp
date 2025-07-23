import streamlit as st
import requests
import json
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# ===== 환경변수 로드 =====
load_dotenv()

# ===== 설정 =====
USE_GITHUB_API = True  # True로 변경하면 실제 GitHub API 사용
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")  # 기본값 설정

# ===== 페이지 설정 =====
st.set_page_config(
    page_title="GitHub Commit Analyzer",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===== 헬퍼 함수들 =====
def get_commits(owner, repo, token=None, since=None, until=None, per_page=10):
    """GitHub API를 통해 커밋 목록 조회"""
    try:
        url = f"https://api.github.com/repos/{owner}/{repo}/commits"
        headers = {}
        if token:
            headers["Authorization"] = f"token {token}"
        
        params = {
            "per_page": per_page
        }
        if since:
            params["since"] = since.isoformat()
        if until:
            params["until"] = until.isoformat()
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            return response.json(), None
        elif response.status_code == 404:
            return None, "Repository를 찾을 수 없습니다. Owner/Name을 확인해주세요."
        elif response.status_code == 403:
            return None, "API 요청 한도를 초과했습니다. GitHub Token을 설정해주세요."
        else:
            return None, f"GitHub API 오류: {response.status_code}"
    except Exception as e:
        return None, f"네트워크 오류: {str(e)}"

def get_commit_detail(owner, repo, sha, token=None):
    """특정 커밋의 상세 정보 조회"""
    try:
        url = f"https://api.github.com/repos/{owner}/{repo}/commits/{sha}"
        headers = {}
        if token:
            headers["Authorization"] = f"token {token}"
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            return response.json(), None
        elif response.status_code == 404:
            return None, "커밋을 찾을 수 없습니다."
        else:
            return None, f"GitHub API 오류: {response.status_code}"
    except Exception as e:
        return None, f"네트워크 오류: {str(e)}"

def filter_files_by_type(files, file_types):
    """파일 타입에 따라 필터링"""
    if not file_types:
        return files
    
    filtered = []
    for file in files:
        filename = file.get('filename', '')
        for file_type in file_types:
            if filename.endswith(file_type):
                filtered.append(file)
                break
    return filtered

def format_commit_date(date_str):
    """날짜 포맷팅"""
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime("%Y-%m-%d %H:%M")
    except:
        return date_str

def get_dummy_commits():
    """테스트용 더미 커밋 데이터"""
    return [
        {
            "sha": "a1b2c3d4e5f6",
            "commit": {
                "message": "feat: 사용자 인증 시스템 개선\n\n- JWT 토큰 만료 시간 조정\n- 비밀번호 해싱 알고리즘 업그레이드",
                "author": {
                    "name": "김개발",
                    "date": "2025-07-22T14:30:00Z"
                }
            },
            "author": {"login": "kimdev"},
            "stats": {"additions": 25, "deletions": 8, "total": 33}
        },
        {
            "sha": "f6e5d4c3b2a1", 
            "commit": {
                "message": "fix: 로그인 버그 수정\n\n- 세션 만료 시 자동 로그아웃 처리\n- 비밀번호 재설정 플로우 개선",
                "author": {
                    "name": "박버그",
                    "date": "2025-07-22T13:15:00Z"
                }
            },
            "author": {"login": "parkbug"},
            "stats": {"additions": 15, "deletions": 5, "total": 20}
        },
        {
            "sha": "9z8y7x6w5v4u",
            "commit": {
                "message": "docs: API 문서 업데이트\n\n- 새로운 엔드포인트 문서화\n- 예제 코드 추가",
                "author": {
                    "name": "이문서",
                    "date": "2025-07-22T12:00:00Z"
                }
            },
            "author": {"login": "leedoc"},
            "stats": {"additions": 45, "deletions": 2, "total": 47}
        }
    ]

def analyze_code_with_ai(code_diff, filename, commit_message, provider, model, analysis_types):
    """AI 코드 분석 함수 - 백엔드 API 호출"""
    try:
        # 백엔드 API 엔드포인트
        api_url = f"{API_BASE_URL}/analyze"
        
        # 요청 데이터
        request_data = {
            "code_diff": code_diff,
            "filename": filename,
            "commit_message": commit_message,
            "provider": provider,
            "model": model,
            "analysis_types": analysis_types
        }
        
        # API 호출
        response = requests.post(
            api_url,
            json=request_data,
            headers={"Content-Type": "application/json"},
            timeout=30  # 30초 타임아웃
        )
        
        # 응답 확인
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                return data.get("result"), None
            else:
                return None, data.get("error", "알 수 없는 오류가 발생했습니다.")
        else:
            return None, f"API 호출 실패: HTTP {response.status_code}"
            
    except requests.exceptions.ConnectionError:
        return None, f"백엔드 서버에 연결할 수 없습니다. ({API_BASE_URL})"
    except requests.exceptions.Timeout:
        return None, "요청 시간이 초과되었습니다. 다시 시도해주세요."
    except Exception as e:
        return None, f"API 호출 중 오류가 발생했습니다: {str(e)}"

def analyze_real_commit(repo_owner, repo_name, commit_sha, analysis_types, github_token=None):
    """실제 GitHub API로 특정 커밋 분석 요청"""
    try:
        api_url = f"{API_BASE_URL}/analyze-real-commit"
        
        request_data = {
            "repo_owner": repo_owner,
            "repo_name": repo_name,
            "commit_sha": commit_sha,
            "analysis_types": analysis_types,
            "github_token": github_token
        }
        
        response = requests.post(
            api_url,
            json=request_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                return data.get("result"), None
            else:
                return None, data.get("error")
        else:
            return None, f"API 호출 실패: HTTP {response.status_code}"
            
    except requests.exceptions.ConnectionError:
        return None, f"백엔드 서버에 연결할 수 없습니다. ({API_BASE_URL})"
    except requests.exceptions.Timeout:
        return None, "요청 시간이 초과되었습니다."
    except Exception as e:
        return None, f"API 호출 중 오류: {str(e)}"

def analyze_specific_commit(commit_sha, analysis_types):
    """특정 커밋 SHA로 분석 요청 (더미 데이터)"""
    try:
        api_url = f"{API_BASE_URL}/analyze-commit"
        
        request_data = {
            "commit_sha": commit_sha,
            "analysis_types": analysis_types
        }
        
        response = requests.post(
            api_url,
            json=request_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                return data.get("result"), None
            else:
                return None, data.get("error", "알 수 없는 오류가 발생했습니다.")
        else:
            return None, f"API 호출 실패: HTTP {response.status_code}"
            
    except requests.exceptions.ConnectionError:
        return None, f"백엔드 서버에 연결할 수 없습니다. ({API_BASE_URL})"
    except requests.exceptions.Timeout:
        return None, "요청 시간이 초과되었습니다. 다시 시도해주세요."
    except Exception as e:
        return None, f"API 호출 중 오류가 발생했습니다: {str(e)}"

def display_analysis_result(result):
    """AI 분석 결과를 보기 좋게 표시"""
    if result:
        st.markdown(result)
    else:
        st.warning("분석 결과가 없습니다.")

def check_api_connection():
    """API 서버 연결 상태 확인"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

# ===== 메인 UI =====
st.title("🤖 GitHub Commit Analyzer")
st.markdown("GitHub 커밋을 AI로 분석하여 코드 품질, 보안, 성능 등을 평가합니다.")

# API 연결 상태 확인 및 표시
with st.expander("🔧 시스템 상태", expanded=False):
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**API 서버 설정**")
        st.code(f"API_BASE_URL: {API_BASE_URL}")
        
    with col2:
        st.markdown("**연결 상태**")
        if check_api_connection():
            st.success("✅ API 서버 연결됨")
        else:
            st.error("❌ API 서버 연결 실패")
            st.warning("백엔드 서버가 실행 중인지 확인해주세요.")

# 사이드바 설정
with st.sidebar:
    st.header("⚙️ 설정")
    
    # GitHub 설정
    st.subheader("🔗 GitHub 설정")
    repo_owner = st.text_input("Repository Owner", value="", placeholder="예: microsoft")
    repo_name = st.text_input("Repository Name", value="", placeholder="예: vscode")
    github_token = st.text_input("GitHub Token (선택사항)", type="password", help="Rate limit 증가를 위해 사용")
    
    # 분석 옵션
    st.subheader("📊 분석 옵션")
    commit_option = st.selectbox(
        "커밋 조회 방식",
        ["최근 커밋", "특정 커밋", "기간별 커밋"]
    )
    
    if commit_option == "최근 커밋":
        commit_count = st.slider("조회할 커밋 수", 1, 50, 2)
    elif commit_option == "특정 커밋":
        specific_sha = st.text_input("커밋 SHA", placeholder="예: abc123def456")
    else:  # 기간별 커밋
        start_date = st.date_input("시작 날짜", value=datetime.now() - timedelta(days=7))
        end_date = st.date_input("종료 날짜", value=datetime.now())
    
    # 파일 필터
    st.subheader("📁 파일 필터")
    file_types = st.multiselect(
        "분석할 파일 타입",
        [".py", ".js", ".ts", ".java", ".cpp", ".c", ".go", ".rs", ".php", ".rb"],
        default=[".java"]
    )
    
    # AI 설정
    st.subheader("🤖 AI 설정")
    llm_provider = st.selectbox("LLM 제공자", ["Azure OpenAI", "OpenAI", "Claude"])
    llm_model = st.selectbox("모델", ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"])
    
    analysis_options = st.multiselect(
        "분석 유형",
        ["코드 품질", "보안 취약점", "성능 최적화", "버그 탐지", "리팩토링 제안"],
        default=["코드 품질", "버그 탐지"]
    )
    
    st.divider()
    
    # 특정 커밋 직접 분석
    st.subheader("🔍 특정 커밋 분석")
    st.caption("Repository와 커밋 SHA를 입력하여 분석")
    
    # Repository 정보 입력
    direct_repo_owner = st.text_input(
        "Repository Owner",
        placeholder="예: facebook, microsoft, google",
        help="GitHub 사용자명 또는 조직명",
        key="direct_repo_owner"
    )
    
    direct_repo_name = st.text_input(
        "Repository Name", 
        placeholder="예: react, vscode, tensorflow",
        help="Repository 이름",
        key="direct_repo_name"
    )
    
    commit_sha_input = st.text_input(
        "커밋 SHA", 
        placeholder="예: abc123, def456, ghi789 (더미) 또는 실제 SHA",
        help="더미 데이터: abc123(인증), def456(DB), ghi789(보안)",
        key="commit_sha_direct"
    )
    
    direct_analysis_options = st.multiselect(
        "분석 항목 선택",
        ["코드 품질", "보안 취약점", "성능 최적화", "버그 탐지", "리팩토링 제안"],
        default=["코드 품질", "버그 탐지"],
        key="direct_analysis_options"
    )
    
    if st.button("🚀 커밋 분석 시작", type="primary", use_container_width=True, key="direct_commit_analyze"):
        if not commit_sha_input.strip():
            st.error("커밋 SHA를 입력해주세요.")
        elif not direct_analysis_options:
            st.error("분석 항목을 선택해주세요.")
        else:
            # Repository 정보가 있으면 실제 GitHub API, 없으면 더미 데이터
            if direct_repo_owner.strip() and direct_repo_name.strip():
                # 실제 GitHub API 호출
                with st.spinner(f"GitHub에서 {direct_repo_owner}/{direct_repo_name} 커밋 조회 중..."):
                    real_result, real_error = analyze_real_commit(
                        direct_repo_owner.strip(),
                        direct_repo_name.strip(), 
                        commit_sha_input.strip(),
                        direct_analysis_options,
                        github_token  # 기존 설정에서 가져옴
                    )
                    
                    if real_error:
                        st.error(f"❌ {real_error}")
                    else:
                        st.success(f"✅ 실제 커밋 {commit_sha_input[:7]}... 분석 완료!")
                        st.session_state['direct_analysis_result'] = real_result
                        st.session_state['direct_analysis_sha'] = f"{direct_repo_owner}/{direct_repo_name}@{commit_sha_input[:7]}"
            else:
                # 더미 데이터 사용
                with st.spinner(f"더미 커밋 {commit_sha_input[:7]}... 분석 중..."):
                    direct_result, direct_error = analyze_specific_commit(
                        commit_sha_input.strip(),
                        direct_analysis_options
                    )
                    
                    if direct_error:
                        st.error(f"❌ {direct_error}")
                    else:
                        st.success(f"✅ 더미 커밋 {commit_sha_input[:7]}... 분석 완료!")
                        st.session_state['direct_analysis_result'] = direct_result
                        st.session_state['direct_analysis_sha'] = f"더미@{commit_sha_input[:7]}"

# 메인 화면
col1, col2 = st.columns([3, 1])

with col1:
    st.header("📋 커밋 조회")

with col2:
    if st.button("🔄 커밋 조회", type="primary", use_container_width=True):
        if not USE_GITHUB_API:
            # 테스트 모드: 더미 데이터 사용
            st.session_state['commits'] = get_dummy_commits()
            st.success("✅ 테스트 커밋 데이터를 불러왔습니다!")
        else:
            # 실제 GitHub API 사용
            if not repo_owner or not repo_name:
                st.error("Repository Owner와 Name을 입력해주세요.")
            else:
                with st.spinner("GitHub에서 커밋을 조회하는 중..."):
                    since_date = None
                    until_date = None
                    
                    if commit_option == "기간별 커밋":
                        since_date = datetime.combine(start_date, datetime.min.time())
                        until_date = datetime.combine(end_date, datetime.max.time())
                    
                    commits, error = get_commits(
                        repo_owner, 
                        repo_name, 
                        github_token,
                        since=since_date,
                        until=until_date,
                        per_page=commit_count if commit_option == "최근 커밋" else 30
                    )
                    
                    if error:
                        st.error(f"❌ {error}")
                    else:
                        st.session_state['commits'] = commits
                        st.success(f"✅ {len(commits)}개의 커밋을 조회했습니다!")

# 커밋 목록 표시
if 'commits' in st.session_state:
    commits = st.session_state['commits']
    
    st.markdown("### 📝 커밋 목록")
    
    for i, commit in enumerate(commits):
        with st.container():
            # 커밋 카드
            col1, col2, col3 = st.columns([5, 2, 2])
            
            with col1:
                commit_message = commit['commit']['message'].split('\n')[0]  # 첫 번째 줄만
                st.markdown(f"**{commit_message}**")
                st.caption(f"SHA: `{commit['sha'][:8]}...` | 작성자: {commit['commit']['author']['name']}")
            
            with col2:
                commit_date = format_commit_date(commit['commit']['author']['date'])
                st.text(commit_date)
                
                if 'stats' in commit:
                    st.text(f"+{commit['stats']['additions']} -{commit['stats']['deletions']}")
            
            with col3:
                if st.button("🤖 코드 분석", key=f"analyze_commit_{i}", use_container_width=True):
                    st.session_state[f"ai_analyze_commit_{i}"] = commit['sha']
        
        st.divider()

# AI 분석 팝업 (st.dialog 사용 - 업그레이드 완료)
if 'commits' in st.session_state:
    commits = st.session_state['commits']
    
    for i, commit in enumerate(commits):
        if f"ai_analyze_commit_{i}" in st.session_state:
            ai_analyze_sha = st.session_state[f"ai_analyze_commit_{i}"]
            
            @st.dialog(f"🤖 AI 코드 분석 - {ai_analyze_sha[:8]}", width="large")
            def show_ai_analysis():
                # AI 분석 내용
                if not USE_GITHUB_API:
                    commit_detail = commit
                    error = None
                else:
                    commit_detail, error = get_commit_detail(repo_owner, repo_name, ai_analyze_sha, github_token)
                
                if error:
                    st.error(f"커밋 정보 조회 실패: {error}")
                elif commit_detail:
                    # 커밋 정보 표시
                    st.info(f"**커밋 메시지:** {commit_detail.get('commit', {}).get('message', '')}")
                    
                    files = commit_detail.get('files', [])
                    filtered_files = filter_files_by_type(files, file_types)
                    
                    if not filtered_files:
                        if len(files) == 0:
                            st.warning("이 커밋은 파일 변경사항이 없습니다. (Merge commit이거나 Empty commit일 수 있습니다)")
                        else:
                            st.warning(f"선택한 파일 타입과 일치하는 파일이 없습니다. 전체 파일 수: {len(files)}개")
                            st.info("💡 사이드바의 '분석할 파일 타입'을 조정하거나 모두 해제해보세요.")
                    else:
                        st.success(f"📁 분석 대상: {len(filtered_files)}개 파일")
                        
                        # 파일 목록 표시
                        for file in filtered_files:
                            with st.expander(f"📄 {file.get('filename')} ({file.get('status')}) +{file.get('additions', 0)} -{file.get('deletions', 0)}"):
                                if file.get('patch'):
                                    st.code(file.get('patch'), language='diff')
                        
                        st.divider()
                        
                        # AI 분석 시작 버튼
                        if st.button("🚀 AI 분석 시작", type="primary", use_container_width=True, key=f"dialog_ai_{ai_analyze_sha}"):
                            all_patches = []
                            for file in filtered_files:
                                if file.get('patch'):
                                    all_patches.append(f"=== {file.get('filename')} ===\n{file.get('patch')}")
                            
                            if all_patches:
                                combined_diff = "\n\n".join(all_patches)
                                
                                with st.spinner("🤖 AI가 코드를 분석하는 중..."):
                                    analysis_result, analysis_error = analyze_code_with_ai(
                                        code_diff=combined_diff,
                                        filename=f"{len(filtered_files)}개 파일",
                                        commit_message=commit_detail.get('commit', {}).get('message', ''),
                                        provider=llm_provider,
                                        model=llm_model,
                                        analysis_types=analysis_options
                                    )
                                
                                # 분석 결과를 즉시 표시
                                if analysis_error:
                                    st.error(f"❌ AI 분석 실패: {analysis_error}")
                                elif analysis_result:
                                    st.success("✅ AI 분석이 완료되었습니다!")
                                    st.markdown("### 📊 AI 분석 결과")
                                    display_analysis_result(analysis_result)
                            else:
                                st.warning("분석할 코드 변경사항이 없습니다.")
                
                # 팝업 닫기 버튼
                col1, col2 = st.columns([3, 1])
                with col2:
                    if st.button("❌ 닫기", use_container_width=True, key=f"dialog_close_{ai_analyze_sha}"):
                        del st.session_state[f"ai_analyze_commit_{i}"]
                        st.rerun()
            
            # 팝업 실행
            show_ai_analysis()
            break

# 직접 커밋 분석 결과 표시
if 'direct_analysis_result' in st.session_state:
    st.markdown("---")
    st.markdown("## 🎯 직접 커밋 분석 결과")
    
    col1, col2 = st.columns([5, 1])
    
    with col1:
        if 'direct_analysis_sha' in st.session_state:
            st.markdown(f"**분석 커밋:** `{st.session_state['direct_analysis_sha']}...`")
    
    with col2:
        if st.button("❌ 결과 닫기", key="close_direct_result"):
            del st.session_state['direct_analysis_result']
            if 'direct_analysis_sha' in st.session_state:
                del st.session_state['direct_analysis_sha']
            st.rerun()
    
    # 분석 결과 표시
    with st.container():
        st.markdown(st.session_state['direct_analysis_result'])
    
    st.markdown("---")

# 하단 정보
st.markdown("---")
st.markdown(f"""
### 📖 사용 방법
1. **환경 설정**: `.env` 파일에서 `API_BASE_URL={API_BASE_URL}` 설정
2. **GitHub 정보 입력**: 왼쪽 사이드바에서 Repository Owner, Name 입력 (테스트 모드에서는 생략 가능)
3. **분석 옵션 선택**: 최근 커밋, 특정 커밋, 기간별 커밋 중 선택
4. **AI 설정**: Azure OpenAI 모델 및 분석 유형 선택
5. **커밋 조회**: '커밋 조회' 버튼 클릭
6. **코드 분석**: 각 커밋의 '🤖 코드 분석' 버튼으로 AI 분석 실행
7. **직접 분석**: 사이드바 하단에서 특정 커밋 SHA로 직접 분석 가능

### 💡 현재 모드
- 🧪 **테스트 모드**: 하드코딩된 3개 커밋으로 AI 기능 테스트 가능
- 🌐 **실제 API 모드**: 파일 상단 `USE_GITHUB_API = True`로 변경하여 실제 GitHub 연동
- 🔍 **직접 분석**: Repository 정보 입력 시 실제 GitHub 연동, 생략 시 더미 데이터 사용

### 🔧 환경 설정
현재 API 서버: `{API_BASE_URL}`
""")