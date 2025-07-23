import aiohttp
import asyncio
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

from ..models.github_models import (
    GitHubConfig, 
    CommitResponse, 
    CommitDetailResponse,
    Author,
    CommitInfo,
    GitHubUser,
    CommitStats,
    FileChange,
    AnalysisOptions
)

logger = logging.getLogger(__name__)

class GitHubService:
    BASE_URL = "https://api.github.com"
    
    def __init__(self):
        self.session = None
    
    async def get_session(self) -> aiohttp.ClientSession:
        """aiohttp 세션 생성"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    def _get_headers(self, token: Optional[str] = None) -> Dict[str, str]:
        """GitHub API 요청 헤더 생성"""
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "GitHub-Commit-Analyzer/1.0"
        }
        if token:
            headers["Authorization"] = f"token {token}"
        return headers
    
    async def get_commits(
        self,
        config: GitHubConfig,
        per_page: int = 10,
        page: int = 1,
        since: Optional[str] = None,
        until: Optional[str] = None
    ) -> List[CommitResponse]:
        """커밋 목록 조회"""
        session = await self.get_session()
        url = f"{self.BASE_URL}/repos/{config.owner}/{config.repo}/commits"
        
        params = {
            "sha": config.branch,
            "per_page": per_page,
            "page": page
        }
        
        if since:
            params["since"] = since
        if until:
            params["until"] = until
        
        headers = self._get_headers(config.token)
        
        try:
            async with session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return [self._parse_commit(commit) for commit in data]
                elif response.status == 404:
                    raise Exception("저장소를 찾을 수 없습니다.")
                elif response.status == 403:
                    raise Exception("API 제한 또는 권한이 없습니다.")
                else:
                    error_text = await response.text()
                    raise Exception(f"GitHub API 오류: {response.status} - {error_text}")
                    
        except aiohttp.ClientError as e:
            raise Exception(f"네트워크 오류: {str(e)}")
    
    async def get_commit_detail(
        self,
        config: GitHubConfig,
        sha: str
    ) -> CommitDetailResponse:
        """특정 커밋의 상세 정보 조회"""
        session = await self.get_session()
        url = f"{self.BASE_URL}/repos/{config.owner}/{config.repo}/commits/{sha}"
        headers = self._get_headers(config.token)
        
        try:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_commit_detail(data)
                elif response.status == 404:
                    raise Exception("커밋을 찾을 수 없습니다.")
                else:
                    error_text = await response.text()
                    raise Exception(f"GitHub API 오류: {response.status} - {error_text}")
                    
        except aiohttp.ClientError as e:
            raise Exception(f"네트워크 오류: {str(e)}")
    
    async def get_repository_info(self, config: GitHubConfig) -> Dict[str, Any]:
        """저장소 기본 정보 조회"""
        session = await self.get_session()
        url = f"{self.BASE_URL}/repos/{config.owner}/{config.repo}"
        headers = self._get_headers(config.token)
        
        try:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "name": data.get("name"),
                        "full_name": data.get("full_name"),
                        "description": data.get("description"),
                        "language": data.get("language"),
                        "stars": data.get("stargazers_count"),
                        "forks": data.get("forks_count"),
                        "size": data.get("size"),
                        "created_at": data.get("created_at"),
                        "updated_at": data.get("updated_at"),
                        "default_branch": data.get("default_branch")
                    }
                else:
                    error_text = await response.text()
                    raise Exception(f"GitHub API 오류: {response.status} - {error_text}")
                    
        except aiohttp.ClientError as e:
            raise Exception(f"네트워크 오류: {str(e)}")
    
    async def analyze_commits(
        self,
        config: GitHubConfig,
        commit_shas: List[str],
        file_types: List[str],
        analysis_options: AnalysisOptions
    ) -> Dict[str, Any]:
        """커밋 분석 (향후 LLM 연동)"""
        analysis_results = []
        
        for sha in commit_shas:
            try:
                commit_detail = await self.get_commit_detail(config, sha)
                
                # 파일 타입 필터링
                filtered_files = self._filter_files_by_type(
                    commit_detail.files, file_types
                )
                
                if filtered_files:
                    analysis_result = {
                        "commit_sha": sha,
                        "commit_message": commit_detail.commit.message,
                        "author": commit_detail.commit.author.name,
                        "date": commit_detail.commit.author.date,
                        "files_analyzed": len(filtered_files),
                        "files": [
                            {
                                "filename": file.filename,
                                "status": file.status,
                                "changes": file.changes,
                                "patch": file.patch
                            }
                            for file in filtered_files
                        ],
                        "analysis_status": "ready_for_llm"  # LLM 분석 대기
                    }
                    analysis_results.append(analysis_result)
                    
            except Exception as e:
                logger.error(f"커밋 {sha} 분석 중 오류: {str(e)}")
                analysis_results.append({
                    "commit_sha": sha,
                    "error": str(e),
                    "analysis_status": "failed"
                })
        
        return {
            "total_commits": len(commit_shas),
            "analyzed_commits": len([r for r in analysis_results if "error" not in r]),
            "failed_commits": len([r for r in analysis_results if "error" in r]),
            "results": analysis_results
        }
    
    def _parse_commit(self, data: Dict[str, Any]) -> CommitResponse:
        """GitHub API 응답을 CommitResponse로 변환"""
        commit_data = data.get("commit", {})
        author_data = commit_data.get("author", {})
        committer_data = commit_data.get("committer", {})
        
        return CommitResponse(
            sha=data.get("sha", ""),
            commit=CommitInfo(
                author=Author(
                    name=author_data.get("name", ""),
                    email=author_data.get("email", ""),
                    date=datetime.fromisoformat(author_data.get("date", "").replace("Z", "+00:00"))
                ),
                committer=Author(
                    name=committer_data.get("name", ""),
                    email=committer_data.get("email", ""),
                    date=datetime.fromisoformat(committer_data.get("date", "").replace("Z", "+00:00"))
                ),
                message=commit_data.get("message", ""),
                comment_count=commit_data.get("comment_count", 0)
            ),
            author=self._parse_github_user(data.get("author")) if data.get("author") else None,
            committer=self._parse_github_user(data.get("committer")) if data.get("committer") else None,
            stats=self._parse_stats(data.get("stats")) if data.get("stats") else None,
            html_url=data.get("html_url", "")
        )
    
    def _parse_commit_detail(self, data: Dict[str, Any]) -> CommitDetailResponse:
        """GitHub API 응답을 CommitDetailResponse로 변환"""
        commit_response = self._parse_commit(data)
        files = [self._parse_file_change(file) for file in data.get("files", [])]
        
        return CommitDetailResponse(
            **commit_response.dict(),
            files=files
        )
    
    def _parse_github_user(self, data: Dict[str, Any]) -> GitHubUser:
        """GitHub 사용자 정보 파싱"""
        return GitHubUser(
            login=data.get("login", ""),
            id=data.get("id", 0),
            avatar_url=data.get("avatar_url", ""),
            html_url=data.get("html_url", "")
        )
    
    def _parse_stats(self, data: Dict[str, Any]) -> CommitStats:
        """커밋 통계 정보 파싱"""
        return CommitStats(
            total=data.get("total", 0),
            additions=data.get("additions", 0),
            deletions=data.get("deletions", 0)
        )
    
    def _parse_file_change(self, data: Dict[str, Any]) -> FileChange:
        """파일 변경 정보 파싱"""
        return FileChange(
            sha=data.get("sha", ""),
            filename=data.get("filename", ""),
            status=data.get("status", ""),
            additions=data.get("additions", 0),
            deletions=data.get("deletions", 0),
            changes=data.get("changes", 0),
            patch=data.get("patch")
        )
    
    def _filter_files_by_type(
        self, 
        files: List[FileChange], 
        file_types: List[str]
    ) -> List[FileChange]:
        """파일 타입으로 필터링"""
        if not file_types:
            return files
        
        return [
            file for file in files
            if any(file.filename.endswith(ext) for ext in file_types)
        ]
    
    async def close(self):
        """세션 종료"""
        if self.session and not self.session.closed:
            await self.session.close()