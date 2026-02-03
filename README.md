# 마이크로서비스 Pod 구조 설계

## 현재 상황
- 사용자 pod만 구현됨
- 추론pod, 사용자pod, 메시지pod로 확장 예정

## 제안하는 폴더 구조

```
project/
├── common/                     # 공통 모듈
│   ├── __init__.py
│   ├── config/
│   │   ├── __init__.py
│   │   ├── base_config.py      # 기본 설정
│   │   └── database_config.py  # DB 설정
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base_model.py       # 공통 모델 베이스
│   │   └── shared_models.py    # 공유 모델들
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── base_schema.py      # 공통 스키마
│   │   └── shared_schemas.py   # 공유 스키마들
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── logger.py           # 로깅 유틸
│   │   ├── auth_utils.py       # 인증 유틸
│   │   └── validation.py       # 검증 유틸
│   └── middleware/
│       ├── __init__.py
│       ├── cors.py
│       └── error_handler.py
│
├── user_pod/                   # 사용자 관리 Pod
│   ├── __init__.py
│   ├── main.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── health.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── api.py
│   │       └── endpoints/
│   │           ├── __init__.py
│   │           ├── auth.py
│   │           ├── users.py
│   │           └── social.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── database.py
│   │   └── security.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── user.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── response.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── user_service.py
│   │   ├── friend_service.py
│   │   └── social_auth_service.py
│   └── tests/
│       ├── __init__.py
│       └── test_user_api.py
│
├── inference_pod/              # 추론 Pod
│   ├── __init__.py
│   ├── main.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── health.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── api.py
│   │       └── endpoints/
│   │           ├── __init__.py
│   │           ├── inference.py
│   │           └── models.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── ml_engine.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── inference_request.py
│   │   └── inference_result.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── inference.py
│   │   └── model_schema.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── inference_service.py
│   │   └── model_service.py
│   └── tests/
│       ├── __init__.py
│       └── test_inference_api.py
│
├── message_pod/                # 메시지 Pod
│   ├── __init__.py
│   ├── main.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── health.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── api.py
│   │       └── endpoints/
│   │           ├── __init__.py
│   │           ├── messages.py
│   │           ├── chat.py
│   │           └── notifications.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── websocket.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── message.py
│   │   └── chat_room.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── message.py
│   │   └── chat.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── message_service.py
│   │   ├── chat_service.py
│   │   └── notification_service.py
│   └── tests/
│       ├── __init__.py
│       └── test_message_api.py
│
├── docker/                     # Docker 설정
│   ├── user_pod/
│   │   └── Dockerfile
│   ├── inference_pod/
│   │   └── Dockerfile
│   ├── message_pod/
│   │   └── Dockerfile
│   └── docker-compose.yml
│
├── scripts/                    # 배포/관리 스크립트
│   ├── deploy.sh
│   ├── migrate.sh
│   └── test_all.sh
│
├── docs/                       # 문서
│   ├── api/
│   ├── architecture.md
│   └── deployment.md
│
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## 각 Pod의 역할

### User Pod (사용자 관리)
- 사용자 인증/인가
- 프로필 관리
- 친구 관계 관리
- 소셜 로그인

### Inference Pod (추론 서비스)
- AI/ML 모델 추론
- 모델 관리
- 추론 결과 캐싱
- 모델 버전 관리

### Message Pod (메시지 서비스)
- 실시간 메시징
- 채팅방 관리
- 알림 서비스
- 메시지 히스토리

### Common (공통 모듈)
- 공통 설정 및 유틸리티
- 공유 모델 및 스키마
- 미들웨어
- 로깅 및 모니터링