  
---

**∧,,,∧**  
**( ̳• · • ̳)**  
/ づ♡

# **냥냥편지**

N Y A N G   N Y A N G   L E T T E R

---

# ***스마트폰 행동 데이터 기반 정신 건강 패턴 분석 서비스***

## 

## 

## 소속 

## 작성자

## 작성일

# **목차**

**1\.  서론**

1.1  프로젝트 개요 및 배경

1.2  프로젝트 목표 및 기대 효과

**2\.  요구사항 분석**

2.1  비즈니스 요구사항

       2.1.1 서비스 목표 

       2.1.2 사용자 가치

2.2  기술 요구사항

 2.2.1 데이터 수집 / 저장

 2.2.2 이상 탐지 / 상태 분류 

 2.2.3 이벤트 기반 트리거 

 2.2.4 음성 / 콘텐츠 생성 파이프라인 

 2.2.5 보안 및 컴플라이언스

2.3  비기능 요구사항

2.3.1  응답 성능

2.3.2  처리 성능

2.3.3  동시 처리

2.3.4  확장성

2.3.5 운영 / 확장 요구

**3\.  시스템 아키텍처 설계**

3.1  시스템 아키텍처 개요

      3.1.1 전체 구성도 

      3.1.2 서비스 간 연계 구조

3.2 컴포넌트별 상세 설계

3.2.1  클라이언트 계층 (Kotlin Android)

3.2.2  API 서버 (EKS \+ FastAPI)

3.2.3  DB 설계  (RDS / DynamoDB)

3.2.4  이벤트 처리 (Lambda / SQS)

3.2.5  AI 모델 (SageMaker / 이상치 탐지 모델)

3.3  서비스 흐름 설계

3.3.1  인증 흐름

3.3.2  데이터 저장 흐름

3.3.3  이벤트 처리 흐름

3.3.4  알림 흐름

3.3.5  AI 분석 흐름

3.4 API 설계 및 데이터 흐름 

3.5 CI/CD 구축 전략

**4\.  인프라 구축 및 운영**

4.1  클라우드 인프라 구성

4.2  네트워크 구성 (로드 밸런싱, VPC, 서브넷)

4.3  고가용성 및 확장성 설계 (Auto Scaling, Multi-Region)

4.4  보안 및 접근 제어 정책 (IAM, 보안 그룹, WAF 등)

**5\.  데이터 파이프라인 설계**

5.1  데이터 저장소 설계 (Data Lake, Data Warehouse)

5.2  데이터 수집 및 전처리 (ETL)

5.2.1  Bronze → Silver

5.2.2  Silver → Gold

5.3  실시간 데이터 처리 (Kafka, FastAPI, WebSocket 등)

5.4  데이터 분석 및 활용 방안

**6\.  AI 모델 및 데이터 분석**

6.1  모델 연구 개요

6.2  시스템 구조

6.2.1  전체 구조 개요

6.2.2  모델 학습 및 추론 구조

6.2.3  모델 파이프라인

6.3  데이터 분석 (EDA)

6.3.1  데이터셋 개요

6.3.2  주요 분석 결과

6.4  Feature Engineering

6.4.1  입력 데이터

6.4.2  일 단위 집계

6.4.3  생성 피처

6.5  모델 설계 및 구현

6.5.1  입력 및 기본 전처리

6.5.2  Quality Gate & Context Flag

6.5.3  개인 베이스라인 (ST/LT \+ Early)

6.5.4  Z-score 생성

6.5.5  이상탐지 모델 (Isolation Forest)

6.5.6  최종 위험도 산출

6.6  디코더 설계 (상태 해석 로직)

6.6.1  디코더 목적

6.6.2  입력 신호 구조

6.6.3  상태 체계 정의

6.6.4  우선순위 기반 판정 구조

6.6.5  Reason Code 설계

6.7  운영 및 확장 고려사항

6.7.1  모델 재학습 전략

6.7.2  모델 품질 점검 지표

6.7.3  Fallback 설계

**7\.  성능 테스트 및 최적화**

7.1  부하 테스트 계획 및 실행 결과

7.2  트러블슈팅 및 병목 현상 해결

7.3  성능 개선 방안

**8\.  프로젝트 운영 및 유지보수 전략**

8.1  배포 및 릴리즈 전략

8.2  서비스 운영 모니터링 및 장애 대응

8.3  보안 정책 및 지속적인 개선 계획

8.3.1  알림 중복 발송 방지

8.3.2  서비스 장애 시 오발송 방지

8.3.3  보안 정책

8.3.4  모델 개선 방향

**9\.  결론 및 향후 발전 방향**

**부록**  

# 

# 

# **1\. 서론**

## **1.1 프로젝트 개요 및 배경**

현대인의 정신 건강 문제는 외부에서 직접적으로 감지하기 어렵다는 특성을 가진다. 연구에 따르면 개인의 정서 상태 변화는 스마트폰 사용 패턴의 변화로 선행적으로 나타날 수 있으며, 이는 행동 데이터 기반의 간접적 상태 추론 가능성을 시사한다.

기존의 정신 건강 모니터링 방식은 사용자가 직접 체크인하거나 이상 상황을 신고하는 형태에 의존하는 경우가 많다. 그러나 이러한 방식은 심리적 부담이 크고, 정작 도움이 필요한 순간에는 사용자 스스로 행동하기 어렵다는 한계가 있다.

냥냥편지 프로젝트는 이러한 문제의식에서 출발한다. 사용자가 의식하지 않아도 자연스러운 스마트폰 사용 로그를 통해 상태가 반영되는 비침습적(non-invasive) 접근 방식을 채택하여, 장시간 무반응 상태를 자동으로 인지하고 주변인에게 간접적 안부 신호를 전달하는 체계를 구현한다.

서비스의 핵심 컨셉은 고양이 캐릭터를 매개로 한 감성 커뮤니케이션이다. "고독사"와 같은 민감한 표현 없이도 상태 변화를 자연스럽게 전달하고, 메시지·하트·BGM 등 감성 콘텐츠를 통해 사용자 간 연결을 강화한다. 이를 통해 안전 확인이라는 무거운 행위를 일상적인 감정 교류의 형태로 전환하는 것이 본 프로젝트의 차별점이다.

## **1.2 프로젝트 목표 및 기대 효과**

**1.2.1 목표**

고양이 캐릭터를 매개로 가볍고 부담 없는 감정 교류를 돕는 비동기 감성 커뮤니케이션 서비스를 구현한다. 구체적으로는 다음 세 가지 기술 목표를 달성한다.

첫째, 스마트폰 행동 로그 기반 이상 탐지 모델을 운영하여 사용자 일상 상태를 STABLE·SLEEP·LETHARGY·CHAOS·CRITICAL·TRAVEL·NO\_DATA 7개 코드로 분류한다. 둘째, 상태 변화 이벤트를 자동으로 감지하고, 메시지·하트·BGM 등 감성 콘텐츠 생성 파이프라인을 이벤트 기반으로 트리거하는 자동화 체계를 구축한다. 셋째, 위급 상황(CRITICAL) 발생 시 친밀도·거리·활동 패턴을 종합 분석하여 최적 구조자를 AI가 선정하고 단계적 알림을 전송하는 에이전트 시스템을 구현한다.

**1.2.2 기대 효과**

서비스 관점에서는 직접적인 신고나 체크인 없이도 사용자 간 자연스러운 일상 연결을 강화하고, 장시간 무반응 상황에서 간접적 안전 신호를 전달하는 체계를 제공한다. 정신 건강 위기 상황에서 개입 시점을 앞당기는 데 기여할 수 있다.

기술 관점에서는 Android 네이티브 클라이언트, EKS 기반 FastAPI 마이크로서비스, AWS 데이터 파이프라인(Firehose·S3·Glue), SageMaker 기반 ML 파이프라인, Amazon Bedrock 기반 AI 에이전트를 통합 설계함으로써 실서비스 수준의 확장 가능한 아키텍처를 구현한다.

# **2\. 요구사항 분석**

## **2.1 비즈니스 요구사항**

### **2.1.1 서비스 목표**

현대인의 일상 연결을 강화하고, 장시간 무반응 상황에서 안전 신호 전달을 지원한다. 사용자 부담이 큰 직접 신고 및 체크인 방식이 아니라, 행동 패턴 변화 기반의 간접 신호로 커뮤니케이션을 보완하는 것을 핵심 방향으로 삼는다.

### **2.1.2 사용자 가치**

사용자는 앱을 의무적으로 사용하지 않아도 자연스러운 스마트폰 사용 로그를 통해 상태가 반영된다. 친구 및 지인은 민감한 표현 없이 상태 변화 및 무반응 알림을 통해 필요한 대응을 취할 수 있다. CRITICAL 상태에서는 AI 에이전트가 친밀도·거리·활동 패턴을 종합 분석하여 가장 빠르게 도움을 줄 수 있는 친구를 자동 선정하고 단계적으로 알림을 전송한다.

## **2.2 기술 요구사항**

### **2.2.1 데이터 수집 및 저장**

모바일 클라이언트는 앱 사용, 화면 On/Off, Wi-Fi 변화, 위치 정보, 걸음 수, Cell LAC 등의 이벤트 로그를 1분 주기로 수집하여 표준 스키마로 전송한다. 수집된 로그는 API Gateway → Lambda → Kinesis Data Firehose → S3 경로를 통해 데이터 레이크에 적재되며, Bronze(원본) → Silver(정제) → Gold(집계) 계층 구조로 관리된다.

사용자 및 친구 관계 정보는 RDS(PostgreSQL)에, 친구 관계 상태 및 로비 조회용 비정규화 데이터는 DynamoDB에 저장한다. 상태 분류 결과, 작업 이력, 알림 이벤트는 이력 조회 및 재처리가 가능한 구조로 보존한다.

### **2.2.2 이상 탐지/상태 분류**

개인별 사용 패턴 편차가 크다는 점을 고려하여 전역 기준이 아닌 사용자별 개인 베이스라인 기반 이상 탐지 모델을 운영한다. Isolation Forest 알고리즘에 단기(14일)·장기(56일) 베이스라인 및 Z-score 정규화를 결합하여 개인 행동 변화를 탐지한다.

모델 출력은 서비스 정책에 따라 아래 7개 상태 코드로 정규화된다.

| 상태 코드 | 설명 |
| :---: | ----- |
| STABLE | 정상적인 사용 패턴 |
| SLEEP | 수면으로 판단되는 비활성 상태 |
| LETHARGY | 활동량이 현저히 감소한 무기력 상태 |
| CHAOS | 불규칙하고 혼란스러운 사용 패턴 |
| CRITICAL | 장시간 무반응으로 즉각 개입이 필요한 상태 |
| TRAVEL | 이동 중으로 판단되는 상태 |
| NO\_DATA | 데이터 수신 불가 또는 분석 불가 상태 |

모델 학습 및 서빙은 버전·파라미터·학습 데이터 기준으로 재현성을 관리하며, 상태 분류 결과와 위험 점수 분포는 지속적으로 모니터링한다.

### **2.2.3 이벤트 기반 트리거**

상태 코드 전환 이벤트 발생 시 후속 처리 파이프라인이 자동으로 시작되어야 한다. 주요 트리거 조건은 다음과 같다.

상태 코드가 변경되는 경우(예: STABLE → LETHARGY), 사전 정의된 시간 이상 무반응이 지속되어 CRITICAL 상태에 진입하는 경우, 사용자가 직접 위험 신호를 발송하는 경우가 이에 해당한다.

트리거된 이벤트는 SQS를 통해 비동기로 전달되며, 메시지 생성·BGM 생성·음성 합성·친구 알림 발송 등 각 처리 단계는 독립적으로 동작한다. 모든 처리 결과는 OutboxEvents 테이블에 이력으로 저장되며 실패 시 Exponential Backoff 기반 자동 재시도가 수행된다.

### 

### **2.2.4 음성/컨텐츠생성 파이프라인**

상태 코드에 따라 고양이 캐릭터 기반 감성 콘텐츠를 자동 생성한다. 생성 대상은 텍스트 메시지, 배경음악(BGM), 고양이 울음소리(Voice) 세 종류이며 각각 독립적인 생성 파이프라인으로 운영된다.

사용자가 업로드하는 고양이 울음소리에 대해서는 유해 콘텐츠 필터링을 위한 오디오 가드레일을 적용한다. BGM은 사용자의 일별 행동 지표를 기반으로 AI 음악 생성 서비스를 통해 개인화된 결과물을 제공한다. 파일 업로드는 확장자 및 크기(10MB 이하) 검증 후 S3에 저장되며, RDS에는 URL만 저장하는 구조를 채택한다.

### **2.2.5 보안 및 컴플라이언스**

사용자 행동 로그 및 상태 정보는 개인 식별 가능 정보(PII)에 준하는 수준으로 관리한다. 데이터 수집 파이프라인에서 user\_id는 DynamoDB 기반 결정적 토큰화(Deterministic Tokenization)를 통해 비식별화하며, GPS 좌표는 소수점 둘째 자리까지 정밀도를 축소하여 저장한다. S3 데이터 레이크는 KMS 기반 SSE 암호화를 적용하고, 서비스 간 인증은 AWS IRSA 기반 IAM Role을 사용하여 Access Key를 사용하지 않는 구조로 설계한다. 사용자 동의 기반 권한 요청 원칙을 준수하며, 권한 거부 시에도 앱의 기본 기능은 유지된다.

## **2.3 비기능 요구사항 (성능, 보안, 가용성, 확장성)**

**2.3.1 응답 성능**

모바일 이벤트 로그 전송 API는 평균 1초 이내 응답해야 한다. 상태 변경 이벤트 발생 시 BGM 및 Voice 작업 트리거는 5초 이내 실행되어야 한다.

**2.3.2 처리 성능**

이상치 분석 모델은 1인 사용자 기준 1일 데이터 분석을 3초 이내 처리해야 한다. 음성 생성 및 합성 작업은 1분 이내 완료를 목표로 한다.

**2.3.3 동시 처리**

최소 동시 1,000명 규모에 대응 가능해야 한다.

### **2.3.4 확장성**

동시 사용자가 급격히 증가하는 상황에서도 응답 성능 기준을 유지해야 한다. 이를 위해 로드밸런서를 통한 자동 트래픽 분산, 이벤트 기반 비동기 처리 구조, 컨테이너 기반 수평 확장(EKS Pod Auto Scaling)을 적용한다.

### **2.3.5 운영 / 확장 요구**

상태 업데이트 및 무응답 감지 이벤트가 발생하면 SQS를 통해 자동으로 후속 처리 파이프라인이 시작되어야 한다. 사용자 증가 시에도 이벤트 기반 비동기 처리 구조와 컨테이너 기반 수평 확장을 통해 시스템이 성능 기준을 유지해야 한다. 개인정보 및 민감정보에 대한 접근 제어, 비식별화, 암호화가 파이프라인 전 구간에 걸쳐 적용되어야 한다.

# **3\. 아키텍처 설계**

## **3.1 시스템 아키텍처 개요**

NYAN-MATE는 스마트폰 행동 데이터를 수집·분석하여 사용자의 정서 상태를 고양이 캐릭터로 시각화하고, 관계망 기반의 돌봄 알림을 제공하는 서비스이다. 시스템 전체는 AWS 클라우드 인프라 위에서 운영되며, 클라이언트 계층 / API 서버 / 데이터 저장소 / 이벤트 처리 / AI 모델의 5개 컴포넌트로 구성된다.

### **3.1.1 전체 구성도**

시스템은 크게 세 가지 흐름으로 동작한다. 첫째, 사용자 스마트폰(Android)에서 수집된 행동 로그가 API 서버를 통해 DynamoDB 및 S3에 적재되는 데이터 수집 흐름이다. 둘째, S3에 적재된 데이터를 기반으로 ETL 파이프라인이 Bronze → Silver → Gold 단계로 정제하고, EKS 위의 Inference Pod가 매일 새벽 CronJob으로 AI 추론을 수행하여 결과를 RDS에 저장하는 AI 분석 흐름이다. 셋째, AI 분석 결과에서 이상 상태가 탐지되면 Lambda가 SQS를 통해 FCM Push 알림을 발송하는 이벤트·알림 흐름이다.

각 컴포넌트와 서비스는 다음과 같이 구성된다.

| 계층 | 구성 요소 | AWS 서비스 |
| :---: | :---: | :---: |
| 클라이언트 | Android 앱 (Kotlin) | \- |
| API 서버 | FastAPI 컨테이너 | EKS, ALB |
| 데이터 저장소 | 정형 데이터, 로그, 모델 아티팩트 | RDS (PostgreSQL), DynamoDB, S3 |
| 이벤트 처리 | 스케줄링, 알림 발송 | EventBridge, Lambda, SQS |
| AI 모델 | 학습(Training), 추론(Inference) | SageMaker, EKS CronJob |

### **3.1.2 서비스 간 연계 구조**

각 컴포넌트는 다음과 같이 연계된다.

Android 클라이언트는 ALB를 통해 EKS 위의 FastAPI 서버에 접근하며, 센서 로그 전송 및 AI 분석 결과 조회, 친구 알림 수신을 처리한다. FastAPI 서버는 수신한 로그를 DynamoDB에 저장하는 동시에 S3 Bronze 경로에도 적재하며, 사용자·친구 관계 등의 정형 데이터는 RDS에서 관리한다.

데이터 파이프라인은 S3 Bronze에 적재된 원시 로그를 Silver(정제 데이터)로, 다시 Gold(Feature 데이터)로 변환하는 ETL 프로세스로 구성된다. Gold 데이터를 기반으로 SageMaker Training Job이 Isolation Forest 모델을 학습하고 모델 파일을 S3에 저장한다. 이후 EKS Inference Pod CronJob이 해당 모델과 Gold Feature를 로드하여 배치 추론을 수행하고, 최종 상태값(STABLE / SLEEP / LETHARGY / CHAOS / TRAVEL / NO\_DATA)과 위험도 스코어를 RDS에 기록한다.

알림 흐름은 RDS에 저장된 분석 결과를 Lambda가 평가하여 이상 상태(Alert / Caution) 발생 시 SQS 큐에 메시지를 적재하고, 이를 FCM을 통해 친구 단말기로 Push 알림을 발송하는 방식으로 동작한다. SQS를 중간에 두어 알림 중복 발송을 방지하고 서비스 장애 시에도 메시지 유실을 최소화한다.

## **3.2 컴포넌트별 상세 설계**

**3.2.1 클라이언트 계층(Kotlin Android)**

Kotlin 기반 Android 네이티브 애플리케이션으로 구성된다. 주요 역할은 다음과 같다.

* 사용자 인터페이스 제공 및 고양이 캐릭터 기반 감성 콘텐츠 표시

* 포그라운드 서비스를 통한 스마트폰 행동 패턴 1분 주기 수집

* 백엔드 REST API와의 통신

* FCM 기반 푸시 알림 수신 및 표시

## **3.2.2. API 서버 계층 (EKS \+ FastAPI)**

백엔드는 Amazon EKS 위에 세 개의 독립 Pod로 구성된 마이크로서비스 구조를 채택한다.

① **User pod**

사용자 계정 관리, 친구 관계 관리, 파일 업로드를 담당하는 핵심 서비스다.

services/user\_service/  
├── app/  
│   ├── api/  
│   │   ├── routes/  
│   │   │   ├── users.py      \# 사용자 관리 API  
│   │   │   ├── friends.py    \# 친구 관리 API  
│   │   │   └── upload.py     \# 파일 업로드 API  
│   │   └── v1/  
│   │       └── api.py         \# API 라우터 통합  
│   ├── core/  
│   │   ├── config.py          \# 설정  
│   │   ├── database.py        \# DB 연결  
│   │   └── security.py        \# 보안  
│   ├── models/  
│   │   └── user.py            \# User 모델  
│   ├── schemas/  
│   │   ├── user.py            \# User 스키마  
│   │   └── friend.py          \# Friend 스키마  
│   ├── services/  
│   │   ├── user\_service.py    \# 사용자 비즈니스 로직  
│   │   ├── dynamodb\_service.py \# DynamoDB 서비스  
│   │   └── s3\_service.py      \# S3 업로드 서비스  
│   └── main.py                \# FastAPI 앱  
├── Dockerfile  
├── requirements.txt  
└── .env

### User 모델은 Google/Cognito Sub를 PK로 사용하여 외부 인증 제공자와 연동하며, 6자리 영숫자 친구 코드를 자동 생성한다. 빠른 사용자 조회를 위해 email과 friend\_code에 인덱스를 적용하였다.

### from sqlalchemy import Column, String, BigInteger, Boolean

### from app.core.database import Base

### import time

### import random

### import string

### 

### class User(Base):

###     \_\_tablename\_\_ \= "users"

###    

###     user\_id \= Column(String(255), primary\_key\=True)

###     email \= Column(String(100), unique\=True, nullable\=False, index\=True)

###     nickname \= Column(String(50), nullable\=False)

###     profile\_image\_url \= Column(String(500), nullable\=True)

###     friend\_code \= Column(String(6), unique\=True, nullable\=False, index\=True)

###     created\_at\_timestamp \= Column(BigInteger, nullable\=False)

###     updated\_at\_timestamp \= Column(BigInteger, nullable\=False)

###     cat\_pattern \= Column(String(20), nullable\=True)

###     cat\_color \= Column(String(7), nullable\=True)

###     duress\_code \= Column(String(100), nullable\=True)

###     meow\_audio\_url \= Column(String(500), nullable\=True)

###     duress\_audio\_url \= Column(String(500), nullable\=True)

###     token \= Column(String(500), nullable\=True)

###     provider \= Column(String(50), nullable\=False, default\="google")

###     profile\_setup\_completed \= Column(Boolean, default\=False)

###    

###     @staticmethod

###     def generate\_friend\_code() \-\> str:

###         """6자리 영숫자 친구 코드 생성"""

###         return ''.join(random.choices(string.ascii\_uppercase \+ string.digits, k\=6))

###    

###     @staticmethod

###     def current\_timestamp() \-\> int:

###         """현재 시간을 밀리초 단위로 반환"""

###         return int(time.time() \* 1000)

### 

② **Inference\_service Pod**

ML 추론 결과를 수신하여 상태 코드를 저장하고, CRITICAL 이벤트를 SQS로 발행하는 서비스다. 일 단위 상태 동기화 배치 작업도 이 서비스에서 관리한다.

| ├── app/│ ├── routes/│ │ ├── health.py \# 헬스 체크 API│ │ └── inference.py \# 추론 이벤트/동기화 API│ ├── schemas/│ │ └── events.py \# 이벤트 요청 스키마│ ├── services/│ │ └── inference\_event\_service.py \# 추론 이벤트 비즈니스 로직│ ├── repositories/│ │ ├── user\_status\_repo.py \# user\_status 테이블 접근│ │ ├── user\_friends\_repo.py \# user\_friends 조회/갱신│ │ ├── critical\_event\_tx\_repo.py \# CRITICAL 1회 처리 트랜잭션│ │ └── outbox\_repo.py \# outbox 이벤트 저장│ ├── jobs/│ │ └── daily\_status\_sync\_job.py \# 배치 동기화 엔트리│ ├── shared/│ │ ├── ddb.py \# DynamoDB 리소스 유틸│ │ ├── sqs.py \# SQS 전송 유틸│ │ └── time.py \# 시간 변환/TTL 유틸│ ├── core/│ │ └── config.py \# 환경 설정│ └── main.py \# FastAPI 앱 \+ 스케줄러├── deploy/k8s/│ ├── deployment.yaml \# API 배포│ ├── service.yaml \# Service│ ├── serviceAccount.yaml \# IRSA용 ServiceAccount│ ├── configMap.yaml \# 환경 변수 ConfigMap│ └── cronjob-daily-status-sync.yaml \# CronJob (옵션)├── scripts/│ └── check\_ddb\_connection.py \# DynamoDB 연결 확인├── Dockerfile├── requirements.txt└── README.md |
| :---- |

③ **message\_service**

**3.2.3 DB설계**

**①  users 테이블 (RDS PostgreSQL)**

**설계 목적**: Google/Cognito Sub를 기본 키로 사용하여 외부 인증 제공자와 연동하며, 6자리 영숫자 친구 코드를 자동 생성한다. 빠른 사용자 조회를 위해 `email`과 `friend_code`에 인덱스를 적용하였다.

| 컬럼명 | 타입 | Key | 설명 |
| :---: | :---: | :---: | :---: |
| user\_id | VARCHAR(255) | PK | Google / Cognito Sub |
| email | VARCHAR(100) | UNIQUE, NOT NULL | 이메일 |
| nickname | VARCHAR(50) | NOT NULL | 닉네임 |
| profile\_image\_url | VARCHAR(500) | NULL | 프로필 이미지 URL |
| friend\_code | VARCHAR(6) | UNIQUE, NOT NULL | 친구 코드 |
| created\_at\_timestamp | BIGINT | NOT NULL | 생성 시간 (밀리초) |
| updated\_at\_timestamp | BIGINT | NOT NULL | 수정 시간 (밀리초) |
| cat\_pattern | VARCHAR(20) | NULL | 고양이 패턴 |
| cat\_color | VARCHAR(7) | NULL | 고양이 색상 (HEX) |
| duress\_code | VARCHAR(100) | NULL | 위험 신호 코드 |
| meow\_audio\_url | VARCHAR(500) | NULL | 야옹 소리 URL |
| duress\_audio\_url | VARCHAR(500) | NULL | 위험 신호 소리 URL |
| token | VARCHAR(500) | NULL | FCM 토큰 |
| provider | VARCHAR(50) | NOT NULL | 인증 제공자 |
| profile\_setup\_completed | BOOLEAN | DEFAULT FALSE | 프로필 완성 여부 |

### 

**설계 특징/효과**

* 비밀번호 관리 불필요 — Google/Cognito 외부 인증 연동

* *`email`*, *`friend_code`* 인덱스로 빠른 조회 보장

* 파일(이미지·오디오)은 S3에 저장하고 URL만 컬럼에 보관하여 DB 용량 절약

---

### **② user\_friends 테이블 (DynamoDB)**

**설계 목적**: 친구 프로필 정보를 비정규화하여 저장함으로써 로비 조회 시 단일 Query로 모든 친구 정보를 반환한다. 기존 RDS 조인 방식에서 발생하던 N+1 쿼리 문제를 1회 Query로 해소한다.

| 속성명 | 타입 | Key | 설명 |
| :---: | :---: | :---: | :---: |
| user\_id | String | PK | 사용자 ID |
| friend\_user\_id | String | SK | 친구 사용자 ID |
| status | String | \- | pending / sending / accepted |
| created\_at | Number | \- | 생성 시간 (밀리초) |
| updated\_at | Number | \- | 수정 시간 (밀리초) |
| email | String | \- | 친구 이메일 (비정규화) |
| nickname | String | \- | 친구 닉네임 (비정규화) |
| profile\_image\_url | String | \- | 친구 프로필 이미지 (비정규화) |
| cat\_pattern | String | \- | 친구 고양이 패턴 (비정규화) |
| cat\_color | String | \- | 친구 고양이 색상 (비정규화) |
| meow\_audio\_url | String | \- | 친구 야옹 소리 (비정규화) |
| duress\_code | String | \- | 친구 위험 신호 코드 (비정규화) |
| duress\_audio\_url | String | \- | 친구 위험 신호 소리 (비정규화) |
| daily\_status | String | \- | 일일 상태 (AI 추론) |

**설계 특징/효과**

* 비정규화로 로비 조회 쿼리 수 N+1 → 1회로 감소  
* 프로필 변경 시 *sync\_friend\_profiles* 호출로 DynamoDB 자동 동기화

\# 친구 요청 보내기 \- 양방향 레코드 생성 \+ 프로필 비정규화  
async def send\_friend\_request(  
    self,  
    user\_id: str,  
    friend\_user\_id: str,  
    friend\_profile: Dict\[str, Any\]  
) \-\> bool:  
    """  
    친구 요청 보내기  
    \- 양방향 레코드 생성  
    \- 프로필 정보 비정규화  
    """  
    now \= int(time.time() \* 1000)  
     
    try:  
        *\# 요청자 → 친구 (sending)*  
        self.friends\_table.put\_item(  
            Item\={  
                "user\_id": user\_id,  
                "friend\_user\_id": friend\_user\_id,  
                "status": "sending",  
                "created\_at": now,  
                "updated\_at": now,  
                *\# 친구 프로필 정보 비정규화*  
                "email": friend\_profile.get("email", ""),  
                "nickname": friend\_profile.get("nickname", ""),  
                "profile\_image\_url": friend\_profile.get("profile\_image\_url", ""),  
                "cat\_pattern": friend\_profile.get("cat\_pattern", ""),  
                "cat\_color": friend\_profile.get("cat\_color", ""),  
                "meow\_audio\_url": friend\_profile.get("meow\_audio\_url", ""),  
                "duress\_code": friend\_profile.get("duress\_code", ""),  
                "duress\_audio\_url": friend\_profile.get("duress\_audio\_url", ""),  
            }  
        )  
         
        *\# 친구 → 요청자 (pending)*  
        self.friends\_table.put\_item(  
            Item\={  
                "user\_id": friend\_user\_id,  
                "friend\_user\_id": user\_id,  
                "status": "pending",  
                "created\_at": now,  
                "updated\_at": now,  
                *\# 요청자 프로필 정보 비정규화*  
                *\# ... (동일한 구조)*  
            }  
        )  
         
        return True  
    except Exception as e:  
        logger.error(f"Failed to send friend request: {e}")  
        return False

