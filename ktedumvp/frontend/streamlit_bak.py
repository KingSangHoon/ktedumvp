import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import random

# 페이지 설정
st.set_page_config(
    page_title="LLM 기반 에러 탐지 시스템",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS 스타일링
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
    }
    .error-critical {
        background-color: #ffebee;
        border-left: 5px solid #f44336;
        padding: 10px;
        border-radius: 5px;
        margin: 5px 0;
    }
    .error-high {
        background-color: #fff3e0;
        border-left: 5px solid #ff9800;
        padding: 10px;
        border-radius: 5px;
        margin: 5px 0;
    }
    .error-medium {
        background-color: #fff8e1;
        border-left: 5px solid #ffc107;
        padding: 10px;
        border-radius: 5px;
        margin: 5px 0;
    }
    .error-low {
        background-color: #e8f5e8;
        border-left: 5px solid #4caf50;
        padding: 10px;
        border-radius: 5px;
        margin: 5px 0;
    }
</style>
""", unsafe_allow_html=True)

# 메인 헤더
st.markdown('<h1 class="main-header">🔍 LLM 기반 에러 사전 탐지 시스템</h1>', unsafe_allow_html=True)

# 사이드바
with st.sidebar:
    st.header("⚙️ 시스템 설정")
    
    # 프로젝트 선택
    selected_project = st.selectbox(
        "프로젝트 선택",
        ["BSS 차세대", "Legacy System", "API Gateway", "Mobile App"]
    )
    
    # 분석 범위 설정
    st.subheader("🔍 분석 범위")
    syntax_check = st.checkbox("문법/구조적 에러", value=True)
    security_check = st.checkbox("보안 취약점", value=True)
    performance_check = st.checkbox("성능 이슈", value=True)
    logic_check = st.checkbox("로직 에러", value=True)
    
    # 알림 설정
    st.subheader("📢 알림 설정")
    sms_alert = st.checkbox("SMS 알림", value=True)
    email_alert = st.checkbox("이메일 알림", value=True)
    slack_alert = st.checkbox("Slack 알림", value=False)
    
    # 심각도 필터
    st.subheader("🚨 심각도 필터")
    severity_filter = st.multiselect(
        "표시할 심각도",
        ["Critical", "High", "Medium", "Low"],
        default=["Critical", "High", "Medium", "Low"]
    )

# 메인 대시보드
col1, col2, col3, col4 = st.columns(4)

# 실시간 통계
with col1:
    st.metric(
        label="🔴 Critical 에러",
        value="3",
        delta="-1"
    )

with col2:
    st.metric(
        label="🟠 High 에러", 
        value="7",
        delta="+2"
    )

with col3:
    st.metric(
        label="🟡 Medium 에러",
        value="15",
        delta="+5"
    )

with col4:
    st.metric(
        label="✅ 빌드 성공률",
        value="94.2%",
        delta="+2.1%"
    )

# 탭 구성
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 대시보드", "🔍 실시간 분석", "📈 통계", "⚙️ 설정", "📋 보고서"])

with tab1:
    st.subheader("📊 실시간 에러 탐지 현황")
    
    # 최근 커밋 분석 결과
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🕒 최근 커밋 분석 결과")
        
        # 샘플 데이터
        recent_commits = pd.DataFrame({
            'Commit ID': ['a1b2c3d', 'e4f5g6h', 'i7j8k9l', 'm1n2o3p', 'q4r5s6t'],
            'Author': ['김개발', '이코딩', '박시스템', '최프로그래머', '정개발자'],
            'Time': ['2분 전', '5분 전', '12분 전', '18분 전', '25분 전'],
            'Status': ['✅ 통과', '🔴 Critical', '🟠 High', '✅ 통과', '🟡 Medium'],
            'Files': [3, 7, 2, 5, 4],
            'Errors': [0, 2, 1, 0, 3]
        })
        
        st.dataframe(recent_commits, use_container_width=True)
    
    with col2:
        st.subheader("📋 실시간 알림")
        
        # 실시간 알림 시뮬레이션
        if st.button("🔄 새로고침"):
            st.rerun()
        
        notifications = [
            {"time": "1분 전", "message": "Critical: Null Pointer 위험 탐지", "severity": "critical"},
            {"time": "3분 전", "message": "High: SQL Injection 취약점", "severity": "high"},
            {"time": "7분 전", "message": "Medium: 성능 최적화 필요", "severity": "medium"},
            {"time": "12분 전", "message": "Low: 코딩 컨벤션 위반", "severity": "low"}
        ]
        
        for notif in notifications:
            severity_class = f"error-{notif['severity']}"
            st.markdown(f"""
            <div class="{severity_class}">
                <strong>{notif['time']}</strong><br>
                {notif['message']}
            </div>
            """, unsafe_allow_html=True)

    # 에러 트렌드 차트
    st.subheader("📈 에러 탐지 트렌드 (최근 7일)")
    
    # 샘플 데이터 생성
    dates = [datetime.now() - timedelta(days=x) for x in range(6, -1, -1)]
    error_data = pd.DataFrame({
        'Date': dates,
        'Critical': [1, 2, 0, 3, 1, 2, 3],
        'High': [5, 7, 3, 8, 6, 9, 7],
        'Medium': [12, 15, 8, 18, 14, 16, 15],
        'Low': [25, 30, 20, 35, 28, 32, 28]
    })
    
    fig = px.line(error_data.melt(id_vars=['Date'], var_name='Severity', value_name='Count'),
                  x='Date', y='Count', color='Severity',
                  color_discrete_map={
                      'Critical': '#f44336',
                      'High': '#ff9800', 
                      'Medium': '#ffc107',
                      'Low': '#4caf50'
                  })
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("🔍 실시간 코드 분석")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📝 코드 입력/업로드")
        
        analysis_type = st.radio(
            "분석 방법 선택",
            ["코드 직접 입력", "파일 업로드", "Git Repository"]
        )
        
        if analysis_type == "코드 직접 입력":
            code_input = st.text_area(
                "분석할 코드를 입력하세요",
                height=300,
                placeholder="""
