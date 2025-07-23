from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class GitHubConfig(BaseModel):
    owner: str
    repo: str
    token: Optional[str] = None
    branch: str = "main"

class Author(BaseModel):
    name: str
    email: str
    date: datetime

class CommitInfo(BaseModel):
    author: Author
    committer: Author
    message: str
    comment_count: int

class GitHubUser(BaseModel):
    login: str
    id: int
    avatar_url: str
    html_url: str

class CommitStats(BaseModel):
    total: int
    additions: int
    deletions: int

class FileChange(BaseModel):
    sha: str
    filename: str
    status: str
    additions: int
    deletions: int
    changes: int
    patch: Optional[str] = None

class CommitResponse(BaseModel):
    sha: str
    commit: CommitInfo
    author: Optional[GitHubUser]
    committer: Optional[GitHubUser]
    stats: Optional[CommitStats]
    html_url: str

class CommitDetailResponse(CommitResponse):
    files: List[FileChange]

class AnalysisOptions(BaseModel):
    check_syntax: bool = True
    check_security: bool = True
    check_performance: bool = False
    check_logic: bool = False

class AnalysisRequest(BaseModel):
    owner: str
    repo: str
    token: Optional[str] = None
    commit_shas: List[str]
    file_types: List[str] = []
    analysis_options: AnalysisOptions = AnalysisOptions()

class ErrorResponse(BaseModel):
    error: str
    message: str
    status_code: int