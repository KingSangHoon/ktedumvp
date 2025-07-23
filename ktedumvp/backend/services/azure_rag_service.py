import os
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential

class AzureRAGService:
    def __init__(self):
        self.endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
        self.api_key = os.getenv("AZURE_SEARCH_API_KEY")
        self.index_name = os.getenv("AZURE_SEARCH_INDEX_NAME")
        
        self.credential = AzureKeyCredential(self.api_key)
        self.search_client = SearchClient(
            endpoint=self.endpoint,
            index_name=self.index_name,
            credential=self.credential
        )
        print(f"Azure RAG Service 초기화 완료 - Index: {self.index_name}")
    
    def detect_external_apis(self, code_diff):
        """코드에서 외부 API 사용 패턴 감지"""
        detected_patterns = []
        
        hr_patterns = [
            'hr-api', 'HRServiceClient', 'EmployeeManager', 'PayrollAPI', 
            'getEmployee', 'updateSalary', 'getOrganization', 'hr-client', 'employee-api'
        ]
        if any(pattern in code_diff for pattern in hr_patterns):
            detected_patterns.append('hr-api')
        
        payment_patterns = [
            'payment', 'PaymentProcessor', 'BillingManager', 'RefundService', 
            'processPayment', 'refundTransaction', 'validateCard', 'payment-gateway', 'billing-client'
        ]
        if any(pattern in code_diff for pattern in payment_patterns):
            detected_patterns.append('payment')
        
        support_patterns = [
            'support-api', 'TicketManager', 'SupportAPI', 'CustomerService', 
            'createTicket', 'updateStatus', 'searchTickets', 'support-client', 'ticket-api'
        ]
        if any(pattern in code_diff for pattern in support_patterns):
            detected_patterns.append('support')
        
        inventory_patterns = [
            'inventory', 'InventoryManager', 'StockService', 'WarehouseAPI',
            'updateStock', 'checkAvailability', 'reserveItems', 'inventory-client', 'warehouse-api'
        ]
        if any(pattern in code_diff for pattern in inventory_patterns):
            detected_patterns.append('inventory')
        
        approval_patterns = [
            'approval', 'ApprovalManager', 'WorkflowEngine', 'ProcessAPI',
            'submitRequest', 'approveRequest', 'getApprovalStatus', 'approval-client', 'workflow-engine'
        ]
        if any(pattern in code_diff for pattern in approval_patterns):
            detected_patterns.append('approval')
        
        url_patterns = {
            'hr-api.company.com': 'hr-api',
            'internal-hr.example.com': 'hr-api',
            'payment.company.com': 'payment',
            'billing-api.internal': 'payment',
            'support-api.company.com': 'support',
            'helpdesk.internal': 'support',
            'inventory-api.company.com': 'inventory',
            'stock.internal': 'inventory',
            'approval-api.company.com': 'approval',
            'workflow.internal': 'approval'
        }
        
        for url, api_type in url_patterns.items():
            if url in code_diff and api_type not in detected_patterns:
                detected_patterns.append(api_type)
        
        return detected_patterns

    def search_api_knowledge(self, detected_patterns):
        """감지된 API 패턴으로 관련 지식 검색"""
        if not detected_patterns:
            return []
        
        try:
            # 유사어 포함된 쿼리 구성
            query_terms = {
                'hr-api': ['hr', 'human resources', 'employee api', '인사 시스템'],
                'payment': ['payment', 'billing', '결제 시스템', '결제 api'],
                'support': ['support', 'ticket', '고객지원', '헬프데스크'],
                'inventory': ['inventory', 'warehouse', 'stock', '재고 시스템'],
                'approval': ['approval', 'workflow', '결재', '승인 프로세스']
            }

            expanded_terms = []
            for pattern in detected_patterns:
                expanded_terms += query_terms.get(pattern, [pattern])

            search_query = " OR ".join(set(expanded_terms))

            print(search_query, "로 RAG 검색 시작")

            results = self.search_client.search(
                search_text=search_query,
                top=1,
                include_total_count=True
            )

            print(results.get_count(), "개 결과 발견")

            knowledge_docs = []

            for result in results:
                captions = result.get('@search.captions') or [{}]
                caption_text = captions[0].get('text', '') if captions else ''
                filename = result.get('metadata_storage_name', '') or result.get('metadata_storage_path', '')
                
                print(f"검색 결과: {filename} - {result.get('@search.score', 0)}")
                
                knowledge_docs.append({
                    'filename': filename,
                    'content': result.get('content', ''),
                    'caption': caption_text,
                    'score': result.get('@search.score', 0)
                })

            print(f"RAG 검색 완료: {len(knowledge_docs)}개 문서 발견")
            return knowledge_docs

        except Exception as e:
            print(f"RAG 검색 실패: {e}")
            return []

    def format_knowledge_for_prompt(self, knowledge_docs):
        """검색된 지식을 프롬프트용으로 포맷팅"""
        if not knowledge_docs:
            return ""

        formatted = "\n\n🔍 **관련 외부 API 가이드라인:**\n"

        for doc in knowledge_docs:
            if doc['score'] > 0.5:  # 기준 완화
                formatted += f"\n### 📋 {doc['filename']}\n"
                if doc.get('caption'):
                    formatted += f"🧠 요약: {doc['caption']}\n\n"
                content = doc['content'][:1500] + "..." if len(doc['content']) > 1500 else doc['content']
                formatted += f"{content}\n"
        return formatted