\# 로비 조회 최적화 \- 단일 Query로 친구 정보 전체 조회  
def get\_accepted\_friends(self, user\_id: str) \-\> List\[Dict\[str, Any\]\]:  
    """  
    수락된 친구 목록 조회  
    \- 단일 Query로 모든 친구 정보 조회  
    \- RDS 조인 불필요  
    """  
    try:  
        response \= self.friends\_table.query(  
            KeyConditionExpression\=Key("user\_id").eq(user\_id),  
            FilterExpression\=Attr("status").eq("accepted")  
        )  
         
        friends \= response.get("Items", \[\])  
         
        *\# 프로필 정보 포함*  
        return \[  
            {  
                "user\_id": friend\["friend\_user\_id"\],  
                "email": friend.get("email", ""),  
                "nickname": friend.get("nickname", ""),  
                "profile\_image\_url": friend.get("profile\_image\_url", ""),  
                "cat\_pattern": friend.get("cat\_pattern", ""),  
                "cat\_color": friend.get("cat\_color", ""),  
                "meow\_audio\_url": friend.get("meow\_audio\_url", ""),  
                "duress\_code": friend.get("duress\_code", ""),  
                "duress\_audio\_url": friend.get("duress\_audio\_url", ""),  
                "daily\_status": friend.get("daily\_status", ""),  
            }  
            for friend in friends  
        \]  
    except Exception as e:  
        logger.error(f"Failed to get accepted friends: {e}")  
        return \[

프로필이 변경되면 update\_user\_profile 호출 시 sync\_friend\_profiles를 함께 실행하여 DynamoDB의 비정규화 데이터도 자동 동기화한다.

\# 프로필 업데이트 \+ DynamoDB 동기화

async def update\_user\_profile(  
    db: AsyncSession,  
    user\_id: str,  
    profile\_update: UserProfileUpdate  
) \-\> Optional\[User\]:  
    """  
    프로필 업데이트 \+ DynamoDB 동기화  
    """  
    user \= await update\_user(db, user\_id, profile\_update)  
    if not user:  
        return None  
     
    await sync\_friend\_profiles(user\_id, user)  
     
    return user   

---

### **③ Messages 테이블 (DynamoDB)**

**설계 목적:** 수신자 기준 단일 Partition 조회로 받은 쪽지함을 처리한다. `created_at` 기반 시간순 정렬을 보장한다.

| 필드명 | 타입 | Key | 설명 |
| :---: | :---: | :---: | :---: |
| pk | String | PK | 파티션 키 (수신자 기준 식별자) |
| sk | String | SK | 정렬 키 (시간 기반 또는 메시지 정렬용) |
| message\_id | String | \- | 메시지 고유 ID |
| body | String | \- | 메시지 내용 |
| from\_user\_id | String | \- | 발신자 사용자 ID |
| to\_user\_id | String | \- | 수신자 사용자 ID |
| nickname | String | \- | 발신자 닉네임 (비정규화) |
| created\_at | Number | \- | 메시지 생성 시간 (Unix Epoch ms) |

**설계 특징/효과**

* PK를 수신자 기준으로 설계하여 받은 쪽지함 단일 Query 처리  
* SK에 *`created_at`*을 포함하여 시간순 정렬 보장  
* *`nickname`* 비정규화로 발신자 조회 추가 쿼리 불필요

### **④ Hearts 테이블 (DynamoDB)**

**설계 목적**: Messages 테이블과 동일한 접근 패턴을 유지하여 받은 하트함 조회에 기능 일관성을 확보한다.

| 필드명 | 타입 | Key | 설명 |
| :---: | :---: | :---: | :---: |
| pk | String | PK | 파티션 키 (수신자 기준 식별자) |
| sk | String | SK | 정렬 키 (시간 기반 또는 이벤트 정렬용) |
| heart\_id | String | \- | 하트 고유 ID |
| from\_user\_id | String | \- | 하트를 보낸 사용자 ID |
| to\_user\_id | String | \- | 하트를 받은 사용자 ID |
| created\_at | Number | \- | 하트 생성 시간 (Unix Epoch ms) |

**설계 특징/효과**

* Messages와 동일한 PK/SK 패턴 적용으로 조회 로직 재사용 가능

* *`to_user_id`* 기준 단일 Query로 수신 하트 전체 조회

---

**⑤ DeviceTokens 테이블 (DynamoDB)**

**설계 목적**: 사용자별 디바이스 FCM 토큰을 관리한다. 다중 디바이스 확장을 고려한 구조로 설계하였다.

| 필드명 | 타입 | Key | 설명 |
| :---: | :---: | :---: | :---: |
| pk | String | PK | 파티션 키 (사용자 기준 식별자) |
| sk | String | SK | 정렬 키 (디바이스 식별자 또는 토큰 식별용) |
| user\_id | String | \- | 사용자 고유 ID |
| token | String | \- | 푸시 알림 토큰 (FCM Token) |
| platform | String | \- | 디바이스 플랫폼 (Android / iOS 등) |
| updated\_at | Number | \- | 토큰 마지막 갱신 시간 (Unix Epoch ms) |

**설계 특징/효과**

* SK를 *`TOKEN`*으로 고정하여 현재는 1기기 1토큰 구조

* 다중 디바이스 지원 시 *SK*를 디바이스 ID로 변경하여 확장 가능

---

### **⑥ OutboxEvents 테이블 (DynamoDB)**

**설계 목적**: Outbox 패턴 기반으로 메시지 저장과 알림 이벤트 발행을 하나의 트랜잭션으로 처리한다. Worker가 PENDING 이벤트만 조회하여 처리하고, 실패 시 Exponential Backoff로 자동 재시도한다.

| 필드명 | 타입 | Key | 설명 |
| :---: | :---: | :---: | :---: |
| pk | String | PK | 파티션 키 (이벤트 그룹 식별자) |
| sk | String | SK | 정렬 키 (이벤트 정렬 기준) |
| event\_id | String | \- | 이벤트 고유 ID |
| event\_type | String | \- | 이벤트 유형 (MESSAGE\_CREATED, HEART\_CREATED 등) |
| payload | Map | \- | 전송 대상 및 알림 데이터(JSON 구조) |
| status | String | \- | 이벤트 상태 (READY / PROCESSING / SENT / FAILED) |
| attempt\_count | Number | \- | 재시도 횟수 |
| created\_at | Number | \- | 이벤트 생성 시간 |
| processing\_at | Number | \- | 처리 시작 시간 |
| sent\_at | Number | \- | 전송 완료 시간 |
| next\_retry\_at | Number | \- | 다음 재시도 예정 시간 |
| last\_error | String | \- | 마지막 오류 메시지 |
| updated\_at | Number | \- | 마지막 상태 갱신 시간 |

### 

### **설계 특징/효과**

* ### *`status-index`* GSI로 Worker가 PENDING 이벤트만 효율적으로 조회

* ### Conditional Update 기반 Claim으로 분산 환경에서 중복 처리 방지

* ### 상태 전이: `PENDING → PROCESSING → SENT / FAILED`

### 

### ---

### **⑦ user\_status 테이블 (DynamoDB)**

**설계 목적:** AI 추론 결과로 산출된 사용자의 최신 일일 상태를 저장한다. 알림 발송 조건 판단 시 불필요한 재계산 없이 즉시 참조할 수 있는 캐시 역할을 한다.

| 필드명 | 타입 | Key | 설명 |
| :---: | :---: | :---: | :---: |
| user\_id | String | PK | 사용자 고유 ID |
| current\_daily\_status | String | \- | 현재 일일 상태 (행복 / 평범 / 우울 / 기절 등) |
| is\_critical | Boolean | \- | 위기 상태 여부 (True / False) |
| last\_inference\_at | Number | \- | 마지막 AI 추론 실행 시간 (Unix Epoch ms) |
| updated\_at | Number | \- | 상태 레코드 최종 수정 시간 |

**설계 특징/효과**

* 상태 판단 시 매번 추론을 재실행하지 않고 최신 결과를 즉시 조회

* *`is_critical`* 플래그로 CRITICAL 이벤트 트리거 조건 판단 단순화

---

### **⑧ critical\_contacts 테이블 (DynamoDB)**

**설계 목적:** CRITICAL 이벤트 발생 시 위기 사용자의 위치 및 알림 대상 친구 목록을 스냅샷으로 저장한다. TTL을 통해 처리 완료된 이벤트를 자동으로 삭제하여 스토리지를 관리한다.

| 필드명 | 타입 | Key | 설명 |
| :---: | :---: | :---: | :---: |
| critical\_user\_id | String | PK | 위기 이벤트 발생 사용자 ID |
| event\_id | String | SK\* | 위기 이벤트 고유 ID |
| created\_at | Number | \- | 이벤트 생성 시간 (Unix Epoch ms) |
| critical\_gps | Map/String | \- | 위기 발생 시점 GPS 정보 |
| friends | List/Map | \- | 알림 대상 친구 목록(스냅샷) |
| ttl | Number | \- | 만료 시각(Epoch seconds), TTL 삭제 기준 |

**설계 특징/효과**

* 이벤트 발생 시점의 친구 목록을 스냅샷으로 저장하여 이후 친구 관계 변경 영향 차단  
* TTL 적용으로 오래된 CRITICAL 이벤트 자동 정리, 스토리지 비용 절감

---

# **3.2.4 주요 API 기능 상세**

각 Pod의 API는 기능 / 메서드 / 엔드포인트 / 파라미터 / 설명 기준으로 정리한다.

## **1\. User Pod**

### **1.1 Users**

| 기능 | Method | Endpoint | Path / Query | Body | 설명 |
| :---: | :---: | :---: | :---: | :---: | :---: |
| 로그인 | POST | /api/v1/users/login | \- | user\_id, token(optional) | 로그인 및 FCM 토큰 저장 |
| 회원가입 | POST | /api/v1/users/signup | \- | JSON 또는 multipart | 회원가입 |
| 회원가입(multipart) | POST | /api/v1/users/signup-multipart | \- | user\_id, email, nickname, cat\_pattern, cat\_color \+ 파일 | 파일 포함 회원가입 |
| 사용자 존재 확인 | GET | /api/v1/users/check | email(query) | \- | 이메일 기반 존재 여부 |
| 프로필 조회 | GET | /api/v1/users/profile/{user\_id} | user\_id | \- | 프로필 조회 |
| 프로필 수정 | PUT | /api/v1/users/profile/{user\_id} | user\_id | JSON 또는 multipart | 프로필 수정 |
| 프로필 초기 설정 | POST | /api/v1/users/setup-profile/{user\_id} | user\_id | nickname 필수 | 최초 설정 |
| 사용자 조회 | GET | /api/v1/users/{user\_id} | user\_id | \- | 특정 사용자 조회 |
| 친구 코드 조회 | GET | /api/v1/users/friend-code-lookup/{friend\_code} | friend\_code | \- | 친구 코드 검색 |
| 전화번호 조회 | GET | /api/v1/users/phone/{user\_id} | user\_id | \- | 전화번호 조회 |
| FCM 토큰 갱신 | POST | /api/v1/users/fcm-token/{user\_id} | user\_id | token | 토큰 저장 |
| 상태 업데이트 | POST | /api/v1/users/status/{user\_id} | user\_id | status | 사용자 상태 변경 |
| 상태 조회 | GET | /api/v1/users/status/{user\_id} | user\_id | \- | 상태 조회 |

### **1.2 Friends**

| 기능 | Method | Endpoint | Body | 설명 |
| :---: | :---: | :---: | :---: | :---: |
| 받은 요청 조회 | GET | /api/v1/friends/pending/{user\_id} | \- | pending 목록 |
| 보낸 요청 조회 | GET | /api/v1/friends/sending/{user\_id} | \- | sending 목록 |
| 친구 목록 조회 | GET | /api/v1/friends/list/{user\_id} | \- | accepted 목록 |
| 친구 요청 | POST | /api/v1/friends/request | user\_id, friend\_code | 친구 요청 |
| 요청 수락 | POST | /api/v1/friends/accept | user\_id, friend\_user\_id | 요청 수락 |
| 요청 거절 | POST | /api/v1/friends/reject | user\_id, friend\_user\_id | 요청 거절 |
| 요청 취소 | POST | /api/v1/friends/cancel | user\_id, friend\_user\_id | 요청 취소 |
| 친구 삭제 | DELETE | /api/v1/friends/{user\_id}/{friend\_user\_id} | \- | 친구 관계 삭제 |

### **1.3 Upload**

| 기능 | Method | Endpoint | Body | 설명 |
| :---: | :---: | :---: | :---: | :---: |
| 프로필 이미지 업로드 | POST | /api/v1/upload/profile-image/{user\_id} | file(binary) | 이미지 업로드 |
| 야옹 음성 업로드 | POST | /api/v1/upload/meow-audio/{user\_id} | file(binary) | 음성 업로드 |
| 위험 신호 음성 업로드 | POST | /api/v1/upload/duress-audio/{user\_id} | file(binary) | 음성 업로드 |
| 파일 일괄 업로드 | POST | /api/v1/upload/batch-upload/{user\_id} | multiple files | 회원가입 시 사용 |

### **1.4 Challenges**

| 기능 | Method | Endpoint | Path / Query | Body | 설명 |
| :---: | :---: | :---: | :---: | :---: | :---: |
| 챌린지 생성 | POST | /api/v1/challenges/ | \- | challenge\_date, title, description | 관리자 |
| 날짜별 조회 | GET | /api/v1/challenges/date/{target\_date} | user\_id(optional) | \- | 특정 날짜 |
| 챌린지 제출 | POST | /api/v1/challenges/{challenge\_day\_id}/submit | \- | user\_id, image, GPS(optional) | 오늘만 제출 가능 |
| 참여 이력 | GET | /api/v1/challenges/users/{user\_id}/history | limit, offset | \- | 이력 조회 |
| 친구 제출 조회 | GET | /api/v1/challenges/date/{target\_date}/friends | user\_id | \- | 친구 이미지 |
| 지도 데이터 | GET | /api/v1/challenges/map | date, user\_id(optional) | \- | GPS 기반 |
| 다음달 생성 | POST | /api/v1/challenges/generate-next-month | \- | \- | 관리자 |

### **1.5 Quick Register**

| 기능 | Method | Endpoint | Body | 설명 |
| :---: | :---: | :---: | :---: | :---: |
| 빠른 등록 | POST | /api/v1/quick/register | nickname 필수 \+ 선택 필드 | QR 기반 등록 |
| QR 사용자 조회 | GET | /api/v1/quick/qr/{user\_id} | \- | QR 대상 조회 |

---

# **2\. Inference Status Service**

| 기능 | Method | Endpoint | Body / Query | 설명 |
| :---: | :---: | :---: | :---: | :---: |
| 크리티컬 이벤트 수신 | POST | /events/critical | event\_id, critical\_user\_id, critical\_gps, friends\[\], occurred\_at | 안전 신호 처리 |
| 일일 상태 동기화 | POST | /jobs/daily-status-sync | target\_date(query) | 하루 단위 분석 반영 |

---

# **3\. Message Service**

### **3.1 Messages**

| 기능 | Method | Endpoint | Body / Query | 설명 |
| :---: | :---: | :---: | :---: | :---: |
| 쪽지 전송 | POST | /messages | from\_user\_id, to\_user\_id, body, nickname | 쪽지 발송 |
| 받은 쪽지 조회 | GET | /messages/inbox | to\_user\_id, limit | 받은 쪽지 |

### 

### **3.2 Hearts**

| 기능 | Method | Endpoint | Body / Query | 설명 |
| ----- | ----- | ----- | ----- | ----- |
| 하트 전송 | POST | /hearts | from\_user\_id, to\_user\_id, nickname | 하트 발송 |
| 받은 하트 조회 | GET | /hearts/received | to\_user\_id, limit | 하트 목록 |

### **3.3 Device Token**

| 기능 | Method | Endpoint | Body | 설명 |
| ----- | ----- | ----- | ----- | ----- |
| 토큰 저장/갱신 | POST | /device-token | user\_id, token, platform | FCM 토큰 관리 |

**Message Service 처리 구조**

Message Service는 쓰기 우선(Write First) 전략을 채택한다. 메시지 저장과 Outbox 이벤트 생성을 *`TransactWriteItems`*로 하나의 트랜잭션으로 처리하며, Push 발송 로직은 포함하지 않는다.

| 처리 단계 | 방식 | 담당 |
| :---: | :---: | :---: |
| 메시지 저장 | 동기 | Message Service |
| 알림 전송 | 비동기 | Push Worker |

**Push Worker 역할**

* *`OutboxEvents`* 테이블에서 PENDING 이벤트 조회

* Claim 기반 이벤트 선점 (Conditional Update)

* FCM 발송 처리

* 실패 시 Exponential Backoff 재시도 (최대 8회)

---

## **3.1.5 이벤트 처리 (Lambda / SQS)**

### **Outbox 패턴**

도메인 데이터 저장 → 이벤트 기록 → 별도 프로세스가 처리하는 구조다. 메시지 저장과 이벤트 생성을 단일 트랜잭션으로 묶어 메시지만 저장되고 알림이 누락되는 상황을 방지한다.

**Message 생성 시 처리 흐름**

### 

### **이벤트 상태 전이**

### **![][image1]**

### 

### **Claim 기반 중복 방지**

*`Conditional Update`*를 사용하여 분산 Worker 환경에서도 하나의 이벤트는 하나의 Worker만 처리하도록 보장한다.

**재시도 전략 (Exponential Backoff)**

실패 시 대기 시간을 지수적으로 늘려 재시도함으로써 외부 시스템 장애 및 트래픽 폭주에 대응한다.

| 설정값 | 값 |
| :---: | :---: |
| BASE\_BACKOFF\_SECONDS | 5 |
| MAX\_BACKOFF\_SECONDS | 300 |
| MAX\_ATTEMPTS | 8 |

**효과**

* 외부 시스템 장애 대응

* 트래픽 폭주 방지

* 무한 재시도 방지

---

## **3.1.7 AI 모델 (SageMaker / 이상치 탐지 모델)**

## **3.1.8 critical agent**

**① 이벤트 기반 마이크로서비스 아키텍처 (Event-Driven Microservices Architecture)|**

* AWS EKS 기반 컨테이너 오케스트레이션

* SQS를 통한 비동기 이벤트 처리  
    
* DynamoDB를 활용한 NoSQL 데이터 저장  
    
* Amazon Bedrock을 활용한 AI 기반 의사결정

**② 메시징 계층**

메시지 큐: Amazon SQS

처리 방식: Long Polling (WaitTimeSeconds 설정)

재시도 메커니즘: Visibility Timeout 기반 자동 재처리

**③ AI 의사결정 계층**

LLM 서비스: Amazon Bedrock (Claude)

프롬프팅 기법: Context Prompting (역할, 예시, 제약조건 명시)

의사결정 로직: 친밀도, 거리, 활동 상태 기반 친구 우선순위 결정

## **3.2 전체 시스템 구성도**

## 

## **3.3 서비스 간 연계 구조**

### **3.3.1 인증 흐름**

사용자 → Cognito 인증

JWT 발급

JWT 기반 API 요청

### **3.3.2 데이터 저장 흐름**

앱 → EKS API

EKS → RDS 저장

### **3.3.2  이벤트 처리 흐름**

* 상태 변화 감지

* Lambda 트리거

* SQS 큐 전달

* 알림 서버 처리

### **3.3.4 알림 흐름**

* 백엔드 → FCM

* 사용자 디바이스 수신

### **3.3.5. AI 분석 흐름**

RDS 데이터 적재

SageMaker 이상치 탐지 수행

분석 결과 이벤트 생성

**3.3.5 CRITICAL 흐름**

SQS 이벤트 수신 → 친구 목록 조회 (친밀도 계산) 

→ GPS 기반 거리 계산 → 활동 패턴 분석 (깨어있을 확률)

→ AI 에이전트 우선순위 재평가 → OutboxEvents 이벤트 생성

→ 푸시 알림 전송 

## **3.4 서비스 주요 기능 및 구성**

## **3.4.1 클라이언트 계층(Kotlin Android)**

## **① 구글 간편 로그인 :** Cognito User Pool 생성 **![][image2]** 

**② Cognito \> App Client \> Identity Providers 세팅**

| 02-02 15:07:11.917 2090 2090 D LoginActivity: ID Token: eyJraWQiOiJ6S2xhc1dcLzF0QU5ycjJOSmVQeGFyakxKYmEybG1rOTRmN3NNaGVlTit3Yz0i  02-02 15:07:11.917 2090 2090 D LoginActivity: Refresh Token: eyJjdHkiOiJKV1QiLCJlbmMiOiJBMjU2R0NNIiwiYWxnIjoiUlNBLU9BRVAifQ.WACzKLpQW02-02 15:07:11.917 2090 2090 D LoginActivity: Token Type: Bearer 02-02 15:07:11.917 2090 2090 D LoginActivity: Expires In: 1770048431916 |
| :---- |

## 

**③ 구글 로그인 로그**

| 02-02 15:15:52.173  2705  2705 D LoginActivity: Access Token: eyJraWQiOiJjOGNNNTFhU3ViOGg2MzhZVStSaFd1ekNKckJPN3BzTnpiVVRkZFQ3OVlNP02-02 15:15:52.173  2705  2705 D LoginActivity: Token Type: Bearer02-02 15:15:52.173  2705  2705 D LoginActivity: Expires In: 177004895217302-02 15:15:52.174  2705  2705 D LoginActivity: User Sub: b4589ddc-a001-7001-77aa-c2c3f3fd6a9802-02 15:15:52.174  2705  2705 D LoginActivity: User Email: wha02068@gmail.com02-02 15:15:52.174  2705  2705 D LoginActivity: Provider: Google |
| :---- |

## 

## **④ 로그인 요청**

| // AuthorizationRequest 생성\- Cognito OAuth2 엔드포인트 설정\- identity\_provider: "Google" 파라미터 전달\- scope: "openid" (사용자 식별 정보)\- prompt: "select\_account" (계정 선택 강제) |
| :---- |

## 

## **⑤ 인증 코드 교환**

| // Authorization Code → Access Token 교환\- Cognito Token 엔드포인트 호출\- ID Token, Access Token 획득 |
| :---- |

## 

## **⑥ 사용자 정보 추출**

| // JWT ID Token 파싱\- Base64 디코딩으로 Claims 추출\- user\_sub (고유 ID), email, provider 정보 획득 |
| :---- |

## 

**⑦ 사용자 상태 확인**

| // Backend API 호출\- /api/v1/users/check: 기존 사용자 여부 확인\- 기존 사용자: /api/v1/users/{userId}로 프로필 로드 → GameActivity\- 신규 사용자: ProfileSetupActivity로 이동 |
| :---- |

**⑧ 자동 로그인**  
SharedPreferences에 user\_sueb, nickname, cat\_color, cat\_pattern저장  
앱 실행시 모든 필드 존재 여부 확인 후 자동 로그인

**⑨ 로그인 화면**  
![][image3]![][image4]

**3.4.2사용자 권한 요청 목록**  
**① 필수 권한 (사용자 동의 필요)**

PACKAGE\_USAGE\_STATS \- 앱 사용 기록 (설정에서 수동 허용)

POST\_NOTIFICATIONS \- 알림 표시

RECORD\_AUDIO \- 오디오 녹음

ACTIVITY\_RECOGNITION \- 활동 인식 (걸음 수 등)

ACCESS\_COARSE\_LOCATION \- 대략적 위치

ACCESS\_FINE\_LOCATION \- 정확한 위치

READ\_PHONE\_STATE \- 전화 상태 읽기

READ\_PHONE\_NUMBERS \- 전화번호 읽기

CALL\_PHONE \- 전화 걸기

**2\. 자동 허용 권한**

INTERNET \- 인터넷 접속

ACCESS\_NETWORK\_STATE \- 네트워크 상태 확인

ACCESS\_WIFI\_STATE \- WiFi 상태 확인

FOREGROUND\_SERVICE \- 포그라운드 서비스 실행  
포그라운드 서비스 알림 ("사용 패턴 추적 중")  
![][image5]

FOREGROUND\_SERVICE\_DATA\_SYNC \- 데이터 동기화 서비스

**3\. 수집 데이터 요약**

| 권한 | 수집 데이터 | 수집 주기 | 저장 위치 |
| ----- | ----- | ----- | ----- |
| PACKAGE\_USAGE\_STATS | 앱 사용 기록 | 1분 | AWS S3 |
| ACTIVITY\_RECOGNITION | 걸음 수 | 실시간 | AWS S3 |
| LOCATION | 위도/경도 | 1분 | AWS S3 |
| READ\_PHONE\_STATE | Cell LAC | 1분 | AWS S3 |
| RECORD\_AUDIO | 울음소리 | 사용자 녹음 시 | AWS S3, 로컬 |

**4\. 개인정보 보호**  
익명화: user\_sub (UUID)로 식별, 개인정보 미포함  
암호화: HTTPS 통신  
최소 수집: 이상치 분석에 필요한 데이터만 수집  
투명성: 권한 요청 시 상세 설명 제공  
사용자 제어: 권한 거부 가능 (앱 사용은 가능)

**3.4.3 사용자 행동 패턴 수집**

| // UsageTrackingService.kt \- 포그라운드 서비스로 백그라운드 추적class UsageTrackingService : *Service*() {    private lateinit var sensorDataCollector: SensorDataCollector        override fun onCreate() {        sensorDataCollector \= SensorDataCollector(this)        sensorDataCollector.startCollecting()        startForeground(1, createNotification()) // 포그라운드 서비스 시작        handler.post(collectRunnable) // 1분마다 수집    }}// SensorDataCollector.kt \- 센서 데이터 수집class SensorDataCollector : *SensorEventListener*, *LocationListener {*    fun startCollecting() {        // 1\. 걸음 수 (TYPE\_STEP\_COUNTER)        sensorManager.registerListener(this, stepCounter, SENSOR\_DELAY\_NORMAL)                // 2\. 위치 정보 (LocationManager)        locationManager.requestLocationUpdates(NETWORK\_PROVIDER, 60000, 0f, this)                // 3\. 통화 패턴 (TelephonyManager)        telephonyManager.cellLocation // LAC/TAC 값    }} |
| :---- |

**3.4.4 프로필 설정**  
사진을 찍어서 개인화된 프로필 사진 생성  
닉네임, 고양이 울음소리, 본인 인증 음성, 고양이 색깔 설정  
**![][image6]**![][image7]

**3.4.5 친구 관리**

## 친구 코드 기반 친구 추가

## 친구 요청 수락/거절

## 친구 목록 관리

## 

## **실시간 업데이트**

## \- 요청 수락 시: loadRequests() \+ loadFriends() 호출

## \- 요청 거절 시: loadRequests() 호출

## \- 친구 추가 시: loadSentRequests() 호출

## \- RecyclerView.notifyDataSetChanged()로 UI 갱신

##  **코루틴 활용**

| // 비동기 네트워크 통신CoroutineScope(Dispatchers.IO).launch {    // API 호출    withContext(Dispatchers.Main) {        // UI 업데이트    }} |
| :---- |

##  **3.4.6 챌린지**

## **3.4.7 푸시 알림 수신 및 표시**

| // MyFirebaseMessagingService.ktclass MyFirebaseMessagingService : *FirebaseMessagingService*() {        override fun onMessageReceived(message: *RemoteMessage*) {        val data \= message.data                // 1\. FCM 데이터 파싱        val dataStr \= data\["data"\]        val innerJson \= JSONObject(dataStr)        val eventType \= innerJson.optString("event\_type")        val payloadJson \= JSONObject(innerJson.optString("payload"))        val nickname \= payloadJson.getJSONObject("data").optString("nickname")                // 2\. CRITICAL 알림 표시        if (eventType \== "CRITICAL\_PUSH") {            showCriticalNotification(nickname, phoneNumber)        }    }        private fun showCriticalNotification(name: *String*, phone: *String*) {        val notification \= NotificationCompat.Builder(this, "critical\_channel")            .setContentTitle("🚨 긴급 상황 발생")            .setContentText("$name 님이 위험합니다\!")            .setPriority(NotificationCompat.PRIORITY\_MAX)            .build()                notificationManager.notify(id, notification)    }} |
| :---- |

![][image8]

## 

**3.4.2 백엔드**

## **회원가입 및 로그인**

Google 인증 연동  
**설계 목적**

- 외부 인증 제공자 연동  
- 중복 없는 친구 코드 생성  
- FCM 토큰 자동 저장

**설계 효과**

- 비밀번호 관리 불필요  
- 보안 강화

async def create\_user\_from\_signup(  
    db: AsyncSession,  
    user\_data: UserSignup  
) \-\> User:  
    """  
    회원가입 처리  
    \- Google/Cognito Sub를 user\_id로 사용  
    \- 친구 코드 자동 생성  
    \- FCM 토큰 저장  
    """  
    now \= User.current\_timestamp()  
     
    *\# 친구 코드 생성 (중복 확인)*  
    friend\_code \= User.generate\_friend\_code()  
    while await get\_user\_by\_friend\_code(db, friend\_code):  
        friend\_code \= User.generate\_friend\_code()  
     
    *\# 사용자 생성*  
    user \= User(  
        user\_id\=user\_data.user\_id,  *\# Google/Cognito Sub*  
        email\=user\_data.email,  
        nickname\=user\_data.nickname,  
        friend\_code\=friend\_code,  
        created\_at\_timestamp\=now,  
        updated\_at\_timestamp\=now,  
        cat\_pattern\=user\_data.cat\_pattern,  
        cat\_color\=user\_data.cat\_color,  
        token\=user\_data.token,  *\# FCM 토큰*  
        provider\=user\_data.provider or "google",  
        profile\_setup\_completed\=False  
    )  
     
    db.add(user)  
    await db.commit()  
    await db.refresh(user)  
     
    return user

## **친구 시스템**

3단계 친구 요청 시스템  
**설계 목적** 

* 명확한 친구 요청 상태 관리  
* 양방향 관계 보장  
* 프로필 정보 즉시 조회 가능

**설계 효과**

* 친구 요청 취소 가능  
* 친구 요청 거절 가능  
* 로비 조회 성능 최적화

**성능 비교**  
기존 방식( RDS 조인 ) 

1. RDS Query : 친구 ID 목록 조회  
2. RDS Query : 각 친구 프로필 조회 (n회)

	\-\> 총 N \+ 1 쿼리  
현재 방식 ( 비정규화 )

1. DynamoDB Query : 친구 정보 \+ 프로필 한번에 조회

	\-\> 총 1 쿼리

class DynamoDBService:  
    def \_\_init\_\_(self):  
        self.dynamodb \= boto3.resource('dynamodb', region\_name\=settings.AWS\_REGION)  
        self.friends\_table \= self.dynamodb.Table('user\_friends')  
     
    async def send\_friend\_request(  
        self,  
        user\_id: str,  
        friend\_user\_id: str,  
        user\_profile: Dict\[str, Any\],  
        friend\_profile: Dict\[str, Any\]  
    ) \-\> bool:  
        """  
        친구 요청 보내기  
        \- 양방향 레코드 생성  
        \- 프로필 정보 비정규화  
        """  
        now \= int(time.time() \* 1000)  
         
        try:  
            *\# 요청자 → 친구 (sending)*  
            self.friends\_table.put\_item(  
                Item\={  
                    "user\_id": user\_id,  
                    "friend\_user\_id": friend\_user\_id,  
                    "status": "sending",  
                    "created\_at": now,  
                    "updated\_at": now,  
                    "email": friend\_profile.get("email", ""),  
                    "nickname": friend\_profile.get("nickname", ""),  
                    "profile\_image\_url": friend\_profile.get("profile\_image\_url", ""),  
                    "cat\_pattern": friend\_profile.get("cat\_pattern", ""),  
                    "cat\_color": friend\_profile.get("cat\_color", ""),  
                }  
            )  
             
            *\# 친구 → 요청자 (pending)*  
            self.friends\_table.put\_item(  
                Item\={  
                    "user\_id": friend\_user\_id,  
                    "friend\_user\_id": user\_id,  
                    "status": "pending",  
                    "created\_at": now,  
                    "updated\_at": now,  
                    "email": user\_profile.get("email", ""),  
                    "nickname": user\_profile.get("nickname", ""),  
                    "profile\_image\_url": user\_profile.get("profile\_image\_url", ""),  
                    "cat\_pattern": user\_profile.get("cat\_pattern", ""),  
                    "cat\_color": user\_profile.get("cat\_color", ""),  
                }  
            )  
             
            return True  
        except Exception as e:  
            logger.error(f"Failed to send friend request: {e}")  
            return False

*   
    
  **고양이 카페 시스템**

def get\_accepted\_friends(self, user\_id: str) \-\> List\[Dict\[str, Any\]\]:  
    """  
    수락된 친구 목록 조회  
    \- 단일 Query로 모든 친구 정보 조회  
    \- RDS 조인 불필요  
    """  
    try:  
        response \= self.friends\_table.query(  
            KeyConditionExpression\=Key("user\_id").eq(user\_id),  
            FilterExpression\=Attr("status").eq("accepted")  
        )  
         
        friends \= response.get("Items", \[\])  
         
        *\# 프로필 정보가 이미 포함되어 있음*  
        return \[  
            {  
                "user\_id": friend\["friend\_user\_id"\],  
                "email": friend.get("email", ""),  
                "nickname": friend.get("nickname", ""),  
                "profile\_image\_url": friend.get("profile\_image\_url", ""),  
                "cat\_pattern": friend.get("cat\_pattern", ""),  
                "cat\_color": friend.get("cat\_color", ""),  
                "meow\_audio\_url": friend.get("meow\_audio\_url", ""),  
                "duress\_code": friend.get("duress\_code", ""),  
                "duress\_audio\_url": friend.get("duress\_audio\_url", ""),  
                "daily\_status": friend.get("daily\_status", ""),  
            }  
            for friend in friends  
        \]  
    except Exception as e:  
        logger.error(f"Failed to get accepted friends: {e}")  
        return \[\]

## 

**3.4.6 agent**

## 위급 상황에서 AI가 친밀도, 거리, 활동 패턴을 종합 분석하여 가장 빠르게 도움을 줄 수 있는 친구를 자동으로 선정하고 알림을 전송하는 생명 안전 서비스

**① 위급 상황 자동 감지 및 대응**  
36시간 연락 두절 감지 시 자동으로 주변 친구들에게 알림 전송

SQS를 통해 위급 상황 이벤트 수신

사용자의 마지막 활동 시간 기준으로 연락 두절 판단

생명에 위험이 있을 수 있는 상황으로 간주하여 즉각 대응  
전체 처리 흐름 오케스트레이션

| def handle\_critical\_event(event: Dict\[str, Any\]) \-\> None:    """    1\. 현재 CRITICAL 상태 확인    2\. 친구 목록 조회    3\. 친밀도 기반 1차 정렬    4\. 거리 및 깨어있을 확률 반영    5\. AI 에이전트 재랭킹    6\. 순위 기반 알림 전송    """    event\_id \= event.get("event\_id")    user\_id \= event.get("critical\_user\_id") or event.get("user\_id")    occurred\_at \= event.get("occurred\_at")    \# 1\. 친구 목록 조회 (친밀도 기준)    friends\_ranked \= get\_friends\_by\_intimacy(user\_id)    if not friends\_ranked:        return    \# 2\. CRITICAL 위치 및 친구 위치 정보 조회    critical\_gps \= None    friends\_gps\_map \= {}    if user\_id and event\_id:        contact \= get\_critical\_contact(user\_id, event\_id)        if contact:            critical\_gps \= contact.get("critical\_gps")            for friend in contact.get("friends", \[\]):                friend\_id \= friend.get("friend\_user\_id")                friend\_gps \= friend.get("friend\_gps")                if friend\_id and friend\_gps:                    friends\_gps\_map\[friend\_id\] \= friend\_gps    \# 친구 객체에 GPS 정보 주입    for friend in friends\_ranked:        friend\_id \= friend.get("friend\_user\_id")        if friend\_id in friends\_gps\_map:            friend\["friend\_gps"\] \= friends\_gps\_map\[friend\_id\]    \# 3\. 거리 계산    friends\_with\_distance \= add\_distance\_to\_friends(        critical\_gps,        friends\_ranked    )    \# 4\. 깨어있을 확률 반영    awake\_probs \= get\_awake\_probabilities(user\_id, occurred\_at)    friends\_with\_awake \= add\_awake\_probability\_to\_friends(        friends\_with\_distance,        awake\_probs    )    \# 5\. AI 에이전트 기반 재랭킹 (Fallback 포함)    try:        friends\_reranked \= rank\_friends\_with\_agent(            user\_id,            friends\_with\_awake,            event        )    except Exception:        friends\_reranked \= sorted(            friends\_with\_awake,            key\=lambda x: (                \-x.get("intimacy", 0),                x.get("distance\_km", float("inf"))            )        )    \# 6\. 최종 알림 전송    send\_critical\_notifications\_batch(user\_id, friends\_reranked) |
| :---- |

2\. AI 기반 최적 구조자 선정  
Amazon Bedrock(Claude)을 활용한 지능형 친구 우선순위 결정

친밀도 분석: Hearts, Messages 테이블 데이터 기반 친구 관계 점수 계산

거리 계산: GPS 좌표 기반 물리적 거리 측정 (Haversine 공식)

활동 패턴 분석: 시간대별 깨어있을 확률 예측

종합 평가: AI가 3가지 요소를 종합하여 가장 빠르게 도움을 줄 수 있는 친구 5명 선정  
AI의사 결정 로직

| \# agent.pyimport jsonimport boto3from typing import List, Dict, Anyfrom .settings import settingsbedrock \= boto3.client("bedrock-runtime", region\_name=settings.aws\_region)def rank\_friends\_with\_agent(    user\_id: str,    friends: List\[Dict\[str, Any\]\],    event: Dict\[str, Any\]) \-\> List\[Dict\[str, Any\]\]:    """    LLM 기반 친구 우선순위 재결정 (Context Prompting 적용)    \- 입력: 1차 정렬된 친구 목록(친밀도 등 기본 정보 포함), 이벤트 컨텍스트    \- 처리: 역할/평가기준/제약조건을 포함한 프롬프트로 LLM 추론 수행    \- 출력: LLM이 선택한 nickname 순서대로 친구 리스트 재정렬    """    \# LLM 입력 데이터는 핵심 feature만 요약하여 전달 (토큰/노이즈 절감)    friends\_summary: List\[Dict\[str, Any\]\] \= \[\]    for f in friends\[:10\]:  \# 상위 N명만 요약        friends\_summary.append({            "nickname": f.get("nickname"),            "intimacy": f.get("intimacy"),            "distance\_km": f.get("distance\_km"),            "awake\_probability": f.get("awake\_probability"),            "status": f.get("status"),            "daily\_status": f.get("daily\_status"),        })    prompt \= \_build\_prompt(        user\_id=user\_id,        occurred\_at=event.get("occurred\_at"),        friends\_summary=friends\_summary,    )    raw\_text \= \_invoke\_bedrock(prompt)    decision \= \_parse\_agent\_decision(raw\_text)    ranked\_nicknames \= decision.get("ranked\_friends", \[\])    return \_rerank\_by\_nicknames(friends, ranked\_nicknames)def \_build\_prompt(user\_id: str, occurred\_at: Any, friends\_summary: List\[Dict\[str, Any\]\]) \-\> str:    """역할/상황/평가기준/출력 포맷/제약조건을 포함한 Context Prompt 템플릿 구성"""    return f"""당신은 위급 상황 대응 전문가로, 연락이 두절된 사람을 도울 최적의 친구를 선택합니다.\#\# 역할 (Role)\- 위급 상황 대응 AI 에이전트\- 친밀도, 거리, 활동 상태를 종합 분석하여 가장 빠르고 효과적으로 도움 가능한 친구를 선정\#\# 상황 (Context)\- 사용자 ID: {user\_id}\- 위급 사유: 36시간 동안 휴대폰 로그 없음 (연락 두절 의심)\- 발생 시각: {occurred\_at}\- 심각도: 매우 높음\#\# 친구 목록 (Data){json.dumps(friends\_summary, ensure\_ascii=False, indent=2)}\#\# 평가 기준 (Criteria)1\) 친밀도(intimacy): 높을수록 좋음2\) 거리(distance\_km): 가까울수록 좋음3\) 깨어있을 확률(awake\_probability): 높을수록 좋음4\) 활동 상태(status): ACTIVE 선호5\) 일상 상태(daily\_status): 활동적일수록 선호\#\# 출력 형식 (Output Format)\- 반드시 JSON만 출력:{{"ranked\_friends": \["nickname1", "nickname2", "nickname3"\], "reasoning": "선택 이유"}}\#\# 제약조건 (Constraints)\- 반드시 JSON 형식으로만 응답\- 최소 3명, 최대 5명 선택\- reasoning은 1\~2문장으로 간결하게""".strip()def \_invoke\_bedrock(prompt: str) \-\> str:    """Bedrock 호출 후 LLM 텍스트 결과 반환"""    response \= bedrock.invoke\_model(        modelId=settings.bedrock\_model\_id,        body=json.dumps({            "anthropic\_version": "bedrock-2023-05-31",            "max\_tokens": 1000,            "messages": \[{"role": "user", "content": prompt}\],        })    )    payload \= json.loads(response\["body"\].read())    \# Claude 계열 응답 형태를 가정: content\[0\].text    return payload\["content"\]\[0\]\["text"\]def \_parse\_agent\_decision(text: str) \-\> Dict\[str, Any\]:    """    LLM 출력(JSON)을 파싱하여 의사결정 결과 반환    (보고서용으로는 단순 파싱만 유지)    """    return json.loads(text)def \_rerank\_by\_nicknames(    friends: List\[Dict\[str, Any\]\],    ranked\_nicknames: List\[str\]) \-\> List\[Dict\[str, Any\]\]:    """LLM이 선택한 nickname 순서대로 원본 friends를 재정렬"""    friends\_by\_nickname \= {f.get("nickname"): f for f in friends}    reranked \= \[friends\_by\_nickname\[n\] for n in ranked\_nicknames if n in friends\_by\_nickname\]    return reranked |
| :---- |

**③ 다단계 알림 시스템**  
Transactional Outbox 패턴 기반 안정적인 푸시 알림

OutboxEvents 테이블에 알림 이벤트 저장

우선순위 순서대로 최대 5명의 친구에게 알림 전송

알림 내용: 발신자 정보(전화번호, 닉네임), 위급 상황 정보

실패 시 자동 재시도 메커니즘  
푸시알람 클릭시 전화 권한이 있으면 즉시 전화 발신

**④ 실시간 위치 기반 서비스**  
GPS 좌표를 활용한 지리적 근접성 평가

critical\_contacts 테이블에서 위급 상황 발생 위치 조회

각 친구의 마지막 위치 정보와 비교

거리(km) 계산 후 우선순위 결정에 반영

가까운 친구일수록 물리적 도움 가능성 높음

**⑤ 시간 기반 응답 가능성 예측**  
사용자 활동 패턴 분석을 통한 즉각 응답 가능성 판단

시간대별 활동 이력 분석

깨어있을 확률(awake\_probability) 계산

현재 활동 상태(ACTIVE/INACTIVE) 고려

즉각 응답 가능한 친구 우선 선정

**⑥ 비동기 이벤트 처리**  
CRITICAL 이벤트는 SQS에 적재되며, Worker가 Long Polling으로 수신  
메시지는 성공적으로 처리된 경우에만 삭제되어,  
위급 상황 이벤트가 유실되지 않도록 At-least-once 처리를 보장

| \# worker.pyimport jsonimport astimport timeimport threadingfrom typing import Optionalimport boto3from botocore.exceptions import ClientErrorfrom .settings import settingsfrom .handlers import handle\_critical\_event\_stop\_event \= threading.Event()def stop\_worker() \-\> None:    """워커 종료 신호"""    \_stop\_event.set()def worker\_loop() \-\> None:    """    SQS 메시지를 Long Polling으로 수신하여    CRITICAL 이벤트를 처리하는 Worker 루프.    \- 메시지 처리 성공 시 삭제    \- 처리 실패 시 삭제하지 않음 (Visibility Timeout 기반 재시도)    """    sqs \= boto3.client("sqs", region\_name=settings.aws\_region)    while not \_stop\_event.is\_set():        try:            response \= sqs.receive\_message(                QueueUrl=settings.sqs\_queue\_url,                MaxNumberOfMessages=settings.max\_messages,                WaitTimeSeconds=settings.wait\_time\_seconds,                VisibilityTimeout=settings.visibility\_timeout,                MessageAttributeNames=\["All"\],                AttributeNames=\["All"\],            )            messages \= response.get("Messages", \[\])            if not messages:                continue            for message in messages:                receipt\_handle \= message\["ReceiptHandle"\]                body \= message.get("Body", "")                try:                    event \= \_parse\_message\_body(body)                    \# 핵심 비즈니스 로직 실행                    handle\_critical\_event(event)                    \# 성공적으로 처리된 경우에만 삭제                    sqs.delete\_message(                        QueueUrl=settings.sqs\_queue\_url,                        ReceiptHandle=receipt\_handle                    )                except (json.JSONDecodeError, ValueError, SyntaxError):                    \# 형식 오류 메시지는 재처리 의미 없으므로 즉시 삭제                    sqs.delete\_message(                        QueueUrl=settings.sqs\_queue\_url,                        ReceiptHandle=receipt\_handle                    )                except Exception:                    \# 처리 실패 시 삭제하지 않음 → Visibility Timeout 후 재시도                    pass        except ClientError:            time.sleep(2)        except Exception:            time.sleep(2)def \_parse\_message\_body(body: str) \-\> dict:    """    SQS 메시지 Body를 안전하게 파싱.    \- JSON 형식 우선    \- Python dict 문자열 fallback    """    try:        return json.loads(body)    except json.JSONDecodeError:        return ast.literal\_eval(body)def start\_worker\_thread() \-\> threading.Thread:    """백그라운드 워커 스레드 시작"""    thread \= threading.Thread(target=worker\_loop, daemon=True)    thread.start()    return thread |
| :---- |

**⑦ 장애 복구 및 재시도**  
다층 안전장치를 통한 높은 신뢰성 보장

AI 평가 실패 시 규칙 기반 알고리즘으로 폴백

SQS 메시지 재처리 메커니즘

OutboxEvents 기반 알림 재전송

상세한 로깅을 통한 문제 추적

**3.4.7 음성 인식을 통한 본인 인증**  
**고양이가 기절하면 본인인증을 통해서 기절 상태를 해제할 수 있다.**  
**구현중**

## **3.5 API 설계 및 데이터 흐름** **회원가입**

| @router.post("/signup", response\_model=UserResponse)async def signup(    user\_data: UserSignup,    db: AsyncSession \= Depends(get\_db)):    """    회원가입    \- Google/Cognito Sub를 user\_id로 사용    \- FCM 토큰 자동 저장    \- 친구 코드 자동 생성    """    \# 이메일 중복 확인    existing\_user \= await user\_service.get\_user\_by\_email(db, user\_data.email)    if existing\_user:        raise HTTPException(status\_code=400, detail="Email already registered")       \# 사용자 생성    user \= await user\_service.create\_user\_from\_signup(db, user\_data)       return UserResponse(        success=True,        message="User created successfully",        data=user    )\*\*요청 예시\*\*{  "user\_id": "google-oauth2|123456789",  "email": "user@example.com",  "nickname": "고양이집사",  "cat\_pattern": "solid",  "cat\_color": "\#FF6B6B",  "token": "fcm\_token\_here"}\*\*응답 예시\*\*{  "success": true,  "message": "User created successfully",  "data": {    "user\_id": "google-oauth2|123456789",    "email": "user@example.com",    "nickname": "고양이집사",    "friend\_code": "ABC123",    "profile\_setup\_completed": false  }}로그인 (로비 포함)@router.post("/login", response\_model=LoginResponse)async def login(    login\_data: LoginRequest,    db: AsyncSession \= Depends(get\_db)):    """    로그인    \- 사용자 정보 조회    \- FCM 토큰 업데이트    \- 친구 목록 자동 조회 (로비)    """    \# 사용자 조회    user \= await user\_service.get\_user\_by\_id(db, login\_data.user\_id)    if not user:        raise HTTPException(status\_code=404, detail="User not found")       \# FCM 토큰 업데이트    if login\_data.token:        await user\_service.update\_user(            db,            login\_data.user\_id,            UserUpdate(token=login\_data.token)        )       \# 친구 목록 조회    friends \= dynamodb\_service.get\_accepted\_friends(login\_data.user\_id)       return LoginResponse(        success=True,        message="Login successful",        user=user,        friends=friends    ) |
| :---- |

\*\*요청 예시\*\*  
POST /api/v1/users/login  
{  
  "user\_id": "google-oauth2|123456789",  
  "token": "new\_fcm\_token\_here"  
}

\*\*응답 예시\*\*  
{  
  "success": true,  
  "message": "Login successful",  
  "user": {  
    "user\_id": "google-oauth2|123456789",  
    "email": "user@example.com",  
    "nickname": "고양이집사",  
    "friend\_code": "ABC123"  
  },  
  "friends": \[  
    {  
      "user\_id": "google-oauth2|987654321",  
      "nickname": "친구1",  
      "profile\_image\_url": "https://...",  
      "cat\_pattern": "solid",  
      "cat\_color": "\#FFA500"  
    }  
  \]  
}

### **친구 관리 API**

친구 요청 방식은 3단계 요청 방식

**상태정의**

* sending : 친구 요청을 보낸 상태  
* pending : 친구 요청을 받은 상태  
* accepted : 친구 요청이 수락된 상태

**상태전이도**  
**\[사용자 A\]                    \[사용자 B\]**  
    **│                             │**  
    **│ send\_friend\_request()       │**  
    **├──────────────────────────\>  │**  
    **│ status: sending             │ status: pending**  
    **│                             │**  
    **│                             │ accept\_friend\_request()**  
    **│ \<────────────────────────── │**  
    **│ status: accepted            │ status: accepted**

**친구 요청 송신**  
@router.post("/request", response\_model\=FriendResponse)  
async def send\_friend\_request(  
    request\_data: FriendRequest,  
    db: AsyncSession \= Depends(get\_db)  
):  
    """  
    친구 요청 보내기  
    \- 친구 코드로 사용자 검색  
    \- 양방향 레코드 생성 (sending/pending)  
    \- 프로필 정보 비정규화  
    """  
    *\# 친구 코드로 사용자 검색*  
    friend \= await user\_service.get\_user\_by\_friend\_code(  
        db,  
        request\_data.friend\_code  
    )  
    if not friend:  
        raise HTTPException(status\_code\=404, detail\="Friend code not found")  
     
    *\# 자기 자신에게 요청 방지*  
    if friend.user\_id \== request\_data.user\_id:  
        raise HTTPException(status\_code\=400, detail\="Cannot add yourself")  
     
    *\# 요청자 정보 조회*  
    user \= await user\_service.get\_user\_by\_id(db, request\_data.user\_id)  
    if not user:  
        raise HTTPException(status\_code\=404, detail\="User not found")  
     
    *\# DynamoDB에 친구 요청 생성*  
    success \= await dynamodb\_service.send\_friend\_request(  
        user\_id\=request\_data.user\_id,  
        friend\_user\_id\=friend.user\_id,  
        user\_profile\=user.\_\_dict\_\_,  
        friend\_profile\=friend.\_\_dict\_\_  
    )  
     
    if not success:  
        raise HTTPException(status\_code\=500, detail\="Failed to send friend request")  
     
    return FriendResponse(  
        success\=True,  
        message\="Friend request sent"  
    )  
\`\`\`

\*\*요청 예시\*\*  
POST /api/v1/friends/request  
{  
  "user\_id": "google-oauth2|123456789",  
  "friend\_code": "ABC123"  
}

**친구 요청 수락**  
@router.post("/accept", response\_model\=FriendResponse)  
async def accept\_friend\_request(  
    accept\_data: FriendAccept,  
    db: AsyncSession \= Depends(get\_db)  
):  
    """  
    친구 요청 수락  
    \- pending → accepted  
    \- 상대방 sending → accepted  
    """  
    success \= await dynamodb\_service.accept\_friend\_request(  
        user\_id\=accept\_data.user\_id,  
        friend\_user\_id\=accept\_data.friend\_user\_id  
    )  
     
    if not success:  
        raise HTTPException(status\_code\=500, detail\="Failed to accept friend request")  
     
    return FriendResponse(  
        success\=True,  
        message\="Friend request accepted"  
    )

\*\*DynamoDB 구현\*\*  
*\# services/user\_service/app/services/dynamodb\_service.py*

async def accept\_friend\_request(  
    self,  
    user\_id: str,  
    friend\_user\_id: str  
) \-\> bool:  
    """  
    친구 요청 수락  
    \- 양방향 상태 업데이트 (pending/sending → accepted)  
    """  
    now \= int(time.time() \* 1000)  
     
    try:  
        *\# 요청 받은 사람: pending → accepted*  
        self.friends\_table.update\_item(  
            Key\={  
                "user\_id": user\_id,  
                "friend\_user\_id": friend\_user\_id  
            },  
            UpdateExpression\="SET \#status \= :accepted, updated\_at \= :now",  
            ExpressionAttributeNames\={  
                "\#status": "status"  
            },  
            ExpressionAttributeValues\={  
                ":accepted": "accepted",  
                ":now": now  
            }  
        )  
         
        *\# 요청 보낸 사람: sending → accepted*  
        self.friends\_table.update\_item(  
            Key\={  
                "user\_id": friend\_user\_id,  
                "friend\_user\_id": user\_id  
            },  
            UpdateExpression\="SET \#status \= :accepted, updated\_at \= :now",  
            ExpressionAttributeNames\={  
                "\#status": "status"  
            },  
            ExpressionAttributeValues\={  
                ":accepted": "accepted",  
                ":now": now  
            }  
        )  
         
        return True  
    except Exception as e:  
        logger.error(f"Failed to accept friend request: {e}")  
        return False

**친구 목록 조회**  
@router.get("/pending/{user\_id}", response\_model\=FriendsListResponse)  
async def get\_pending\_requests(user\_id: str):  
    """받은 친구 요청 목록 (status: pending)"""  
    friends \= dynamodb\_service.get\_pending\_requests(user\_id)  
    return FriendsListResponse(  
        success\=True,  
        message\="Pending requests retrieved",  
        friends\=friends  
    )

@router.get("/sending/{user\_id}", response\_model\=FriendsListResponse)  
async def get\_sending\_requests(user\_id: str):  
    """보낸 친구 요청 목록 (status: sending)"""  
    friends \= dynamodb\_service.get\_sending\_requests(user\_id)  
    return FriendsListResponse(  
        success\=True,  
        message\="Sending requests retrieved",  
        friends\=friends  
    )

@router.get("/list/{user\_id}", response\_model\=FriendsListResponse)  
async def get\_friends\_list(user\_id: str):  
    """친구 목록 (status: accepted)"""  
    friends \= dynamodb\_service.get\_accepted\_friends(user\_id)  
    return FriendsListResponse(  
        success\=True,  
        message\="Friends list retrieved",  
        friends\=friends  
    )

##  

## **3.6 CI/CD 구축 전략**

## **3.7 인프라 아키텍처**

## **3.8 클라우드 인프라 구성** **3.9 네트워크 구성 (로드 밸런싱, VPC, 서브넷)**

## **3.10 고가용성 및 확장성 설계 (Auto Scaling, Multi-Region)**

## **3.11 보안 및 접근 제어 정책 (IAM, 보안 그룹, WAF 등)**

## **3.11.1 API Gateway → Lambda → Kinesis Data Firehose**

본 프로젝트에서는 **모바일 클라이언트에서 수집되는 로그 데이터**를 안전하게 저장하기 위해  
 Mobile Client → API Gateway → Lambda → Kinesis Data Firehose → Amazon S3 구조를 사용하였다.  
 아래 Lambda 함수는 **외부 요청이 내부 데이터 레이크로 유입되기 직전의 보안 관문(Security Gate)** 역할을 수행한다.

본 설계는 데이터의 **무결성(Integrity), 기밀성(Confidentiality), 가용성(Availability)** 확보를 목표로 한다.

**① 요청 추적성 확보 (Request Traceability)**

**보안 효과**

* 로그 위·변조 탐지  
* 침해 사고 분석(Forensics) 시 핵심 식별자 제공  
* Firehose, CloudWatch Logs와 연계한 엔드투엔드 추적 가능

| request\_id \= context.aws\_request\_id |
| :---- |

**② Header 기반 인증 (API Key Authentication)**

| api\_key \= (    headers.get("x-api-key")    or headers.get("X-Api-Key")    or headers.get("X-API-KEY"))if api\_key \!= EXPECTED\_API\_KEY:    return response(403, {"error": "Forbidden"}) |
| :---- |

**보안 효과**

* 무작위 스캐닝 및 악성 트래픽 차단  
* 내부 데이터 레이크 오염 방지  
* API Key는 환경 변수로 관리하여 코드 노출 시에도 키 유출 방지

**③ Base64 디코딩 검증 (Transport Layer Safety)**

**보안 효과**

* 깨진 데이터, 인젝션 시도 조기 차단  
* 인코딩 오류로 인한 Lambda 장애 방지 (가용성 확보)  
* Firehose에 비정상 데이터가 적재되는 것을 사전 차단

| if event.get("isBase64Encoded"):    raw\_body \= base64.b64decode(raw\_body).decode("utf-8") |
| :---- |

**④ JSON 파싱 및 입력값 검증 (Input Validation)**

**보안 효과**

* JSON Injection, 비정형 데이터 공격 방지  
* 데이터 카탈로그/ETL 파이프라인 깨짐 방지  
* S3 적재 후 Glue, Athena 분석 단계에서 오류 확산 방지

| body \= json.loads(raw\_body) |
| :---- |

**⑤ 이벤트 정규화 (Payload Normalization)**

허용하는 Payload 유형

1. **{ "events": \[...\] }** (배치 전송)  
2. { "event": "...", ... } (단건)  
   \[ {...}, {...} \] (모바일 SDK 기본)

**보안 효과**

* 스키마 불일치로 인한 데이터 품질 저하 방지  
* 분석 단계에서 조건 분기 감소 → 보안 사고 표면 축소  
* 의도치 않은 대용량 데이터 폭탄 공격 방지

| def normalize\_events(body: Any) \-\> List\[Dict\[str, Any\]\]: |
| :---- |

**⑥ 이벤트 수 제한 (Rate / Volume Control)**

**보안 효과**

* Lambda 메모리 및 Firehose 처리량 보호  
* S3 저장 비용 예측 가능성 확보  
* 안정적인 데이터 수집 파이프라인 유지

| MAX\_EVENTS \= 500if len(events) \> MAX\_EVENTS:    return response(413, {"error": "Too many events"}) |
| :---- |

**⑦ Firehose 전송 시 예외 처리 (Fault Isolation)**

**보안 효과**

* Firehose 장애가 API 전체 장애로 확산되는 것을 방지  
* 실패 요청은 로그로 남겨 사후 분석 가능  
* 데이터 손실 여부를 명확히 식별 가능

| firehose.put\_record\_batch(...)except Exception as e:    return response(500, {"error": "Firehose delivery failed"}) |
| :---- |

**⑧ 부분 실패 감지 (Partial Failure Awareness)**

**보안 효과**

* 데이터 무결성(Integirty) 보장  
* 장애 은닉(Silent Failure) 방지  
* 운영 환경에서 신뢰 가능한 데이터 파이프라인 유지

| failed\_count \= firehose\_response.get("FailedPutCount", 0\) |
| :---- |

**⑨ 로그 최소화 원칙 (Secure Logging)**

**보안 효과**

* CloudWatch 로그 자체가 새로운 보안 리스크가 되는 상황 방지  
* GDPR, 개인정보 보호 관점에서 안전한 로깅 설계

| "raw\_body": raw\_body\[:300\] |
| :---- |

| import jsonimport boto3import osimport base64import loggingfrom typing import Any, Dict, List\# \===============================\# 기본 설정\# \===============================logger \= logging.getLogger()logger.setLevel(logging.INFO)firehose \= boto3.client("firehose")DELIVERY\_STREAM\_NAME \= os.environ\["DELIVERY\_STREAM\_NAME"\]EXPECTED\_API\_KEY \= os.environ\["EXPECTED\_API\_KEY"\]\# 🔥 누락되어 있던 상수 (필수)MAX\_EVENTS \= 500\# \===============================\# 공통 응답 함수\# \===============================def response(status\_code: int, body: Any) \-\> Dict\[str, Any\]:    return {        "statusCode": status\_code,        "headers": {            "Content-Type": "application/json",            "Access-Control-Allow-Origin": "\*"        },        "body": json.dumps(body)    }\# \===============================\# 이벤트 정규화\# \===============================def normalize\_events(body: Any) \-\> List\[Dict\[str, Any\]\]:    if not isinstance(body, dict) or len(body) \!= 1:        raise ValueError("invalid root schema")    user\_id, activities \= next(iter(body.items()))    if not isinstance(activities, dict):        raise ValueError("invalid user payload")    normalized\_events: List\[Dict\[str, Any\]\] \= \[\]    for activity, events in activities.items():        if not isinstance(events, list):            raise ValueError(f"invalid activity payload: {activity}")        for evt in events:            if not isinstance(evt, dict):                raise ValueError("event must be an object")            normalized\_events.append({                "\_user\_id": user\_id,                "\_activity": activity,                \*\*evt            })    if not normalized\_events:        raise ValueError("no events found")    return normalized\_events\# \===============================\# Lambda Handler\# \===============================def lambda\_handler(event, context):    request\_id \= context.aws\_request\_id    logger.info({        "message": "request received",        "request\_id": request\_id    })    \# 1️⃣ 인증    headers \= event.get("headers") or {}    api\_key \= (        headers.get("x-api-key")        or headers.get("X-Api-Key")        or headers.get("X-API-KEY")    )    if api\_key \!= EXPECTED\_API\_KEY:        logger.warning({"message": "unauthorized", "request\_id": request\_id})        return response(403, {"error": "Forbidden"})    \# 2️⃣ Body 디코딩    raw\_body \= event.get("body", "")    if event.get("isBase64Encoded"):        raw\_body \= base64.b64decode(raw\_body).decode("utf-8")    \# 3️⃣ JSON 파싱    try:        body \= json.loads(raw\_body)    except json.JSONDecodeError:        return response(400, {"error": "Invalid JSON"})    \# 4️⃣ 정규화    try:        events \= normalize\_events(body)    except ValueError as e:        return response(400, {"error": str(e)})    \# 🔥 여기서 이제 정상 동작    if len(events) \> MAX\_EVENTS:        return response(413, {"error": "Too many events"})    \# 5️⃣ Firehose 전송    records \= \[{"Data": json.dumps(evt, ensure\_ascii=False) \+ "\\n"} for evt in events\]    logger.info({        "message": "sending to firehose",        "request\_id": request\_id,        "count": len(records),        "stream": DELIVERY\_STREAM\_NAME    })    resp \= firehose.put\_record\_batch(        DeliveryStreamName=DELIVERY\_STREAM\_NAME,        Records=records    )    failed \= resp.get("FailedPutCount", 0\)    if failed \> 0:        logger.error({            "message": "firehose put failed",            "failed": failed,            "responses": resp.get("RequestResponses")        })        return response(500, {"error": "Firehose put failed", "failed": failed})    return response(200, {        "received": len(events),        "failed": 0    }) |
| :---- |

**3.11.2 Kinesis Data Firehose Transform Lambda**  
**① 개요**

본 프로젝트는 모바일 클라이언트에서 수집된 로그 데이터를 Amazon S3 데이터 레이크에 저장하기 전에 개인정보를 보호하기 위해 Firehose Transform Lambda를 적용하였다.

데이터 흐름은 다음과 같다.

| Mobile Client → API Gateway → Ingestion Lambda → Kinesis Data Firehose → Transform Lambda → Amazon S3 |
| :---- |

Transform Lambda는 데이터 레이크 적재 직전에 실행되며, 사용자 식별 정보를  
	비식별화하고 민감 정보를 최소화하는 **개인정보 보호 계층(Privacy Enforcement Layer)**  
	역할을 수행한다.

**2\. 보안 설계 목표**

본 설계는 다음 세 가지 보안 목표를 중심으로 구성되었다.

1. 기밀성(Confidentiality) 확보  
2. 무결성(Integrity) 보장  
3. 개인정보 최소화(Data Minimization)

**3 사용자 식별자 토큰화 (User ID Tokenization)**

원본 user\_id필드는 그대로 저장되지 않으며, DynamoDB 매핑 테이블을 통해 토큰으로  
 	대체된다.

| if "\_user\_id" in obj:    obj\["user\_token"\] \= get\_or\_create\_user\_token(obj.pop("\_user\_id")) |
| :---- |

**보안 효과**

* S3 데이터만 유출되어도 사용자 식별 불가  
* 가명처리(Pseudonymization) 조치 충족  
* 개인정보 보호법 및 GDPR 기준 대응 가능

**4\. 앱 식별자 토큰화 (Application Tokenization)**

앱 패키지명(package) 또한 직접 저장되지 않고 토큰으로 변환된다.

| if "package" in obj:    obj\["package\_token"\] \= get\_or\_create\_app\_token(obj.pop("package")) |
| :---- |

**보안 효과**

* 외부 데이터 유출 시 앱 구조 노출 방지  
* 내부 분석에는 영향 없음

**5\. 토큰 생성 및 무결성 보호**

토큰은 secrets 모듈을 사용하여 안전하게 생성된다.

| def generate\_token(prefix: str, length: int \= 10\) \-\> str:    return prefix \+ secrets.token\_urlsafe(length) |
| :---- |

**보안 효과**

* 암호학적으로 안전한 랜덤 토큰 생성  
  * 토큰 역추적 공격 난이도 상승

**6\. GPS 정밀도 축소 (Location Data Minimization)**

위치 정보는 소수점 둘째 자리까지로 축소 저장한다.

| def reduce\_gps\_precision(gps: str) \-\> str:    lat, lon \= gps.split(",")    return f"{float(lat):.2f},{float(lon):.2f}" |
| :---- |

**보안 효과**

* 특정 개인 위치 추적 가능성 감소  
* 분석 목적 유지하면서 민감도 축소

**7\. 부분 실패 격리 (Fault Isolation)**

Transform 중 예외 발생 시 개별 레코드만 실패 처리한다.

| output.append({    "recordId": record\["recordId"\],    "result": "ProcessingFailed",    "data": record\["data"\]}) |
| :---- |

**보안 효과**

* 가용성(Availability) 확보  
* 장애 전파 차단  
* 데이터 손실 범위 명확화

**3.11.3 KMS 암호화가 아닌, 토큰화 선택**

본 설계에서는 사용자 식별자 및 앱 식별자 처리 과정에서 AWS KMS 기반 암호화를 적용하지 않고, DynamoDB 기반 결정적 토큰화(Deterministic Tokenization)를 선택하였다. 이는 보안을 약화한 결정이 아니라, **파이프라인 특성을 고려한 최적의 보안 배치 전략**에 따른 것이다.

* Transform Lambda의 구조적 특성  
  Firehose Transform Lambda는 모든 로그 레코드에 대해 동기적으로 실행된다.  
   즉, 이 단계에서 병목이 발생하면 전체 로그 적재 지연으로 이어진다.  
  따라서 해당 계층에서는 반드시 다음 원칙을 지켜야 한다.  
* 가볍고 결정적인 처리만 수행  
* 외부 서비스 호출 최소화  
* 네트워크 기반 암호화 연산 배제  
  KMS는 암호화·복호화 시 네트워크 호출이 필요하며, 대량 레코드 처리 시 지연(latency)과 비용(cost)을 증가시킬 수 있다.  
  실시간 로그 파이프라인 특성상, 보안 강도를 높이는 것보다 **보안을 적절한 위치에 배치하는 것이 더 중요하다고 판단하였다.**


  Transform Lambda는 다음 연산만 수행한다.  
* DynamoDB 단순 조회 및 조건부 쓰기  
* 랜덤 토큰 생성  
* GPS 소수점 연산

  이는 CPU 연산 또는 단순 Key-Value 조회 수준이므로 트래픽 증가 시에도 수평 확장이 가능하다.  
  반면, KMS 기반 암호화는 다음과 같은 리스크를 동반한다.  
* API 호출 지연 누적  
* TPS 제한에 따른 스로틀링 가능성  
* 비용 증가  
* 암호화 키 관리 복잡성 증가  
  따라서 실시간 경로에서는 고강도 암호화를 적용하지 않고, 비식별화 중심 경량 처리 구조를 유지하였다.

| import jsonimport base64import boto3import secretsimport timeimport loggingfrom botocore.exceptions import ClientErrorfrom typing import Dict\# \===============================\# Logging\# \===============================logger \= logging.getLogger()logger.setLevel(logging.INFO)\# \===============================\# AWS Clients\# \===============================dynamodb \= boto3.resource("dynamodb")app\_table \= dynamodb.Table("app\_token\_map")user\_table \= dynamodb.Table("user\_token\_map")\# \===============================\# Config\# \===============================APP\_TOKEN\_PREFIX \= "APP\_"USER\_TOKEN\_PREFIX \= "USR\_"\# \===============================\# Token Helpers\# \===============================def generate\_token(prefix: str, length: int \= 10\) \-\> str:    return prefix \+ secrets.token\_urlsafe(length)def get\_or\_create\_app\_token(package: str) \-\> str:    now \= int(time.time() \* 1000\)    resp \= app\_table.get\_item(        Key={"package\_name": package, "token\_type": "APP"}    )    if "Item" in resp:        app\_table.update\_item(            Key={"package\_name": package, "token\_type": "APP"},            UpdateExpression="""                SET                    last\_seen\_at \= :now,                    version \= if\_not\_exists(version, :zero) \+ :one            """,            ExpressionAttributeValues={                ":now": now,                ":one": 1,                ":zero": 0            }        )        return resp\["Item"\]\["app\_token"\]    token \= generate\_token(APP\_TOKEN\_PREFIX)    try:        app\_table.put\_item(            Item={                "package\_name": package,                "token\_type": "APP",                "app\_token": token,                "created\_at": now,                "last\_seen\_at": now,                "version": 1            },            ConditionExpression="attribute\_not\_exists(package\_name)"        )    except ClientError as e:        if e.response\["Error"\]\["Code"\] \!= "ConditionalCheckFailedException":            raise    return tokendef get\_or\_create\_user\_token(user\_id: str) \-\> str:    now \= int(time.time() \* 1000\)    resp \= user\_table.get\_item(        Key={"user\_id": user\_id, "token\_type": "USER"}    )    if "Item" in resp:        user\_table.update\_item(            Key={"user\_id": user\_id, "token\_type": "USER"},            UpdateExpression="""                SET                    last\_seen\_at \= :now,                    version \= if\_not\_exists(version, :zero) \+ :one            """,            ExpressionAttributeValues={                ":now": now,                ":one": 1,                ":zero": 0            }        )        return resp\["Item"\]\["user\_token"\]    token \= generate\_token(USER\_TOKEN\_PREFIX)    try:        user\_table.put\_item(            Item={                "user\_id": user\_id,                "token\_type": "USER",                "user\_token": token,                "created\_at": now,                "last\_seen\_at": now,                "version": 1            },            ConditionExpression="attribute\_not\_exists(user\_id)"        )    except ClientError as e:        if e.response\["Error"\]\["Code"\] \!= "ConditionalCheckFailedException":            raise    return token\# \===============================\# Data Helpers\# \===============================def reduce\_gps\_precision(gps: str) \-\> str:    try:        lat, lon \= gps.split(",")        return f"{float(lat):.2f},{float(lon):.2f}"    except Exception:        return gps\# \===============================\# Lambda Handler\# \===============================def lambda\_handler(event, context):    output \= \[\]    for record in event\["records"\]:        try:            payload \= base64.b64decode(record\["data"\]).decode("utf-8")            obj: Dict \= json.loads(payload)            \# \---------------------------            \# Tokenization            \# \---------------------------            if "\_user\_id" in obj:                obj\["user\_token"\] \= get\_or\_create\_user\_token(obj.pop("\_user\_id"))            if "package" in obj:                obj\["package\_token"\] \= get\_or\_create\_app\_token(obj.pop("package"))            \# \---------------------------            \# Privacy            \# \---------------------------            if "coarse\_gps" in obj:                obj\["coarse\_gps"\] \= reduce\_gps\_precision(obj\["coarse\_gps"\])            new\_data \= json.dumps(obj, ensure\_ascii=False) \+ "\\n"            output.append({                "recordId": record\["recordId"\],                "result": "Ok",                "data": base64.b64encode(new\_data.encode("utf-8")).decode("utf-8")            })        except Exception:            logger.exception("Firehose transform failed")            output.append({                "recordId": record\["recordId"\],                "result": "ProcessingFailed",                "data": record\["data"\]            })    return {"records": output} |
| :---- |

  **3.11.4 KMS 기반 데이터 레이크 암호화 전략**

  KMS(Key Management Service) 키 정책은 데이터 레이크(Bronze → Silver) 구간에서 저장 데이터 암호화를 보호하기 위해 설계

  **① 암호화 구조 개요**

**데이터 흐름**

| API Gateway → Lambda → Firehose → S3 (SSE-KMS)                   ↓                 Glue (Decrypt) |
| :---- |

KMS는 다음 계층에서 사용된다.

* Firehose → S3 적재 시 데이터 키 생성  
* S3 객체 암호화  
* Glue ETL 시 복호화

**② 권한 관리**

**Root 계정 전체 권한**

**보안 효과**

* 키 잠금(lock-out) 리스크 방지  
* 관리 실수로 인한 키 접근 불가 상황 대비

| {  "Sid": "EnableRootPermissions",  "Effect": "Allow",  "Principal": { "AWS": "arn:aws:iam::333673271664:root" },  "Action": "kms:\*",  "Resource": "\*"} |
| :---- |

  **키 관리자 역할 분리**

  **보안 효과**

* 키 오남용 방지  
* 책임 추적 가능 (CloudTrail 기반)

| "Principal": {  "AWS": "arn:aws:iam::333673271664:role/AdministratorAccess\_ameowzon"} |
| :---- |

  **③ Firehose Delivery Role의 키 사용 권한**

  **보안 효과**

* S3에 저장되는 모든 객체는 KMS로 암호화  
* 키 없이 객체 복호화 불가  
* 내부자 유출 리스크 감소

| "Principal": {  "AWS": "arn:aws:iam::333673271664:role/FirehoseDeliveryRole"} |
| :---- |

**④ Firehose 서비스 직접 호출 제한**

**보안 효과**

* 다른 리전 또는 타 계정에서 키 사용 불가  
* 키 오남용 방지  
* 교차 계정 공격 차단

| "Principal": {  "Service": "firehose.amazonaws.com"}Condition:"kms:ViaService": "firehose.ap-northeast-2.amazonaws.com" |
| :---- |

**⑤ S3 서비스 키 사용 허용**

**보안 효과**

* S3 단에서 KMS 기반 서버측 암호화 수행  
* 버킷 외부 서비스 접근 차단

| "Principal": {  "Service": "s3.amazonaws.com"} |
| :---- |


**⑥ Grant 기반 리소스 접근 통제**

* 임시 권한 남용 방지  
* 서비스 기반 접근만 허용  
* 권한 상승 공격 차단

| "kms:CreateGrant","kms:ListGrants","kms:RevokeGrant"Condition:"kms:GrantIsForAWSResource": "true" |
| :---- |


**⑦ Glue 복호화 권한 제한**

* 데이터 레이크 계층 분리 (Bronze → Silverㅁ  
* 무단 분석 방지  
* 내부 접근 최소화

| "Principal": {  "AWS": "arn:aws:iam::333673271664:role/ameowzon-silverGlue"} |
| :---- |

## 

## **3.12 데이터 파이프라인 설계**

### **3.12.1 설계 목적**

본 데이터 파이프라인은 모바일 클라이언트에서 생성되는 이벤트 로그를 **실시간 수집 → 정제 → 적재 → 분석 준비 상태**까지 자동 처리하도록 설계된 스트리밍 중심 아키텍처이다.  
 핵심 설계 목표는 다음과 같다.

* 스트리밍 기반 데이터 수집 안정성

* 장애 격리 및 자동 복구

* 입력 데이터 품질 보장

* 실시간 처리와 배치 처리의 계층 분리

### **3.12.2 파이프라인 전체 흐름 구조**

데이터 흐름은 단일 직선 구조가 아닌 **단계별 책임 분리형 파이프라인**이다.

Client  
→ API Gateway  
→ Ingestion Lambda  
→ Firehose  
→ Transform Lambda  
→ S3 Raw 저장  
→ Spark ETL  
→ Feature 생성  
→ 분석/모델 입력

각 단계는 독립적으로 확장·장애 처리 가능하도록 설계되어 있다.

---

### **3.12.3 단계별 처리 책임 정의**

#### **① Ingestion Layer — 요청 검증 계층**

역할: 외부 입력 검증 및 정규화

처리 항목:

* API Key 인증

* JSON 형식 검증

* Base64 디코딩 검사

* 이벤트 수 제한

* 스키마 정규화

설계 특징:

외부 입력은 항상 신뢰하지 않는다.

즉, 이 계층은 보안 장치이자 데이터 품질 필터 역할을 동시에 수행한다.

---

#### **② Streaming Layer — 실시간 전달 계층**

Firehose는 메시지 브로커가 아니라 **Delivery Stream Processor** 역할을 수행한다.

특징:

* 자동 배치 전송

* 재시도 처리

* 백프레셔 완충

* 버퍼링

이는 트래픽 급증 시에도 Lambda 호출 폭주를 방지한다.

---

#### **③ Transform Layer — 실시간 처리 계층**

Transform Lambda는 데이터 저장 직전에 실행되는 **경량 처리 단계**다.

처리 정책:

* 토큰화

* 위치 정밀도 축소

* 민감정보 제거

* 레코드 단위 실패 처리

설계 원칙:

이 단계에서는 절대 무거운 연산을 수행하지 않는다.

이유: Firehose 동기 호출 구조이기 때문.

---

#### **④ Storage Landing Layer — Raw 적재**

Raw 저장 단계는 어떠한 변형도 최소화한다.

목표:

* 재처리 가능성 확보

* 장애 복구 가능

* 감사 로그 보존

---

#### **⑤ Batch Processing Layer — 정제 처리**

Spark 기반 ETL에서 수행:

* timestamp 변환

* null 제거

* 컬럼 의미 통일

* 품질 검사

이 단계는 실시간이 아닌 **정합성 중심 처리 단계**다.

---

#### **⑥ Feature Engineering Layer**

사용자 행동 패턴 분석용 Feature 생성:

예:

* 이동성 지표

* 화면 사용 빈도

* 알림 인터럽트

* 네트워크 변화

이 단계부터 데이터는 이벤트 로그가 아니라 **분석 데이터셋**으로 변환된다.

---

### **3.12.4 파이프라인 설계 원칙**

본 구조는 다음 6개 원칙을 따른다.

| 원칙 | 의미 |
| ----- | ----- |
| Fail Fast | 오류 데이터 조기 차단 |
| Loose Coupling | 단계 간 의존성 최소 |
| Idempotency | 재처리 안전 |
| Observability | 전체 추적 가능 |
| Isolation | 장애 전파 방지 |
| Elasticity | 자동 확장 |

---

### **3.12.5 장애 대응 전략**

파이프라인은 실패를 전제로 설계되었다.

| 실패 위치 | 대응 |
| ----- | ----- |
| API 인증 실패 | 즉시 차단 |
| Transform 실패 | 레코드 격리 |
| Firehose 실패 | 재시도 |
| ETL 실패 | 날짜 재실행 |

핵심 설계 철학:

하나의 실패가 전체 시스템을 멈추게 해서는 안 된다.

---

### **3.12.6 데이터 일관성 전략**

시간 기반 로그 시스템에서 가장 중요한 요소는 **event ordering**이다.

이를 위해:

* millisecond timestamp 유지

* 서버 시간 의존 제거

* client timestamp 사용

* timezone 보존

---

### **3.12.7 확장성 구조**

확장성은 수동 조정 없이 자동으로 동작한다.

확장 축:

* 요청량 증가 → API Gateway 스케일

* 이벤트 증가 → Firehose 버퍼 증가

* 분석 증가 → Spark parallelism 증가

즉, 병목은 단일 지점이 아니라 각 계층별로 분산된다.

---

### **3.12.8 설계 평가**

이 파이프라인은 다음 유형의 아키텍처 특성을 가진다.

* Streaming-first Architecture

* Validation-driven Ingestion

* Fault-tolerant Processing

* Privacy-aware Transformation

---

### **3.12.9 결론**

본 데이터 파이프라인은 단순한 로그 수집 경로가 아니라

보안 · 품질 · 확장성 · 분석 준비 상태를 동시에 만족하는 실시간 데이터 처리 체계

이다.

특히 입력 검증 → 스트림 전달 → 변환 → 저장 → 정제 → 피처 생성으로 이어지는 구조는 현대 데이터 플랫폼의 권장 패턴인

**Ingestion → Processing → Storage → Analytics**

라이프사이클을 충실히 반영한다.

## **3.13 데이터 저장소 설계 (Data Lake · Data Warehouse)**

## **3.13.1 설계 목표**

본 데이터 저장소는 단순 로그 저장 시스템이 아니라 다음을 동시에 만족하도록 설계되었다.

* 실시간 수집 데이터 안정 저장  
* 개인정보 보호  
* 분석 친화 구조  
* 대규모 확장성  
* 비용 최적화

이를 위해 저장소는 단일 구조가 아닌 **Medallion 기반 계층형 저장 구조**로 설계하였다.

## **3.13.2 전체 저장소 아키텍처**

Ingestion → Bronze → Silver → Gold → Analytics

| 계층 | 저장 역할 | 시스템 유형 |
| :---: | :---: | :---: |
| Bronze | 원본 저장 | Data Lake |
| Silver | 정제 저장 | Data Lake |
| Gold | 집계 저장 | Data Warehouse |

즉 본 시스템은Data Lake \+ Data Warehouse 통합 구조 (Lakehouse Architecture)이다.

## **3.13.3 Bronze 저장소 설계 (Raw Data Lake)**

### **역할**

원본 로그 영구 보존

### **저장 위치 구조**

s3://ameowzon-raw/raw/date=YYYY-MM-DD/

### **저장 정책**

* append only  
* schema 없음  
* 변환 없음  
* 삭제 없음

  ### **저장 포맷**

* gzip

  ### **설계 이유**

Bronze는 분석용 데이터가 아니라 재처리 가능성을 보장하는 안전 저장소다.

## **3.13.4 Silver 저장소 설계 (Refined Data Lake)**

Silver 계층은 분석 가능한 상태로 정제된 이벤트 데이터 저장소다.

Silver는 분석 결과를 만드는 계층이 아니라 분석 가능한 데이터 상태를 만드는 계층

### **① 저장 경로**

| s3://ameowzon-silver/events/event\_date=YYYY-MM-DD/ |
| :---- |

### **② Silver ETL 처리 로직**

#### **Raw 로드 (Fail-safe)**

→ 손상 데이터 존재해도 Job 실패하지 않음

| df\_raw \= (   spark.read   .option("mode","PERMISSIVE")   .json(RAW\_PATH)) |
| :---- |

#### **시간 정합성 처리**

| df \= (   df\_raw   .withColumn("event\_time",       F.to\_timestamp(F.col("event\_ts")/1000))   .filter(F.col("event\_time").isNotNull())   .withColumn("event\_date",F.lit(TARGET\_DATE))) |
| :---- |

#### **품질 검증**

| qc \= df.select(   F.count("\*").alias("rows"),   F.count(F.when(F.col("user\_id").isNull(),True)).alias("null\_user"),   F.count(F.when(F.col("event\_ts").isNull(),True)).alias("null\_ts")) |
| :---- |

#### **Silver 저장**

| (df.repartition(10).write.mode("append").partitionBy("event\_date").parquet("s3://ameowzon-silver/events/")) |
| :---- |

### **③ Silver 저장소 설계 특징**

| 특징 | 효과 |
| :---: | :---: |
| 정규화 | 분석 안정성 |
| 타입 통일 | 모델 입력 안정 |
| 오류 제거 | 품질 보장 |
| Parquet | 쿼리 성능 |

## **3.13.5 Gold 저장소 설계 (Analytical Warehouse)**

Gold 계층은 사용자 상태 요약 데이터를 저장하는 **분석 전용 저장소**다.  
Gold는 저장소가 아니라 분석 서비스 레이어

### **① 저장 경로**

Silver와 동일 파티션 구조 유지:

→ 동일 partition 설계는 조회 최적화를 위한 구조다.

| s3://ameowzon-gold/events/event\_date=YYYY-MM-DD/ |
| :---- |

### **② 집계 기준**

하루 \+ 사용자 \= 1 row

### **③ Gold ETL 처리**

#### **Silver 로드**

| df \= spark.read.parquet(SILVER\_PATH) |
| :---- |

#### **행동 Feature 생성**

| basic\_features \= (df.groupBy("user\_id").agg( F.count(F.when(F.col("event\_name").isin(  "SCREEN\_INTERACTIVE","SCREEN\_NON\_INTERACTIVE"),True)).alias("Screen"), F.count(F.when(F.col("event\_name")=="USER\_INTERACTION",True)).alias("UserAct"), F.count(F.when(F.col("event\_name")=="NOTIFICATION\_INTERRUPTION",True)).alias("Notif"), F.count(F.when(F.col("event\_name")=="KEYGUARD\_HIDDEN",True)).alias("unlock\_cnt"), F.count(F.when(F.col("event\_type")=="heartbeat",True)).alias("heartbeat\_cnt"), F.max("retry\_count").alias("retry\_max"), F.max("queue\_size").alias("queue\_max"), F.sum("step\_count").alias("step\_sum"))) |
| :---- |

#### **이동성 Feature**

| cell\_w \= Window.partitionBy("user\_id").orderBy("event\_ts")df\_cell \= df.withColumn("prev\_cell",F.lag("cell\_lac").over(cell\_w)) |
| :---- |

#### **WiFi Feature**

| WiFi 변화는 BSSID 기준 처리Gold\_ETLwifi\_features \= (df.filter(F.col("\_activity")=="WIFI\_CHANGE").groupBy("user\_id").agg( F.count("\*").alias("wifi\_change\_cnt\_est"), F.countDistinct("curr\_bssid").alias("unique\_wifi\_cnt"))) |
| :---- |

#### **저장**

| (features.withColumn("event\_date",F.lit(TARGET\_DATE)).repartition(1).write.mode("overwrite").parquet(GOLD\_PATH)) |
| :---- |

### **④ Gold 저장소 특징**

| 항목 | 의미 |
| :---: | :---: |
| Columnar | 빠른 조회 |
| 집계 구조 | 분석 최적화 |
| overwrite | 최신 상태 유지 |
| Feature dataset | ML 입력 |

## **3.13.6 저장소 최적화 정책**

### **① Partition 전략**

event\_date partition

**효과:**

* 쿼리 스캔 범위 최소화  
* Athena 비용 절감  
* 병렬 처리 증가

### **② 파일 최적화**

| 방법 | 목적 |
| :---: | :---: |
| repartition | small file 방지 |
| columnar format | scan 감소 |
| compression | 저장 비용 절감 |

## **3.13.7 저장소 보안 설계**

저장소는 단순 저장 영역이 아니라 **보안 경계**다.

**적용 정책:**

* SSE-KMS 암호화  
* 토큰화 식별자  
* IAM 역할 분리  
* 키 사용 제한  
  **핵심 원칙:**  
  저장소 접근 ≠ 데이터 접근

  ## **3.13.8 데이터 수명주기 정책**

| 계층 | 보관 기간 |
| ----- | ----- |
| Bronze | 90일 |
| Silver | 32일 |
| Gold | 32일 |

  **목적:**

* 비용 절감  
* 스토리지 최적화  
* 플레이 스토어 배포 기준 충족(개인정보 90일 이후 삭제)  
* ML 사용자 베이스라인 최대 사용일자 충족(최대 30일 이전 데이터 까지)


  ## **3.14.9 설계 평가**

  본 저장 구조는 다음 아키텍처 유형이다.  
  Enterprise Lakehouse Architecture  
  충족 특성:  
* Streaming 지원  
* Batch 분석 지원  
* ML Feature Store 가능  
* 재처리 가능 구조  
* 보안 내장 구조


  ## **최종 결론**

  본 데이터 저장소 설계는 단순 로그 저장 시스템이 아니라  
  분석 가능한 상태로 자동 진화하는 계층형 데이터 플랫폼  
  이다.  
  Bronze → Silver → Gold 계층 구조를 통해  
* 안정성  
* 확장성  
* 보안성  
* 분석 성능  
  을 동시에 확보하였다.




## 3.15 데이터 분석 및 활용 방안

# 

# **4\. AI 모델 및 데이터 분석**

## **4.1 모델 연구 개요**

본 모델은 모바일 센서 로그 데이터를 기반으로 개인의 일 단위 행동 패턴 변화를 탐지하는 이상 탐지 모델을 설계하는 것을 목표로 한다.

라벨이 충분하지 않은 환경(PHQ8 보유율 18%)을 고려하여, 본 연구에서는 비지도 학습 기반 이상 탐지 모델을 적용하였다. 또한 개인 간 행동 편차가 매우 크다는 점을 반영하여 개인 베이스라인 기반 정규화 구조를 설계하였다.

## **4.2 시스템 구조**

### **4.2.1 전체 구조 개요**

본 시스템은 다음과 같은 두 단계 구조로 설계하였다.

1. 모델 학습 파이프라인  
2. 일 단위 배치 추론 파이프라인

   ### **4.2.2 모델 학습 및 추론 구조**

   #### **모델 학습 흐름**

* 입력: S3 Silver 레이어의 일 단위 Feature 데이터  
* 학습: Isolation Forest 기반 이상 탐지 모델 학습  
* 산출물: 모델 파일 (.pkl)  
* 저장 위치: S3 모델 버킷 (버전 관리 구조 설계)

  #### **배치 추론 흐름**

* 입력: 최신 일 단위 Feature \+ 저장된 모델  
* 실행 방식: Daily Batch 구조로 설계  
* 출력: 사용자별 상태 결과 저장

  ### **4.2.3 모델 파이프라인**

### ![][image9]

## **4.3 데이터 분석 (EDA)**

### **4.3.1 데이터셋 개요**

#### **규모**

* 사용자 수: 342명  
* 총 관측: 9,057 user-days  
* 평균 관측 기간: 26.5일 (최소 7일, 최대 85일)

  #### **센서 구성**

* 핵심 센서: Screen, App, Notification, UserActivity, Location  
* 보조 센서: SMS, Phone, Battery, Wifi  
* 커버리지: 대부분 90% 이상 (일부 Light 72%, Photo 74%)

  #### **데이터 품질**

* 핵심 컬럼 결측률: 0% (uuid, date, sensor\_id, timestamp)  
* 중복 로그: 0.01% (무시 가능)  
* 시간 동기화: ts vs ts\_raw 약 2시간 오프셋 (일관됨)


  ### **4.3.2 주요 분석 결과**

#### **1\. 개인차가 매우 큼**

* Screen 사용량 표준편차 평균 41.9, 최대 331  
* 사용자 간 활동량 분산이 매우 큼

  → 전역 기준 이상 탐지는 부적합  
  	→ 개인별 베이스라인 필요

#### **2\. 평일/주말 차이 존재**

| 센서 | 평일 평균 | 주말 평균 | 차이 |
| :---: | :---: | :---: | :---: |
| Screen | 199 | 160 | \+39 |
| App | 232 | 198 | \+34 |
| Notif | 417 | 336 | \+81 |

     	→ 요일 영향이 존재하며, 행동 패턴 분리가 필요함을 확인

#### **3\. 리듬 및 공백 패턴 이상 관측**

* 야간(0–5시) 활동 평균 6%, 최대 24%  
* Shock Rate (|Z| ≥ 2\) 평균 4.5%  
* 최대 무활동 시간 평균 19.8시간, 최대 149시간

→ 실제 이상 행동 패턴이 데이터 내 존재함을 확인

## **4.4 Feature Engineering**

### **4.4.1 입력 데이터** 

* 형태: 사용자별 CSV 파일 (342개)  
* 각 행: 센서 이벤트 단위 (timestamp 포함)  
* 주요 컬럼: uuid, sensor\_id, ts\_raw, value

### **4.4.2 일 단위 집계**

#### **집계 방식**

* 기준 시간: ts\_raw (디바이스 시간)  
* 집계 단위: 1일 (00:00 \~ 23:59)  
* 결과: (9,057 user-days × 56 features)

### **4.4.3 생성 피처**

#### **1\. 기본 활동량 (Activity)**

| FE 컬럼 | 안드 로그 | FE 처리 | 의미 |  |
| :---: | :---: | :---: | :---: | ----- |
| Screen | SCREEN\_INTERACTIVE / NON\_INTERACTIVE | 일별 count | 화면 사용량 |  |
| UserAct | USER\_INTERACTION | 일별 count | 실제 조작량 |  |
| Notif | NOTIF\_INTERRUPTION | 일별 count | 외부자극 |  |
| unlock\_cnt | KEYGUARD\_HIDDEN | 일별 count | 세션 시작 의지 |  |
| daily\_event\_cnt | Screen+UserAct | sum | 총 활동량 |  |
| has\_activity | daily\_event\_cnt | \>0 → True | 사용 여부 |  |

#### **2\. 시간 패턴 (Rhythm)**

| FE 컬럼 | 안드 로그 | FE 처리 | 의미 |  |
| :---: | :---: | :---: | :---: | ----- |
| rhythm\_event\_cnt | SCREEN / USER / UNLOCK | count | 표본 수 |  |
| night\_ratio | timestamp | (0\~5+1)/(total+24) | 야간비율 |  |
| hour\_entropy | timestamp | entropy | 불규칙성 |  |
| day\_ratio | timestamp | 6\~17 비율 | 낮 패턴 |  |
| evening\_ratio | timestamp | 18\~23 비율 | 저녁 패턴 |  |
| peak\_hour | timestamp | argmax | 주 활동시간 |  |
| peak\_ratio | timestamp | max/total | 쏠림도 |  |
| rhythm\_low\_coverage | rhythm\_event\_cnt | \<50 | 신뢰도 |  |

#### 

#### **3\. Gap / Inactivity (무활동)**

| FE 컬럼 | 안드 로그 | FE 처리 | 의미 |  |
| :---: | :---: | :---: | :---: | ----- |
| gap\_event\_cnt | SCREEN / USER / UNLOCK | count | 표본 수 |  |
| gap\_max | timestamp | max(diff) | 최장 공백 |  |
| gap\_p95 | timestamp | p95(diff) | 대표 공백 |  |
| gap\_cnt\_2h | timestamp | ≥2h count | 긴 공백 |  |
| gap\_cnt\_6h | timestamp | ≥6h count | 매우 긴 공백 |  |
| gap\_long\_ratio | timestamp | sum(diff≥2)/24 | 공백 비율 |  |
| overnight\_gap | prev→today | diff | 야간공백 |  |
| first\_hour | timestamp | min(hour) | 첫 사용 |  |
| last\_hour | timestamp | max(hour) | 마지막 사용 |  |
| gap\_low\_coverage | gap\_event\_cnt | \<50 | 신뢰도 |  |

#### 

#### **4\. Session (연속 사용)**

| FE 컬럼 | 안드 로그 | FE 처리 | 의미 |  |
| :---: | :---: | :---: | :---: | :---: |
| session\_cnt | (SCREEN\_INTERACTIVE / SCREEN\_NON\_INTERACTIVE 기반) | pair count | 사용 덩어리 |  |
| session\_total\_sec | 위 | sum(sec) | 총 몰입 |  |
| session\_mean\_sec | 위 | mean | 평균 몰입 |  |
| long\_session\_cnt | 위 | ≥30min | 과몰입 |  |

#### **5\. Mobility (이동/외출)**

| FE 컬럼 | 안드 로그 | FE 처리 | 의미 |  |
| :---: | :---: | :---: | :---: | ----- |
| cell\_change\_cnt | CELL\_CHANGE | count | 이동량 |  |
| unique\_cell\_cnt | cell\_lac | set size | 장소 수 |  |
| wifi\_change\_cnt\_est | WIFI\_SSID | 연속 변화 | 환경 변화 |  |
| unique\_wifi\_cnt | WIFI\_SSID | set size | 장소 다양성 |  |
| step\_sum | Step\_Count / value | sum | 활동량 |  |
| lat/lon | GPS | 미사용 | 위치 원본 |  |

## 

#### **6\. Meta / QC (운영 상태)**

| FE 컬럼 | 안드 로그 | FE 처리 | 의미 |  |
| :---: | :---: | :---: | :---: | ----- |
| heartbeat\_cnt | HEARTBEAT | count | 앱 생존 |  |
| retry\_max | retry\_count | max | 실패 |  |
| queue\_max | queue\_size | max | 밀림 |  |
| tz\_offset\_min | tz\_offset\_minutes | min | 타임존 |  |
| tz\_offset\_max | tz\_offset\_minutes | max | 타임존 |  |
| tz\_changed | tz\_offset | diff≥60 | 이동 |  |
| qc\_last\_ts\_max | client\_last\_event\_ts | max | 지연 |  |

#### **7\. QC Flags**

| FE 컬럼 | 기반 | 처리 | 의미 |  |
| ----- | ----- | ----- | ----- | ----- |
| qc\_core\_low\_cov | daily\_event\_cnt | \<50 | 부족 |  |
| qc\_core\_very\_low\_activity | daily\_event\_cnt | \<10 | 부분수집 |  |
| qc\_rhythm\_low\_cov | rhythm\_low\_coverage | 그대로 | 불신 |  |
| qc\_gap\_low\_cov | gap\_low\_coverage | 그대로 | 불신 |  |
| qc\_meta\_low\_heartbeat | heartbeat\_cnt | \<1 | 앱죽음 |  |
| qc\_meta\_retry\_warn | retry\_max | ≥3 | 불안 |  |
| qc\_meta\_queue\_warn | queue\_max | ≥20 | 병목 |  |

#### **8\. Context Signals (보정 신호)**

| FE 컬럼 | 기반 | FE 처리 | 의미 |  |
| :---: | :---: | :---: | :---: | ----- |
| partial\_signal\_raw | core+retry+queue | 점수화 | 부분수집 |  |
| delay\_signal\_raw | heartbeat+ts | 감소 | 지연 |  |
| tz\_change\_signal | tz\_changed | 0/1 | 이동 |  |
| travel\_signal\_raw | tz+cell+wifi | 합산 | 여행 |  |

#### **9\. Delta (변화량)**

| FE 컬럼 | 기반 | 처리 | 의미 |  |
| :---: | :---: | :---: | :---: | ----- |
| \*\_d1 | 주요 피처 | today-yday | 변화 |  |
| \*\_r1 | event/session/step | ratio | 추세 |  |

## **4.5 모델 설계 및 구현 (Modeling Pipeline)**

### **4.5.1 입력 및 기본 전처리**

* 입력: daily\_feature\_v2.csv (key: uuid, date)  
* 처리: 날짜 정규화, key 결측 제거, uuid-date 정렬  
* 메타 생성:  
  * is\_weekend  
  * cold\_stage (ONBOARD/WARMUP/SEMI\_READY/READY)  
     → 콜드스타트 구간 정책 적용을 위한 구분값

### **4.5.2 Quality Gate & Context Flag**

* QC 플래그(qc\_core\_low\_cov, qc\_rhythm\_low\_cov, qc\_gap\_low\_cov)를 표준화하고, QC 결측이 있는 경우(qc\_missing\_any)는 보수적으로 LOW\_CONF로 취급 가능하도록 설정  
* 컨텍스트 시그널(partial/delay/travel/tz)은 threshold 기반으로 flag로 변환  
* 최종적으로  
  * quality\_state ∈ {GOOD, LOW\_CONF, CRITICAL}  
  * context\_mode ∈ {NORMAL, PARTIAL|DELAY|TRAVEL…}  
     을 생성

  ### **4.5.3 개인 베이스라인 (ST/LT \+ Early)**

  사용자별 개인차가 크므로 개인 베이스라인을 사용했다.

* **ST(Short-term)**: 14일 윈도우 (요일 분리 split \+ global \+ LT fallback)  
* **LT(Long-term)**: 56일 윈도우 (global)  
* **Early baseline**: 초기 구간 대응(min\_periods=3)

  **출력:**  
* baseline\_ready: 정식 ST 기준선 준비 여부  
* early\_ready: 초반 사용자용 early 기준선 준비 여부  
* analysis\_ready: ST 없으면 early로 fallback 포함한 분석 가능 여부

### **4.5.4 Z-score 생성**

* baseline\_ready이고 quality\_state=GOOD인 날에 대해 Z-score 산출  
* Z-score는 안정성을 위해 tanh clip 적용:

  ***z \= Z\_CLIP \* tanh(z / Z\_CLIP)***

         **출력:** \*\_z 피처 리스트

### **4.5.5 이상탐지 모델 (Isolation Forest)**

* 입력: Z-score 피처(Z\_USE)  
* 학습 데이터: 최대한 깨끗한 날만 사용  
   (baseline\_fit\_mask & baseline\_ready & quality\_state==GOOD)  
* score 데이터: z\_mask 구간 전체  
  **출력:**  
* anomaly\_score\_raw  
* 유저별 분위수 기반 0\~1 스케일링한 anomaly\_score  
* anomaly\_flag (상위 분위수 이상)

### **4.5.6 최종 위험도 산출 (risk)**

최종 위험도는 Z 기반 변화량 \+ anomaly score를 결합해 산출

* **z\_score**: Z 그룹 대표값을 soft squash로 0\~1 변환  
* **a\_score**: anomaly\_score (0\~1)  
  **결합:**  
* risk\_pre \= 0.85\*z\_score \+ 0.15\*a\_score  
  **컨텍스트 보정:**  
* PARTIAL/DELAY/TRAVEL 시 risk 할인(risk\_adj)  
  **스무딩:**  
* user 단위 EMA 적용(risk\_score)  
  **콜드스타트 대응:**  
* 정식 risk 없으면 early\_risk로 fallback하여 final\_risk 생성

## **4.6 디코더 설계 (상태 해석 로직)**

### **4.6.1 디코더 목적**

* 점수 → 상태 매핑  
* 데이터/시스템 문제 보호 처리  
* 컨텍스트 보정 (여행 등)  
* 알림 수준 결정  
* 사유 코드(reason) 생성

  ### **4.6.2 입력 신호 구조**

  #### **System Level**

* backend\_critical\_flag  
* backend\_device\_state

  #### **Data / Quality Level**

* quality\_state  
* baseline\_ready  
* partial\_flag  
* delay\_flag

  #### **Context Level**

* travel\_flag  
* tz\_flag

  #### **Analysis Level**

* final\_risk  
* risk\_score  
* \*\_z (Top-Z 피처 추출용)

### **4.6.3 상태 체계 정의**

| Code | 의미 | 주요 반응 신호 |
| :---: | :---: | :---: |
| STABLE | 정상 범위 | low risk |
| SLEEP | 수면 리듬 이상 | night\_ratio\_z, overnight\_gap\_z |
| LETHARGY | 활동 감소 | daily\_event\_cnt\_z, Screen\_z, UserAct\_z |
| CHAOS | 전반적 불규칙 | hour\_entropy\_z, gap 계열 |
| TRAVEL | 환경 변화 | travel\_flag |
| NO\_DATA | 데이터 부족 | LOW\_CONF |
| CRITICAL | 시스템 위기 | backend\_critical\_flag |

### **4.6.4 우선순위 기반 판정 구조**

디코더는 다음 계층적 구조로 판단한다.

#### **System Level (최우선)**

* backend\_critical\_flag \== True  
   → CRITICAL

  #### **Data Level**

* backend\_device\_state \!= OK  
* risk NaN  
* quality\_state \!= GOOD  
  → NO\_DATA

  #### **Context Level**

* travel\_flag \== True  
* tz\_flag \== True  
  → 상태 유지하되 TRAVEL 보정 적용

  #### **Analysis Level (기본 상태 생성)**

* final\_risk 기반 risk\_band 생성  
* Top-Z 피처 분석  
* 상태 매핑:

| IF risk 낮음 → STABLEELIF 활동 급감 → LETHARGYELIF 야간 급증 → SLEEPELIF 전반적 불규칙 → CHAOS |
| :---- |

  ### **4.6.5 Reason Code 설계** 

  디코더는 상태와 함께 사유 코드도 생성

  예시:

* DATA\_NO\_DATA  
* DATA\_PARTIAL  
* SYSTEM\_CRITICAL  
* CONTEXT\_TRAVEL  
* RISK\_HIGH  
* TOPZ\_SCREEN\_DROP  
* TOPZ\_NIGHT\_SPIKE

## **4.7 운영 및 확장 고려사항**

### **4.7.1 모델 재학습 전략**

현재 모델은 사용자별 행동 분포를 기반으로 학습되는 비지도 모델이므로, 데이터 분포 변화에 대응하기 위한 재학습 전략을 설계하였다.

* 기본 재학습 주기: 주 1회  
* 학습 데이터: 최근 누적 데이터 기준  
* 모델 파일: 날짜 기반 버전 저장 구조 설계

  ※ 현재는 오프라인 학습 기반으로 운영하며, 자동 스케줄링은 추후 인프라 연동 시 적용 예정

  ### **4.7.2 모델 품질 점검 지표**

  라벨이 제한적이므로(no-label 환경), 다음 지표를 통해 모델 상태를 점검한다.  
* risk\_score 분포 (p50, p90, p99)  
* 상위 위험 비율 (Top 1%, 5%)  
* 사용자별 위험 발생 빈도  
* 연속 위험 구간(run-length) 분포

  이를 통해 아래 사항을 점검한다  
* 과도한 알람 발생 여부  
* 특정 사용자 편향 여부

* 노이즈성 단일 spike 여부

  ### **4.7.3 Fallback 설계**

  서비스 안정성을 위해 최소한의 예외 처리 정책을 정의하였다.  
* 모델 점수 산출 불가 시 → NO\_DATA  
* 시스템 critical 감지 시 → CRITICAL  
* baseline 미구축 초기 구간 → early\_risk 사용

  점수 기반 판단이 불가능한 경우에도 서비스 레벨의 상태 표현은 유지하도록 설계하였다.

**5.3 기술 스택**

## **Backend Framework**

* FastAPI

* Python 3.11

* Uvicorn

  ## **Database**

* Amazon RDS (PostgreSQL)

* Amazon DynamoDB

  ## **Storage**

* Amazon S3

  ## **Infra**

* AWS EC2

* Docker

* Amazon ECR

  ## **Authentication Source**

* AWS Cognito (Sub 값 기반 사용자 식별)

# **5.4 FastAPI 프로젝트 구조**

# **5.8 파일 업로드 시스템**

## **5.8.1 지원 파일**

* 이미지  
* 오디오

  **업로드**

class S3Service:  
    def \_\_init\_\_(self):  
        self.s3\_client \= boto3.client(  
            's3',  
            region\_name\=settings.AWS\_REGION  
        )  
        self.bucket\_name \= settings.S3\_BUCKET\_NAME  
     
    async def upload\_file(  
        self,  
        file: UploadFile,  
        user\_id: str,  
        file\_type: str  
    ) \-\> str:  
        """  
        S3에 파일 업로드  
        \- 파일 크기 검증 (10MB)  
        \- 파일 확장자 검증  
        \- 고유 파일명 생성  
        """  
        *\# 파일 크기 검증*  
        file\_size \= 0  
        content \= await file.read()  
        file\_size \= len(content)  
         
        if file\_size \> 10 \* 1024 \* 1024:  *\# 10MB*  
            raise ValueError("File size exceeds 10MB")  
         
        *\# 파일 확장자 검증*  
        allowed\_extensions \= {  
            "profile\_image": \[".jpg", ".jpeg", ".png", ".webp"\],  
            "meow\_audio": \[".mp3", ".wav", ".m4a"\],  
            "duress\_audio": \[".mp3", ".wav", ".m4a"\]  
        }  
         
        file\_ext \= os.path.splitext(file.filename)\[1\].lower()  
        if file\_ext not in allowed\_extensions.get(file\_type, \[\]):  
            raise ValueError(f"Invalid file extension: {file\_ext}")  
         
        *\# S3 키 생성*  
        timestamp \= int(time.time() \* 1000)  
        s3\_key \= f"{file\_type}/{user\_id}/{timestamp}{file\_ext}"  
         
        *\# S3 업로드*  
        try:  
            self.s3\_client.put\_object(  
                Bucket\=self.bucket\_name,  
                Key\=s3\_key,  
                Body\=content,  
                ContentType\=file.content\_type  
            )  
             
            *\# URL 생성*  
            url \= f"https://{self.bucket\_name}.s3.{settings.AWS\_REGION}.amazonaws.com/{s3\_key}"  
            return url  
        except Exception as e:  
            logger.error(f"S3 upload failed: {e}")  
            raise

**프로필 이미지 업로드**  
@router.post("/profile-image/{user\_id}", response\_model\=UploadResponse)  
async def upload\_profile\_image(  
    user\_id: str,  
    file: UploadFile \= File(...),  
    db: AsyncSession \= Depends(get\_db)  
):  
    """  
    프로필 이미지 업로드  
    \- S3 업로드  
    \- RDS URL 저장  
    """  
    try:  
        *\# S3 업로드*  
        url \= await s3\_service.upload\_file(file, user\_id, "profile\_image")  
         
        *\# RDS 업데이트*  
        await user\_service.update\_user(  
            db,  
            user\_id,  
            UserUpdate(profile\_image\_url\=url)  
        )  
         
        return UploadResponse(  
            success\=True,  
            message\="Profile image uploaded",  
            url\=url  
        )  
    except ValueError as e:  
        raise HTTPException(status\_code\=400, detail\=str(e))  
    except Exception as e:  
        raise HTTPException(status\_code\=500, detail\="Upload failed")  
\*\*요청 예시\*\*  
POST /api/v1/upload/profile-image/google-oauth2|123456789  
Content-Type: multipart/form-data

file: \[binary data\]

\*\*응답 예시\*\*

{  
  "success": true,  
  "message": "Profile image uploaded",  
  "url": "https://ameowzon-test-files.s3.ap-northeast-2.amazonaws.com/profile\_image/google-oauth2|123456789/1707724800000.jpg"  
}

**설계목적**

* 파일 안전 저장  
* 파일 크기 및 형식 검증  
* 고유 파일명 생성 (타임스탬프 기반)  
  **설계 효과**  
* S3 저장으로 확장성 확보  
* RDS 에 URL 만 저장 (용량 절약)  
* 파일 버전 관리 가능

## **5.8.2 검증 로직**

* 확장자 검사  
* 파일 크기 제한 (10MB)

## **5.8.3 저장 흐름**

┌─────────────┐  
│   Client                      │  
│ (Upload)                   │  
└──────┬──────┘  
       │ HTTP Multipart  
       ▼  
┌─────────────────────────────────────┐  
│         FastAPI Application                                                       │  
│                                                                                               │  
│   ┌─────────────────────────────┐             │  
│   │   Upload Endpoint                                             │             │  
│   │   \- 파일 확장자 검증                                            │             │  
│   │   \- 파일 크기 검증 (≤10MB)                                 │             │  
│   │   \- S3 Key 생성                                                  │             │  
│   └──────────────┬──────────────┘             │  
└──────────────────┼──────────────────┘  
                   │  
                   ▼  
          ┌──────────────────┐  
          │    Amazon S3                        │  
          │   (File Storage)                      │  
          └────────┬─────────┘  
                   │ 업로드 완료  
                   ▼  
          ┌──────────────────┐  
          │   Amazon RDS                      │  
          │  (URL 저장)                           │  
          └────────┬─────────┘  
                   │  
                   ▼  
            ┌─────────────┐  
            │  Response                │  
            │  (URL 반환)               │  
            └─────────────┘

# **5.9 FCM 토큰 관리**

## **기능**

* 로그인 시 자동 갱신  
  @router.post("/login", response\_model\=LoginResponse)  
  async def login(  
      login\_data: LoginRequest,  
      db: AsyncSession \= Depends(get\_db)  
  ):  
      """  
      로그인  
      \- FCM 토큰 자동 갱신  
      """  
      user \= await user\_service.get\_user\_by\_id(db, login\_data.user\_id)  
      if not user:  
          raise HTTPException(status\_code\=404, detail\="User not found")  
       
      *\# FCM 토큰 업데이트*  
      if login\_data.token:  
          await user\_service.update\_user(  
              db,  
              login\_data.user\_id,  
              UserUpdate(token\=login\_data.token)  
          )  
       
      *\# 친구 목록 조회*  
      friends \= dynamodb\_service.get\_accepted\_friends(login\_data.user\_id)  
       
      return LoginResponse(  
          success\=True,  
          message\="Login successful",  
          user\=user,  
          friends\=friends  
      )  
  

  **설계 목적**  
* 로그인 시 FCM 토큰 자동 갱신  
* 푸시 알림 전송 준비  
* 토큰 만료 방지  
  **설계 효과**  
* 푸시 알림 전송 성공률 향상  
* 토큰 관리 간소화

  # **5.10 주요 기능 구현**

# **5.11 배포 환경 및 인프라**

10.1 빌드 및 배포 흐름

┌────────────────────┐  
│   Local Machine    │  
│  (Developer PC)    │  
└─────────┬──────────┘  
          │ docker build  
          ▼  
┌────────────────────┐  
│   Docker Image     │  
│  (FastAPI App)     │  
└─────────┬──────────┘  
          │ docker push  
          ▼  
┌────────────────────┐  
│    Amazon ECR      │  
│  (Image Registry)  │  
└─────────┬──────────┘  
          │ docker pull  
          ▼  
┌─────────────────────────────────────┐  
│              EC2 Instance           │  
│                                     │  
│   ┌─────────────────────────────┐   │  
│   │     Docker Container        │   │  
│   │     FastAPI Application     │   │  
│   └─────────────────────────────┘   │  
└─────────────────────────────────────┘

## **현재 운영 환경**

┌─────────────────────────────────────┐  
│             EC2 Instance            │  
│                                     │  
│   ┌─────────────────────────────┐   │  
│   │       Docker Container      │   │  
│   │                             │   │  
│   │     FastAPI User Service    │   │  
│   │                             │   │  
│   │   \- User API                │   │  
│   │   \- Friend API              │   │  
│   │   \- Upload API              │   │  
│   └─────────────────────────────┘   │  
└─────────────────────────────────────┘

# **5.12.보안 구조 현황**

## **5.12.1 FCM 토큰 암호화 저장**

* class User(Base):  
*     \_\_tablename\_\_ \= "users"  
*      
*     user\_id \= Column(String(255), primary\_key\=True)  
*     email \= Column(String(100), unique\=True, nullable\=False)  
*     nickname \= Column(String(50), nullable\=False)  
*     token \= Column(String(500), nullable\=True)  *\# FCM 토큰*  
*     *\# ... 기타 필드*  
*   
* *async def update\_user(*  
*     *db: AsyncSession,*  
*     *user\_id: str,*  
*     *user\_update: UserUpdate*  
* *) \-\> Optional\[User\]:*  
*     *"""*  
*     *사용자 정보 업데이트*  
*     *\- FCM 토큰 자동 저장*  
*     *"""*  
*     *user \= await get\_user\_by\_id(db, user\_id)*  
*     *if not user:*  
*         *return None*  
*      
*     *\# FCM 토큰 업데이트*  
*     *if user\_update.token is not None:*  
*         *user.token \= user\_update.token*  
*      
*     *await db.commit()*  
*     *await db.refresh(user)*  
*     *return user*

  ##     **5.12.2 RDS PostgreSQL 보안**

  **VPC 구성**  
* Private Subnet 에 배치  
* Security Group 으로 EC2 에서만 접근 허용  
* 포트 5432 ( 내부 전용 )  
    
  **접근 제어**  
* Username: user\_admin  
* Password : 환경 변수로 관리  
* SSL 연결 강제

  ## **5.12.3 DynamoDB 보안**

  **IAM 정책**

* EC2 인스턴스 역할에 DynamoDB 접근 권한 부여  
* 특정 테이블(user\_friends) 에만 접근 허용  
  **작업 권한**  
* Query, GetItem, PutItem, UpdateItem, DeleteItem  
* Scan 작업 제한 (성능 및 비용 관리) 

  ## **5.12.4 S3 버킷 보안**

  **버킷 정책**  
* EC2 인스턴스 역할에서만 업로드 허용  
* 퍼블릭 액세스 차단  
* 버전 관리 활성화   
  **암호화**  
* 서버 측 암호화 (SSE-S3)  
* 전송 중 암호화 (HTTPS)

# **5.13 성능 고려 사항**

* DynamoDB 비정규화 설계

* 친구 조회 단일 Query 처리

* Timestamp 기반 정렬 최적화

  # **5.14 향후 확장 전략**

  ## **EKS 전환**

* Pod Auto Scaling

* Blue/Green 배포  
    
  **상세 데이터 흐름 다이어그램**

┌─────────────┐  
│   Client    │  
└──────┬──────┘  
       │ HTTP/HTTPS  
       ↓  
┌─────────────────────────────────────────┐  
│            EC2 Instance                 │  
│  ┌───────────────────────────────────┐  │  
│  │        Docker Container           │  │  
│  │                                   │  │  
│  │        FastAPI Application        │  │  
│  │  ┌─────────────────────────────┐  │  │  
│  │  │        Router Layer         │  │  │  
│  │  └──────────────┬──────────────┘  │  │  
│  │                 │                 │  │  
│  │  ┌──────────────▼──────────────┐  │  │  
│  │  │        Service Layer        │  │  │  
│  │  │  \- User Service             │  │  │  
│  │  │  \- Friend Service           │  │  │  
│  │  │  \- Upload Service           │  │  │  
│  │  └──────────────┬──────────────┘  │  │  
│  └─────────────────┼─────────────────┘  │  
└────────────────────┼────────────────────┘  
                     │  
          ┌──────────┴──────────┐  
          ▼                     ▼  
   ┌──────────────┐      ┌──────────────┐  
   │     RDS      │      │  DynamoDB    │  
   │ PostgreSQL   │      │  Friends     │  
   │ (User Data)  │      │              │  
   └──────────────┘      └──────────────┘  
          │  
          ▼  
   ┌──────────────┐  
   │   S3 Bucket  │  
   │   (Files)    │  
   └──────────────┘

# 

# 5\. 인프라 구축 및 운영

* 인프라 구축 과정 및 자동화 (Terraform, Ansible)  
* 로깅 및 모니터링 (Prometheus, Grafana, ELK Stack)  
* 장애 대응 및 복구 계획 (백업, DR 전략)  
* 비용 최적화 전략

# 6\. 성능 테스트 및 최적화

## 6.1 부하 테스트 계획 및 실행 결과

## 6.2 트러블슈팅 및 병목 현상 해결

## 6.3 성능 개선 방안

# 7\. 프로젝트 운영 및 유지보수 전략

## 7.1 배포 및 릴리즈 전략

## 7.2 서비스 운영 모니터링 및 장애 대응

## 7.3 보안 정책 및 지속적인 개선 계획

### 7.3.1 모델 개선 방향

* 개인화 threshold 자동 조정  
* 사용자 피드백 기반 semi-supervised 확장  
* 디코더 설명 로직 고도화 (Top-Z 기반 메시지 정교화)

# **8\. 비기능 요구사항 (구현 반영 내용 추가)**

### **알람 중복 발송 방지**

Claim 기반 Conditional Update 적용  
 → 분산 환경에서도 단일 이벤트 단일 처리 보장

---

### **서비스 장애 시 오발송 방지**

* 메시지 저장과 이벤트 생성을 트랜잭션으로 묶음

* 메시지만 저장되고 알림이 누락되는 상황 방지

---

### **보안 정책**

* Access Key 미사용

* IRSA 기반 IAM Role 인증

* Pod 단위 최소 권한 적용

# 8\. 결론 및 향후 발전 방향

**프로젝트 수행 과정에서의 주요 도전 과제 및 해결 방안**

캘린더로 일일챌린지(예. 파란색 찍기, 달 찍기) \- 60일간 데이터 유지 외출 및 협력 장려

에이전트 전략  
본 시스템은 위험도 코드와 사용자 관계, 사용자간 거리, 친구의 활동 시간 컨텍스트 기반으로 알림의 발송 여부, 발송 지점, 대상을 동적으로 결정한다.  
발송 순위 순서로 전화 호출.

보이스 클론, 작곡 모델

* 프로젝트 결과 분석 및 평가  
  * 향후 추가 개선 및 확장 계획

# 부록

* 주요 기술 스택 및 버전  
  * 코드 및 설정 파일 예시  
  * 참고 문헌 및 레퍼런스

  ### 

—-- 뭔지 모르겠음 —---

## 4 데이터 파이프라인

firehose

## 

## 

## 5 API 서버 (EKS \+ FastAPI) 회원가입 및 사용자 정보 관리 

* 친구 관계 관리

* 프로필 파일 업로드

* 푸시 알림 토큰 관리

* 사용자 로비 데이터 제공

##  

## 6 데이터 저장소 (RDS / DynamoDB) 

## 7 이벤트 처리 (Lambda / SQS) 

## 8 AI 모델 (SageMaker / 이상치 탐지 모델)

[image1]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAASQAAAF8CAIAAADpRlEhAAAoTklEQVR4Xu2da3QUZbrv93fX+XD2/nBmrb2Wy332/jBrMeJizziKgncZdWREx3GJHnRUdkAzGZBBGDMooBAyIkEyxiDiSBgFgUkIkQAJl3TuIYSQ0CEhVxKSdMiFhJCEXEzo87z1VldXv9Xd6XS6q6tS/996llbeunTqz/NLVVd3V/+LEwCgC/8iDgAAwgNkA0AnIBsAOgHZANAJyAaATkA2AHQCsgGgE5ANAJ2AbADoBGQDQCcgGwA6AdkA0AnIBoBOQDYAdAKyAaATkA0AnYBsAOgEZANAJyDbFKjvGvympPX+rQWz43ItW7T7FAJFIaYDJgOyTU7z9VubT9Qr3Rabcfkfpe2tN0a7h360VNEuF17po91XorgnLpfCEfMCPoBsk9A3NKb01g5bc1nrTW0XWq0oBIpCiYUiElMD3oBsPukeGOXNtPx7u62hV9tzKCoKh6dEcYkJAk8gm08eTyymHlqQVKLtMJS6KCIKiuIqaLwuhghUQDYv7C5qkf9aaxoL5at4YhSdmCZwAdlEvjvXRk3zWGKxtp9Q/qvwSh9FRwGKmQIJyCZC7TJ/e1Fx8w1tM6EmLYqOAjxd2yPGCiCbwNLvKnH2OM3i55NisgCyqdlVyJ6qfXSiXttAqMDrI+k1SQpTzNfyQDY3uCgSqjpZ24ODmxbIJhN9gL1eVHVtUNs6qCCKwqRIxZStDWRjVDluUnNsPF6nbRpUcEVhsj9ejpti1hYGsjH4e4u1HYOaTs2W3rUsZm1hIBsDz9bCUbgsKQDZGNQTfzh0SdsuqOkURQrZ1EA255GL16gnwv0qNv8zT/X6odraATZiP1qoDCrH1Xel6TJpAVbFZbM/v2iXpt3Lx+euPVpf1jvssfG99Wy64eILcbkP7KlVZrG1+CxeAzejv8jn24lOU42HoShSehSKV0zcqkA256enGv87Pk/bK6Et1t+f5C9IkBr984vdLnlohBdfjMv2wjGHvKIgW7y08DaunLyKvHGVbLPj3LM8ZOtu/DiRrcs28ilNlCmLhakoWIpXTNyqQDbn73afX/69XdsooS2m0FGmUFkGc6zbJZuwmCQbG7/CRwTZ3Meo3rQ9+bO/kY9ggmxr9+W/kNHOZ6nXUjzXrShYildM3KpANue9n+THZdVrGyW0pciW/T07uHWLp5HyQYbL1n2pYvan5bYBP7LRCWEtW9K1cbVsR/nIl9UeazVcnJ1QUaz5xcJaFCzFKyZuVSCb85643K2nG7WNEtqSZeu78Qg7A2SfkfM8jSzni8myDQ2zWWkt/mQbqvcj294v5eeBHrK5NqVIrtpaWIqCvQfXSFxANv2ObPScbfHXZcUd8oUNP6eRNHGlsPSBuFw7HeJ8yUYeJlS4N+4pG+lK56uP7KuvzS2RZ12vmR1X/FWbx6+kfuhwFI5saiCb87EdxbEZl7WNEtqSj2yqEf+y0bOy77/Off1AuXfZBto/+9y9QW+y0TIts+PyPzxQ6lqLvUvmkQNXlMfSPnrIi4KleMXErQpkc8YctD/35Tlto4S2fMnm7WqkfHLI1/JyNZJdSMz9xRfyYU1eTCvb0I9H90kXP12KXjlfvjBevhr5gDShbCFMRcFSvGLiVgWy6fQ6mwULr7MJQDZnY/cQ9cTu4lZtu6CmUxQpBUvxiolbFcjGoJ745dYCbbugplO/lN7eLWZtYSAbgz2xCf8TGKsVT1XM2sJANsbH0oevKtsHtB2DCq4oTIqUghWztjCQTQaf1A5tzcYntTVANpmzzeyehzq84GaRojApUjFlawPZ3OCZW6jqxd1leLamBbK5wa3sQlK4lZ0vIJsHzddvUaOcqr2u7SFUIEXRUYBzP8WtR7wA2URwr/+gC/f69w9k8wJ/8na8plvbTyhfRXE9uI2921NME7iAbN45WO6gvvnzkZr2fst9ne9UiyKioPhfKDFHoAKy+QRfhhhg4csQAwSy+YOOb/zUCGeV2qJAog9WUTIUEQUlZgc0QLbJab5+a7N0OZtXbMblf5S2t96w3Okl7XLhlT7afSWKe+JyKRwxL+ADyBYoKWfZB0bU9ZudpYu/KV+SUjHj67W9FbSzwu5TIH1DY2JMwDeQLRjquwZ3FbasSr20bP/FN7+t1LPiPtlGpR0Pd9HO0i6fqO4SswABA9lMxmcS4igwA5DNZEA28wLZTAZkMy+QzWRANvMC2UwGZDMvkM1kQDbzAtlMBmQzL5DNZEA28wLZTAZkMy+QzWRANvMC2UwGZDMvkM1kQDbzAtlMBmQzL5DNZEA28wLZTEZYZWs8mXyorJ9Pn/08ik+U71ntwSfZ7hXAVIBsJiMQ2aI+PysOBUb25qjV3zU6suLJqZXRsmwCUevSxSEQGJDNZIRVto9joqNjEp0j/f29/TnbPWUrTeS3GYlKxA1YgwSymQxfsvGzPsfh9LOybI70z9khyHE4liRJjIpNb3emr4uKikqkZaOkH5UTRU7y2qjuCadzoj86Zv2+y2OuuY3JXyazil+dwCe+TC7vVa8HAgWymQzvspUmqs/u5CMbDUqcVcmWWMrmxB6WjlKug5Wb/sbyY/sko/aNTajGJ8YKCjPTzxQUVF5VjYKpAdlMhnfZ2tNj2SFLhsmm6NfOjnUByrYyJjbxcE5/r6OmLCd6VbI8ejV9fXR0ZmFBQWFO+pcfJ5fiO7KDBLKZDO+yMRzsKLYu3SEf2c7y41rs54lTkG17ztUReTohZiWfaNy/Onqz67A51h0Vj6uRQQLZTIZv2UJAwZ6PY1dGsyuRy6Mz7fJrAPQszn40MTpmJQ1Hr4x14O51wQLZTEZYZQNhBbKZDMhmXiCbyYBs5gWymYN4H4jLAQMD2cyBKJkLcTlgYCCbOaiurhY9i4+nQXE5YGAgm2k4evSoIJu4BDA2kM00NDQ0QDZTA9nMhNq0rKwscTYwNpDNTKhla2lpEWcDYwPZzEROTg43jSbEecDwQLbgGb5RNdRTMtiVp2d9teNtKu14uIt2Vtx/MEUg25Tprt3eWvL6pbR/q/rn/7JU0S7XZ99Luy8mAgIDsgXE6OCVmh/+Q2m72syfdlx4t+/K32+2/XPAkW6Fop2lXb5a8LwSAgVy7eIHYlLAN5BtEroubea91Zz79O2R9tujHShWI+0UCE+GIhJTA96AbP6oz76P91Nr0Utit6FGOwY7Mnk+FJSYHdAA2bxze2KEt1F3zWZtk6HURRHxrK4WLxFzBCogmxfGbrU1nnmUumeo86S2t1DaoqC4bxSdmCZwAdlEfhy+xvtG21Io/9Vx/g+UGwUoZgokIJsItYuj7G1tJ6ECKYqOPcUt/R8xVgDZBHrq/oZj2jSLnxeIyQLIpuaKjV3LHnCkaRsIFXhRgBQjhSnma3kgmxs8VQtVXat4Dwc3LZBNpqv6r9QfvY27tK2DCqIoTIpUTNnaQDZGb+PX1Bx9TV9pmwYVXFGY0h+vr8WsLQxkYzSeeRwnkCEvipSCFbO2MJCNgWdr4ShclhSAbAzqiYbsX2rbBTWdokghmxrI5hzoPEM90X91n7ZdUNMpipSCpXjFxK0KZHO2nVt2+Yf/0vbKVOt40h3Hd9516uu72ETKJj54JumOrK9dg0l3jLsWLv07+5GW5+NltXXKdkabt7o29ZPjSbOFjZ/6+teXHNKSN/YfVzaesqlTWiwrmW2NP9yZnFJlXT7RmTObbWfXG67HKqUfiy/IjzvesoP/MrR61k73LkynKFiKV0zcqkA2Z5PtV005j2kbZaql9HfxLtayfJBkq5cmOnPupcH6Yb4w6/K6tmY2PVhad+Snx3culrfTuulM8h1ZB+VGv5rzR2HjSnWc/OnxlA/4dM3JHZJsBWyxkwU0Mtq2o7zIh2xu5z1ko187K3VH5035x/JjO9QPF1xRsBSvmLhVgWzO6iP/3nH+D9pGmWopPvCe5oOKbLe7d9iS7qjpZ9P1aXfY8i+q181KuqNdmqBljic/72fjSrFH2eVSVC4mT1ZainZd9ypJdwxdWOw6Eqpk697h9XGnWRQsxSsmblUsKptt7ix1dV58X9soUy3Zh8G6LCbME3zQ4zRyDz9MlVak3FHR6rFusctJtljafq8bl08jv9/a7RqsOyIdqZLvGnKNjLallO5hx64K1XmpIBtN2OhsM/nXHrKRga7HZdtkJZ/BTqcoWFwjUbCKbG0H/mFf/Y7yY96jPy/+zaMV77xetSbmbMxd1yrXaBtlquXqUdb9xRfkXj/jGsxKTbkhLynJ1uKxbqFatlTx0MTHhSMbr/JDTOOstP2Kb7dHm/O/pkf8ifI7aGXj57RDgmyux5WeGd4VEtko2Eup/1v172BpZrhsrfu+4ceulr1fDdTViLMlao/f3VryirZRplpefVBOI0vZE7l/5YPD554/vmuZarE6xYdy6cKJch1FKa8bd5XHUy9ekuTySaZWNqrxxvfod1CtyJ7veW4zBLJRsBSvmLhVmeGy3Wq5cu6V50a7O8UZKkJ+gURdimzD9jfo9LLuhjQ+zDq7uVN1gcR1hZCeUNFitpPyJw+afV8gaTr5BndyvGUTaVxaTdP7lcsbx9lp5zJlmk+oZZOXUVlKj1tYUjDML+EMng6JbLhAombGyXb7dtepE3Qo6ys/J87yQXftdnpeMXbTru2VKZXWh9vqCyRUnTvo7E6eHiy17f5X1u67ZtuOieeNZfvky4bFObJ1/Ede/FFuVG1iF+jpHHLPEzfli5wXbXvuYlf/k39iv1ynHB59ycaulHgeEivS7uXbPL7rrpom97O+4IoipWBxn0mFGSVbbfwG0qxq7R/FGX6Z+HGAeqLjwrvadkFNpyhSCpbiFRO3KjNKNjLtenG+OBoAeLtWOApv1xKYUbIFDd6IHI7CG5EFTC9b79lCKnF0iuAjNuGoKnzExhNzy1afEJc7b3bniR/EGVPl9kTND//ReHq+tmNQwRWFSZFSsGLUFsbEstVuWV/49DxxNFj4LZDrjt+t7RtUEMXOFCZGxJStjVll6ynMtc2dNdTcJM6YBnjmFqq6hhv+eMOssoWDW73lOLhNvyhAipHCFPO1PJDNA9ykdfqFi5C+MJls14vz2dljyxVxRuhosv2qCq9xB1sUHd6f5QszyTY+NEimXdmdJM4INfXZ91LTtBYLnxZD+SuKq4p9Udu9YprAhZlkq1oTUxnzljgaBvCVUVMtfGVUIJhGtr7ycwW/ekAcDSedri/4xd3//RS/sz9VJ77sdzJMI1ukwHdqey98p/bUgWyT016+gndVdfr/aS15ZbS/XOw8KxXtPoVAUfBMKBwxL+ADE8h2efO6qvcN8S/aWvpm9ZF/501m5aIQKAoxHTAZRpftRsV529xZwx3t4ozI0V27vbXk9Utp/6btQh1q29aNVNpxHYp2uT77XnwYNGiMLhuZdu7VReKohflMQhwFZsDQsnUcPVz36SZx1NpANvNiaNmc0gvZ4pC1gWzmxeiyAQHIZl4gm8mAbObFoLKVvvzszUsXxVEA2cyMQWWzzZ0lDgEJyGZejChbT35O5Yql4iiQgGzmxXCyDTbU4bDmB8hmXgwnG3Gr7ao4BFxANvNiRNmAHyCbeTGWbB1HD4tDwBPIZl6MJNvERNGzD+Mc0j+QzbwYSDb7n97GpZFJgWzmxUCy2R74WQjvcDxTgWzmxUiyzZ11q+WKOAo8gWzmxUCygUCAbOYFspkMyGZeIJvJgGzmxRCy3ay2482QAQLZzIshZGtM2uZIPyiOAm9ANvMSedkG6i/j5bXAgWzmJfKyXfnqc8gWOJDNvERetvbU/fXbcP/qQIFs5iXysoEpAdnMC2QzGZDNvERYtitfJg7UVoujwDc+ZHNkf7Ka/b8jO351Cv2YWOo5+3BsVGKBx5BCb3mja5IWOsunOrJXe+JaBARPhGU7/8ZLeD/klPAlW/q6KPb/9nQSRisbzY1anuAxpNCeLgumlm1irL+331U1+96XNg6mR4Rlw3XIqRKgbAlnmCc00F2dszomun+CzYyNjl69OWXIY0Wn/avo2MMOp5PZ5ZZNgrYpSWvfHROrGgZBAtlMhg/Z+ssPJid/ySvbfWQbkY9ONd/FRm3PkY9U/WPySmOOlcvX77s8NNaYvj46utt1ZOsvO8Q3tT4manW8a7MnlZNNECSRlG381lDRsw+Lo8AvPmRjFBQWKFXTw0YcWfHCUy/GJ9nyChON5Z2ulcfINVm2oavl6k3JdZktAKZDJGUDQeBHNvWzLPVztvUx0QnS0Sk6Onr9Hrt7BjFxNX1DdGah/Wpvf8GxlPVHlHtSDEWv+phrlrAuOnpDunolEByQzWT4kS1qbbzrTDI5Wznp680+pBg0Zk9Z7Xmpoyw56v1Dyk+rY3bLLran26WneRLdmR/jAkkIgGwmw59satalO1zjKZtjV0rnjys3JKaXi2eDQ5czo5dH0wJRMasdrmdzTvdaK2mtTDu71gKmScRkq92yHldHgsCPbMDgREy2std+C9mCALKZl4jJRqZdfHeZOAomA7KZl0jK1pXjugYNAgaymZeIyVawYO5we5s4CiYDspmXiMkGggOymRfIZjIgm3mJjGy3WlvEIRAYkM28REa2/Md+IQ6BwIBs5iUCso319eIVtqCBbOYlArJ1HE2DbEED2cxLBGRr+mI7ZAsayGZeIiDbxOjIYGOdOAoCA7KZlwjIBqYDZDMvkM1kQDbzEgHZip97rPPkMXEUBAZkMy8RkM02d1ZndqY4CgIDspmXyMg27MBbkIMEspmXCMhW8KsHxCEwGfE+EJcDBkZv2cZvDZ175TlxFExGWlqa6Fl8PA2KywEDo7dsIDgmJia2bdsmyEaD4nLAwIRIttGbfT3dmro5Ki4HgqehoUGQTVwCGJsQyXZ2a94LC1g9/d/yBKutTeJyYFqoTUtMTBRnA2MTItl6csu2fMBqxQJ5YssHF4vEWxQ62R3sPuwtLRJHQWCoZWtpwWcCTUaIZBuvVhzzL1vV+ysGLl8SR0Fg7Ny5k5tGE+I8YHhCJJvTefG1BXWnT8p1cI0XzyTKlrzw403cXjdIOjo6uGw0Ic4DhieEsr2o+im3QfWDmsKnHhSHzEZy0aF30uL+c8vCOzc9bamiXX585zLafTEREBghlG2Wba67fMlme/Buccg8xKT/ddbWF7VdaLWiECgKMR0wGSGTbajvpuqn7uuqH8zO+8f+xpvsp588vyxt88XrTV1j/ZYt2n0KgaLgmVA4Yl7AByGTbaayLfcfvKt+992aa6M3tM1nzaIoKBCeDEUkpga8ESLZlNfZXljQlL/G9vD9to25ZXPX+DqZNAUJLs0y64u03YbiReHwlBKg3GSESDaF1hInybYxt8CHbKa4+4ijv/s3f19JDWS7ekHbXihtUVBcOYpOTBO4CK1sN+s+vH8GyPb4zmXUN1Gpm7RdhfJVFBeFRtGJaQIXoZKtu2rXGtvyHa0DTrPL9mLKamqav2R/oe0n1KRF0VGAYqZAIlSyVZcufbho68nOUZdsy7cWmVM2apc/HduubSNUIEXRUYArj2wVYwWhk41zs2Hjwz+Kgx5UvPO6OGQYKh111Cjzk97U9hAq8KIAKUYKU8zX8oRWNnPDn+Jruwc11Vp/aiclKeZreSCbzOj4GA5rISwKkyIVU7Y2esvWd75UHDIAE7dvz0l4+Zm//1HbNKjgisKkSClYMWsLE1LZRkdGnc6CjbniuApjXiBZ9M0qnECGvChSClbM2sKEUra+I2/m7ajgsjV9u9XrB2mMKRuerYWjeKpi1hYmlLLl/W5HOz+yjec2jTuL3vhG+24Cw8r2xK7l2nZBTacoUsimJmSyjTbuq6hhE0y21m9+dDorXjDH62yDo7fuxKvYYSiKlIKleMXErUqIZBsfqdqysGlgZKCnm8lWs8PJPuHmRTYDXiBJLjpEPXG576q2XXSuRvt3s+KkD4ztWMFHotQfJEvcQyOH97LpLU3KWidpmYRmNv2wemFWS7UPoWdRpPRr4MOmCiGSTaL82VeqOvkFkuqy0215W0v8v8BtEF5MWb0oZZW2V3Su15lmv+XTjfYkPqGIpBSXjeq3p1qkEbdsvCoylz6cWa1eJYJFweLdWwqhlK01eUHR/jZ+gaToyVkNA+ICxmTe528sS9usbRSdSzourRcGfcn2JJkZzxc2tGwULMUrJm5VQikbp6lGe1nEjQHfrvV/457dcHqXtlF0rorst9khKyF247l6ZVB9GskV4rJ1jVRu/OzpP1X2G1w2CpbiFRO3KqGUrbVTHNGS//gvxaFIQ727KWe3tlH0r0b7Hu7VAYc8QiL916eL5ySwWnyKSSjLRnMrt9/5WZLBZaNg78QFSRchkq0utWzLBwUr2O0i26XpsiPVXj9iU7p44cTIiDgaUWZtfXHt8URto0SsRuqpQdukaV+nkXw6Kp7mVm5MMK5sFCzFKyZuVUIkm5r8NQXfsmduXmW7uGr5ULOx7kpukAsksZlFNYN8uoN0qpEG/cvWNdbCj4SGlQ0XSNSETDbl+zT8y1a9fk1/VYU4GlFWZWz7+fZXtY2ic0kXSJ5jZ4zxT98Zt5gPqk8j5ySs7hJl62dXSgwsGwVL8YqJW5WQyeZ05rKnbPlr/MtmQPKayqlfU2tytL2Cmk5RpBQsxSsmblUgG95BEq7CO0gEQiVbd9mWN0ulb7FxdlY3NY80sZv+V5vlVq38mY+2XVDTKZ6qmLWFCZVsgTLW11v2uuEuT+EjNuGoO/ERG0/0ls15+3bRs4+Ig5Hm2/OZ1Bl7K49pOwYVXFGYFCkFK2ZtYXSXTXrj/2iPv3eZRITE/H3UHCkVmdq+QQVRFCZFKqZsbSIjW09+jjhqAPDMLVSFG/54JTKyOQ4fEEcNwEt72TdF4M7+0yx+938KU8zX8kRANiOzqyQNB7dpFi5C+gKyidyJOyJPo3BHZD9ANpGuwV48eQuu1h5PZLkN9oqZAokIyFb36SYD3olEDb4yaqqFr4wKhAjI1ro/xeCyOV03SKZKKPxO21sodVFEPKvlqZvFHIGKCMg21NxkfNk4T37JbsZG9eahjdomQ526co7nQ0GJ2QENEZDt9sRE7oN3i6NGBd+p7bXwndpBEAHZiKadn43d6BNHDUxLb8echJd5b1Hdl/jaX7K/2GfPyqjNP9ZQPOPreEMx7Szt8pLvP1BCoEDiTn8tJgV8ExnZTE1y0aF30uL+c8tCpe0sUrTLj+9chvtABg1kC56azitlrdVFzZVWKNpZcf/BFImYbJfjPjDXmSQA0yRistnmzuo9VyyOAjBziaRs1RvWiqMAzFwiJlvBk/fbzPMCAADTJ2KyXXx3mVle2gYgJERMtrHe60a7NTIAYSVisgFgNSAbADoRSdmGO9ovLH9NHAVghhJJ2YjcebPFIQBmKBGWDRckgXWIsGyFTz04MYprksASRFi2S+tW9ZWViKMAzEQiLBsA1gGyAaAThpBtuL1NHAJgxhF52exr/oBrksAKRF62joxUyAasQORlIy4sX3KzpkocBWBmYQjZ2g5915i0TRwFYGZhCNkAsAKQDQCdgGwA6IRRZJsYHcl/7Bd4nySYwRhFNqf0CYDOEz+IowDMFAwkW+nLz9oe+Jk4CsBMwUCyjQ8O5D00Z2J4WJwBwIzAQLIRdVs/GuvDl8SCmYmxZANgBgPZANAJw8k2cq3j0rpV4igA5sdwshF1n25q/manOAqAyTGibKPdnQVP3i+OAmByjCibU7qfJL4JAMwwDCrbSOc1cQgAk2NQ2QCYeUA2AHTC0LLdart648I5cRQAc2Jo2ZzSRwHaDn4rjgJgQowuW8Nn8Ya991bv2aL21P2XP46tiHmrIvr3M7Ni3qIdbEzaRjsr7j+YIkaXbWJ05OyLT107dkScETlGrjkcRw6VPP8k/RWwVNEuV3/4Hu2+mAgIDKPLZhwGLl9Sd17V6ujrp07culw9cb3HCkU7S7tc+NSDSgIUiJgR8AtkC4iB2mqlyRq3b+krytO2o0WKdl+JovqD1WJSwDdmku3K7iRxKPx0Zmfyxrq8Ya2286xcFAhPhiISUwPeMI1sI13sDZNth74TZ4SNwaYG3kyOA3u1rYbiReHwlCguMUHgiWlkc7Krf4W58+/R7alCwYK51EOVK5ZqOwylLoqIgqK4rpcUiCECFWaSjah6fyX9u96emBBnhJSuU8f5X2ttY6F8FU+MohPTBC5MJhsxfuuWOBRSlKuO2n5C+a/OjH/acJXSN+aTLdyUvvIcnqcFXRQdBTh+a0iMFZhXtltXm4sWPiqOTpv21P04pk2z+HmBmCwwtWyFz8yv2/qROGMaDLe35T00p+T5J7QNhAq8KECSDV/drMWssnHOvvRMxTuvjw8NijOCAk/VQlU1H76Hg5sWc8tGVES/Ub1+jTg6dbptp6g/mv72qbZ1UEEUhUmRiilbG9PL5pTerCwOTZ2KmLfyH7t3rL1V2zchKX7YpCr5a1pXFxu5tmuRMqgcUcv4y+jSAqyOrbC9mnRNmnYvP+++sl1HHe2eG489yqarkgrmzsr7c5oyi63FZ/HqcpT+fr60nTmlO1TjoS4KkyIVU7Y2M0E2hfwn7nPevi2OBkD9ts3Uf0OX7NqmCVXR9gt2se2XPSOrxeURFpNku882b4k8Isjm0qZ2wzO0bmWle+Mess2d1ezSVb1W5RL20I0NDv5jzYbt8qOEoShMeiwKVszawswo2ehf98Ky/zfU3CTOmIzCp+dp+z60pcjm2Mk8mfAnGxvv4yM+ZJu43lz75/ts78lHMEG2sg3zC3aeH9WsxRZbkiQ8YviKHo6CFbO2MDNKNqLzxA9nX3wq79Gf36g4rx5vSdl162qzekQN60JN34e2FNkaN92nls1VK/hiXLbRs/G2Z9axo5NP2eiEMI2WVDaulq2ej0SleKxVlWRbFH9V84uFr/iuiVlbmJkmm8CPAze7c9nT9Iro3yud3XE0Tb3MmNQWV75I0LZLCMvt1bz5ZceaJ/we2dgEO9tc5E+29u9tc+WzTa1sNFE0b1btVU/ZXt7ukJbPW/QElfbRQ1sUKT0ExatO28rMcNn4i9S1W9arZaO69JdVXadP8GV6Cmw00nsmS9suISz2uE/ML1q1pq1JHvEvW9/RFfTU6xod4nzINkoeLop3b1yQjZ2vLsrbcLQn7W15FpPzJXutx6+kTIejKFJ6CIrX89/Eusxw2TjXMtNz581Wy6auc4sXFi98RNsroS2b6zRSKf+ysapNYb+hN9kuLJ1jU1209CobVR7fR9dadKyzzZ3Tc02a2+XQPnrIi4K9/HGs+O9hVSwhm9PzNFJbF/7nFW2jhLZ8ycbP6Kj4oIds3CK1bA/dxxZ+iplmWyof1uTFvMlWv0G6yu+Src+2rkDyLW/RfBubCLtsFOyFt18X/zGsCmSblffQnLq4D7WNgpp+UbAFC+aK/xhWxaKyqZ+z2fDGkbAVBWvDBUkXVpRNuBqZ++DdTTs+0TYKavpFwVK86rStjFVk8/M6W9HCR3EznzAVBRuOT0KZFKvI5gf7e9Flr/xG2yio6RcFS/GKiVsVyOZs2PHXvIfmaBsFNf2iYCleMXGrAtnkm444Dn6r7RXUdIoiteGWJCogG8OGe7CGofhdXMWsLQxkY/CrlNp2mXHl6G9oHqjM1oz3TNQWiyPTLp6qmLWFgWwM/sKAtl10KOFtJd6rKkl5U0hA5bk82VV7JK3267evXT9aNnfFtV3ud6i4H/2Y/LGDEBZFSsGKWVsYyMZwHDlEndGZ8U9tx4S7dJCNV8/elyaYbC/Z/6zc0ciRF5crT4daNn4PSQpWzNrCQDaZpi+2U3NcP3VC2zdBlvQ2RZoomLuosqqnTPov9fQ16V2OE9ftZcfYYt7eMCl9xEa1vCIP36A8SIcO9Sdurvfw5dlH4zSyVS69r2jXeUk295HtwpL5PfuW2JZI77EMtWwUJkUqpmxtIJvMaE8X9ceF5a9p+ybIYrKxDq58dRZ55RLjqKSBvXKX3NxeZJOW9FjeLRtfi2+kh+vqWUwnQba2A+tK9p4fds3lsg2d3V6yj/Trcex761JtWGSjSMWUrQ1kc1P064eoRcY62rWtE0y5ZKuPZbJ5SmUvi5UPL75k8xgXZespoGVEPY6yI5s32ai60lYUPPVE2YY1VHlLPpIH977lXkbcWvBFARY/9ziFKeZreSCbB/b3okN2pcRTNukET7rmyc/02N/+FfXSmaFyT4QJ9YfWlOWlcZv0CR1FNrbYq+LdRNjysSuYbJpP9Fx4YX7ZkTo+bY+ar2ykt6FOKenQF4Liv7aYLIBsAsPtbdQoN8tLtT1kqCJPArqy4qrRplz7hiV5C+fnPTX/whF5RTqyKZ+mo2rUrBVEUXQUILvNGdAA2USadu6gdqmMUZ1iGazkQ6Vm3AhF0VGAYqZAArJ5QX3+hgq87H96GyeQfoBs3uFP3sJ629aZVPyWrDDNP5DNJw2JW3GIC6R4ShSXmCDwBLL5g7fR+SXPh/LF7plVFA6OaQEC2SaHNxPVjbNF2m6zZlEUSixiXsAHkC1QqqXvHGP1wM8qVyy9WXZW24Izu2iXW/d8SbvPc6BA+i9dFGMCvoFsU6AxaVvRwkeVv+gXli6+vGGt48De3jNZvbZTM7POZNEONid/Rjur7DiFQFGI6YDJgGxB0pGRemH5Ev4OLysU7Szt8mBTgxgECBjINl2G29tuVJzvO186I4t2jXZwfHhY3G0wdSAbADoB2QDQCcgGgE5ANgB0ArIBoBOQDQCdgGwA6ARkA0AnIBsAOgHZANAJyAaATkA2AHQCsgGgE5ANAJ2AbADoBGQDQCcgGwA6AdkA0AnIBoBOQDYAdAKyAaATkA0AnYBsAOgEZANAJyAbADoB2QDQCcgGgE5AtiDpHx531NpbesVxp3PY26BPhttr7c194qiIz20GsO406fP2AMO07+IYmAzIFjAdJQcVTldnlDhKMg6erpFn0g+u5RzqwdNnTrurqNa1DJvp3ppMRkmHam7aYY60jnubjI6Satck/SaqGSpqTtP2hLEMj4fwSm2+/LCH2a/PFq7mD3Ba+TXZI7J991wRTA5kmxLDFVlykwmytRQcdi3jIZtr0AuD9fkZqancw9TUVM/vifG0S/ixOT842QKgmlZzTXvI5mI483wfZAsOyDYl3E12+OS57MOKbH3lxw46XMsEKBtt6kTFoPzDQMW5TvVMUbbMAru9Sj5z6zufqRygRNlq5COQIhv7jQ/Kvycb6mAj1dJStKa8sBsP2bJL6UHdYjPo9+xhsyBbEEC2KUAtlpp7ztYw7vQ8slXTkSm3/uAPJQ42x+0Jez5WZc88eFjqWqoWZVOM8f6WikJ+znbafWLIEWVTfhysOZ2aZss8lFHSzh7MUzbVWp5HtgxpOUU2PkgOSv+vVp1b+juy9VfRQ/NVIFswQLYpkHEos7zHmZqWXdE9rpJt/GDa6eoBZ8kPB1NP2zWeyC0uwD1UVx9xQzmXdG1kbLCtoaVPtc0MepCaQfbYUt97yqbSRpFNPtZ5kS1DttGrbGN9A4JsY6kHZcMhW3BAtsDp4Y3GUWQb71Yfr8YUT1pcFqmObF6uXkpb8fG8y41LtnGP38EpysYOVuznjhIum7LxgGVT4yFbflmTxyzINnUgW5DUtg+rL5CoEI9s/pmabBoCWDdohh23nJoLJBzIFgyQDQCdgGwA6ARkA0AnIBsAOgHZANAJyAaATkA2AHQCsgGgE5ANAJ2AbADoBGQDQCcgGwA6AdkA0AnIBoBOQDYAdAKyAaATkA0AnYBsAOjE/weKtLPTh/VNlAAAAABJRU5ErkJggg==>

[image2]: <data:image/png;base64,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>

[image3]: <data:image/png;base64,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>

[image4]: <data:image/png;base64,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>

[image5]: <data:image/png;base64,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>

[image6]: <data:image/png;base64,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>

[image7]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAQkAAAI9CAYAAAApa41CAACAAElEQVR4XuydB5wkVbX/ZzYv2YiAT+D5fE8FRPmrCCiPICgoWdAnSQkqCAsLEhckrcAuS84iWUAlZyRnNszMzgY27+ScU09P7PO/51ZXd9U5t7qrqqur7/TW5fOlu6urqrtn6/ftc2+FLmmPbYRc6eivhUK3qqoquPXWW6GmpoY+5bsNDw/D9ddfD/X19fSpUNrg4KD8PMrPlBiH+j32gERJifZUfeFzAGPj5htPfQTzs/X396emFbLd9s+b4ZYnF7jmjcX/pqvQqvUNtkFXrN4f8YYUJTTwnhmoFpIoTIisrbm5GW6//XZYu3Ytfcp3GxoaggULFkBbWxt9KrTmKAlsa9awQOoIlJfRdy5bxs9WgOZOEvPhkZcepItq2TxLwiKG4CQhBKGLJDo6OuDOO++ElStX0qd8t3g8DjfffDN0d3fTp0JrZpBQgqyJb+eRSZNEEEtZMHVhtHSSeJ9j9J1DV1fXhJPErf+6EbqGOuhi2jZPkhAy6BjigvAniaQYJMnHaUmYJWX4DUvWu+66C8rLy+lTvhuW+7fddhsMDAzQp0JrIyMjqTAlEulS3WwNu+zCgqkTzTvumHqv1ndvfqa+vj7L1MK2TJKorKoQ779w27efllUSCiEg3YN23EvCKgeCDpUEhumee+6Bjz/+mD7lu6EcUDyjo6P0qVCbGajxccVGOjwMndOns3DqQP/UKQCxGH3HsulWRWAzJDHfJoc7n7ptwsnBbEpJKKTgJAf3klBIgaKDJLD99a9/hXfffZdO9t2wJL777rvp5NCbqsuB38rGN3MCBq64kgVUB7p//Ws5wEobjvHoK4kbUoJYur4C7PXPxGq9Fkl0DjoLgkqBopaEQgSZ0EUSDz/8MLz22mt0su9WW1srxVPoZu1yKKsJEcTWmZuxkBaS7mnTxPviAcMuk/lZcGBYl4bVgtndePqdf4nHOI6i+FtPoCYrCYUQ3MrBWRIKCWRDF0k888wz8MQTT9DJvtvixYvhgQceoJML0sxg1dXVkbEJY0MeKytPDmJiSM3bwoCDlcPPPqf8Dm5sbNSyisA3i5JYXr2cPmM01YfRvPXF25kkvMjBLglF8L2giyRwA8TjJdrb25WDfBinP62ogS1fWARbvLgINn8BWZi8XQRbPr8QXujsl9vDsmVL4YYbbpCh1KFZv4HHFHsLZFu2DMZLJ0OitHB7O8ZLSwA+/ABUqXL1GaIWWLNKggbfCyU08H7QRRLYXnnlFXj00UflYCOW5jh6bgqjon8QJr1cDqWvLpWUJG9LXzWm4eMthDT+/uq/Yd68efDPf/6TrL2wzQwYdoOUTXzMhv3+lwU3LFAQNbt/i76rVMP3je+/urqaPhW1PDSUBA28H4pOEtjw2//pp5+G++67T26Ql19+OVx33XXwyydeIHJYClNeTt+f/EqFvL3pmRfFl/IyLb/tTFH09PTQp5ItAXUHHghjIVcTY0IQ1d/aXTkOgS0Wi+nZzSji1h9JInvDSgLBLsjy5cvhTx8vFyIoh81eXAzTXiqD6QLsgZrTDnuvHKa/XAEtdEUaNbNkR/llOsgrIZ4fnjyVhTkfjE6aBOPLV9C3kGpWQego3mJtg8OdLPB+CEgSevTbs7WHGlpg/9fLoVXcR15s74YqcbtB0Cj4vzc/gamiO6KzJLC5Hvxbvx5aNsvvXo+OGTNgfGmFaggi1bJ2k6KWlzY02s8C7wffkugY2JhGgxO83DSUxIGvL4bdn/8A3hCPURDVgo2Ct2NxOOW194UkyrSXBDYzeFhR4C5S1szQitvRp56CloB3kbbPmAnDuHvY1r2w7zK0DlRmFVrUAm/x4R4WeD94loRNDhNQEtOEBLBamCm6FzhIae7d2OzFRTBDTMMxiYkgiewBtAQWczw8BNXHHAO9U3PpgkyCfrF81cEHia+peFJE+Drq4wms7095fEfU8tpCH5NgYpiAkvh7Y1tqkDLFK8tSezcQ3PuBXZGJ0qxB7OzspE9begGWU7W7u6Hv54dB7RabQ2zKFBl+LgSDwSmToU7M177vfngWHR+YVHQzent7swgsamG00CTBhKBigkhibXxYDlIyUVjY6vlPQJ9TjrI3rCjMXYtIpsFM1kbHjHMr6huh8647Yf3558Gy354M62fPho7bbxX9sI3G86OK7oxDw13OVkGojleJWjgtr5LocCuHCSYJ3Fybxf/2fr0MvvLk2zZ2/NfbcNiHK0GfA4W9NetgJoJ7EQIPaKp7wRt2J6yvX6gL9UQt3fIiiY6BKi4AN0wQSShrY0VzN5eezRpUBK+Jkc+G519YKxkkano0/5JoFDSlkJLwXDlQJsgu0GJu1qoB93hYQ4sHl2UcOEx4FyO+Hq7X+jr4ulHTp/mTRFoOKUmwwLsGq46kYDQ9mGpTb1jy08oCv/X9XkQHD4qiVYMpoajp19xLwl45UHxKwqw+Ikno1ug4BN1Van7jWwOO13fAbol5NCTe4mM8Uc5aLdAKBaEVCn39qBWuuZMElwLFoySIHCJJTKiGJ71ZL/jih9bWVnkV8ajp35wlkblyoLiUhEIMkSQmVKPf8FgBYLWAXRJVhYDgdKwksJtBK4ao6d/UkuASyEYGSVjGHBzojNVAh6BzoIG+v6hFLWoFboYkvFUNKhSS4DKwIveGJOVgEkkialHTr/UPdrDAe2KoUZKURPaqQULkEEkialHTt/mVRE88LYikJBQycCGGSBJRi5rezYsk5CXuLGJwJwmFDJyIJBG1qOnXuCRU4xNcChQuCYUEshFJImpR069xSbirHChSEuZeCr9Ekoha1PRrSkkoJJCNEhp4P0SSiFrU9Gs2SSjC75ZIElGLWpG2PpSEIvReiSQRtagVaesbameB90MkiahFrUhbJImoRS1qGVskiahFLWoZW26SwMHOZkkkiahFrUibV0n0xPHWEENPPE0kiahFrUibN0kYcqCCiCQRtagVVTOvGWLc9g62KmSQBgWQSQ6BSqIjhhediS5bFrWo6dQ6++1S6Bx2VzlQApIEXgg1+rXoqEVNnzYO7QP1rHpwK4Y8SKIGmtuiKyZHLWq6tN7+TsAv71zkEJgkzJPD1tYupe8zalGLWoHautrl0ClPA/cvh8AkYVLT+il097XT9xq1qEUt5DYw2Av1bevkiV008H7IWRJtg8ZtY+daWFtTSd9v1KIWtVBbAtbXroCW7mp9JIFgl6Otb6MQxRpYU4Xdjujy61GLWvhtHNZWr4Cmzo3yZy5o2P2SsyRQEHJcYqAaWnrWQ23rSli1sQz4LlH6OGpRSzfcOqxbSNCPzWmZHk/0trZqmexmtPfVQVfMOA4iCHxJwhQDxRQFVhTr6yuhuTX6hemoRS3fraOrGarqP4WmriopiKC6GSaeJUHFQGnvr4LW3g2i5Fkjq4rVGysgPtQHxeftqEWtcA1/kW14JAZrNxrVQ0t3lexiBFlBmGSVBJWAKwYssuhaCw0dn0phVDWsgA11y2B9baWC5RqzgrGujk9DNtQVgpU21tfn9jgjdF6vj+s+Tb7ep/JxlbjdONGpXyVwug2W6obVUN20WoqhqWsjtPbU5E0OJo6SYMH3CXZBUBg4sInSwO6IMxsV06yYy6tucVmH226873CbgVakpyojLb0oQ0OIrb3GZ0zfuoEuY73F9Trcitdu663OK619/HE2+Hy18ralP/m8eGysT3WbT2oU07LT2uewXH+doCYJPna6xfmcbim4jOVxX73sPlBQCni+FIohn3IwYZKwBVwR+lxgl+/XlX60c21WOgfq2GcMBXxdTcGj/DoH6210JG+7YoUEQ4W3RrD80jko1hNvlJekDx5cL17unl8Cn0KDnE9SkmAb4qaKYsOndIkgdA3Whg/b8DWCbfAN0DFk3PJfti4EPGieYOdABIn7k60KQQkLySaF8ZsjnQPJqiAFfWyVQwEEQQOpE4NcDiY8qCERr0/eb0yiCL1b5IVY8gkPpW5supJwEIEKDGonDW6+oWHUDYUUCioGhiLwXmBhDhJcPw+jrmx6knAjh5gxjxHYkCsHrFZkEBt4MAuMHFdQiEEfOYgA0rB7JW+Vg1i35t0KJzYdSbiRQxIW3DBQhFIX9JeDIuwekJ+DhTooJqYYrBS/JFzKQQaCBjcMFKHUBoUUikkOEhbqIJnYcjApXklEcvCPQgqRHLyA6+dhm6gUnyQUIlAhw0CDGwY0kDqhkII+clAE3SM9ePwBC3SQ8IAVA8UjCYUIVIQ+EInQMOqGQgp6iAER4VME3hN5lcPEH3PIxsSXhCmA5B4JFTIINLhhQQOpC9oPRooA0rB7Zcg4MpIHOwi4HIpVFBNXEgoZqIgqBwUKMRSbHPIHl0OxM/EkoRABRQaBBjcMaBh1QyGGSA5u2fTkYDIBJOHcjaAU5pwK8+AnPcEAUinoIwcRPhp0TzTmebwB171pisGK3pJQiEBFKhQswHlGEUptUEhBL0HQwPuAhTpIIjmY6CcJhQSUyMOXo8rBRobBSD3EIMJHg+6FOF47IV9ywPVGYlChlySoCJwYLMAJVwgNpQakrtOgkII+ckDMsDda7nuAhTpINt3xBjdoIAmXYw5R1cDJUDnwkBYCEUAadi/krWpAcN2RHNxQWElQESgwwhBVDgyFGDqHaEgLiSL0XmChDpJIDl4IQBLGhVvw6lblGxYqae2vkvPUd2+A0y/7A5x40Slww4MLQFYR/XVw4sWnycue4caP09a3roInXnsM1rWsFBsMBrZGLHMqC/Ga5hUWlkNzbxU8885TQih1cMG8C+U89/zrTljw0IIUNz2wQE6fe+9foCNOqxPdKwcuBn2qBxE+GnSvRJWDlgQgiTRtImSU8xdcCNUd6wBPuDrhIkMGWCG8t+xtWFG3VN7H6b+54BQ5/zX3zIWzrj4L2uP1cO5158PymnIZYJUk2sQ87eLbE+dFGvuq4FlTEvMNSZxz7XlSBuY4hqxI4tVSEu2mJGgYdSOevhScPlIwUYTdKyzQQYHrjqTgmsEW+/0kgUoidTm4FLVw2pw/QF3XRimDky45PdmNqIdm8dxjLz9iSAIriWRgUQbyvrygai3Mnn+BvK+SRFX7ajjzmrPhsdcekYE3JPG0rZJASVx333VJrpfrPPnCU4SY8HUUgdQJRbWgjyBECGnYPZK/PRUIrjsShG/yJ4ka6BqogRaxERsyaJDhbunDK1DXwkmim3HJzZfBquZPxfTT5Lc/Bhkrib+Ib3YMME43JFAtb0+68NSUPKgkarrWpSSBYkFJnHDR6UI6p0hJ4PuZde1sUkkYXYq5914HHWJjNwPZM6AIaSFQCEEPKZjwsHtBfhYW6KBIdyciObjAWjmYjxUEKgnZlRCcdLFZMRgVQEfyPj7/0scvwF3/vBPWNa9Ihd0qALyfCrSY/7Q/n8HmQbpFJVLXvT4ticFkJfGufUwCK4m//PVauPqea2DOrZfD+fMuANxtOPfea22SKDhFtKcCLw1Pp8nlWaiDQqw/EkRuKOQQrCTIHgmrJN5c/ErqPoYBf4MBK4oTLj5VVhB436wokBsfWQC/vfR0Od5wyiW/h41tnyolgdT3boQzrjkHHn31UWgWffaG1JhEbUoS2FVpExstCsH62w9z7/mLHpJQSEEvOdCweyOsyoFt9BGZUcjAiRwkgd/06WMcOkS53h4zOPGS0+VtR/IxDkiaR0eeIp5rsQQdxxJQGMbjGnn74PP3w1lXz4L7n/9rarpdEjUyYDjtlDm/g3OvO08ORDb0m5KoNySRDOIZV5wFS6uWWMKJg50iiIX8wRhF5YCh1EMQjUl46F2TtwvKImL9kSD8oxBBJrxLglQNJvc//Ve47xmDvyXv3//MffA35Nn7oB1DIQL+24uNKsEuiVMsAlBzUmqswhnsbjwjBy6tkmgQkpgFZdVl0Co2MCthDlxi+OR9RcVQeClYUQTeCyzQQRJJwTeK8LvFvSQUYlCCQZChxarAGHw0wfXg7XvL3oI7/nEn3PrY7fDaopfB6ZoPPbH0/cdffZQ9byMZRvOn5V549+nUtNr2NVDdhqxN3hq09RkVSd5RSEEvOSjC7hUW6KDAdUdy8I0i9F7JLgkqAUJ3f/o+C66CwI+cpIFUkP13KPF3Hum03IkuRZ8LkRxyQhF2v2SWhEIKFCMMivA6gHsl6DSn5a2VBEMRSm1QSKGY5JDf8YZoL0VOKEKeK2pJKGTAiBldh1ChYdQNS+WAYdRPDogi9G5hgQ6aSAy+UAQ7SNKSoBJwwAiDIsCBYB/DsEEDqRODvGLQSw6KwGfAeN+WaXmtHFA+kRx8oQh0UPTGBUMGJVQCTrDQhgUNpE4opKCPHHj4PcMCHQw9UjppMfQNKgIQ4Ywi1EFhisFKVkmw0IYBDaNuKKSgjxwQReBdIj+DItjBEVUNvlGEOiioGLJKQgaBBjcf0NehYdQIDB8VQrGIId9ywA08kkOOKIKdM2K9VAgqjDGJsOVAUYRSKxRiKBY55GO8oXPY+jgShG9oqAOEiiATspKQQaDBzQf0dWgYNQIDSKVQTHLI72naSCQG3yhCHRRUAG4oYUEOA0UodQEDSKVQTHLgYQ6aSA6+UAQ6SGjwvRCuJBSh1AaFFAorBwy1eb8x+dg/8nOwQAdF1KXwjSLQQUHD7pl4qyT/kqBh1IDUYdqDXAiFFQPFDHmj5b4H8jDekEasPxKDfxShDgoWdq8k5ZB/SSjCqRUKMRRWDhhs+jgHWKhzAWVgeRxvSU5TbPwRmVGEOihY2P1ABJEfSdAw6oRCCnpdhl4EkIbdC1HloC+KUAcFC7pXFGLIjyRoIHUiw9mYha0erChC7wUW6lwglUMkB/8oQh0ULOxeUQhBRW6SSP5WhpaI4DmNOfCAFgIRPhp0r8hvdxrwoMB1Kzb6iOwoAp0zyfVaz6nwjUIEmfAvCRpKnUhWDsX6WxX5PcYB1x1VDq4xA2zezxMysDTsXlEIwA3eJUEDqQkYPioEvcQgAqgIvCfyWjlEYvCNItRBwYLuFUXoveJOEopQuiN9xafugRZoqovB6iUDUPlev7xta+kV05uV87tGIQV9xKAIega6sEKwPO7sbYL169dD+ZKlUL54Gaxbvw46+jDQQcgC15E+vmEiC8J8770iVO1dTbBi+aewZOFSWLFsJTQ01srpdBl/GOehpFCEOihY2L2iCLtfnCWR03hDg/1xpxDD23FY9iYwcHpnZz+kf4cTlyXLK8BjHTCIXXgxW/GPl1EOcWPecBFBVIjAGfwMxjI9guXLlsPiDyttLEE+WgbLKpdbwt6gEIBYlzx/gj5nPk4LggfBC9j1odMKgfhMfa2w+KNy9jczKIeObrqMF8jnpKF2mu4DFnavKEKeK1wSikB6wx7wyg96hAwSsHJJD3T3t0HXAFYLDfK2p78LVi02nq9e069YlwJF1dAVr7OEs94uhVAF4VUMCkTFtUhu7BXQ0WtsfKmQx7HqahXPV8jnO/voXghnzGs4dAYihyS4YdNpodMI9fW1UgbLKpZDb6wt/b4wdIOtKeEuWlgOLPBuUQTaFm4Rpp5BhD+HdMeMSodOl8vSoHtFEewgsUuCBjJHWpr7ZLWwuqzbmJb8KT0MlDlPt2B1GYpiXM5P14HIIyRxGSKHDiGbj5cvBCOcpgzMoOJ9I3gVqyugqasmOS1o8PUCkIMMcVNSEEuhR8iABj0VeLFhyY1efEM6dz2aYF3jeljfsAHWNlaJ+xsFeLtB/C0VIfDBwuWL2LRwaYK2rmb596oUguDPJxF/r09Xfir/Zo3N9fz5DOCBY4uWlxlhVgTcQIh7RbliukUEgjV168T60jKRIaSB94Ii0PmghAYyCGSoe3qg8q1xqFmXDn5L/SAsfQe7HkNQKW47OlEehjCWvx+TougeaErOnxyfSArhh4ccITjc4GdHwIbG1SL4tfDDQw8DDGtPMrS//v0ZULluhbz/zL9fgPqOGjjpzLPEBo0yoQEPAkXgvWAJdlXtOrnBdw3gEY009ISY2HjFvKvXruLPJekYEpVbvB2qWuthr0OPEht9h9hI240NNxmCHx1yGPzq1NPh16f/LsWPxLwfLV1ozCOqjh8d+jMWno6BZvlvQqeHDf69Fn1SIf6W4ps67lwl9caaoL6hFhZ+VCkq2Hb2PHLsqafCsaecBvuIz3+s+Jscd+op4m/VJv5GR6T+ZviZMeh9Iuh1rVXw4tuvi+faxfSjbFKYfdllct4DjzhGbMdGdXP97beK99lphI8G3iuKMOeLEto9CIoNK4zqoEcOTNZBewtWFYn0eMQbeDsObS1GN6NTCAOf7+jslI8xgNaq4YeHHgFGn73R+NYVzxuSOEJO60l+jh8f+Qs4//LL5PPPvv4ifFC+GA7+xa8ClgS+viLwXmBHRzbLKqKyYhkLuxOfrsJvxwq5bHp6U/Ixfgu2QuXa5XJjnXXp5XDunDlC4B3JUBhl975Cus2dtZawNMFPjj5OSCJdJaCIrcsgOkiiu9+oqMxuWVYGjflXLFvBn7PMg5+rK4ZCbRMy7haf/8hU+Pc55Gg44vjfwBEnnAyHHnd8UhJtUixd8U6xjjZ48qXnYd+fHy4rhoef/Bccd8opspJASfQMdfDAu0UR4DDISyWBLH0nDsveGZT38Re7l701xgYtl78FotoYk/NgBVH5TgzWVPSz8QZTEjSszd114h/tKPjp0cfKx619DcL+p4p5fw6dYn3PCEnUdTTASWcEVUkowu4B/Bw06CZd/ca3Im6I9DknesQ/IG70rZ24XrqXogX+eOH5sGzdstS3IFYRjz//FFxwxZxUKLCSWFe3Buraq1IcdMyxDpJIo4Mk1q5eJyqDcvGt3iLAv4fTeEOTrCTw77Dkk3IpY+vz8m+WlMC6ho3wpyuugp8ccxzUiEphyadl4nOmJYEVQ/cgVmOtUNtaDS++9SZgJYHyWFi5SM6z32FHSmEY3ZNW+XfCkF93+83+JKEIbpjkTRJYJVS812M8HmiF5Yo9GybdsXYZoKXviy7K+wNGmAZREBgu4z7+Qx1y3K/EBnwc7PuzI0UJfDg0CUmY8rjxrluSXY9GGcgfHfJzWUnUd1QnuxuLUuvyDg+8F4wNkYfcCn4bYuDtVUE2muQyDc01crnUhi82zn3F5/+R+Nvg38Toqh0lb/c51KB7EMc8mmFN7SpYVbMmxeratfK2tbchtT78ljxKfHOaPPTEg4YkFPIIDawKROAXflzGn3MAuyMVi5caMrasR4o51gyH/PLXsN/PjK7FyqrVsN/hx0BjZ50hw1Tgj0z+PQ2MSgKnp7sb+x6C22EX9ImA9w+lJeGrklCENmzyJ4m3R6HiXWM8olt8Sy6X3Qs12L/GrkTFu72w8pNYShJWusQfv0N8O+Jtlwgeku5uoFAa5TTrQGJN8zpo72+AV95+Gapb1rJ1ZocH3gu4EfJgqzEl4X4ZXL9RSTS3pQNt3fixu4F0im+1A488TmygbclpRmWxcsNyWCa6I9glqVy7LHlrTFsqwH8X+X5EBWKnRYtKYtnS5aKSyC6JXstAbdniCjmWYwZags+hdFYuEf9uOH4g/kbicXuvMchY07zRMi/+DfFvYNxiVwO5/4mH5bw4z6xLLoV/ii5Hr5Bwa2+T3EY9SUIR1EKSN0ksfa9bdDGGUo8r3+9icsBqYylWGyiFWBtUvj0M9RsHwBZUc/emmGf/w7DUa0w91z7QAHc8cI9t/n0PPVR2N/BbDquJfQ7Bb9Kj4BPX3Q0eds/4OGy6Sw5EVoiug5tljQ2+swslITb4gTYWDOSjpYsFS2zc9uBDqTGIuraNUNNiUN1SI0NvPkZQEvK08LghGwOs+tqhs9/4hizk5fBbW7GSqhBdiVb2nJ1kN2TQ+BsvxurDKgkLvzv/PLj6ppsFN0muufEmW5WA/OiQn6UrNLwV7HPokamQ94jqASu5w399opynpacxKYlbMktCEVAdyJskqtfiwKWoEvq65OOevk4hjVGbJCrfHhQbeJeURH1Ncv7+DqDB7cVBSVEp7H/Y0WCVhBFKPi+d9stTfw+frMjW3VCE3Ss+5GBl8cflsHhhGXQpd2vSMYdmKF9SCUs+rlCEwuDHRx4jB3IPtNzud9gxZKDSAL8ZVZXB/of9TJbYuNwhx/0ajvvtKXDy2X8UlYQxwEfnD5WYMRC5sWoDf85KKuDtcv7Vq1YzOZj8/rzzwRhzSE/74c/SYxIGhjCxgpAnXMWNgUspiOEW6EuehNUz1C6rN1MCjpJQBFMX+sT7D14SqSMnG+VA5NJ349A90AnGkZGim9DTBR2tcXHbDWbg8ZtQVhXvDsrHMuyD5gFSGEBzN2i6X40lnOwfHnp4ahl74M37jVISzgOXirB7INNgpGeSG33lUuseDi4HvL+8coXRPRFhZaFIgt9uZasroXxVBZSvNlkKje3VbF4ss12HflCP7gaCh18bA75GNWGrbCyhRkHggCUOdMougu15iyREJXHk8ScKTkjd0koC6U+KAEPUl9y7YQ0+yoKKYJ5VEopA6oT8XEmCl4TJYD30Dhi7PfGYCOzjmXssrCHtFcFY9m4MKt8agd7+XttzFHMsgmJ0SRrZ/CYtPXXQySoMnJ+H3hM05DlRL2+XLDIOLW5pE58tKQe50VnOG2hrNwYsF8sjCHlwTO586K9w10P3MVauX8bmRerbati0TNQrZBM6IqALP6qQR6HisQvGNHug8ajLRViloVRFpUqftyLHGwY7k2BVa5BaF60CkrT2NLBplLbeBlFl8EDqhFUO+ZPEoPUUbVFV9PQJSeB5GwlY/kkvNNZ2Q0+XuK3rhuXvDyYlEhelI36b0SAb9GCAFNP9IQJJw+4VFvAgaYa6+mpDAh9VwtLKCnnSEp57sHzZMjENvzkrocpSYuN7YuHJxDBKxz7NHNyzDvJNGER4F8tD1ZdC2ScVUN9YK7qt7dDQVAvlZcbfC8/r6Oq1dyMyklyveZ8GniIrGFo9WMEQDvFQ6gIVQ14kgQG0H99gnLBkVg5NNX2iOyEqC1ExLH8jYdx+2AONYro9wAgNdm705CwGYx88D3RQ4LoR+4aP5xwYh2kbJyrh/WWiK9KHR/DRoCjAXX50WkbMcLjGo5zyRTLMzc0N8oxZOTj5odENwV2ktXXVXAIuSF/gJbskHAWhCKQuUBk4kbskbGIwMX+Z2hLUGIZVBCGGNBu3jlLA5+g0v9DA+4CFOkjs4w1WjN2cuMHiYwwwwufLhNO6nXEbfHLadNiYQlOE2xiDyHzCVSZkiGjYnZDzNiVRyaGdhbPQUAlkw58kkld+kudoMEHQkIZNYxJF2F2Tz8oB1+snvBESRaiDoBCXhQsbGn63uJYECsFJCnrIwSQddB5+F7BQBwnfUxHhEkWwg4KF3SuKQOoEDb1X3Ekigxx4SAuBCCANuxfyVjUguO5IDr5RhDonzHUGUTkgilDqAg27X7JLQiEG3HvBg1oozLA3Wu57gIU6SCI5+IaGO0BkiGjYvaIIpS7QkOeKWhKDXAz6VA8ifDToXokqB31RhDoQosrBN3ZJJKsEvaRgogi7V1iggwLXHUnBNTK0lvt5hIXcK4ow6gINc74wJKGoFvQRhAghDbtH8renAomqhpxQBDsQgqgcFMHUBRrkfFKinxRMeNi9ID8LC3RQRGLwhAyt5X6+iGc/6ImBoaOPNYYGOAxskuBBLQQ88E6Yl6C3kdeqAdedFkQkCR/QYAdEsR/nQIMbJlISPKiFgEvAEyzQQRJJwTeKQAdG3EflQFEEUidoYAtBCQ9rmDQmUYTeLeyCskGC8okE4Rsa6gBhYfeKIpA6QYNaSAokCUXYvcICHSSRFHyjCHRQsKD7QRFIXaDh1IWQJaEIuxfyOt4QVQw5oQh1ULCge0URSJ2godSNkCShCLwHoj0VGqMIdVCwsHtFEUidoGHUi3ZBhySPkhABVATeEyzQQRLtpcgJRaiDgoXdK4pA6gIPo24YYrCSR0koQu8WFuigicTgC0Wgg4SF3SuKUOoED6ROcDnkSRKKwGfA2P0alhxw/ZEcfKEIdFBExzcUGi4FSgCS4OH3DAt0MODVkyIx5IAi1EHBgu4HRSh1gYdRN7gMnMhREorAuyS/g5FIJAffKEIdFCzoXlEEUid4GHWDSyAbPiTBA++WfIsBN/BIDjmiCHbOxAM4MhJRhFIXeBh1ggffCx4kwUPviTwcGdk5bH0cycE3NNQBwoLuFUUgdYIHUid44P3gQhKKwHtB+ZN1QRLJwTeKUAcFC7tXFIHUCR5IneBBz4UMklAE3gsszEETycEXikAHCQu7FxRh1AkeRp1IH/wUNCX2371QhN0rLMxBEo05+EYR6KBgYfeKIpA6wQOpGzzYQZKsJMyQN/LQuyEP4w1pUDyRGHyhCHRgFPnxDQgPo07kr3KglLDAe4WFOhdQBpbHYkOMBOETGuoAYWH3gyKUusADqRs8yPnEnySiykFfFKEOChZ0rygCqQs8iLrBw5t/2qF/uN2bJHAj5KHOBbq+SA6+UYQ6KFjYvaIIpU7wQOoEDW44oBxM3EkisN2YDYppuG7FRh+RGUWYgyQ6p6KQhDfeYCctBteSwI2RhzooDDlEgnAJhtd6P0/IENGwe0URSl3ggdQNGtywaGNycJaEHG8IqnKgRGLICUWog4IF3SuKQOoED6NOYOVQiOqBC4FjGbjM33kVaTFEgvCJItRBwcLuFUUgdYIHUidoaMPCuWqwyqF/uFNSIn+7ggU7KKLKIScUoQ4KFnavKAKpEzyQOhFW1WB9HaNa4TJQkRaElAQPdhBEVYNvFIEOChZ0ryjCqBs8kLpAAxwWbqoGk7QY8iyJSA6+UIQ6KGSAaOC9oAijTvBA6kRYVQOHS0CFvWpQEZAkIjH4QhHoIGFh94oikDrBA6kbPLhhwEWggsvAiRwkEY035IQi1EGR8zEOikDqBA+jbpiBDbeK4CJQkb1yoPiQRDTekBOKUAcFC7tXFIHUCR5GneChzT/Ga3MRqODhd4sHSURyyAlFqIMgFSIaeK8oQqkLPJA6QYMbDlwCTvDQe8WlJCI5+EYR7KBgQfeKIpA6wQOpEzy44eCmcuBBz4UMkojE4BtFoINCBoiG3SuKQOoCD6Nu0NCGAxeBCh7wIFBIIpKDbxShDox4AFecVoRSF3gYdYMHNxzCrxwoFklwOdDHEQ7QQAcIC7pXFIHUCR5G3aChDQcuAor3vRR+KYkGJHNEEewgYGH3gyKUusDDqBs8uPnHTdUQnhxMpCTMDT4ShUsUoQ4KFnSvKAKpEzyMOkFDGxZu5IDwAIdBCQtAhDOKUAdBzgc/aS4HHkadoIENCyoAJ8KvHCiRJNygCHYQyBDRsHtFEUpd4IHUDRrccOAicIIHthBEknBCEeogKPaqAeFh1IlCXeDFjRxwnsJXDpRIEhRFsIOChd0rikDqBA+kbvDghgGXgQoeTl2IJGGiCHVOmOuMKocCUoiqoTN1n4uAol/VoCKSBA13gLCwe0URSJ3ADZ0HUydogMNA7z0Vfth0JaEIdSAEUTkgilDqAA+iToRRNahew5AlFwHFHHOYGBWESXFLQobWcj+PsJB7RRFIXeBh1A0a2rBwIwYeuolGcUvCRBHqoGBh94MimDrAw6gjNLhhQEXgBK0Y6OOJQXFJAoNrvZ8v4j5OtsLg0ceawoOoGzS0YbFpVA6U4pKEFRrsgJBBogLwiiKYusADqROq8YCgUb0GFYETE7NSyEbxSEIR6MCI+6gcKIpA6gQPpE7Q0IaBm6rBhAermCgOSdBQBwgLu1cUgdQJHkidoMENA697Knioio2JKwlFoIOCBd0PikDqAg9jocFwmvdV5X4YuBEDwkNU7Ew8SShCHRQs6F5RBFIneDh1olByoBJwgodnU2HiSEIR6qBgYfeKIpA6wQOpE4WRA5eAVQb08aaN/pJQhDooWNi9ogikTvBA6gQPbv4xXpuLQQUPy6aKnpJQBDpIWNi9ogikTvBA6gQNbhhQAWSCh2RTRy9JKAIdGEGcU6EIpC7wMOoGDW5YuKkceDAi0ughCRroAGFB94MilLrAw6gbNLRh4HY3Jg9EBKewklCEOihY0L2iCKRO8DDqBg1uGLgRQyQHrxRGEopQB0I8gCMjEUUodYGHUSdoaMODi0AFD0BEdsKVBA11gLCge0URSJ3ggdQJHtpwiCqHMAhHEopQBwULu1cUgdQFHkbdoKENi0gOYZI/SSgCHSQs7F5QBFI3eCB1gQY2TCI5FILgJaEIdFCwsHtFEUad4IHUDRracOAScIJv4BG5E4wkFIEOjOj4hgKj22HTVjaNszALTe6SoKEOEBZ2PyiCqQs8kLrBwxsGXAYq+MYckR/8SUIR6KAo9l+44kHUDR7a/EMF4ERUORQC75JQBDsoWNi9ogilTvBA6gQNbjhwERBGrIOVfAOOyD/ZJaEIc5BElUMhKcx4Q1Q5TCwyS0IR6qCQIaJh94oilLrAAxkMsaEeiI/0seneocENBy4CFXxDjSgcXBKKQAdGPIDDphWB1AkexmDoj4vwiG/gmTNnQkVFBXveHYX4bUyESkDFpnPNyImGXRI01AHCwu4VRSB1ggcyeA46+ADA9uyzz7LnMkNDq8KUR3AS4SJQEYlBdwxJKEIdFCzsXlEEUid4IPPHtGnThCIS8Mwzz7Dn1LgPfH+8B3535mmiWkn/KrZ7rK9DJeBEVDlMFEpoqIOABd0rijDqBA9jnhluhZdff0FWEdiee+45Pk8KGuDMNLRWC/lMgS9u+3n45i5fhxkzp7F53OH2kOlIDBONQCUhQ0QD7wVFIHWCBzIsOuELX/hiShLqSsJ91ZCmS0hhBsyZM0fUJwm57mkzpijmywwXgYpIDhOVQCTBwu4VRSB1ggcyXKZOn5wSBLYZM2aAEVB8nofWDY2ttbDFFlvC0HAstd4f/OAH8NtTT2LzOsFFoIJvdBETi5wkkfMxDopA6gQNa6GYOm2qRREgxyawujDAwHqvIqZPnwFTp5rrxSoiAdtvv70UEp3XDpWAE1HlUCz4kgQLu1cUgdQJGtJC0jXQAm+88YbVEVISA/Eu4AF2x+ZbzITLLrvMtk5skyejIFQDl8Z74SJQwTeyiInLwEiXe0mkQkQD7wVFIHWCBlQH9vnfvWmWRRUwHUbHh4GHOTtvvvM6TJkyha4SHn30UZg5czqZ360YIjkUEyiGNN3uJMHC7hVFIHWBhlIv2uW3O21YSYyNjwAVQDaw+lAJAhtOnzZjqvibGFeaRrgIKHwDy0bfCJ8WoQd2OfSkcJQEC7ofFKHUBR5I3cBjF7ph2223pXmWYwleJdE73CFEMBl23313ujrZcJ0ffPw2cBGo4BuYO7rZtEgahSc22p2qGqxycJQEC7ofFKHUBR5G3TCD3Sa6FEM0y7JhdwMbFUEm2ruaLAOVvOFzxmAjFUIQcrCD4x540BadHhEuTpUDJSUJFnSvKAKpEzyMusGDfcwxR9EsyyYlkfAiiU6xzFTo6+uTyxtHRKTbOeecI7owkwFFMMDEENReim7Yb///FTKaIoWE56BgVwoP5OLzRuQLuxgyyyElCRZ2PyhCqQs8jLpBA51mylT1+AGGbFxE3TpvxfIyWLayHCpXlEHl8nL4wV7fFV0MYw/IpMmT5LEVTm2vvfaCE078NeRHDp3w0cL35HtGKeAtsutuu8F///d/y/GVz31hG7ZMRPB4lUPuklAEUid4GHWCC0HFZpttRvMsW2VlJWy++eayosBbDBoe93DZ5ZfC8y8+K3gOXnjpWfif//maDOZLrzwvlhqnq0k1DO1vTzsRgu1WtENMVDAPPHKffI9qSSXg4J/+WLzHUsXyEUHgp3KgeJeEIpC6wMOoC94PdsI+O5bm2K644gpoamqCI444Qg5kohwSCdppyNYS8Oqrr0p6e3ttz+D6BoZ62AaWK1OmToYZ04zxE1UzPkNCCGRacpkuto4If6SloB6M9IJ7SShCqQs8lLrBJZCZbvnti23rrbeWYbIip9nSZn3A2+zZs+Uuzi222EKuFyuUnXbaKfU8PhekJKTkxC2+Ht/laojB+jgalwiOXKsGFZkloQikTvAw6oS/C7zgOMThhx8O8XgcDj74YCYIZHx8HA44wLi2RKb2yiuvyCphw4YNbB1jY2OpvR2zzzvXsqEF821+/An/Jwcns7VDDz0UPv/5z0JQr7upEmTlQFFLQhFIneCB1A0efjd89Ws7w7vvvivDU19fnwr0yMgIHHXUUbaQo0AytVWrVsmxCnN+bFbJ4C0OWJ5yyimwfv06ttHlQktnXfLaF9kbSiw2ZOynVx1HEeFMEOMNbrBLQhFIneBh1AV/VYNJ/xAe6DRFXnEKmzXc+G2Pg37yiEjL9EyVBAbvmmuuSc37ta99TU4z9yyYkkBw3ThGsbj8k8AObMLTzc0L5GRqxmeKuhp+yGflYGAeYNWVlIQikDqBI+U8mLrAQ+8esXy8UwR1Ooxb9j584xvfkAH++c9/LscPMHBYupsDlsiiRYsscUu3Dz/8EGpra1MVw5577ilFYB6bgPfxGpnmenDd+Fx9fR0s/7SCbYze6Zbrwy5Opj0qN910k3w/66pXKdYR4UQYlQOtUEpoIHWBh1En/FcNlBmbTU9VENhKS0tleHFMAr9p8THKAW/NSuLEE0+0xM3ecJDSFAAuZy6LgcTbSZMmweLFi23zmGMHIyND8EnZB2zD9MKyT8thu+22I+/K3p588kn5ultuvSVbPoJjrxryXzlQtJIED6Nu8JDnwpe2+yLU1NTYAoR7HzC8uAcDqwgEj3XYcsstZbCwOnDq7x9//PGp8C9ZskTOZy6LwkEZ4PpRQOZ8+Hx5eXlqHTM3w92R/scGZsx03uWJDXfh4mf6y/VXs2Uj7OS/YkC4FChaSIKHUUd4yHMDD5U2A5Xuu+NRiBhe7BYgGCjz2/6jjz5KPadqpmDMboRxkNX0VHcD14X3zXnMSsLaBuQl7abBgGKjdQNdn7U99dRT8vmttt4Kor0ZzqQDmq+qAXGuHCgFlQQPom7QYLsDD4QaiPdI8DqSfF2dItAzobu7G2i/3QwvBtr85sew41WjcPrRRx8N/f39tmWw4VjEHXfcwSSB4LpMSfz4xz+2SeLYY48lazKuUOXnuInYUC/MmK4WGDZ8/fk3XM+Wi6BjDQgNdRC4F4OVgkmCB1In/Iw5pK/o1D9kXLfBGBMwBgunTJ0Ep/7+t/Ds809C2bLF5JDrdCVx++23pwKMYcVlDzzwwNQ0fnCS0T744AN4+umnbRUCCgLnNwc/zW95pyrCbNt/aTs4+TfH2zZi+bmU3/7padt/OfNYBEpPvY5Nm3Qg8znmwMPvllAlwcOoGzT4Xsksl+qG9bBsZZm8uAtWCDNnzoAdd9yRBemhhx6yfds7hRqnmQ0rCbyKtjkvPjb3XJiVhHVdKB+ng53wvd1xx22w627fhG99exeYLt7v/3zja/Df//Nf8mcG1WMWXWI59bkmZvvitl9QLLdpYg8iDXRQ+KscKKFJggdSFzIHOzjSr3P+BefKgI4nRo30kMMJHnjgARli81yL/fbbT86/cOHCVMARlMZPfvITuQytJBA8mhHn2bhxo206jm3svPPOttd87bXX5Lzf/e53YTqOSQgZSIaRDjkgiaeb43kW+x90INvoURJOYyVmO/74XymW27RIhy8fVYN1fTzs3jDfX3d+JcEDqRNhycFgIG7eb4M/XXyO+HbfHEZGk5ezdzjmqLGxEdauXSvvf/vb305Nx/Cbx01YG54Ahs2UgfWgKRMcGMUf9zHb2rVrkveMN4HVDd2w3dElPlNmSQwO9ymW2zRIh48GO0iCqRzoevMiCR5InQhXDmnwmpEdcMttC+Sp0XjMgnnuRLb29a9/3fY403LGBWSmwV133SXPz2htbZXjHCiVX/3qV3R2OPfcc+WxFZOnTBbSmQa33LoAbrx1PtvIs9MFkyaV0tXbGh5+zZcrbpyCFyw05H6g60wTqCR4IHUiZDmMmAOZbfK6Crt+6+tQUlICpZNLoHLlYsCjSCdPnQQHHXQQzZKy4bK77LKLcZTiunX0afmcteE8WP6vX78+VY3wZuxZ2W233WDK1FLo6GuRG/ayFWUweVqpHINwv5ejS4ivhKw/3e69995NShJuwpcb+akaVAQiCR5InVAEOO8YV5o+8KD9xLf6VNj/wH2hR3Q3+kf4peH+fM1lMsx4kNHSpUtptlINuwrWhlK48847ld0ONw3HMuSyM6bDmg0rbRv4hZecC2efewacM/ss+XxbTxMLAafL8X3ge8fn+DLFhZ8Aeoe+hl/oep3JSRI8kDpBgxsGaQHM3NzYszB9MzyBqR1iyen43gxZdMJUeXKT8e36+puvyN/lxDCNjY3YzuVQtccff1x2K/DcDC8NA4vHWkwTXYvnnnsWdtltl9R7cH9VKntFgBsdSkJ1+X+z4d+iL/m5iw2/4fMGDbkf/A2UepYED6Nu0OCGAa0QnBDzin8srC7kr3fLjcwIDv4jmhvdmWf/DvCkL9yTgPPeevvNMDqmvnK2l2YeK4FjENhuvPFGeP2NV2FABHyvffYUt/67Ayg8p70beNDYtOl4NW5jXux+0eUnIvYA8nAFQ3jdCidcS4KHUTdocMOASiAbXfKgqsqV5WyDS2NIw6BbHlcxc7Pp8sQsDHl8GC8957A7xNJ23XVXeYtnfJpdkuefx2td2ltqb4YI7ne+u5vi/bihW66/s7MT6BGk2PCArovnXMiW643T9UwEaGh5qIKBhtwvdL3eySoJHkbdoMENAze/bmUNu/EjNDffeiP0DRoVg9trN+A/NMoFKxC8ve2OW2BoBA/L5mE0m7mHY9asWXDrrbfSp23t748+muz2GK/3wCP3svegxqg6sCpACf3oRz9KrpG/L3wezwnh65hYBB0+NTTkfqDrzA1HSfAw6gQNbThk//EaLofcSF/WHl//uF8dLcMfdMMrVJ14El5Sn76+lXTIcUM07nfLPRq454U2s9ZBQWy9zdbJ+YP824SDEZT8BTANDbob6HJ0ncHAJMEDqRM8uOHgvXLIB1jSz5kzxxbGoFr2g6jo73Dg+SnGaegDAwN0dbLhhXBxwDI2Qc/XCCOAPPh+oOsMFikJHkbdoKENi0LLwQxmB6zf+GleqgizTZ0yBT5a+L7iPajolmMkTud+mA0PGJtz5UVyfr4OPQkvgPR1/EDXmR9KeCB1gQY2TAotB0oXTBWCOOyww2kOA2t4UNf0aek9ECpww8QDonBPBQrLqYLANnfuXNh8i83ZOnQlvPDRoPuBrjO/aCoJGtpw4BJwgm9k+eTY444S38rOxyAE1fAELudTufEU+F65p8JpV6fZcJcnzjcRKojwwkeD7ge6znDQTBI8uGHAJaCCb2D5ZmCoE1q76uVYxDbbbE2zGGjDg6xwAHOvvfcEI9z2MYjb77xZvg+sIGKx5IlpDk3OJ3C7B6cQhBc+GnSv+DsAKkg0kQQPbhhwEajgG1h44FGMpfJ6EKOjydPK89yMCsD+Pnb4svHTgnjR3mwNBzOx0sCfCaDrKTQ8gDwQwUBfxw90nYWjQJII+WSrFFQATuixgf/t4bvk3gM86hJgjOaRNTxUO9eGQjJP9ELwKEwUx/wbr4dMB3G99dZbyR8GNo8k1Qd7+PL1zUwPsvILXW/hCVkSNLRh4WIgcsQ6D9/QCgGegWleUj9bw4vO4B6HXBuef9HUWidfHw+UKp1UKiqImUIPKAg8UIofLIUNRYKvr9NRlOGEj4bcL3S9+hCSJKLKwQ9H/+IoKQjr73I4NSoSc/zAa1u9erVcdmCoG/50wWx53xCEuuFVs/A6FNOmTwZj0NNp4DM80sHLV9WABFE55PP9BUcIkqDBDQcuAhV8A9OJmeIbHLsbeIUpa/vlL39pe4yNCgEfl5WV2aaZjZ52Tht2G7beZkvYasut4OSTT5DTnJbYYovNYKuttmLvvRDYA8g39uCgYXeL9T3SdepLniShc+VgHl7NNzK9MK7PoNrdSCuLRx99FO6+++7U4+9973tMGtguvfRSuOSSS+hk1vB1jdfG6iSBVqGzyN8axde4/KpLk++3MH9Tewjz9c1sXu+Rht4L5jrouvUnYEnQ0IYDF4GKwmzEfsF/HLOfT7/58YK31kYvZ4eSwJDvscce8nblypW257FhwIeHh+lk2XBcAl+7p6eHPiVbQ0ODfF9TRRcDA0DfexjwEPKNO3foa/hlYsrBJCBJhFU5WF+HSsCJiSUHk7VVn6a+0a0NL45LW7pqMGTy5S9/WS53wQUXpGdyaP/4xz/opNTrGj8exBu+3sE/PQgKMf4QTvhyrRpM6HonJjlIggY4LFzsqZjAcjDZ4cvby290xFpJ4G98Wtt7773HRIJdFFV3w23DszqxOlHtLZk6dbr8HQ76fvNN/sJnXR8NuV/oa0xsfEgirKqBw0WgYmLLwWTadOMXwL761a/aQkqF8P7777Np+DgXSaTHJOzjIThAicdsxEK8NkQ44Ysqh0x4kAQPbVhwEajgG9hEBvcw4IFNX/va12xBpT/zh8dHGEJI7wHBKmD//fdPz+Sx7bDDDlIQeJYnnu6NdQz+zqjqaMx8kQ5evroUNOB+oestPlxIwj4OQAOcP6gEnCiOyoGCB1FNnjwJRsdGbAGmp2enuxtpScyY4e8K2tb2yiuvyO6GeUEZXN+VV1/O3meQ2MOXDzmYexiCqByS72+417gtUmIjGSVBQxsGbscbEL6RFQd4chX+Gpbxq+K0YVitYxRYSRjdgrQkcB48WSvXhlUEVjTY8JgN/l6Dg4UvcGjI/ULXW5zER3pTKCRBgxsGkRxMBgR/feguGXw6JoCNVggoCToNf8oPuyBuf/jHqW233XZSVI3NdfI1gj712x6+fMkBoUH3A11n8REbTYth0HI/KQka2rBwKwe+gRUrxunV+AvdfEzi2GOPtY1JYD3xfmpMwt7kodJiOu4dwYpg7733prOw4y9UzbwEXfpiubl378ILHw26H+g6ixNr5UAp4cHNP1wCTvANbFMBxxWwkrDu3TjuuONsQhgdG5bz0EoiPjSQ/ObHdXXBE/98RB74ZPyWh1GhqA7tVjWsJKZOnWK5TqX/aiI2ao4F5LNqQGjQ/UDXWXxYK4dMhCyJqHJwy+ZbGHsXrD8WbO6aNBsGdquttmDdku/8v2/JXZXp9ZnBxttu+OrXdhLrmSGrBDx6MlubPDW3vRrhhI+G3A90ncXJ4HDmyoESmiS4CCh849qUKZ08CaZMtu/uxCrCenQlzicPfJpiPyx7ivz90f9l67QyIDaUz3xmGykdOkA6MoaHaxunhicE6S6G+yrCOYD5qCLoa3mFrq84GVQIwA15loSbyiH3Pm7x0S2/5XFMIt3GZaCnTEmfy4Hzbr75ZmxMAscQnH4NHEPx3e9/B6bPNCoVPMvUqSVgFOQPA8W9HTwVTgBp0P1A11l8eK0aVORJEm7kgPANLALB37SYwk7cQhngb4gOjQwIYnLe1996Nd0FSY5D4tWh+DrxKtfGjxjTA7KszRwcNasW4/4U+OCTdxTrTBNeAOnr+IGus/jA8Yah0T4WeD8EKgkuASf4RhZhpUt+y9OxBpTBTv/5ldR8fUOd8IaQxIzpM+CAAw6Q88SGemE6kQRemxK7ID/84Q9t68OG60RxmL8XioLB+Q88eH+5LvwxYf7+0oQXPhp0P9B1Fh948BMNea4EIgkuARU4X+YNLsKkSwbX2o3YWL1BPv7KTjvIefC3NX9x7FHywrM4L57DgaXEfgfsC9fPvzY5Tw9MFXLA5/HITLPh2aFG1wWrhKlSDP948u/ydWX3InmV674RYwxiYKSDXbcy3PDRsHuFrq84oeEOipwkwUXgBA1BBGXm5oYUZk43dmnaBxMT8Pd/Piyn/1tUDhjs9Dd/+ozPwZE+Y3flUDfcevuNqe7CbrvtJkVhrlcuO2M6HHBQ5sFNFeEFL4hDp+k6iw+3uzFzwZckuARU8A0sworxN6prrAI88AnDjCF+7rnnLHIwBDEyFocpUycbYxKK4yKMhnshumRVcMGF58p5TSkY68brUE6Fb+7yDWhsqZKvjUHi74sTXvjo6/iBrrM4iSnCnC9cS4JLwAm+kUWo+fWJv5QBxr0YThebxenYZcC9Hd/5znfo06mGA5NvvvealMj39txDjiesXFUpq4pse5CcfkQnvADS1/EDXWdxQgMcBlklwSXgBN/IIpw54eRfym/57bbbluZdNlTG8OggHH7kz+Wh1TvuuCN51mjHH3887LQTHhw1TR7KjRUHfS0Eg0SnpbH/+4UXQPo6fqHrLT5ocMOkxOn0by6BTNCNLiIz+Mtck2HeDddZgp9u4+Mj8MY7/xaBN3aDPvPsM4BiwJO55EVmppmDjthNmQz77b+vrBz463gjvPDR1/EDXWfxgXsqcMwhiGMdcoFUEm6Ob+AbV4QfulPHQeBRjeOJcRgc6oNv7voNGX6UyMIlH8JLrz4vKw68toMc2BT38XiHRWUfyXXguvpGaHfC75GRfEMNDhpyt4Q5WKoHfo+MzBcpSXAZqKAbmWpahFtuvnWBHEMwD3DC+1gZPPjI/WxeuvsYQ+P0nFvsYeQba3DQ4PuBrrP4CGNPhR9KuAgofOOKCBJ/AfdLOOGjr+EXut7iA7sSulUOCArLJIsk+EYWMXEJJ4T0NfySjxPB9IIGM2ycKherIBwkwTeuiImLPXh8Qw2GIA58Kn4pIIUehHSCiiGDJPhGFjEx4SHkG6x/rIGmr+OHTUQQinDqAJUCpYRuXBETm3Tw+EYaHEFUDghdb/Ghoxjw+pVUBJmIJFEkhBM8GnI/0HUWJzSYhQADTh/7IZLEBCac8EVVQyZwjMG8jwc/FUPlQIkkMQEJJ4D0NfxC11t85OMaDkFAw+6XSBITiHDCR0PuB7rO4sFaOSA0mDqQa+VAiSQxAQgngFG3wgs0mDpAwx0UkSS0xRq8fO4ipCH3C11vcUKDqQM01EETSUJD0sHTXQ50ncUJDaUO0CDnk0gSmmBskGEEkAbdDXQ5us7ihAZTB2iAwyCSRIFRBzIf0NfxA11ncUKDqQO4a5WGNywiSRSI8AJIX8cNdDm6zuKEBlMHCikHk0gSIRNe+Gjw/UDXWZzQYOoADWohiSQRAuGGj76WH+g6iw8aSl2gAdWBSBJ5Jrzw0aB7JZ97UvRhIp6qXSjwfeFPBUaSyAM8gHxjDQb6On6g6yxOaCh1gQZTF1AOJpEkAsQevnx9M0dHRrolpmnVEPRh00ERt4ghkkTAhBM+GnK/0PUWJ3KjVwS00NBg6gCVAiWSRA6kg5evqgEJonLI5/vTB11P09axcoiPZpdDJIkcsAeQb6zBQcPulg7LfbrO4oSGUwd0lANCJZCNSBIeSAcvX9/MuN5cKwdzHXTdxQcNpQ7ocPCTChp8d/QLBiJJuIEHkW+wuUNfwy90vcVHtBvTPYNjNPhuGLARScIBe/Dy9c2ca9WQz/emF7pe/UnXysFpT4UzRtWgIpIEwR5AvrH6x7o+GnQ/0PUXJ7ruxqSh1AF8Xzz82eBSoESSSBJOAIOoHBC63uJDXlQ2ueHrhI6VA/6dePizwWXgxCYvieCC57QOGnC/0PUWJzSUukCDqQM8+G7hIsjEJiuJdPjy0ac39zDkWjlY91T0Jm+LE13GHKzHWuhYNSD+KgfnMYdsbFKS4AHkG2vu0KD7ha63OKEh1QEaSl3gwXcDD71XNglJ2MMXyaHQ4AZvBlK3cQcaTB3gwc8GD3ouFLUkwgkfDblf6HqLExpKXaDB1AEe/mzwgAdBUUoiNmqOBeSrajChQfcDXWfxgRu8GUadKgcaSh3gwXcDD3aQFJUkwgkfDbkf6DqLExpKHaCh1AV8bzz82eCBzgcTXhLOAcxHFUFfyyt0fcUJDaYO0FDqgjX07g+h5kHOJxNaEuEEkAbdD3SdxYeu51MgNJg6wIOfDf+7MHNlwknCOYBBVw70dfxA11l8mBs8DaYO0GDqgDX47iqHwsnBZMJIIrzw0aD7ga6z+IgpQqkLNJiFxt/BTzyshUJ7SYQbPhp2r9D1FR+40dNQ6gINpw7w8GfDGlD6uDBoK4nwgkeD7hW6vuIEN3gaSh2godQBHnw38HDqglaSCC+A9HX8QNdZnOjaraDB1AHv13BAoVgDqacstJBEeAGkr+MHus7iQ5eTrVTQYOqAdznoKQMnCiqJ8AJIX8cvdL3FBw2lLtBg6oC7vRMUHkLdKYgkwgsffR0/0HUWH1g5yI1ew2MdaDALjbxEvmc58OBNJEKTRHjBoyF3y6Z3GXodf6cCocHUgWLvUmQiFEnYw8g31mCgofcLXW/xITd6RTgLDQ2mDvg7xqHwB0AFSd4kEU746Gv4ha63+MCuhI6VAw2lLnivHHi4ioXAJcEDmK8Q0tfwC11v8UGDGTYydA7TdQPHG7yPORRX5UAJTBLhBI8G3A9Bn+OhJzoOQiI0lDrg5Xcx0/AwFSs5S4KHkG+w/rGuj76OH+j6ixMaTF2g4dQBHn438CAVM74kEV7waMj9QtdbfETjDe4w/048+Nng4dlU8CSJ8IJHQ+4Hus7ihAazEGD46GMd4cF3Aw/NpoYrSYQTPhpyv9D1Fgf4c3fW+zpWDri7kAZTB7zvqYjkYCWjJMIJIH0Nv9D1Fh+DI3pUDhQaSl2Ie95LwQMS4SCJcMJHQ+4Hus78MJYYcWQ8x9vR8SH2egitHGgwdaA4Kofi3n0ZBDZJhBPAXH/6zoSuN3/ks40nxtjrmejYpUBoKHWBCyAbPBARHCEJa/DyeQwBDblf6HrzTz6bkyRoMHWAhlIH8H3x8GeDByHCmZL8B4+G3A90neGSz2aVBA2lDtBQ6gIPvhuiroUfSmgggoMG3Q325fpH6ToLQz5bQkiCBrPQ0EDqBA++G/iGH+GePEiCBt8PdJ3B40VA+Wy6SQLHQWgwdYAH3w18g4/wToCSoEF3iW3QlK4zGHAjo9O8kM+miyR0lIP3E60iMeSDACShCL4D6R/ytdPP1snBqyfRaRnJUCn0D3sboM1nK7QkaDB1gYc/G3zjjgiGHCTBw/7yBy/BSx+8LG5fsd12xFvl89WdVXDyxadLzrhiVnK5HjjhotOgzxLqZVXLYdbVs6FifUVq2oliHvoe8ExHXO686y+Sj9sH2+GF916UXYkL5l0qZXCSWO74i0+Dj1cvlK+D93HeU+ec4Vo8+WyFkgQNpQ7g++LhzwbfqCOCxYckuBxM/vHaPxh/uPocaOipk89jSDuxayFC/OgrT0DrIMrDkASGuVdMf+yVx0WA/wDV7VVw2mVnQlt/i5SBShIISuKPV58r77cJSTwvJIHTUBI4DYVxpngPq+pXyenmek677A/QHmtj61ORzxa2JGgwdYGHPxt8Y47IDy4lwYXglt9e8ntojTXJ9Zx0ye/kLdI+3A5PvfW0vI+SQEEMDPdJWRiDirh8D5xx1Tny1kkStz1+p3yuXwQAK4mTRJXypxsuSUmie6w7KZFuWLy2DP54Bd43KolPG1ez9anIZwtLEjSUusDDnw2+EUfklwyS4IHPRix5+5LodpjTTrrwNOgZEtWDqAYumH8JnD33fPi7qCJOvOhUMA/eQkm8+sm/pRxk4EfxUGTjOVMOVBI4z4UL5sD58y+WYxoniPWtaloLz7+f7m7gfGdffZ4xPjFqiKFfjouISkLep59ZTT5bPiWh42Ak4v2ciuj4hkKikAQPv1v6R5NiEN/m5vow3NbzEJp6G2FV4yroGsKrUxvTTr4wLQBTEubjP849NzWdvteHX3w0NeiJ6+sUlcSL7xqSuGjenNR8+BgrlR4hpd4x435rrFVOx64MXS8lny1fkqDB1AEe/mzwDTYifCySUO95yEZMcVi3VRKr61el7iNNPU0y8L+9+PdyzAG7FytrV6ZE8q83npIDm0url4nb30HbQLOcbpWEde/E2oY1slo56cLTpWzwFh9ffP2lqYHJ8vXlNsoEp19xVlFVElg16Fg5eL/adFQ16EZSEjz87kj/VkWf2BjwGxpBSZj3TczAoRTMPRm4EeEtdjesoVzXuh7m3HIFrG9dl5qmqiQQFEbvcCf0CVmZt92jHanuBnLOVbNFtwM5X3Y/zrnqfENkRSIJXc/G5ALIBt9AIwrL8FjMPHfDD/ht3p2qAD5c/qHkg+QtfWyK4bzrL4QPVnwkxNEtpnXD8toVIrAoAMWxC5aKwUkSJtbdmem9G/g+jWVxAFN2NZL0jfF1OJHP5lcSOlYNCA++G6LqQSdQDFZykAQPk1uuu/8GOFkE96QLToULFlyasew3n/vNBZklYYKywGWwu2FM6052R06T3REr1mMzVJhXnM5n8yMJGkwdiI6OnPhQOfiQhOKb3iPWAcx84+YoThWqX9TOZ3MrCV0rh2hPxcSHSoHiQhI8SIXAzV6ITGSqVhAaSl0kQUOpA/i+ePizwTfOiMJCZeBEBknkXjlMBFSVAyWfzUkSOg5Get9TEclBR6gEsqGQBA9SMUJDmYl8NioJGkwd4MF3C99AIwoDDb4XkpIw9lTQIBUjbioHSj4bSkLX8QZ/lUM05qATNPB+UBxxWXzk+ruY+Wx4+ToazkLDg+8GvoFGFA4a9FwoaknELEHHb0UafreI7/u8MZ4YZSEtFDz42eAbZ0RhoQEPgqKVBA26LtBgFhp/XQq+cUYUFhrsICkqSQRVOQQNDaYO8OC7gW+cEYWDhjlfFIUkaCh1gIZSF/C98fBng2+gEYWDhjjfTGhJ0GDqAA2lLlhD7/4Qar6BRhQOGt6wmHCSyHVPRb6godQFHvxsRLswdYOGNmwmjCRwg6fB1AEaSl2wBt9d5RDJQTdoWAuF9pLADZ4GUxdoMHWAhz8bfOOMKCw0pIVGW0ngBk9DqQs0mDrAw58N64YZVRGFhgZTJ7STBA1kkAwN82luoaGMjfTzaQoGxjI/zkam+ePJwJu3nB7FNOvGaT6m093idTk38+ciLA/LjsT4NAXDI/bHg3S6y/U4YQSxnwVTJ/IuCbfXkDDC2E/CSR8j3Ypp3vAiCxpMhniPmYLshKt1jxqSMI/5SC3Lgu+mkuAbqFtoUBAzLMGR/T3ia6rei1fibFpfcr3Z34MTrv4eFqHQIObKyCifFhR5kwTKIdHTCX1vfgDjr74HY4L+snIY78Pf/UzPR0NpJTHYBZ0P3Qe9s8+B8bP+CC0X/AmG338Lhl3u4RgS8zVU/huu/OlXYN5Bn4e/HLwd3PK7g2A01pRVFGYgR/sb4f5ZR8O9x+4BDx69G9xx3PegY/VH4h8cf7aQhzoVbvwbJO8/cf+t8P3//Dzss9OW8IOdPwOXzPoN9A+0sGWc6BAbwEcN9fBidSM8V9UAr2+shs6xQeAiUDEAA6NxqOgcgJvLauH6ila4qawOPm7uhv7RYSMwLr4NWwcScMTZb8OBZ2yEA87cAL+Z8wlUd46J57Ivi8SHx+Cc2W0waXIjlJSOwtSpn8JFl7TJ6XReJSNxWLOuFyZPmQWlpXNhUulV8JnPzoKOrjEYHsW/hSr8dvqH4/DLMy6Fnfb+teBE+M+9j4MX3lno6vNLRgbh4Uffhx2+fCJst/3ZsMP2v4ezzrlbbC/DfF4b6QpnZKwbxhJNAIkaSCRqITHeLKb1sGA6MZZYC6Ojl8H42BfF8lNhZHhXcfsMjIx3sXmDIi+SQEEMlS+FxCvvARBw2lh7i9g4eDANDAEkGjZC3+xzAf74R0iceaa8lfcFfTfOh/HBzBXFsKg4XrrlXJh/0GfhhoM+I8Bb5HNw7cHbwvoPn2LLINZwxrtr4P5jvg0PHb2rjQeO2Q3+fubPxUaD7wG7HWkhmOAehbgQybEHfk/IYWvG3oKWpvUZqxB8rk58zhdQDoTnqxugrLU1uecCN0IuB7ztH4vDreWNcJ2Qw3UVbTZuLGuAvrERxUZthsIIz73PNgs5bID9z6izceAZVfDCx+JvkAypE70DANtuWwslJeOCRIpS8XiHL1dBbDDBlrG/jzjstc9dMKnkWrHMfAvXC2FcA1df8w5fhlC5vgZ2FnL4yt4nE06Ck8+7Vvy9BzNKJj4yAkcedT1st90swTk2vv6NWaKizCy7kfFBQYeQQ7UUhHFrUgOjiXYWTspYYrWQwxcAoERQmrwtEZKYIsRxoBQQXSYIApdEfEjcfrKYyYEyVLmcBdQEuhuFDNJisAoCzjxL3o/POhtGh0xR2CuLIfH4usO/ahGDlbQwNi5+wZABkQMGr+rD56QMHjxqFyYJk/tO3i+5LJcEss9O28APd+SCsBIbaGXLmSxsbmJySNMsaIJPGpvExm1Kwt4n7xobhRvKm+EvS+1ysDJfPN80bH4T2sttLMHveLKRyWG/M+2PfzNnSVIo9uWRvhjIyiElh1K7KKQsSmNyPpyfBVWs98v/cZUhBJsg7Fxx5XvstU3W1DZKIfzHXicpJGGAAok7VUWigthuhzOYHGyIyqJ/0C7c4bF0twKgkYiBMz7uLIpxeFHIYBqYYlAxPLyXEFErWzZXApfEYEWlkMC7TAoqEjG7HLALMD7QCYPnnM0EYeNM47br2mtEuWWKAr+5jfW8+bcrFHJIM//gz8ICIYt5B39eBIF3G4aHOmXXAkXw8FGmFIzHlMrn7lVK4sDdd2ZCULH3f34OcJzFXE4GTXyWLtGdMGSAosgki0ZY2tZm2zgxaLjBL6hogmsVYqCgKMyASOEkK4h/vdPHBOHEknU8XLGhBGy2eR2Tgoott1ovw0jX8cLLYvlSqxBuYIIwqwp8vTgbaIzJrgWVgooTZ/9F2fU4/oRbuBRSnAvbJ+/vuNMfZFVllQMyOt7JhODEmJjXXG7IXIcIfiIxA6gUUiQMEoKR0YNYyF0j3zt5LAhUEng0JI4/UBk40fv+xzZJIN0P3cel4MDYWaK6aKpKjS9guEaHOuC6g7/AxEBBUeDtp6/+jQV82VN32kTwoEIOJn8T3ZHR4c7kssldt0JcNhns+BkmB8SsMuZfMTt1Nqb8HOL2zZralASerWlgYrDyQlWDDEM6GAPQJvrJVAaU68vT9zfG0t+CuDyK5uA/LmcyoJhVxWGzlon3PpQaAMTbJ/45LAI+xoSgZhwG4uOA3TfzfcSFNDbb/BLRzaBCULEAfvLTe4GOkSxesS5jBWGyo+RE6IxxSWy//ZkKOZjMTt2iLJ57cRUJ3wCMJ+qZDJxIQK19edFNGYVngInBicRUIaVmLgCvJAURuCQSve1MBBl5WVQTfV0pQWBQhs/GKgK7Gry7oaL3isttknl+3hlMCM58Dub+ZHuxQXekBDE+3AX3/OI7TAZOlQSy6LEbbZJ55rF7mBAc2XEb2GvnbWSwjHD1i+5OPxNBNrpH4+lwiaDcvwLHIbgYnLi7ot42ttAeByaEzNTAmiazX47VyCCUTm5XyMCZY3+1whbOd95rVsggA6VzoXfAOjYwCLsc+BsmhEwc/OtZ6c8gqGscUYjBmR22Px2slcTomPsqwmRYdHfN5UfGumBsbGdgMsjAeOIhHno3WMSQN0n0VyzlIsjC6IaNqYAPD/UY4w4eiJ0zyyaJ6475hkIGzswTohiNNaQlMdAoxyKoCDLxt9/9xCaJI/bdncsgC9ZBx75xs6vhnqWtralw9I8PwY1l3iQxr6JZDnKa63i7olchgsyce/3C1PLxYS9VhMGWW7bYuhzf+tYtXARZeP/D2vTfQVRTWB1QEWRip72OTy2PnHhipq6Ggu3PtpXt44lmJoFsoFjM5cegUnQjNgcqgkzEh/+PCyAbCjkEJonBEcug4RsfMAlkY/DjJanlE51NTALZGDvrLLskDt6WiSAbHz15mwh3nwz4+48sYBJwwuyG/FVUHlZJYGVAJeAE7uXA2zFRwZiSqOrvYhLIxhuiS2Ju2N3jYzCvvCUpAL5XQwWOXdQOpbsc5y8wuxq1TAZO/OTMZanlY3GUBB+kzERp6SAMDBoDmMikyZcwCWTj4J88nFp+0coNQhLZuxqUVEU1Eoev/XeWAUsFQyPjqfAlEnVMAtkYTzSll4cnAWAyUBGoKZW3Y2M7cAlQFDJwIidJWMOJeBmPMOl/+8O0JJrrmASygZWH9T1QAbjh8evPSAX80TmnMhlkAysPqyTM4HshMdyZksTKznYmgWy8aJFEZ2LcCH65O0GYrI0NpdZx7HnvMwlk44AzquSycrfw0DCTQDZKS4dSezmkJCZdxiSQiUmlN8A2n708tfwrH5S5Go+w81vR7TUqKhxj+Y+vnMYkkI34SCInSSQSDanlxxP3A5dBZvD4CSYFn4LwLAn8cV68sjOVA5fEu+TWmf63P0hLoqnOc3cjcaYhCTOgVABueOy6P4A56PjIpack92g47/o0MSuJB47+VnJ5Yx04zkAlkA1TEtifXdnZySSQjZdrGpkkrqtod7V3w6AV1iQlgSE/drYfSVSLb1FcvteoJBQiyASXxOXgvDfDyrzU/S23npNa/uUPlgAeB8FFkBlTEoM2SZzLZOCEUhJQxWTghF0SfwMqgWzgcRO5isGXJKgQlLz1oRH+l7kMnIgvKk8tD90tTALZGD37LNu3+F8O/hKTQDYq//1QavmKFx6QwU/v+szOvcca3Q3zB3XwqEoqAQbZ4zGKB6AlN+66gV4mgWy8VZuWRI/sbnirIlAoDaK7YR6n8Oe71xrhP9N9d+OnZ5an3oPnSqI02d2IpyUxefJFCiE4sUDK4oQTXkwtv2xDvc/uhhGsobFB+MY3/8gkkA17d8P9ng2TsURLenl4XkybAlQEmRgZ/WogcjDJKAk8cjJT5UDpL6tgEsjG6Pr1qeWNgUvjYCm34MClGXAM6XVHfZ1JIBM4cDnSX2csP9IHY3213gcuTztYLm+eU/HzvXflUsiC9UCo3tQxEu6paLEOXA77GLhsgX7zG1TwelkPk0A2zpq7SC4v99DgwCUVgQOlydvNt2iV4wDm5/j61zH4VAZOGNXE2+/WpJbvG/YycGnsBdlx7xNs38DH/XI+k0BGtp9lhEsuj7s/fQxcjnekXn8sgQOXM4GKIBPx4eNY0HNBKQm/V39KDPYwCWRCHqI9SF5r1iwmgkzE7rjFVkmUPXsbzEseA+GGq376H2A9DwMPrrrn2D2YCDJR9f7TUg4mSz95g0kgEz/Y+bOpDRvBb7LnFSLIRP94OlzIMxs7mAgy8dDKetlVSAVsdBxcD1qeWSPHI1oG7IdXT562hglBSalxe/0C+0FhGzb2pMLvikm4Oxy7TMYBYVgV7XXEmQohcMyxiz/NvcMmicHhBBdBBnb48ilSDubyeKg0JNx3NRD7WaH9MDq6J1ARqMCDqYz7r7Cg50KJ9SxNvE+D7wV5xKSbwctkd6T/vU9Sy5nr6L7vHrsIkkdXqpAHU9WvT0sCK4Ghdrj+4C/A/B9bz9cwMaYt+LF5/3NQ+fwdcjmraMqfuDkpAGNcAscenLof9x+zO4wPdQq5pCUxPNpjF0GWMYprLz7LFg7kzY11TAROvFBdz5ZvHY4zEVgPnqKsG7CcpJQ8oOngP65MSiCLLM6sg5/NWi7+dvYTnR54MCbC7343KB5MZfscoqqYOfNiLgNL5WDlgAPuAjw2wrqOD8pXwH/szaVAQUngkZmdor9jlQSy3XZnwvZf4kJArNPxYKrH/1lhW3ZICMNLlyMBNTbJIOOJf4npXAopOdhEMRlGx5rFNhhnYfeLrCS8dCmyMVa1kUtBgawihhTLx7ug67xzpATGFWKQnIVdkjMg/sTD4tsiHW6ThmWviW4EFQTyedvj6w/6oiite9hJVnji1gPHfIsJAXngGPvjgdpKeaRnupLAjbMPLjz9V0wGKvb9xpfFP4TinAfbYdlcDCZYcVT38+WROyrqLSLAykI9TnFTmV0y5unY61tAVAg1rGqwPj5A3tZCUy8/SWtwZBS+uYu7w7K/+/0NfHlBbeOYQgiKwczSv4jtZ5StA6uynff+PyYFxj4nwr3/eIkJArn7vjeZHDizYe+9LwQ84tOsAMzlR8axmqh2QY2YV3FGqJg2PrYtWE/qSpGqHgzGxs5gIc+VEhrSXMGqIPbhQkMEL7/L5GAyVLGMLWsC7XVSENazP22I6mJIdEtGhrphYJRf/AWP3bjusJ2TMvicQhYGq9/9BxMEMiBY/frjirEJ++P7TtxXBEp9LQecnn1X6DbQ19PCNmyTjxrxJC4uBisfNeAJXnxZpGN0FBaUNxMp2EUxv6IZaoccTnUWJftNj6aFQE/s2v+Menl7wiVlYD8cOj2+0iXkYTvBSwEOWHb3pwcsTXBsA2+/tN2VXAqE2ef/W76u6m+xdF11Ugbqoy93FNN33vt48a3Pq4hhGfoh+NL2xvES22+v3sux/fazoLd/JLmcWQmkKwLcYwGJ6iTY/eBdkPFEm22ZNAPyeAnctckkYRHHyPB3jRO8ZLgDrCRoQIMAv1nji8qUp4rLa0u0NLJTxWlQEzVroX+2UVFYwV2kPdfOhdG4eb5Ety3o5o/vDo12wT+vOSUpCXsFcd1BX4AVbzwC5gFU5nrkbfKKU7LC6twI9/9idykEe3djN3jw1B/DiPLKT+lv9RHxXn625zcVcsCDqLaBxro1cr5MFyyp6e9Rjk/gtIVNLcpQWOkbH4Kb5anivIJYUNYknscDqNSVCILvbcGjNXDgGdVG5fCHethP3McKAquMf7zZntplmIKcJNUtvL/NNvxUcXz8uc9XQb/lACrrRWVSfxfR7dhl1/lCNoozQUUFce5s3KNhvib/LBi0T5avFd2J45kgkKNOvxTiQgQ8nGnio2NwwIGXgepU8a/+Fx7Ql97t6cTYeDsTg0ENjIHzGaAGOAi6EsbHt4ZUBWFWEdjFGN3HuC6FIuS5khdJmAyL7sT4+g0wiGMPHyyE8U5hOYscqBgouLdirGEjxP92NzRd+CcYffEZSHQ3QUzx7e/E8GALvHHXn2DuUV+Hh88/AtrWvA14Kjmdj5KqCMT99pXvwrOX/gb+evIBsOSR64Sg2lPPUzGo6O1qhHtuuAJ+8F+fh5MP2w/aGzeI9fL5nBgU/1DNIijv1DbA61V1sLZPCAy/4SwnQ2Wja3QEnq3qgNvKquGp9W3QjuMHY0awMknKJCZE8NqSGBz7p3I4/uJKWLhuUFRcw/J90HnVxKCuYQz2O6AVps9YInwvHstzPdwuL96nqHjmzi0TwbwSdv/2zfDUszVcUBZsIcMNXtxubO6Ak8+fB7vufzycN/ce6B5Mnyfhhs6eOCy46XXYceffwiGHXgP1TWIbGzPW7Y4BeaZnItEIifEmGE3gngxV9UBIBnZIdGMSifdhdOxw8e+/p1jHmTA63giy4lEEPAjyKgkD9WAodgloMFUYxx6kT6XONzz82eAbZ2b8LLOJozh9G4NDp1mfmxi4uLalIrQm+HfJNk8QhCAJO3gswsCYu9CrxgvsXYTM4MVj6DQV7n6Xwk62ay2mS2Xrxtyn3OCdsVcK+G1hLm89pdoNuDHRaSbuq4EBj+/fjnHNUnM9/PnsOAuWhcuG/fmh8Wzz+yV76K3v1fF9K4JqEjerFsVz+SLvkhgexYEUPK+gUfTr0qdkuwOvBN0pNig8O7BJ0CY2aHeCMZHXaRjpSmG9wAtCw68GLwuGZSH2G/FELG8BlSPeorswPCxK42H8BuAXV8nGqFh2JJ5E3HfTRbCCYxeDYuOKJck2lqFELIevi+vxsnz6CtMx+d5HhozPgI/pvNkYGRYM9QvE4+HkemnIHBkwulhCEgb0+ezgLs3B8X6IjYtta7zPh3DEv8W42AbHWwVt4n7y2pSKcDoRF+vAL9A+8R5i8guOzxMkgUtiKHmbGC2H2Jq9YXz1ZEisLpWMr54KAxsOEX/oZhZmytBoO4ysuw3GHp8K44+J5R8rEbeTIf7ENpAYXAK46zJ1WXvz1hRDsoIYHWqG6w/7T5hv2cOB959dcDaMjeC5EriRGSJQVxPd8NgTJ8AVV0yCK64sSVIKV1/zJejpwxF9vhFTYr0JuPP8T+GOc9cn2QB3nLcGnr5vZVZZ4DfvWHwYFux2A1xfOg/ml9wgmVc6H+Z9fR4kuvluRxUfV6+H0+5/EE564AHBQ/Cb+x+CU+9/AF5eXimflxu/dRlLeFEGMbFRnjB7Fux+xOE2/vf/jpXCoK+XWjZZ7aAMVn/YAD+ddBn8rORKwVXy9qeT5kD14nb5fDbpQFsbzNn2W3BF6Y5wZZI/T9oRbtrvCLE9GBUWD2SauKBzrA1qyH+1iTqIJbKPS+A1KtugGe5uvRtu6bolxW1tt8Oa0VUi7JYqAsOlWEc/NMJNfd+Cy0enwpyxUsEkuGx0CjzYewT04cVmFAE1QRHgZ7h5/U3w/cV7wv8r/3+wh+D/lX0XfvLJwbA2sTo5b3B7NUzyIomx0Q0wsmobgDUohxJGbO2e4sXrHboT+O0vBPDGT4UUJkk5UEYemwljdfez5awMtH6qPI/DuDCuuD3mm6ndl9YDoYyN0hDEk08dD3++ypSDnT9fMQX6Y/aLpFA+XdwFd8xeZYhBwXP3bcj4bYqCuO4r16bkQLlm2jWQiI1mDNiKtiYpBZQD5WQx/c21q+R89PqO5qAoVgF7oBQOtwji8CNT9/c+7hfQr+w6GH9L7CLdfd7zcEjp5UIMVyQFkeaQ0j/DQ5e+yZY3PxPejvb0wKWTd0rJgXLRZl8V0uehtNI43sgEkRZFDQwkFMcnWKgdq4I72++Am7tutknilq5b4bbOW+HfPa/IKsPo2gzIQFuX74UqmNf/X0k5UCbB3Nh2ojJRVRVG6LECuqf+HtijbA8pB5PvJG+/v/j70JzAAUyjSxJkdRG4JMbGlwlBbMXEQBlctZPYAPj1JbE7MVw2yyIFo4pIPG4XxfjjpQBDFcaRotblR7CCwKMunY+PMLnz9P0dKog+mDd/F1v1QCUhRXHlZMBuCN3AEZGxdOWQgUWvp8+5sILyuHqzK4UMsIKYzwRhMnfGXEj0kSMVk7yyvELI4GGbGFTC+Nt76ovI4ljFnkcfAd+2CkLBtw//uUVU9vGa8pfXMjGoZLHmPfNUd3tXblR0KS6dvCNcNYlL4qqS5P2SneGirf/H8bcnWsdbmBjof7Xiv8GEekyhS9QQdjGkudlyf+XwcrYsMpjohCuHtpJCuHTcLoj/396ZwElR3HucBc/kJTE+MeZ4iYr6ntGooOCJxsQTNeYlzytGDUajogbxvmBZ7mOR0xPUiAeIilwGBbkWwQPEBbkR5WaBvXd2Zufq/6t/9/RV/+pjdmd3undr+Xzp2dmuOev3narqqp6+SfPysNrjmKzKLAFtMC4/vvZxQwxnrMLtWeq2s3pZb1V0ZSrCI2c06E0hJ5LQ5ybgUuno+pOIEJxIVE4gkkjteYd1MWgLIs1LglE/tSMkEtriLA08R2Q1DP6Tv7NTYdcjVrU1UzHNlkRF1QoiBCcGDTqJVGxs+o57ELsYVAomWzPbzbB3G+12LBtRQoTgRNFRhaRFEmWfJrdlWgu6DG6xyQG7H6+yfTSJ4HwK83lo20tuuZlJ4FoiBSunZf7+0LAhpEUTr0zBle37wtWcEHqo2wG2665g+8XjDbbbwMPEz115kyEFvath7XJY2TZnAQkodgN4IfD/vstsd7Cuh3HyWQsv7nuRyMHakhibkcW48nFMKAeM21DHP1J1MKX+ZngaBUFaEIx0O+My/v25qotJSCuU/bbWw5kr7a0IKxcu767dvyDsjaXJkrAGPMmaZMp6KgMn4uuPYU9ov+02Iu//NxGEG9Eto7WymfUXifIN4DbLkufFXpeqTWv1Tc0EZOzYLo6tBxGRmL3bEa1VBFJw5uVBa7VQWD6Biw4pguEuLQiedCyVeQ6a6Fbu3klaDG5M+fxT23PAsHq1IKyc8YdrIGIpj9x9wVDSYnBmAFRvjwOOY+jhTNfVwJMHURk48eRPT1dbE9agHxCMQ7j9q1Hs310RVWphLAv/uApeDmLeKX/bDCnbRmAva0X8gMrBARyviHKTokZsGk5k4EYZ4NoNGvbGkrUksNVgthzsNFSMV8OPYxHgRxbrWVci8lqmvHbSluRbBxMRuBF5q6NaXj/b9Pi/X5hpJVAhiBh62dGQxhO+ZD6JE+mdrBtxMBGBGy9NusIWjtmveXczTLbC+D7azEv9UzRVn8iEHyXhTxRrp64x7h+7Cf94SRuk9MsdE19m5bAFobUi1m3fSkTgxYtvv2k8Bjya06NAH6T0Qtvvxk79wHq4cv7DA4kIRFhbFtVbvrV8itfDdmU7EYHbv53s/bdK5ov4Z0QEbuC4hR4uHBeYm3qQhd9sLfhhp/KJcRvVrG1yzufnCFsNToz7biwJemNJpGLZSYKXAk/Vht9TEXgQ23GHUT4d30Yk4EX8rcNVOehdhgFX/IKIwIuyzcuNyv3d9g8y4fffkujb76hMeS1gYx/9TCADEaZM4nHz/JLVX5cbkhgpEIKIMeeNyYQTp2JHoeekV+C2V7FLQYUg5lU4ENMHbiMw5rWXiQS86Hbt1Ub5RENcIANnehQUqV2TRDJhjC088L3jHbsWTnxR/KIR8IhSA9tYF4IXgdc/vTwORL5R9joRgRdRPCyaCdmwqhOJBLyYH3/CKP+Nshm6ruhGRCBC74b0WNCDhD1bUA46npJwajXY0QYPE+v/k0jAi9pNFxq3o9QvBGOg0gfwJo5NtM9IQmtJDLtU/84N/12O2c89bVTu19+8jUjAm4PUsnpLYHyfDQIh8NhbG6w+arfBmttLnllMJODFsB8PNZ5DldKgjkdYBUClwPMqbKg0z+dwzR09iQS8wC6HVr4OktHsJKGJoh+k68EI6SOHHOdbEvog5tBTLjLKV7OuAy8Ar384PqHPfcB5EJPKXiIS8KIKKoywDYr8lEjAiwmRc4zyJbWLjcOdfsGWBx96P1jF4EsSVATO6Icy0+sPIRJwI826JDXrOpuSiMwkIvCD9aiEFnz7gi4vXivsqVZurBijx/xOIAEx1sOjeriQCX14IYj41i4JyyrIGY/NIBLwYvBBg43yFekGNfjaQOUrwiMaPDjAWbrfPNJyNmsVYPBPE8hAxG8yYFk8bJqsj8OVBVQETuBgZo+CQlDqTEk8erB/Sej0/t5xRvkqpYJIwM8/qyReLHMbtBRTjou1MsErqu9IJOAGHv0YUn2cUX5uxVwiAT/wAnCDlwIPkYS/loOYxIZGtCQ2djclUf8xEYAXZktCw2xJ+GfmhMeNcLz2+i1EBt5oLQlTEn5aEnb0lgSyaNRCIgEvhh0xzChfzVoSfsTAs97Skrjq9tuICLzAgU69fDLWuJaEwrUkeAl4Mfh/ultaEk2XxMRGtCQqLS2JgZFjiAi8GB/papRfUrPI6Eb45ezPcR4SlQEPLwMnDEnwgW8M1Rt+SyTgRcOO243ySvw7cqjTi4QxJqH1pwdc8XMiAS/2ri8xKveWrTMEEnDn6b5H2o5MjHnkcyIBL+IN2jdPYXejovQAkYAXY7s+Y9y/PibBS8AL65jEyEkvqsH325JAzrz6SqN8tmMSiDomkdDPyVAPDxyWvSQ+GzLBKK+OSTTin15eHZPYN1kNvt+jG0gE51tkgjis2mkClTMfNjxilN+ibISzVnQlInDjioWXEyE0Rg6GJPQzPDcdVsEOjCYScCON07XrXsmUN49uZCOKyFtHgXYCWi1gY3te4PvIBqIe3WgwJ0TFG3F044UXL7NJYsYrG4kEnBiP9NlklMX+vHl0wz9fvb7KuA1s7t85cRKRgBvq0Q0MBr6OjNXfbiYS8GL86/8yX0c8umFMwfbHDccWGgFFPrjvaSIBLyo3bzHK4wBiY45uqOUxUGz7ecOnRAJujN8/3hbI2an7iQS82J7GyW1aefXoxhfnEhGI0I+AjPqmmIihMXIwJEHD3niSqW/U8Kc2ahLwOgyaWM8CniozymNroP7d44kIrOBgpfX32MbhRsXEUfFE2ToiAifwXJcTbr+AvYDWyVC1UFyszbbsX0iFIKIu8pWlfGa9Rm8qBCcmFq61lVdnWx40gIjAjn0mZjpq/Q7MCHy2czsRgRuTly3VDhvqq0yTWc6TuPYaqMNylpDf2kWbWel3bKJiq/3EL+naanjKZTo2z+Mdf2ObdYnPY39qHxGB8J96FOQ7dbAT12nowcJWwdgsWhFT9k/RAqmXhz1Q2PB9IgIncC0HP09iwPoiIgQ7Z9l+3wPa9OymiMFKTiWhzbg8nsiAJ71R28bLi9X5DeoXBWfWT6R2vsHCT2dcqlhbGOxybMp/QiqB03mtIa+DQdeeSIRgxVi/wYhVbLGFCzlQvtwmAaf1G0j/gccCOUclzrh8aC1ocyCwpUDFYEpkM+z6xiyrHyFZ0PdjgRjE9D+iMHO/5u1EWEjsRzh4zCMet7HLNeqMS+uszTr47U03EhlYsXZFeg3AOQ72iUzximRmzQYVghVsceAaDr2rYb2NsRf/mcjAiU3T5oB2ujkTbE2YKnBvVWgzLs3Dlwh+98YLZbioi1+zQcEZlxWWQUtcd4G393rk/4gM7GLQL7eH8dXnmgHPbA8oZQIx2FsPOhd8eoH6+vFBbwo5lkQNpFNfQmrt4ZoQ1rcngtCJrf8ZewHM77/USSSqILb8dioIThba2g3tex54sPswPLN2gz9r9gjL6faf+Ws3UlYPyMBBxxIhUNqzirjP1tXQidf4W7uxZMZubUo1N606kYhC0SG4doNKwcqgg4YAVIvXbkxf+YVADpTx8/D8kFoZ67RonJTV5ZqriBx41AFLqxwsLJu2hkhBxOqPtElQ/Lkf0ux1eaoDFQLPQ4ceyyo0vX9kX3qvuojLnIBt/WdeF7PMbzBpgHKXtRtWvmpYRcrjqffqlQoojDu0JvRp2Ww7uPbn6gxN/jaQf5b2JoLgwRWhW2ATCXlTybkkkHTkbVdBJNb9AJQGrJh2QRiiSFZAdGpHKgeDAqj98PckFNYWxQfjHiYtCA1NGngURJ1pSW5DI57aDUVFRwnEYDL/4yfJ/Vr517A1GRk4yOLR1UwQUVUy9nUP2gldq1ZWwJCDBhMx6OCS8QOfm4cteVnh2MTQmTOJFBB9HccTU6cY53sQsatyH5ECL4iSr75Qw82LQu16sAp+9Y8eswjBvmYDufrIx7UwCAKObHh7pnoo1FjQxdGPESszv/UKsa6fwPUbTmMTuiL2pfSFVXSpNY4PvHfgXSIFDa2F8cLe543nS4nBqvQkJorDiST0BV/YzdgHKwVltRZFlVIJVy+7hohBQ1sZOm3fVBLwXJBzSWDXAY+WKKlPoWb9qUQQkQ0XsDveA7wYeFKJ/RBfMwiw65F+wxQEzrCEyCeZ/WiltqLU74VBl/3UJgkch/jX0zez1ga2YmgZG4lqeOHFq2xi6F9UAH37/RDKKsQrJ+3l66G2QlGnXY/rY+li9NkCk59ZpX7KaPsKnkumZZGOJqDwZ2aLojiz7duxLygHtPNJxFyWm6NsPt64HnpO0s4noS/46sm2Uz//1FUQOrgmo8ffbtWkYFnwdeY1PdTBTj7UPFjJV/17K+tS2Fd/4u/rFmX6z4JyZnnWoti9Rz3awYui76/PZe+z9/kgtPNJ0PEJ9XwSwhYEZS/r7Y9Xl4trgsCFXdjFKI2vdhaE/hjY5RrYCUOrj1dbDdrqz/bq5WcrL4ZqH6s38T6K1vVTWwxWSVz4SXdYkyol4c4VOZeEnWpIJndBMrVVJZHE4/BaIPSvxBOhLd/WKmiSdUmSCXYbie0MbIqZ35npDZ7IFpcbV5okcICU388dtVuU3s9eMPy0wpPgcqdudwmpRlRd4RhviLNt3CIHF7jbTDZE1QlKyUhcnYNA9vcAH2+E9a9r0zF1a2+5CCRlQa/o2qdyjPXztfMb8EH0IsE+UZMNCUjFEuy9wOnXmVPYW8PkAnYnUg14ng18Pdg2TvdxJWmevEVHC6C5JNsZbR8sH0nXMqqhLs0+EPHsVmRfMTjmg/dZny5nZXeq1KetYxj+wG4RLkSrTldAnVID8XRuBiidaDZJYGsCK1/MOF8DNskx4M6njHP6VLOeL5JvUmcLhgNvL5vb4ZdAU8TdjWhKv949hC2N9tzFj9m2nyVguhSMcyzmDPv9ZIt+NIM/yYsNQdByhT646IT477RLo+LxWDGw8TQf4gb2AcZfl1tyLgkz9HgZP3GtIsDKR+XAV862QNMl5f26+b0PXs4kZA64BpPfTw9BI3E6oYwrgqD5CaMTqiAF1yMogwSex1TwN7/gkRT+OoQPrRVdGnHB33JFziRhBl5bjYlElEp4DsbBbyu7w2XVl8GX8AVrXulfaOP9SYbUw3fwxvzH4eHRF0HJ2kkQVfaTprgoDPp1yXgdKJu2QN2S5dCwcjVAlT4W4e/+sXLCtijUv7AM9g+cA8rcjZCOed8/op40lgFVCYBnV8OmLsVQ+ZdpAHsVxzIEtfXEHsOOFCzuMQ5mnFUEiRnfqdep8nDt6phnicIjFdM/WghPDh0Nb874N+B3eej7YQXHrS1ctsDVsX2YrJYsgIEnngAjTzsV4uvXsK6g+ExOTlRAOfx53B/h6L/9BArn9mX98HLLfYnvXz2cp7cWlDp4fdNk6DHuSrhl8s2wvGqZdshScF+ioOF2L9TB03PGwlWj7oKRi19jdZTu60YdRGHa7qVw4/S+8OjS56GMXeMUbhEomq/LvoGTr+oOF932J1i2CSfB0f0QPqwarOXAXrlhz/eBux6/GmYufBkS6dwe8uRpsiSsLQL9VHA4GeSvkZvgkOSh0A4KDAqgPRzKrvsY5rEXSxRS89NxT81auL/4NOj1zPEcnWDkGzeyfrHzkQm14rNwxNdt1L5FDL+gWKVE/Rax5IclkN6Lg6e0nA6e81EpZ4/x/pkA98y2ke41G+oGzVNPrWYtwwdfqW2A8stfBaXjBICOzwIcNUGD/R792WiAre7jI3h7tSXfwtJjBsDyowbBpx0HG5QcMxDWPvAOuU9CIgqPDRwLD/QfQ+jTf5Rn9wHHAUr6PQ1DOnSAkQUFMLJdZssY1r49rJ38iuenfAXrd//XfT+Hdne2g3Z3FNg4vvexUINrHQTl1LCksCUSgVtevxlOGNEJjh95vI3/HnYSPP/ZBGN/p0/71eVboOuwG+G0ETcYnJ7hgXeHsQ+vzP05gDJ5qOQ5uGBWH7hgtsb5c7Ttn2f1hUrAqdi0JWHtbkycOQUKuvyK0KHzr2DQy2PMMraQNhiX40ot3NCrK1x/7xkcneHhQTexffiyuaFRknA6L6TaekhXQo/yy2xyoHSAu+vvohU6Q21yuyoDKgiTe4tPBm2Mg5ZXWfAJ+YpBnlSZsyiUFTsg1WuWJoa77ZLQr6t6crZjSLG1Ef0pE8FRFjlwpI4eD7DfaRCyFlb0fM0mBiuGNG6eBIm4uDURYdc/2P8ZIgeN0ZooikZDea3zSWDnPfaQTQwiBp/yP46iqGEyb//39kwQiC6J9jZRdGB/r1E4UWBgMpcvGXsJkQNywshj1e1xxcfD+OXOJ1rZWLMDfjP8epsgdM7A7cjr4axhNwkFgy017C79bsZDhhxEXMjkUWlZs2GiDXh2uvwcIgeefs+PIgHV2XFgvSGFG+49zRTEfacbl3s+cCkkFVq2qWQtCV4KPM8nx0OB0kEgBjsd0nhcmIY0lqqE+0Z0JlIwOcG4/G7JQLWMGVStJaKU7ydCEJGauwTw6AffJ8fQJe7LCMIFBbe77KLSH0vkgQ+JFETsPG0MJKP0HJdQ0wDLjra3Hj47isoC96mdS2eNIk8PHy+Qg4XCcWw7lomkWHi0IvntJtZasAthuOVyMWNEhsSBXVz5OnU1Zde+XTUZZARRYGtJmLL4/aDf28rrj2dnYhscP0ITAS8JKyeNOJG1BjLdH2vIWfC7DbnJlMLwm+A3I+0tCp1pa+YJQh6F97cvJUIwf+/NeEC9fM+8kcKuR1ldORFC+85UEnjdtopdJKTIDfd0E7QgumREYUrjX++MIGWbii9J8CJwopY1Gw9JHUKEwIPdDtyev+cCEtCJ7A2wisCdE2Bv9VpbefUQ2YdUCE6kv9thK6/y4UYiBCca7pvBWg32Q5pKfZS1EsYRIThR0Y87pTz79JrRrT+TgF0SIj47egjregyAFH7pj+U2qmprqBRc2Fa2zx5Sdhv9Dz2ECaAdaTmIGHDEDyFlOT8lMrX0LU4K7tRx55fESVBnDjuDCMGJf0y5k4R0xd61RAY8pw/XJNJ5+I2wL1VlK4+ti4tnPEhaDiKw+zGnfAWoYwwZWeHlI84+iQjBiUO64Pkw7CFd/+3nAkE4k+sxCldJ8BLw4lvYRIQgQpcEtiZ2wjbb4Bt2I6gMnJnw7t8zZbUxDuW7bZoAMuMPXkTnlajjF/r9pxtYE7nPDCIDMdjamAnpL3YajwGlpyzaTUTgRuUvRxv3jyRZS2Y5ayF8JpCCE0pNUi2rt2Ref+/fRARujHzuVTOgrGIrsWq1hcDLwAkcn0ju3w3Wr7r7/i3fIyJwpj2Mnz/WlBRjc91GIgI3Th56MtTj/VtCfu2E+4gUnMCux/CPJhnjCCiI/eyjj5eBE93ZB9xV7zxiu//t1XugvUAGjrDWBM5FsYb0/r7/S0Tgxr6ab0nQm4JQEnz4/RGBO/f/nQjBi+Fx/WQpeBs1YI5F+GtNaGMTZsCiC5dpg5U+wX3TUe3xq5KpjKsDk1QIzpQXfWB7DNsvfYGIwA0cm7COK6SrE5wEvFsUK56abr4GSbexCDF9GOqncCakm6ZPs3UtPGnXHkZddIFaFisWnrCFisCdI/5xpO1oxR8nXktE4E4n+GQPnhtEC2gV1LHuhbhr4USXYdfbQv7U8klEBm5cNPtBoyy+nmfd2IOKwIN5Xy4zAhpTauD6Xl1sYw9ePDzwFhL0pmCThNuApDta5Typ/ASuxdCOSIHnD7V/MLocOAPNa8DSJojRneDeUSca948kPtSCz8vAjeROs8sRW7wpE356VIMyC9JsW9d7hq01tP+4UUQEnpRrLQHkwPzNRAIiPrPIY9H5o9SyGK5oqoGFXhuY9EufwjGwv7rSmPvwxg3/p4Y/m9bE44cfagQcZyTyEvCi/d87sM9t81usTh18ikAEDhQfyzgOHp1rfpKvrtiqHr3QBfCbkVQKGlp3Q/97LLNUHLfXz+irhl8/kuGHaogYj+GQ0zH4x6rhbycQgoibn7zfCKg2YNmZiMCNG+45mwS9KaiSoKH3wgyllcMThxEJuKK0g1PLfm2Ur06uIyLwppPtMfAC8EPt6q+N8juf/VggA3fSTBbWx5DCQ568BLzYlvleTyabVSM+IkLwYtEvBxoBjaUTRAJ++Ga3uUjqsZ/+hEjAi+EF+I1mWvnadCWRgBftWZejgjXw9YCdPPR/qAw8OLfYPAnsh1s+FQjBG/1waD2TRI/3HiMS8GIfa8HoATvojF8SCXjxn+edYpQv3bSYSMAPfNAbSzLdAO2oAJwQzWvgJJHMUhKMU/aakqhKfi2QgBemJLBy8gLwQ51FEjsmZCcJ5W6tNWF9HdIdx1MJeJGRBLaqvhz+IZGAF4v/yyKJVJwIwA+6JHA84NFjjiYS8GJ4e1w63wRJ/L3pkug23Dy/49zNy4kA/GCXxKNEAl7YJUEl4MWPzznZKP9VIyRxHWt58GHPBhSDFZ+SoELgwYrx09pfEAl4cXHlxcZt1Ka2ql0IKgJn7h11gu1xJOdSCXjR8M03Rvnq91cREXgRu3+G7THU/NcYKgEvysxzQmyb+iWRgBeLTh+mnVHJkP6pHuUAAB5YSURBVER23Q1kd/kBI+QTLrqQSMCLfoeY3Y26dBWRgBfYkqjB7kYm5L8ecjKRgBe3vnWLWhYHHz/ds9bW3fBLNCMJXMj2v+8/RSTgRRXrbuiBOxi7G52za01cdPv/GeW37FoF2Xc3upLg+4UXhIcksOXg3XqwckvZzUQCFO3Ihs7A2ACjP4/fJo4tg3tHURk4YR24xGnK9T4mUVlRPlgM6Xpz5qNSHlNbBrwI3CjvN8c2JrHtomepBFxIs+4JrvLEsnh0Il3RQCTgycNvZwKq9Ydx4BIHIzH8vQVCEF2PqxT1kK9/azKRgDPaYdKh3c40ymc7cImHSn/4jyPMdR6MK5/rwYJ/HBGBE50Yi3Z9rJbFQcMKpdYcuBwpnkzF02X4Dcb9I4+UPE8k4MZFs/rYFlydeu3FavD9jkcgsz9dqJbF24ky2fIScOM6xj/7Xk/C7wYvBR4HSVABuKEPPC6HpQIpOIOHQr8EPK6cuS0WtHtHnURE4Mxx8OiE7vbH89UaIgI31CnaDWZ5nONQ/8+ZvkSh3DNH3da/s9r2GCLPriQiIHQ051FEfjbWVj4V9S+J5UfjdhDAt9r7poe0sPh5IgU3nhwyjpXTWiIIHNjlOdPSyoj2BRBZsdwoH2efxh1uP4jIwI1rR1xrC+i8PR+ZEsCBSYEYrJw44gSoSJlLr7ElcF7xLWr41ZmVI7yOdNwE143rbXsMX6d3wfmztMlSTlgHNS+b/pAtgIvXrSAS8KIqVm3eBnsON/c+D24QCIHnul7aEZBVGxYREYjgZeBERhLZtxpE4Bz8g431GvYWg/U67bhHAXTb241Mpnpuei/we4QDuxo7K/EktJnHjp/COJlq7mIiAyfS33yXuW/L85+xngjBifh9s5hYcDKVWV6pa8hqXKLq4bnktZxxRiERgojlTBC4jiMdz5ybIQNOtVZbC4XO3Q69JdG7aDRs2cnPmKyHokMPUQ9t8kIQMeAH34e0dTIVC9hLy15kLQT7FGwhd2pb9ct6sRWQWQMRZa2izllMprpt8q1kMtXS7V8KZEDBbkln1oooS2a6O5nngOMzv53pPJmKP+rxzp6ltiDixKj/6HoCEYETBzP4yVSrNizJiMDPYdDOnpOpeAl40S4XcrDyp5o/WaTgfgh0E6wn5aPpMriv+L+JEEQ8+dylrHlqXSSlfZrG1q4nMhCh/HsxJOJ0WnaatSYUn3MlYrPtrQid7ac8Q2QgouYXz4BSY1+/gRU0tT1GhODEyrvfMMKpH8LEtRR6d8Ob0WYwLHwxsB+RgRNb584m5fFj4/Ceh1MpCPj+3/6DBByZseV9IgOeTsWdVOwnodVbE/WZVoQmAl4OegsCt7dP7meWzUgC6V0yjshBxOXTH4GYooXQGsr3ln5EZODEyMnPmWFOZZaCs+egTsG2TL92oteT1xApNFYOFknQCt4UapVK6F7e3dZiICgFcHPdX0hZnfLoRrC2Ju4Zzbcg2HbUySwQVbZy+nkX1FmH8y0zLh1mX6Ys8yP420gs3gxpfYGXgf336sdmqZLhbwNRolGIHeM+NVtd4LU90wrhAoYsv+4lIgTEOhOz5I/Pq1Oy7WUj6u1VR+vU+Q82IRTaV4TifArrgKURjszl9+/oqYnA0qIY0c4+VXvgcb80F3hlgqWeX4FVzAOJfVCgLvAqEK4CRXCBl7WbwHPhM93tUiCi6AQD5xcZ98uXX7l/AxEDP2eiy7AbMwu8tFaMHiy8HGXB/53j1Gxt4RfOttyXtnQT9PKZ7c8v7gL6fAkneg19wtifb01s2IZTs3EA03kQ87Z//lbt5uVCDFZyLgmkPl0DV1ZfoU671mSB3Qytq3EQu+59eNdy1iYx28q/gPtG/pprPWizMAtfvIJ9QuBp5Gg5HZxqHVu1RjixCrsjye3b1f1EqzjxS35wq5TVQfJeXQxztAVd92hjETVPzSFLxa3g7SrVCdh39nOgWFeCZpaMJ37CBLHOnLzEo36HCKugFbPWk4VeyLKfDILP/oLLtDHQ5lgET4xVlIcGiLscffo/o/6dL8Pzbs/b1MObvCSGty+AZSOHQhLPeSEIp87+1H448h9HZqRg7350vKsjVFnPKyEoj6/RVc/3YHIwl4rrC75OHH4iFH3Yn5ThWb5rNZw5zFzoZeXWVx43ziuBoeCDjrD2Jtzx0QiBJPrA1TOfYM/APOzpxMCJY4RTtPG6uwc+DrwYTOLqNq5UMxmcKRTFXU9crY5f6PvzQW8KzSIJJJKugo9gLhy/7zj1HBKHxQ+Hy8ovg6Ww2ONEKYgWUjz/3+i3esK9xaeocrh/RGeY8Ukx+7T3Pg+Dfjm1YwfE5pWossBBysgnn4ESEZe3lsPVofg7HIjAvoEfQOz+WZBiLYnKB9+H5Oc7IdVgfQ4i4WnnwUw1RKFmwELYdcII9SgGDlKW/W0KwDYaRicaVpfDR5eOgiXHDGTCGAzTT3oSYqXlLJyZYInQQ5fSRDGv5DNVCroc3v33fKh3K89Rv2U9PPSj/4ChTBa4TqPw2F9B2bIlwk9uHtwnkq6Dvzz7Fzj4b9pg5mG3Hg49X/iber25Lz0fgw52G5bsXgSnDTpNPa/EScNOhHMHnwNbo7gClu7Pg3Wugn143TbxCTiLtRqw64GrQ1/7YobWgiDBpMSUKExcNwt6vPOI2nL43Yw+0HfpS+qJaPh9reBtY9cBL5d8/QX87MLT1BWfHTofCz/qehJsLcdvDct0LQTlrdQnKmD0pCfg+l5nwXX3dYYbep0DX25YaJznUgt2SCShospAD5AoSGKczkGpf8Jni7Ucfxv8eET2+DgahJ+0GTHy4XPD1oS3XG/eTna3x6N+8jicB8LYR/D3hOXs0n4CyqO+HknnE8RkgxpCwfVW9IFQ9TLX6uFD2FzoknDC6+861seNATbKk3AnBNc1jmaTBD0vY52PFkQG4X5+BOG0j9P1LYcZskhm/KFpAfdHju9DEEA73oFtKtbANwU+fO7oYWzwHeaWgA9zc9FskkCwNZCIsyfUwIjF1G+lMv4uFAEFTy6qla9Xt/oncr7RzgZOr7dCQhZWBCELK3zQwgof5OakGSShfWqjEDa+sRH6fa8f68MOY33ZoTD0+KGwey5+dydfxg5+nyNulSqA8acsgVGHfArj262BYd9bDG//cSUkYwlSxon7/3kvtGvXzuCIHx8BO3brcyO8OVC5F4YMHQL9+xcy+qvMm/+hp+SsIVu4aAG8/fZUxtsqcz6YBVU13BEFF5LsE0xRFDB/FEil4mS/nCMIWVjhQxZW+AC3BDmXBDZx09EkDDx4EPlaOvWr6XB70ghIeXzBzFuXrYLxBathQru1TBBrbdtnDloB22fbD3/y7N23yyYHniOP/HHm8TqH/b333jXEIKI2Yv8WMD5k323/xhADz9SpU6Fk6eLMvs5nnVaUlEUO9Mc6lTpnCEIWRviAhRU+tC1NziWh1KRh8MHa91fqX0lnZWS7EWw7HAb8cICw64DfjVny2HYmhK9VIYhZo7Ys4ACGRCuHYyDGoCTr5vBSEHHqb05VQ8E/BmTUqJFECiK0UAmCxp4bLwYR6zZ8TctiJWdbBaytB+cf0RyLRiMIW9jgQxZW+LDmi5xLYvy541hrAUVABcET34lfd28fVEyUpWB0h5UCMVCKf/ExJBv0Fol5O3+49ioiBBEFBQUQjdOjE7F4HZGBE++9P40GLYWCmEKEIGaqKje+PFYSvz9pJUnKZ40gbGGDD1lY4UOab3IqCaU+DSMKqAx0sKsx0vL7gMOLIBnXTiKrHfKshWd/+SmRgRsbJu22PYZ9B/YQGbjRpUtn+/NgLYAJE8YRGYgpUreRqP2U9CgeKgNnZs+eSULr1c3gf/jyvhAELWzwAQsrfDCDRE4lUb2iioiBUmxeZkJJbkrY5iqM6fAlPCuQgRPPdMRzGprlL7vsEiICL2zPg0mCysCZoqIimDHzPSN4OPfg67WlRARe8AHO9gcrmq9uhyBoYYUPWljhQxk0ciIJPeT9OvUTSMGdd29927gdpVZRg69JYg0RgojRB1mWmjOwC8FLwItVq8zbwMFGXgReoCisQZw2bRqRgBfW8vhNTNn+YMuDCKEVyoEPWJjhwxhUciIJBPvVA384gEjAi+Izio3bSO1OEwl4Ma6g1PY4eAH4oaio0Cg/a/Z0IgE/GAFnLQleAH6wBjqZ9j8eYf4oVAxSDoGED2HQyYkk9CnUw13GI0SMLCiGx3/8mHE7ic0pIgE/WB8LLwA/XHNND6P8+PFjiQD8YA0mLwA/qGHIlE+l47wBfP1IOQQXPnhhIieS0BlymHboMxsGHj/AKJ/clr0kcC6F9THwAvBDr153GeF6481/EQH4IZeSwDcm+59MS0IQtDDChyys8IELIzmVRNExRRYBeB8GxXkUL185ySifLtfGJPyCYxdj2+NXt5utGV4AfnjnPbO5/8XKT9XQ4zgDLwJHWHfFLglzdqVfrOUTancjzVvA9QdnZPJBCxt8wMIMH7Qwk1NJLBuzlIjAix1z7Cd+Gdu+lMjAjeGH249udOp0HJGAF2ol1UPKLhMJePDSxBcsAY/CkpIlRAJeWCWBjyHbn1QqQUIXJviQhRU+YK2BnEpCqVHU4I8s0FoRohmXiDo1G7cFw0GJpGy3UXzoJ2r49SnYXsy6caOt/DvvTiES8MIW0BQeAjXXafhhy9aNtvIHKvYSCTihHQmZSh5Dtj986MICH7KwwgerNZFTSeAcg6If9CdScGJZ8VK1nLqsXJ2iXQvfvl/Bwu82Jdtk1GHLIBUxvx5Pow4OPewwIgIxBbCvHL/k1h7Qsv17iAicGDh4ACmP8DKgmIdJyw7Qx5BWshu85MMXZPiAhRU+TK2V3EqCseODbWoLwTqzUkObRKVfjytD01G6mhNXeA740WwiBBFfj65W13rwJ37Z+t0mKCBCsKP/HffnA4oUFlEhUIogEsPZlvQ2vl77FRPAOxkR6FvK9OnvkrI6fn+wwvJBDCJ8yMIKH6LWTs4lgexesEMTQoFldqXBCBh08CCo/bqalNMXaMUbYjDqe1q3w47Zwnip2zJSXgcDdsedPYkYePhQ8gwcOEAgBp1C+Gj+XFLGypw5s4gUrEx7h860tIInOcGjFm4/eD5DPoxBgw9ZWOHD01ZoFkkgqV0peOqIJ4gkBh47ANIxbb2GmFr1SEWyIQGfFG0DfublmA4rILE5Tc7nYJ5mzfxUr62vhHYFVA6XXPo7tQwfShEvTXqRk8MAKGSC2FOG5yWk+/PURqqIHJB/f/gB2VdFEDKxKNKZvzeQ/YMCH7KwwoemrdFsklBhQS5ftB8+ePAD+PCxuQAVivDclTwYFv0yVACsHr8P3uu5Aspmx0GJmN+Zad3fjXenvw09b78Nhg0bDFU15eTvXtREKmHxkoUwc+Z0WL9xDfm7Jywwu3bvgOXLl8Kar0tBuLQ8s58TCSaDdDqhrvhMBrz1wIcsrPBhaas0rySaERKwMCIIWFjhAxZW+IBIQigJErQwIwhb2OBDFmb4cEg0QiMJErCwIghaGOEDFlb4QEgogZcECVmYEYQtbPAhCyt8ECTOBFYSJGBhRRC0MMKHLKzwAZB4EyhJkICFFUHIwggfsLDCV3pJdgRCEiRkYUUQtDDChyzM8BVekj15lQQJWVgRBC2M8AELK3wllzSNvEiChCzMCMIWNviQhRW+cktyQ4tKggQsrAiCFkb4kIUVvlJLckuLSIKELKwIghZG+JCFFb4yS5qHZpMECViYEQQtjPAhCyt8JZY0LzmXBAlYWBGELIzwAQsrfMWVtBw5kwQJWVgRBC2M8CELK3yFlbQ8TZYECVlYEQQtjPAhCyt8RZXkj0ZLgoQsrAiCFkb4kIUVvoJK8k08O0mQgIUZQdDCCB+ysEIrpyS/xBkJFV+SIAELCxgk/vdWAB+wsEIrpqRlQRHwv2tisOIqCRK6sCIIWhjhQxZmaIWV5BcqB0dJkICFGUHQwggfsLBCK6akZfHXcuCxSYKELMwIwhY2+JCFFVpZJfmHysCJdiRcYUUQsjDCByzM0IopyS/+Wg46+P2ySOuQhCBsYYQPWVihlVOSX6gA3NDl0IySoN2WnHdlBAELK3zAwgqtmJL84t1qQAHwv4toBklYSDZAVVkSNq2MwleLIgaljdy6we9r3brB7yvausHvm+3WDX5f69YNfl/R1g1+32y3bvD7Wrdu8PuKtm7w+2a7bSz87WS7dWPzFzGo2pOEZDKZkQLKgcrAC14KPM0jiWQMvlkdhdULkrD6Y5BIJM3JghRsWRVlgU9Zwu+vJeGHnEuial9afdD44EsXCJ6QRCJpFkoXpKFiV9pVErwA/NBkSZhf1MsuJ5gcFijsASPWJ8D/LpFImgcFWC8/J3LImSQMklEoXSi7FxJJPimdzz6QWYsimdJaFHzgG0POJFFfp3UxJBJJ/qmrSpOwN5bcSEJtRdSTByqRSPLDVwvjLOC5EUVOJJGIYxNHtiQkksCwQIFEFEjgG0NuJNEgGqyUSCT5Q4FojUIC3xhyKAn+QUokknxSn6NxiZxIIiklIZEEjkBJQrYkJJLgISUhkUhcCY4kcCWjlIREEjjyLwnrcmcpCYkkcOREEkqyEZIQnRNBSiIk4HyWJFmdu3NtGnZtSMHaJQltH1IuU5ZcJwkyTZIEk4OOf0kI5CAlER42fh4DBQAUBf/HCwBbVsbUv6Xi2lXrP48Y+0NK28cJnNGn7Svf+6CStSRwrYdFDv4kIRCCCCmJYFO6IAGQ1kTQUKNApCIjirT291SD9qtNEri/QA7qfwrepi4JSVDJShICObhLQiACN6Qkgk3pwphmAQz3QjwZUKbpANrfdUlsLq2CtZ8kYc0CJozlMVj3aRTWI8uj6mVEE4WURBjwlIRDy4GHSkIgAS+kJIIOaxYkM1YwWgRAWhL4U1+pXae3PIx9uR8pieDjKgmBDJwwJSEIv1+kJMLBpi/rQR+SWLM0s2p3vmJIouZAHPZ/k4I188HoWmxYWQMbV9QTSuWCvsBDJOGz5cDTjg98Y5CSCCJp43IaJaCPMXA/sVqHgUtt6IGOSWTYvSkquE9JkEBJqCeeEQQ/G6Qk2gDRqpRmAf0Hg47SYMRrHAYurUWsXZTM77s3a0dGJMElWp0mgW8MUhJtBdY9KN+pwIFd+F7paH8TtSQQfVxi9eKoelo0/bDomsWyFREGpCQk2bFAH4nULlsl8dXCBJQubADsony1KGq0MowfveXB/54U3I8kMEhJSLLEPFyRxmkTApK1eIi0now/OJLi70MSJKQkJFlibQrwP9qAQyrKl+HR3mc8+mHdSoKJlIQke9Q1G/jdKLh+Q7DFv/FlJKFFSkKSJeYhUUnbQEpCIpG4IiUhyTHyPWxtBEoSyZisYBJJ0AiUJGRLQiIJHk2RRDptIiUhkbRSorWNk4RVELmThPyaP4kkWOA3izcAEYAbvBxyKok4ezSli+zz/iUSSf4oxS8MVvy1JHgp8DRZEolUTKX6AJ5ElT5YiUTS8uzbESMyyEYMOZGELgeTBnIWZolE0rLgat3ShQlIOrQieAH4IWtJUDmYROv0Bytn90kk+aKuUsmJHLKWBC8EJ+qrwWxRLKRPQCKRNBMLElBXDsDaEWq4cyEIxFUSvAD8k4Dtm2LyZKkSSUuwIAnb1jVAKq21IPiQNxWhJGjoG0scGmoAviltgNLFNSpfNWHrhnXfVdzWDX5f0RZv12lrvd/GbPnbs275x2HduiG6H37rBr9vtlvRc/Gz5W9Hfz5Bgn/MXlss05StG1tWJaChGg9zplnbITetBhE2SdCQh5NkukGSV+KC35GEL8jp34NCmg4E5hs+0M2BKgk+ZGGFVlZJ/qEScIMEMwCoj0sQ0HzDh7m5aMcHLYzQiinJL/5bDUEVQxBbDQgf4JYg1JKglVOSX6gA3CDBDAqCcAYBPrwtRegkQSumJL94txowePzvgQMflyCY+YYPbD4IjSRo5ZTkFyoDL0gwg4AgmEGAD2o+CbwkaOWU5BfvlgMPCWYewUqvXsatIJz5hA9nUAisJGjllOQXGn43+HAGAfVxCcKZb/hQBo1ASYJWTEl+yW5+g5RDdvBhDCqBkQStoJL8QcPvBR/MwCAIZ77hQxh08ioJWjkl+aV1tBxU0jScQYAPYBhoUUlgRdS3kqCQnRSCLAf1cQmCmW/40IWNFpeEJGhQAbjBBzMQCIIZBPiwhZUWkQStmJL8QsPvBQlmAFAflyCc+YYPWdhpNknQiinJPzT8bvChDAyCYAYBPlythWaRBK2ckvxBw+8FCWVQEAQzCPCham3kVBK0gkryBw2/H0gwg4AgmPmGD1JrJieSoBVUkj9o8L0goQwKgnDmGz5AbYFGS4JWTkl+oeH3goQyCKRpMIMAH5y2Qyp7SdDKKckv2c1zIKEMCoJg5hsamLaDoigGviVBK6ckv1ABuEFCGRQE4QwCfGjaCoqSsgnClyRo5ZTkj+xaDYGVAz4uQTCDAB+atgGKIU3k4CoJWjklLQ+GXL/cSuSACIIZBGhw2ga8EETYJEErqiS/0PD7gQQz3+BjEgQz3/CBaTvQLoUbqiRo5ZS0PBhw/nf/kGAGBUE48wkNTFvCuUvhRjtaWSX5I5zdCv5xYIXkwxkEaGjaCtm1HLTxCSyjDWRKSeQdGnw3+IAGBfWxCYKZb2hg2g40/F6gGChSEnkjnK0GIYJwBgJBcNoCosOY7ugtBzFSEi0KDb4fSCgDAFZGEsoAwAemLUHD7wUVgggpiRajlbQc8HEJwhkE+NC0DbJtNSDuLQceKYlmh4bfDRLKoCAIZb6hgWlL+DlSYd2Hht8vUhLNRitpOQjCGQRoaNoKGFxeBm5k12oQISWRc2j43SChDADq4xIEM9/QwLQdaPi9oGFvLFISOaGVtBoQQTjzjTUs/O+tHRp+L5recuCRkmgSNPxekFAGBUE48w0fmLYEDb8faMBzgZREo6Dh94KEMigIwplv+MC0JWjwvaChzjVSEllDBeAECWRQSNNg5hs+LG0Jt2XaztAwNxdSEr6gAvCCBDMICMKZb/jAtCVo8N3QRUJD3NxISbhCw+8ECWSQEIQz3/CBaVtg+HgJeEHD21JISQihEnCDhDIoCMIZBGho2gZa6Pjwe0FD29JkJIGVXd/qh/P0b5i2gvs0ZcvffrZb/vb8bt2wPrbsIcHMM3qF5IMZBPjQtBWyH3OgQc0n7c7sehZIJM3FWWdJwo6UhKRZ4CuaJLxISUhyCl/BJOFHSkKSM/jKJWkdSElImgRfoSStDykJSaPgK5Kk9SIlIfEFX3EkbQcpCYknfKWRtC2kJCRC+IoiabtISUgIfCWRtG2kJCQqfMWQSHRarSQ6n9mFXNflrDNV3PZpa+gVoXPnzoQuXbqo8JVGYgdfI3y9zjzzTPK31kCrlMQZXTrDm1PeUrfW6/9x9102SYybMB46c/u0BawVACv42WefDYsXL4aSkhLC5MmT1QDwFUeigWL485//rL5WrfV1arWSWLK0xJAEiuGKHlfCvya/ZrQe8LrFJUvUNxl/7yy4ndYG/+bjc3/99dfVCt6tWzfSkkCGDx+u/p0vK9Fev4cffrhVCwJpE5JARJLAfXRJdBHcTmuBf9N1sGJjBb/wwgsdm8rY0liwYAHMnz9fdj0s4Gtx3XXXwdKlS7U65PD6tQakJDKSaI3wb7YVfN533nknvPrqq54VXJdJa/60zAb99ViyZEmbeE2kJFqhJPg3WQQ+71deeQWeeOIJKQkfdO3aVd3iazBx4sQ2IwhESqIVSYJ/c93A5/3mm2/C/fffT/7GIyWhob8O06ZNa1OvhZREyCXBv6F+0SXRu3dv8jceKQkNfM1uvPFG9bW4/PLL28wYjZRESCXBv5HZgs973LhxUFhYKLsbWYCvQffu3dXX49577/V87VoDUhIhlAT/JjaW8847Dz7++GPP8J9//vlSEhy6OF9++eVW36KQkgiRJPg3r6noFf2GG25w/ETEfXCQ7r333iN/a+vorx+O67RmgbZqSZze+QzjOidJWGdgBhH+Dcs1l1xyiVrRsUWBE6ceffRReOyxx9QtHh7Fv02ZMqVVh6Ap6BJtzS2tVikJFEH/AUWqLM7q1lW9Di+fc965hhRwe/Mtf7W1NoIE/0Y1F9iCwMo9ffp0VRR6hV+0aBHMmzcP/vrXv7bayp8r8PXBCWet9XVqlZIIM/wb1JKoXS8L/N8lzrTm10tKIgDwb4pEEiSkJPIM/4ZIJEFDSiJP8G+ERBJUpCRaGP4NkEiCjpREC8C/6BJJmJCSaCb4F1oiCStSEs0A/yJLJGFGSiJH8C+sRNJakJLIAfyLKpG0JqQkGgn/QkokrZX/B/houop9qsEsAAAAAElFTkSuQmCC>

[image8]: <data:image/png;base64,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>

[image9]: <data:image/png;base64,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>