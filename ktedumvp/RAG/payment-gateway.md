# RAG 문서 2: 결제 처리 API (Payment-Gateway)

## API 식별 패턴
- URL: `payment.company.com`, `billing-api.internal`
- Package: `payment-gateway`, `billing-client`
- Class: `PaymentProcessor`, `BillingManager`, `RefundService`
- Method: `processPayment()`, `refundTransaction()`, `validateCard()`

## 주요 주의사항

### 🚨 보안 이슈 (최우선)
- **PCI DSS 준수**: 카드 정보 처리 시 PCI DSS 표준 준수 필수
- **카드번호 마스킹**: 로그에 카드번호 마지막 4자리만 표시
- **암호화**: 모든 결제 데이터 TLS 1.3 암호화 전송
- **토큰화**: 카드 정보는 토큰으로 변환하여 저장

### ⚡ 성능 이슈
- **타임아웃**: 결제 API 30초, 환불 API 60초 타임아웃
- **재시도**: 네트워크 오류 시 최대 3회 재시도
- **멱등성**: 중복 결제 방지를 위한 거래 ID 생성
- **큐잉**: 대량 결제 처리 시 메시지 큐 활용

### 🐛 일반적인 실수
- **금액 처리**: 부동소수점 사용 금지, 정수(원) 단위 사용
- **통화 코드**: ISO 4217 표준 통화 코드 사용 (KRW, USD)
- **환불 로직**: 부분 환불 시 잔액 확인 필수
- **결제 상태**: 결제 중(PENDING) 상태 적절히 처리

### 📋 보안 체크리스트
- [ ] 카드번호 로깅 방지
- [ ] PCI DSS 스캐닝 통과
- [ ] 거래 ID 중복 검증
- [ ] 부동소수점 사용 금지
- [ ] 환불 권한 검증

### 💥 치명적 위험
- **이중 결제**: 멱등성 키 누락으로 중복 결제 발생
- **카드 정보 노출**: 로그나 에러 메시지에 카드번호 노출
- **금액 오차**: 부동소수점 연산으로 인한 금액 차이

---