예시:
public class Example {
    public static void main(String[] args) {
        String[] data = null;
        System.out.println(data.length); // Null Pointer 위험
    }
}
                """
            )
            
        elif analysis_type == "파일 업로드":
            uploaded_file = st.file_uploader(
                "코드 파일 선택",
                type=['java', 'js', 'py', 'cpp', 'c', 'cs']
            )
            
        else:
            repo_url = st.text_input("Git Repository URL")
            branch = st.text_input("Branch", value="main")
        
        language = st.selectbox(
            "프로그래밍 언어",
            ["Java", "JavaScript", "Python", "C++", "C#", "자동 감지"]
        )
        
        if st.button("🔍 분석 시작", type="primary"):
            with st.spinner("코드 분석 중..."):
                time.sleep(2)  # 분석 시뮬레이션
                st.success("분석 완료!")
    
    with col2:
        st.subheader("📊 분석 결과")
        
        # 분석 결과 시뮬레이션
        analysis_results = {
            "전체 라인": 156,
            "분석된 파일": 8,
            "발견된 이슈": 12,
            "처리 시간": "2.3초"
        }
        
        for key, value in analysis_results.items():
            st.metric(key, value)
        
        st.subheader("🚨 발견된 에러")
        
        errors = [
            {
                "line": 23,
                "type": "Null Pointer Exception",
                "severity": "Critical",
                "description": "변수 'data'가 null일 가능성이 있습니다.",
                "suggestion": "null 체크를 추가하세요: if(data != null)"
            },
            {
                "line": 45,
                "type": "SQL Injection",
                "severity": "High", 
                "description": "사용자 입력이 직접 SQL 쿼리에 사용됩니다.",
                "suggestion": "PreparedStatement를 사용하세요."
            },
            {
                "line": 67,
                "type": "Resource Leak",
                "severity": "Medium",
                "description": "FileInputStream이 닫히지 않습니다.",
                "suggestion": "try-with-resources 구문을 사용하세요."
            }
        ]
        
        for i, error in enumerate(errors):
            severity_color = {
                "Critical": "🔴",
                "High": "🟠", 
                "Medium": "🟡",
                "Low": "🟢"
            }
            
            with st.expander(f"{severity_color[error['severity']]} Line {error['line']}: {error['type']}"):
                st.write(f"**심각도:** {error['severity']}")
                st.write(f"**설명:** {error['description']}")
                st.write(f"**제안사항:** {error['suggestion']}")

with tab3:
    st.subheader("📈 통계 및 분석")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 에러 유형별 분포")
        
        error_types = pd.DataFrame({
            'Type': ['Null Pointer', 'SQL Injection', 'Resource Leak', 'Index Out of Bounds', 'Logic Error'],
            'Count': [15, 8, 12, 6, 9]
        })
        
        fig_pie = px.pie(error_types, values='Count', names='Type', 
                         title="에러 유형별 분포")
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        st.subheader("📅 월별 에러 탐지 현황")
        
        monthly_data = pd.DataFrame({
            'Month': ['1월', '2월', '3월', '4월', '5월', '6월', '7월'],
            'Errors': [45, 38, 52, 33, 41, 29, 35],
            'Build Success Rate': [91.2, 93.5, 89.8, 95.2, 92.7, 96.1, 94.2]
        })
        
        fig_bar = px.bar(monthly_data, x='Month', y='Errors',
                         title="월별 에러 탐지 수")
        st.plotly_chart(fig_bar, use_container_width=True)
    
    # 상세 통계 테이블
    st.subheader("📋 상세 통계")
    
    detailed_stats = pd.DataFrame({
        '개발자': ['김개발', '이코딩', '박시스템', '최프로그래머', '정개발자'],
        '커밋 수': [45, 38, 52, 33, 41],
        '에러 발견': [8, 5, 12, 3, 7],
        '에러율 (%)': [17.8, 13.2, 23.1, 9.1, 17.1],
        '평균 수정 시간': ['15분', '12분', '18분', '8분', '14분']
    })
    
    st.dataframe(detailed_stats, use_container_width=True)

with tab4:
    st.subheader("⚙️ 시스템 설정")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔧 LLM 설정")
        
        llm_model = st.selectbox(
            "LLM 모델 선택",
            ["GPT-4", "GPT-3.5-turbo", "Claude-3", "Custom Model"]
        )
        
        analysis_depth = st.slider(
            "분석 깊이",
            min_value=1,
            max_value=5,
            value=3,
            help="1: 기본 문법 검사, 5: 심화 로직 분석"
        )
        
        timeout_setting = st.number_input(
            "분석 타임아웃 (초)",
            min_value=10,
            max_value=300,
            value=60
        )
        
        st.subheader("📧 알림 설정")
        
        notification_email = st.text_input("알림 이메일", "admin@company.com")
        notification_phone = st.text_input("알림 전화번호", "010-1234-5678")
        
        critical_only = st.checkbox("Critical 에러만 즉시 알림")
        daily_report = st.checkbox("일일 리포트 발송", value=True)
    
    with col2:
        st.subheader("🛡️ 보안 설정")
        
        api_key = st.text_input("Azure AI API Key", type="password")
        webhook_url = st.text_input("Webhook URL")
        
        st.subheader("📊 로그 설정")
        
        log_level = st.selectbox(
            "로그 레벨",
            ["DEBUG", "INFO", "WARNING", "ERROR"]
        )
        
        log_retention = st.number_input(
            "로그 보관 기간 (일)",
            min_value=7,
            max_value=365,
            value=30
        )
        
        st.subheader("🔄 백업 설정")
        
        auto_backup = st.checkbox("자동 백업", value=True)
        backup_interval = st.selectbox(
            "백업 주기",
            ["매일", "매주", "매월"]
        )
    
    if st.button("💾 설정 저장", type="primary"):
        st.success("설정이 저장되었습니다!")

with tab5:
    st.subheader("📋 분석 보고서")
    
    report_type = st.selectbox(
        "보고서 유형",
        ["일일 보고서", "주간 보고서", "월간 보고서", "프로젝트 요약"]
    )
    
    date_range = st.date_input(
        "기간 선택",
        value=(datetime.now() - timedelta(days=7), datetime.now())
    )
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 보고서 생성"):
            with st.spinner("보고서 생성 중..."):
                time.sleep(2)
                st.success("보고서가 생성되었습니다!")
    
    with col2:
        if st.button("📧 이메일 발송"):
            st.success("보고서가 이메일로 발송되었습니다!")
    
    with col3:
        if st.button("📥 다운로드"):
            st.success("보고서가 다운로드되었습니다!")
    
    # 보고서 미리보기
    st.subheader("📖 보고서 미리보기")
    
    st.markdown("""
    ## 🔍 LLM 기반 에러 탐지 시스템 주간 보고서
    
    **기간**: 2025.07.15 ~ 2025.07.22  
    **프로젝트**: BSS 차세대
    
    ### 📊 요약
    - **총 커밋 수**: 127개
    - **분석된 파일**: 1,234개  
    - **발견된 에러**: 35개
    - **빌드 성공률**: 94.2% (전주 대비 +2.1%)
    
    ### 🚨 주요 발견사항
    1. **Critical 에러 3개**: Null Pointer 위험 2개, Security 취약점 1개
    2. **High 에러 7개**: SQL Injection 3개, Resource Leak 4개
    3. **개선 사항**: 평균 에러 수정 시간 14분 (전주 대비 -3분)
    
    ### 📈 트렌드 분석
    - 에러 탐지율이 전주 대비 15% 향상
    - 보안 취약점 조기 발견으로 잠재적 위험 차단
    - 개발팀 코드 품질 향상 확인
    
    ### 🎯 권장사항
    1. Critical 에러 발생 빈도가 높은 모듈에 대한 추가 교육 필요
    2. 자동화된 단위 테스트 강화 권장
    3. 코드 리뷰 가이드라인 업데이트 필요
    """)

# 하단 상태바
st.markdown("---")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("🔄 시스템 상태", "정상 운영")

with col2:
    st.metric("⏱️ 평균 분석 시간", "2.3초")

with col3:
    st.metric("💾 저장소 사용량", "78%")

with col4:
    st.metric("🌐 API 응답율", "99.8%")

# 푸터
st.markdown("""
---
<div style='text-align: center; color: #666; padding: 20px;'>
    <strong>LLM 기반 에러 사전 탐지 시스템</strong> | 
    Version 1.0.0 | 
    © 2025 Development Team
</div>
""", unsafe_allow_html=True)