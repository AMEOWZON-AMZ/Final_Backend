"""
빠른 등록 API (QR 코드용)
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.schemas.quick_register import QuickRegisterResponse
from app.services.quick_register_service import quick_register_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/register", response_model=QuickRegisterResponse)
async def quick_register(
    nickname: str = Form(...),
    target_user_id: Optional[str] = Form(None),  # 시연용으로 선택 사항으로 변경
    phone_number: Optional[str] = Form(None),
    cat_pattern: Optional[str] = Form("solid"),
    cat_color: Optional[str] = Form("#FF6B6B"),
    meow_audio: Optional[UploadFile] = File(None),
    train_voice: Optional[list[UploadFile]] = File(None),  # 3개의 암구호 녹음 파일
    db: Session = Depends(get_db)
):
    """
    빠른 등록 (QR 코드용) - Form 데이터
    
    사용자 생성 + 친구 등록 + 음성 파일 업로드를 한 번에 처리합니다.
    
    **시연용 설정:**
    - target_user_id를 전달하지 않으면 자동으로 고정 사용자와 친구 등록됩니다.
    - 고정 사용자 ID: 44082dbc-b071-70c4-4794-81b840c61c4e
    
    **사용 시나리오:**
    1. 사용자 A가 QR 코드 생성 (자신의 user_id 포함)
    2. 사용자 B가 QR 코드 스캔 → 웹 페이지 이동
    3. 웹 페이지에서 닉네임 + 음성 파일 입력
    4. 이 API 호출 → 사용자 B 생성 + A와 친구 등록 + 음성 파일 업로드
    
    **Parameters (Form):**
    - nickname: 새 사용자 닉네임 (필수)
    - target_user_id: 친구로 등록할 대상 사용자 ID (선택, 미입력시 시연용 고정값 사용)
    - phone_number: 전화번호 (선택, 010-1234-5678 형식)
    - cat_pattern: 고양이 무늬 (선택, 기본값: solid)
    - cat_color: 고양이 색상 (선택, 기본값: #FF6B6B)
    - meow_audio: 야옹 소리 음성 파일 (선택, File)
    - train_voice: 암구호 학습용 음성 파일 3개 (선택, File array)
    
    **Returns:**
    - user_id: 생성된 사용자 ID
    - nickname: 닉네임
    - friend_code: 친구 코드
    - friend_added: 친구 등록 성공 여부
    - target_nickname: 대상 사용자 닉네임
    - meow_audio_url: 야옹 소리 URL (업로드한 경우)
    - train_voice_urls: 암구호 학습용 음성 URL 배열 (업로드한 경우)
    
    **Example (JavaScript Fetch):**
    ```javascript
    const formData = new FormData();
    formData.append('nickname', '새친구');
    // target_user_id 생략 가능 (시연용 고정값 사용)
    formData.append('phone_number', '010-1234-5678');
    formData.append('cat_pattern', 'stripe');
    formData.append('cat_color', '#FFD700');
    formData.append('meow_audio', meowAudioFile);  // File object
    formData.append('train_voice', trainVoiceFile1);  // File object
    formData.append('train_voice', trainVoiceFile2);  // File object
    formData.append('train_voice', trainVoiceFile3);  // File object
    
    const response = await fetch('/api/v1/quick/register', {
      method: 'POST',
      body: formData
    });
    ```
    """
    try:
        # 시연용: target_user_id가 없으면 고정값 사용
        DEMO_TARGET_USER_ID = "44082dbc-b071-70c4-4794-81b840c61c4e"
        actual_target_user_id = target_user_id or DEMO_TARGET_USER_ID
        
        logger.info(f"📱 Quick register request: {nickname} → {actual_target_user_id}")
        if not target_user_id:
            logger.info(f"🎯 Using demo target user ID: {DEMO_TARGET_USER_ID}")
        
        # 사용자 생성 및 친구 등록
        result = await quick_register_service.create_user_and_add_friend(
            db=db,
            nickname=nickname,
            target_user_id=actual_target_user_id,
            phone_number=phone_number,
            cat_pattern=cat_pattern or "solid",
            cat_color=cat_color or "#FF6B6B",
            meow_audio=meow_audio,
            train_voice=train_voice
        )
        
        # 성공 메시지 생성
        if result['friend_added']:
            message = f"환영합니다! {result['target_nickname']}님과 친구가 되었습니다."
        else:
            message = f"계정이 생성되었습니다. (친구 등록 실패: 나중에 다시 시도해주세요)"
        
        return QuickRegisterResponse(
            success=True,
            message=message,
            user_id=result['user_id'],
            nickname=result['nickname'],
            friend_code=result['friend_code'],
            friend_added=result['friend_added'],
            target_nickname=result['target_nickname'],
            meow_audio_url=result.get('meow_audio_url'),
            train_voice_urls=result.get('train_voice_urls', [])
        )
        
    except ValueError as e:
        logger.error(f"❌ Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"❌ Quick register failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to register user")


@router.get("/qr/{user_id}")
async def get_qr_info(
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    QR 코드 정보 조회
    
    QR 코드 스캔 후 웹 페이지에서 대상 사용자 정보를 표시하기 위한 API
    
    **Parameters:**
    - user_id: 대상 사용자 ID (QR 코드에 포함된 값)
    
    **Returns:**
    - user_id: 사용자 ID
    - nickname: 닉네임
    - cat_pattern: 고양이 무늬
    - cat_color: 고양이 색상
    
    **Example Response:**
    ```json
    {
      "user_id": "abc123-...",
      "nickname": "냥냥이",
      "cat_pattern": "stripe",
      "cat_color": "#FFD700"
    }
    ```
    """
    try:
        from app.models.user import User
        
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {
            "user_id": user.user_id,
            "nickname": user.nickname,
            "cat_pattern": user.cat_pattern,
            "cat_color": user.cat_color
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get QR info: {e}")
        raise HTTPException(status_code=500, detail="Failed to get user info")
