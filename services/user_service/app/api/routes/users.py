from fastapi import APIRouter, Depends, HTTPException, status, Request, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional
import json
from loguru import logger
from pydantic import EmailStr

from app.core.database import get_db
from app.schemas.user import (
    UserCreate, UserResponse, UserUpdate, UserProfile, TokenInfo, 
    LoginResponse, ProfileSetupData, UserSignup, LoginRequest
)
from app.schemas.response import success_response, error_response
from app.services.user_service import UserService
from app.services.s3_service import s3_service
from app.models.user import User

router = APIRouter()


@router.post("/login", response_model=dict)
async def login_and_get_lobby(
    request: Request,
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    로그인 시 프로필 동기화 + 온라인 상태 설정 + 로비 친구 정보 반환

    Request Body:
    - user_id: 사용자 ID (필수)
    - token: FCM 토큰 (Firebase Cloud Messaging) - 푸시 알림용 (선택)

    FCM 토큰 사용 시나리오:
    1. 클라이언트에서 FirebaseMessagingService.onNewToken() 호출
    2. 받은 토큰을 로그인 API에 함께 전송
    3. 서버에서 자동으로 토큰 저장/업데이트
    4. 이후 푸시 알림 전송 가능
    """
    # 요청 로깅
    logger.info(f"🔥 LOGIN REQUEST: {request.method} {request.url}")
    logger.info(f"👤 User ID: {login_data.user_id}")

    # FCM 토큰 로깅
    if login_data.token:
        logger.info(f"📱 FCM Token received (first 20 chars): {login_data.token[:20]}...")

    try:
        user_service = UserService(db)

        # 1. 사용자 조회
        user = await user_service.get_user_by_id(login_data.user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error_response(message="User not found", error_code="USER_NOT_FOUND")
            )

        # 2. FCM 토큰 업데이트 (제공된 경우)
        if login_data.token:
            user = await user_service.update_fcm_token(user.user_id, login_data.token)
            logger.info(f"✅ FCM Token updated for user: {user.user_id}")

        # 3. 본인 daily_status 조회 (DynamoDB)
        from app.services.dynamodb_service import dynamodb_service
        my_daily_status = await dynamodb_service.get_my_daily_status(user.user_id)
        logger.info(f"📊 본인 daily_status: {my_daily_status}")

        # 4. 로비용 친구 목록 조회
        lobby_friends = await user_service.get_lobby_friends(user.user_id)

        # 5. 사용자 프로필 정보 (본인 daily_status 포함)
        # S3 URL을 presigned URL로 변환
        from app.services.s3_service import s3_service
        import json
        
        profile_image_url = user.profile_image_url
        if profile_image_url:
            try:
                profile_image_url = s3_service.generate_presigned_url(profile_image_url, expiration=3600)
            except Exception as e:
                logger.warning(f"Failed to generate presigned URL for profile image: {e}")
        
        meow_audio_url = user.meow_audio_url
        if meow_audio_url:
            try:
                meow_audio_url = s3_service.generate_presigned_url(meow_audio_url, expiration=3600)
            except Exception as e:
                logger.warning(f"Failed to generate presigned URL for meow audio: {e}")
        
        # train_voice_urls 파싱 및 presigned URL 변환
        train_voice_urls = []
        if user.train_voice_urls:
            try:
                # JSON 문자열을 리스트로 변환
                urls = json.loads(user.train_voice_urls) if isinstance(user.train_voice_urls, str) else user.train_voice_urls
                # 각 URL을 presigned URL로 변환
                for url in urls:
                    try:
                        presigned_url = s3_service.generate_presigned_url(url, expiration=3600)
                        train_voice_urls.append(presigned_url)
                    except Exception as e:
                        logger.warning(f"Failed to generate presigned URL for train voice: {e}")
                        train_voice_urls.append(url)  # fallback to original URL
            except Exception as e:
                logger.warning(f"Failed to parse train_voice_urls: {e}")
        
        user_profile = UserProfile(
            user_id=user.user_id,
            email=user.email,
            nickname=user.nickname,
            phone_number=user.phone_number,
            provider=user.provider,
            profile_image_url=profile_image_url,
            friend_code=user.friend_code,
            cat_pattern=user.cat_pattern,
            cat_color=user.cat_color,
            meow_audio_url=meow_audio_url,
            train_voice_urls=train_voice_urls,
            token=user.token,  # FCM 토큰 추가
            daily_status=my_daily_status or "",  # 본인 daily_status 추가
            created_at_timestamp=user.created_at_timestamp,
            updated_at_timestamp=user.updated_at_timestamp
        )

        # 6. 통합 응답
        login_response = LoginResponse(
            user=user_profile,
            friends=lobby_friends,
            total_friends=len(lobby_friends)
        )

        response_data = success_response(
            data=login_response,
            message="Login successful and lobby data retrieved"
        )

        # 응답 로깅
        logger.info(f"✅ LOGIN SUCCESS: user_id={user.user_id}, friends_count={len(lobby_friends)}")
        logger.info(f"📤 Response: {json.dumps(response_data, indent=2, default=str)}")

        return response_data

    except HTTPException:
        raise
    except Exception as e:
        error_detail = error_response(message=str(e), error_code="LOGIN_ERROR")
        logger.error(f"❌ LOGIN ERROR: {str(e)}")
        logger.error(f"📤 Error Response: {json.dumps(error_detail, indent=2)}")

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_detail
        )



@router.post("/signup", response_model=dict, status_code=status.HTTP_201_CREATED)
async def signup(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    회원가입 (JSON 또는 Multipart 자동 감지)
    
    Content-Type에 따라 자동으로 처리 방식 결정:
    - application/json: URL만 받음
    - multipart/form-data: 파일 직접 업로드
    """
    content_type = request.headers.get("content-type", "")
    logger.info(f"🔥 SIGNUP REQUEST: {request.method} {request.url}")
    logger.info(f"� Content-Type: {content_type}")
    
    try:
        user_service = UserService(db)
        
        if content_type.startswith("multipart/form-data"):
            # Multipart 처리
            logger.info("📦 Processing as MULTIPART")
            form = await request.form()
            
            user_id = form.get("user_id")
            email = form.get("email")
            nickname = form.get("nickname")
            phone_number = form.get("phone_number")  # 전화번호 추가
            cat_pattern = form.get("cat_pattern")
            cat_color = form.get("cat_color")
            token = form.get("token")
            
            profile_image = form.get("profile_image")
            meow_audio = form.get("meow_audio")
            train_voice = form.getlist("train_voice")  # 배열로 받기
            
            logger.info(f"📝 User: {user_id}, {email}, {nickname}, {phone_number}")
            logger.info(f"🎨 Cat: {cat_pattern}, {cat_color}")
            
            # 파일 업로드 처리
            profile_image_url = None
            meow_audio_url = None
            train_voice_urls = []
            
            if profile_image and hasattr(profile_image, 'filename'):
                logger.info(f"📤 Uploading profile image: {profile_image.filename}")
                profile_image_url = await s3_service.upload_profile_image(profile_image, user_id)
                logger.info(f"✅ Uploaded: {profile_image_url}")
            
            if meow_audio and hasattr(meow_audio, 'filename'):
                logger.info(f"📤 Uploading meow audio: {meow_audio.filename}")
                meow_audio_url = await s3_service.upload_meow_audio(meow_audio, user_id)
                logger.info(f"✅ Uploaded: {meow_audio_url}")
            
            if train_voice:
                # 3개의 암구호 파일 업로드 + 병합
                train_voice_files_data = []  # 병합을 위해 파일 데이터 저장
                
                for idx, voice_file in enumerate(train_voice[:3], 1):  # 최대 3개만
                    if hasattr(voice_file, 'filename'):
                        try:
                            logger.info(f"📤 Uploading train voice {idx}: {voice_file.filename}")
                            
                            # 개별 파일 업로드
                            voice_url = await s3_service.upload_train_voice(voice_file, user_id, idx)
                            train_voice_urls.append(voice_url)
                            logger.info(f"✅ Uploaded: {voice_url}")
                            
                            # 병합을 위해 파일 데이터 저장
                            await voice_file.seek(0)  # 파일 포인터 리셋
                            file_data = await voice_file.read()
                            train_voice_files_data.append(file_data)
                            
                        except Exception as e:
                            logger.error(f"❌ Failed to upload train voice {idx}: {e}")
                
                # 3개 파일을 합쳐서 추가 업로드
                if len(train_voice_files_data) == 3:
                    try:
                        from pydub import AudioSegment
                        import io
                        
                        logger.info("🔗 Merging 3 train voice files...")
                        
                        # 각 파일을 AudioSegment로 변환
                        audio_segments = []
                        for idx, file_data in enumerate(train_voice_files_data, 1):
                            try:
                                audio = AudioSegment.from_file(io.BytesIO(file_data))
                                audio_segments.append(audio)
                                logger.info(f"  - File {idx} loaded: {len(audio)}ms")
                            except Exception as e:
                                logger.error(f"❌ Failed to load audio file {idx}: {e}")
                                raise
                        
                        # 3개 파일 합치기 (순차적으로 이어붙이기)
                        merged_audio = audio_segments[0] + audio_segments[1] + audio_segments[2]
                        logger.info(f"✅ Merged audio length: {len(merged_audio)}ms")
                        
                        # WAV 형식으로 변환
                        merged_buffer = io.BytesIO()
                        merged_audio.export(merged_buffer, format="wav")
                        merged_bytes = merged_buffer.getvalue()
                        
                        # S3에 업로드
                        merged_url = await s3_service.upload_merged_train_voice(merged_bytes, user_id)
                        train_voice_urls.append(merged_url)  # 4번째 URL로 추가
                        logger.info(f"✅ Merged train voice uploaded: {merged_url}")
                        
                    except Exception as e:
                        logger.error(f"❌ Failed to merge and upload train voices: {e}")
                        # 병합 실패해도 개별 파일은 이미 업로드됨
            
            # UserSignup 스키마 생성 (빈 문자열은 None으로 변환)
            signup_data = UserSignup(
                user_id=user_id,
                email=email,
                nickname=nickname,
                phone_number=phone_number if phone_number and phone_number != "" else None,
                cat_pattern=cat_pattern,
                cat_color=cat_color,
                profile_image_url=profile_image_url,
                meow_audio_url=meow_audio_url,
                train_voice_urls=train_voice_urls,
                token=token if token and token != "" else None
            )
            
        else:
            # JSON 처리
            logger.info("📄 Processing as JSON")
            body = await request.json()
            signup_data = UserSignup(**body)
            logger.info(f"📝 Request Body: {signup_data.model_dump()}")
        
        # 사용자 생성
        user = await user_service.create_user_from_signup(signup_data)
        
        response_data = success_response(
            data=UserResponse.model_validate(user),
            message="회원가입이 완료되었습니다"
        )
        
        logger.info(f"✅ SIGNUP SUCCESS: user_id={user.user_id}, email={user.email}")
        logger.info(f"📤 Response: 사용자 생성 완료 - 친구코드: {user.friend_code}")
        
        return response_data
        
    except ValueError as e:
        error_detail = error_response(message=str(e), error_code="SIGNUP_ERROR")
        logger.error(f"❌ SIGNUP ERROR: {str(e)}")
        logger.error(f"📤 Error Response: {json.dumps(error_detail, indent=2)}")
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_detail
        )
    except Exception as e:
        error_detail = error_response(
            message="회원가입 처리 중 오류가 발생했습니다", 
            error_code="INTERNAL_ERROR"
        )
        logger.error(f"❌ SIGNUP INTERNAL ERROR: {str(e)}")
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_detail
        )


@router.post("/signup-multipart", response_model=dict, status_code=status.HTTP_201_CREATED)
async def signup_multipart(
    request: Request,
    user_id: str = Form(...),
    email: EmailStr = Form(...),
    nickname: str = Form(...),
    phone_number: Optional[str] = Form(None),  # 전화번호 추가
    cat_pattern: str = Form(...),
    cat_color: str = Form(...),
    profile_image: UploadFile = File(None),
    meow_audio: UploadFile = File(None),
    train_voice: Optional[list[UploadFile]] = File(None),  # 3개의 암구호 녹음 파일
    token: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    회원가입 (Multipart/form-data 방식)
    
    파일을 직접 업로드하는 방식
    
    필수 필드:
    - user_id: Google/Cognito sub 값
    - email: 이메일 주소
    - nickname: 닉네임
    - cat_pattern: 고양이 패턴
    - cat_color: 고양이 색상
    
    선택 필드:
    - profile_image: 프로필 이미지 파일
    - meow_audio: 야옹 소리 파일
    - train_voice: 암구호 학습용 음성 파일 3개 (배열)
    - token: FCM 토큰 (푸시 알림용)
    """
    # 요청 로깅
    logger.info(f"🔥 SIGNUP REQUEST (MULTIPART): {request.method} {request.url}")
    logger.info(f"📝 User ID: {user_id}, Email: {email}, Nickname: {nickname}")
    logger.info(f"🎨 Cat: pattern={cat_pattern}, color={cat_color}")
    
    if profile_image:
        logger.info(f"🖼️ Profile image: {profile_image.filename}")
    if meow_audio:
        logger.info(f"🐱 Meow audio: {meow_audio.filename}")
    if train_voice:
        logger.info(f"🎤 Train voice files: {len(train_voice)} files")
    
    try:
        user_service = UserService(db)
        
        # 파일 업로드 처리
        profile_image_url = None
        meow_audio_url = None
        train_voice_urls = []
        
        if profile_image:
            logger.info(f"📤 Uploading profile image to S3...")
            profile_image_url = await s3_service.upload_profile_image(profile_image, user_id)
            logger.info(f"✅ Profile image uploaded: {profile_image_url}")
        
        if meow_audio:
            logger.info(f"📤 Uploading meow audio to S3...")
            meow_audio_url = await s3_service.upload_meow_audio(meow_audio, user_id)
            logger.info(f"✅ Meow audio uploaded: {meow_audio_url}")
        
        if train_voice:
            # 3개의 암구호 파일 업로드 + 병합
            train_voice_files_data = []  # 병합을 위해 파일 데이터 저장
            
            for idx, voice_file in enumerate(train_voice[:3], 1):  # 최대 3개만
                try:
                    logger.info(f"📤 Uploading train voice {idx} to S3...")
                    
                    # 개별 파일 업로드
                    voice_url = await s3_service.upload_train_voice(voice_file, user_id, idx)
                    train_voice_urls.append(voice_url)
                    logger.info(f"✅ Train voice {idx} uploaded: {voice_url}")
                    
                    # 병합을 위해 파일 데이터 저장
                    await voice_file.seek(0)  # 파일 포인터 리셋
                    file_data = await voice_file.read()
                    train_voice_files_data.append(file_data)
                    
                except Exception as e:
                    logger.error(f"❌ Failed to upload train voice {idx}: {e}")
            
            # 3개 파일을 합쳐서 추가 업로드
            if len(train_voice_files_data) == 3:
                try:
                    from pydub import AudioSegment
                    import io
                    
                    logger.info("🔗 Merging 3 train voice files...")
                    
                    # 각 파일을 AudioSegment로 변환
                    audio_segments = []
                    for idx, file_data in enumerate(train_voice_files_data, 1):
                        try:
                            audio = AudioSegment.from_file(io.BytesIO(file_data))
                            audio_segments.append(audio)
                            logger.info(f"  - File {idx} loaded: {len(audio)}ms")
                        except Exception as e:
                            logger.error(f"❌ Failed to load audio file {idx}: {e}")
                            raise
                    
                    # 3개 파일 합치기 (순차적으로 이어붙이기)
                    merged_audio = audio_segments[0] + audio_segments[1] + audio_segments[2]
                    logger.info(f"✅ Merged audio length: {len(merged_audio)}ms")
                    
                    # WAV 형식으로 변환
                    merged_buffer = io.BytesIO()
                    merged_audio.export(merged_buffer, format="wav")
                    merged_bytes = merged_buffer.getvalue()
                    
                    # S3에 업로드
                    merged_url = await s3_service.upload_merged_train_voice(merged_bytes, user_id)
                    train_voice_urls.append(merged_url)  # 4번째 URL로 추가
                    logger.info(f"✅ Merged train voice uploaded: {merged_url}")
                    
                except Exception as e:
                    logger.error(f"❌ Failed to merge and upload train voices: {e}")
                    # 병합 실패해도 개별 파일은 이미 업로드됨
        
        # UserSignup 스키마 생성 (빈 문자열은 None으로 변환)
        signup_data = UserSignup(
            user_id=user_id,
            email=email,
            nickname=nickname,
            phone_number=phone_number if phone_number and phone_number != "" else None,
            cat_pattern=cat_pattern,
            cat_color=cat_color,
            profile_image_url=profile_image_url,
            meow_audio_url=meow_audio_url,
            train_voice_urls=train_voice_urls,
            token=token if token and token != "" else None
        )
        
        # 사용자 생성
        user = await user_service.create_user_from_signup(signup_data)
        
        response_data = success_response(
            data=UserResponse.model_validate(user),
            message="회원가입이 완료되었습니다"
        )
        
        # 응답 로깅
        logger.info(f"✅ SIGNUP SUCCESS: user_id={user.user_id}, email={user.email}")
        logger.info(f"📤 Response: 사용자 생성 완료 - 친구코드: {user.friend_code}")
        
        return response_data
        
    except ValueError as e:
        error_detail = error_response(message=str(e), error_code="SIGNUP_ERROR")
        logger.error(f"❌ SIGNUP ERROR: {str(e)}")
        logger.error(f"📤 Error Response: {json.dumps(error_detail, indent=2)}")
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_detail
        )
    except Exception as e:
        error_detail = error_response(
            message="회원가입 처리 중 오류가 발생했습니다", 
            error_code="INTERNAL_ERROR"
        )
        logger.error(f"❌ SIGNUP INTERNAL ERROR: {str(e)}")
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_detail
        )


@router.get("/check", response_model=dict, status_code=status.HTTP_200_OK)
async def check_user_exists(
    email: str,
    db: Session = Depends(get_db)
):
    """
    사용자 존재 여부 확인
    
    Google/Cognito 로그인 후 호출하여 해당 이메일의 사용자가 등록되어 있는지 확인
    
    Args:
        email: 확인할 이메일 주소
        
    Returns:
        - exists: 사용자 존재 여부 (true/false)
    """
    logger.info(f"🔍 USER CHECK REQUEST: email={email}")
    
    try:
        user_service = UserService(db)
        user = await user_service.get_user_by_email(email)
        
        exists = user is not None
        
        if exists:
            logger.info(f"✅ User exists: user_id={user.user_id}, nickname={user.nickname}")
        else:
            logger.info(f"❌ User not found: email={email}")
        
        return success_response(
            data={"exists": exists},
            message="사용자 존재 여부 확인 완료"
        )
            
    except Exception as e:
        logger.error(f"❌ USER CHECK ERROR: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_response(
                message="사용자 확인 중 오류가 발생했습니다",
                error_code="CHECK_ERROR"
            )
        )


@router.get("/profile/{user_id}", response_model=dict)
async def get_my_profile(
    request: Request,
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    사용자 프로필 조회
    
    - user_id는 URL 맨 뒤에 명시
    - 인증 없음 (보안 주의)
    - S3 URL은 presigned URL로 변환 (1시간 유효)
    """
    # 요청 로깅
    logger.info(f"🔥 GET_PROFILE REQUEST: {request.method} {request.url}")
    logger.info(f"👤 User ID: {user_id}")
    
    user_service = UserService(db)
    user = await user_service.get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_response(message="User not found", error_code="USER_NOT_FOUND")
        )
    
    # S3 URL을 presigned URL로 변환
    from app.services.s3_service import s3_service
    import json
    
    profile_image_url = None
    if user.profile_image_url:
        try:
            profile_image_url = s3_service.generate_presigned_url(user.profile_image_url, expiration=3600)
            logger.info(f"✅ Generated presigned URL for profile image")
        except Exception as e:
            logger.warning(f"⚠️ Failed to generate presigned URL for profile image: {e}")
            profile_image_url = user.profile_image_url  # fallback to original URL
    
    meow_audio_url = None
    if user.meow_audio_url:
        try:
            meow_audio_url = s3_service.generate_presigned_url(user.meow_audio_url, expiration=3600)
            logger.info(f"✅ Generated presigned URL for meow audio")
        except Exception as e:
            logger.warning(f"⚠️ Failed to generate presigned URL for meow audio: {e}")
            meow_audio_url = user.meow_audio_url  # fallback to original URL
    
    # train_voice_urls 파싱 및 presigned URL 변환
    train_voice_urls = []
    if user.train_voice_urls:
        try:
            # JSON 문자열을 리스트로 변환
            urls = json.loads(user.train_voice_urls) if isinstance(user.train_voice_urls, str) else user.train_voice_urls
            # 각 URL을 presigned URL로 변환
            for url in urls:
                try:
                    presigned_url = s3_service.generate_presigned_url(url, expiration=3600)
                    train_voice_urls.append(presigned_url)
                except Exception as e:
                    logger.warning(f"⚠️ Failed to generate presigned URL for train voice: {e}")
                    train_voice_urls.append(url)  # fallback to original URL
            logger.info(f"✅ Generated presigned URLs for {len(train_voice_urls)} train voice files")
        except Exception as e:
            logger.warning(f"⚠️ Failed to parse train_voice_urls: {e}")
    
    profile = UserProfile(
        user_id=user.user_id,
        email=user.email,
        nickname=user.nickname,
        phone_number=user.phone_number,
        provider=user.provider,
        profile_image_url=profile_image_url,
        friend_code=user.friend_code,
        cat_pattern=user.cat_pattern,
        cat_color=user.cat_color,
        meow_audio_url=meow_audio_url,
        train_voice_urls=train_voice_urls,
        token=user.token,  # FCM 토큰 추가
        created_at_timestamp=user.created_at_timestamp,
        updated_at_timestamp=user.updated_at_timestamp
    )
    
    response_data = success_response(
        data=profile,
        message="Profile retrieved successfully"
    )
    
    # 응답 로깅
    logger.info(f"✅ GET_PROFILE SUCCESS: user_id={user.user_id}")
    
    return response_data


@router.put("/profile/{user_id}", response_model=dict)
@router.post("/profile/{user_id}", response_model=dict)  # POST도 지원
async def update_my_profile(
    request: Request,
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    프로필 수정 (JSON 또는 Multipart 자동 감지)
    
    Content-Type에 따라 자동으로 처리 방식 결정:
    - application/json: URL만 받음
    - multipart/form-data: 파일 직접 업로드
    """
    content_type = request.headers.get("content-type", "")
    logger.info(f"🔥 UPDATE_PROFILE REQUEST: {request.method} {request.url}")
    logger.info(f"👤 User ID: {user_id}")
    logger.info(f"📋 Content-Type: {content_type}")
    
    try:
        user_service = UserService(db)
        
        if content_type.startswith("multipart/form-data"):
            # Multipart 처리
            logger.info("📦 Processing as MULTIPART")
            form = await request.form()
            
            # 디버깅: form 전체 키 출력
            logger.info(f"🔍 Form keys: {list(form.keys())}")
            
            email = form.get("email")
            nickname = form.get("nickname")
            full_name = form.get("full_name")  # full_name도 지원
            phone_number = form.get("phone_number")  # 전화번호 추가
            cat_pattern = form.get("cat_pattern")
            cat_color = form.get("cat_color")
            
            # 프로필 이미지는 파일 또는 URL로 받을 수 있음
            profile_image = form.get("profile_image")
            profile_image_url_str = form.get("profile_image_url")  # URL 문자열
            generated_image_url = form.get("generated_image_url")  # Gemini 생성 이미지 URL
            
            meow_audio = form.get("meow_audio")
            
            # train_voice_urls는 인덱스 포함된 이름으로 옴: train_voice_urls[0], train_voice_urls[1], train_voice_urls[2]
            # form의 모든 키를 순회하면서 train_voice_urls로 시작하는 파일 찾기
            train_voice = []
            for key in form.keys():
                if key.startswith("train_voice_urls[") and key.endswith("]"):
                    voice_file = form.get(key)
                    if voice_file and hasattr(voice_file, 'filename'):
                        train_voice.append(voice_file)
                        logger.info(f"🎤 Found train voice file: {key} -> {voice_file.filename}")
            
            logger.info(f"📝 Update fields: email={email}, nickname={nickname}, full_name={full_name}, phone={phone_number}")
            logger.info(f"📁 Files received: profile_image={profile_image.filename if profile_image and hasattr(profile_image, 'filename') else None}, meow_audio={meow_audio.filename if meow_audio and hasattr(meow_audio, 'filename') else None}, train_voice_count={len(train_voice)}")
            logger.info(f"🔗 URLs received: profile_image_url={profile_image_url_str}, generated_image_url={generated_image_url}")
            
            # 파일 업로드 처리
            profile_image_url = None
            meow_audio_url = None
            train_voice_urls = []
            
            # 프로필 이미지: 파일 업로드 > generated_image_url > clean URL 순서
            if profile_image and hasattr(profile_image, 'filename'):
                logger.info(f"📤 Uploading profile image: {profile_image.filename}")
                profile_image_url = await s3_service.upload_profile_image(profile_image, user_id)
                logger.info(f"✅ Uploaded: {profile_image_url}")
            elif generated_image_url:
                logger.info(f"🎨 Using generated image URL: {generated_image_url}")
                profile_image_url = generated_image_url
            elif profile_image_url_str:
                # presigned URL 체크: query parameter나 AWS signature가 있으면 무시
                is_presigned = '?' in profile_image_url_str or 'X-Amz-' in profile_image_url_str
                if is_presigned:
                    logger.info(f"⏭️  Ignoring presigned URL (keeping existing DB value)")
                    profile_image_url = None
                else:
                    # clean S3 URL이면 사용
                    logger.info(f"✅ Using clean S3 URL: {profile_image_url_str}")
                    profile_image_url = profile_image_url_str
            
            if meow_audio and hasattr(meow_audio, 'filename'):
                logger.info(f"📤 Uploading meow audio: {meow_audio.filename}")
                meow_audio_url = await s3_service.upload_meow_audio(meow_audio, user_id)
                logger.info(f"✅ Uploaded: {meow_audio_url}")
            
            if train_voice:
                # 3개의 암구호 파일 업로드 + 병합
                train_voice_files_data = []  # 병합을 위해 파일 데이터 저장
                
                for idx, voice_file in enumerate(train_voice[:3], 1):  # 최대 3개만
                    if hasattr(voice_file, 'filename'):
                        try:
                            logger.info(f"📤 Uploading train voice {idx}: {voice_file.filename}")
                            
                            # 개별 파일 업로드
                            voice_url = await s3_service.upload_train_voice(voice_file, user_id, idx)
                            train_voice_urls.append(voice_url)
                            logger.info(f"✅ Uploaded: {voice_url}")
                            
                            # 병합을 위해 파일 데이터 저장
                            await voice_file.seek(0)  # 파일 포인터 리셋
                            file_data = await voice_file.read()
                            train_voice_files_data.append(file_data)
                            
                        except Exception as e:
                            logger.error(f"❌ Failed to upload train voice {idx}: {e}")
                
                # 3개 파일을 합쳐서 추가 업로드
                if len(train_voice_files_data) == 3:
                    try:
                        from pydub import AudioSegment
                        import io
                        
                        logger.info("🔗 Merging 3 train voice files...")
                        
                        # 각 파일을 AudioSegment로 변환
                        audio_segments = []
                        for idx, file_data in enumerate(train_voice_files_data, 1):
                            try:
                                audio = AudioSegment.from_file(io.BytesIO(file_data))
                                audio_segments.append(audio)
                                logger.info(f"  - File {idx} loaded: {len(audio)}ms")
                            except Exception as e:
                                logger.error(f"❌ Failed to load audio file {idx}: {e}")
                                raise
                        
                        # 3개 파일 합치기 (순차적으로 이어붙이기)
                        merged_audio = audio_segments[0] + audio_segments[1] + audio_segments[2]
                        logger.info(f"✅ Merged audio length: {len(merged_audio)}ms")
                        
                        # WAV 형식으로 변환
                        merged_buffer = io.BytesIO()
                        merged_audio.export(merged_buffer, format="wav")
                        merged_bytes = merged_buffer.getvalue()
                        
                        # S3에 업로드
                        merged_url = await s3_service.upload_merged_train_voice(merged_bytes, user_id)
                        train_voice_urls.append(merged_url)  # 4번째 URL로 추가
                        logger.info(f"✅ Merged train voice uploaded: {merged_url}")
                        
                    except Exception as e:
                        logger.error(f"❌ Failed to merge and upload train voices: {e}")
                        # 병합 실패해도 개별 파일은 이미 업로드됨
            
            # UserUpdate 스키마 생성 (None이 아닌 값만 포함)
            update_dict = {}
            
            if email is not None and email != "":
                update_dict["email"] = email
            if nickname is not None and nickname != "":
                update_dict["nickname"] = nickname
            if full_name is not None and full_name != "":
                update_dict["full_name"] = full_name
            if phone_number is not None and phone_number != "":
                update_dict["phone_number"] = phone_number
            if cat_pattern is not None and cat_pattern != "":
                update_dict["cat_pattern"] = cat_pattern
            if cat_color is not None and cat_color != "":
                update_dict["cat_color"] = cat_color
            
            # 파일 업로드가 있었을 때만 URL 필드 추가
            if profile_image_url is not None:
                update_dict["profile_image_url"] = profile_image_url
            if meow_audio_url is not None:
                update_dict["meow_audio_url"] = meow_audio_url
            if train_voice_urls:
                update_dict["train_voice_urls"] = train_voice_urls
            
            # 디버깅: update_dict 내용 로깅
            logger.info(f"📋 Update dict: {update_dict}")
            
            profile_data = UserUpdate(**update_dict)
            
        else:
            # JSON 처리
            logger.info("📄 Processing as JSON")
            body = await request.json()
            
            # URL 필드 처리: presigned URL이면 제거, clean URL이면 유지
            if 'profile_image_url' in body and body['profile_image_url']:
                is_presigned = '?' in body['profile_image_url'] or 'X-Amz-' in body['profile_image_url']
                if is_presigned:
                    logger.info(f"⏭️  Removing presigned profile_image_url (keeping existing DB value)")
                    body.pop('profile_image_url', None)
                else:
                    logger.info(f"✅ Using clean profile_image_url: {body['profile_image_url']}")
            
            if 'meow_audio_url' in body and body['meow_audio_url']:
                is_presigned = '?' in body['meow_audio_url'] or 'X-Amz-' in body['meow_audio_url']
                if is_presigned:
                    logger.info(f"⏭️  Removing presigned meow_audio_url (keeping existing DB value)")
                    body.pop('meow_audio_url', None)
                else:
                    logger.info(f"✅ Using clean meow_audio_url: {body['meow_audio_url']}")
            
            if 'train_voice_urls' in body and body['train_voice_urls']:
                # train_voice_urls는 배열이므로 첫 번째 URL만 체크
                first_url = body['train_voice_urls'][0] if body['train_voice_urls'] else ''
                is_presigned = '?' in first_url or 'X-Amz-' in first_url
                if is_presigned:
                    logger.info(f"⏭️  Removing presigned train_voice_urls (keeping existing DB value)")
                    body.pop('train_voice_urls', None)
                else:
                    logger.info(f"✅ Using clean train_voice_urls")
            
            profile_data = UserUpdate(**body)
            logger.info(f"📝 Request Body: {profile_data.model_dump(exclude_unset=True)}")
        
        # 프로필 업데이트
        updated_user = await user_service.update_user(user_id, profile_data)
        
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error_response(message="User not found", error_code="USER_NOT_FOUND")
            )
        
        response_data = success_response(
            data=UserResponse.model_validate(updated_user),
            message="Profile updated successfully"
        )
        
        logger.info(f"✅ UPDATE_PROFILE SUCCESS: user_id={user_id}")
        
        return response_data
        
    except Exception as e:
        logger.error(f"❌ UPDATE_PROFILE ERROR: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_response(message=str(e), error_code="UPDATE_ERROR")
        )


@router.post("/setup-profile/{user_id}", response_model=dict)
async def setup_profile(
    user_id: str,
    nickname: str = Form(...),
    cat_pattern: Optional[str] = Form(None),
    cat_color: Optional[str] = Form(None),
    profile_image: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    """
    프로필 설정 (Multipart/form-data 지원)
    
    - user_id는 URL 맨 뒤에 명시
    - 인증 불필요
    
    필수 필드:
    - nickname: 닉네임
    
    선택 필드:
    - cat_pattern: 고양이 패턴
    - cat_color: 고양이 색상
    - profile_image: 프로필 이미지 파일
    """
    logger.info(f"🔥 SETUP_PROFILE REQUEST: user_id={user_id}")
    logger.info(f"📝 Nickname: {nickname}, Pattern: {cat_pattern}, Color: {cat_color}")
    
    if profile_image:
        logger.info(f"🖼️ Profile image: {profile_image.filename}")
    
    try:
        user_service = UserService(db)
        
        # 파일 업로드 처리
        profile_image_url = None
        if profile_image:
            logger.info(f"📤 Uploading profile image to S3...")
            profile_image_url = await s3_service.upload_profile_image(profile_image, user_id)
            logger.info(f"✅ Profile image uploaded: {profile_image_url}")
        
        # ProfileSetupData 생성
        profile_dict = {
            "nickname": nickname,
            "cat_pattern": cat_pattern,
            "cat_color": cat_color
        }
        
        updated_user = await user_service.setup_user_profile(user_id, profile_dict)
        
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error_response(message="User not found", error_code="USER_NOT_FOUND")
            )
        
        # profile_image_url 별도 업데이트
        if profile_image_url:
            updated_user.profile_image_url = profile_image_url
            db.commit()
            db.refresh(updated_user)
        
        logger.info(f"✅ SETUP_PROFILE SUCCESS: user_id={user_id}")
        
        return success_response(
            data=UserResponse.model_validate(updated_user),
            message="Profile setup completed successfully"
        )
    except Exception as e:
        logger.error(f"❌ SETUP_PROFILE ERROR: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_response(message=str(e), error_code="PROFILE_SETUP_ERROR")
        )


@router.get("/{user_id}", response_model=dict)
async def get_user(
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    특정 사용자 조회
    
    Parameters:
    - user_id: 조회할 사용자 ID (예: 12345678)
    
    예시:
    - user_id: 12345678 (고양이집사1)
    - user_id: 23456789 (고양이집사2)
    - user_id: 87654321 (내닉네임)
    """
    user_service = UserService(db)
    user = await user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_response(message="User not found", error_code="USER_NOT_FOUND")
        )
    
    return success_response(
        data=UserResponse.model_validate(user),
        message="User retrieved successfully"
    )


@router.get("/friend-code-lookup/{friend_code}", response_model=dict)
async def get_user_by_friend_code(
    friend_code: str,
    db: Session = Depends(get_db)
):
    """
    친구 코드로 사용자 조회
    
    Parameters:
    - friend_code: 조회할 사용자의 친구 코드 (예: ABC123)
    
    예시:
    - friend_code: ABC123
    - friend_code: DEF456
    """
    user_service = UserService(db)
    user = await user_service.get_user_by_friend_code(friend_code)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_response(message="User not found with this friend code", error_code="USER_NOT_FOUND")
        )
    
    return success_response(
        data=UserResponse.model_validate(user),
        message="User found by friend code"
    )


@router.get("/phone/{user_id}", response_model=dict)
async def get_user_phone_number(
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    사용자 전화번호 조회
    
    Parameters:
    - user_id: 조회할 사용자 ID
    
    Returns:
    - user_id: 사용자 ID
    - phone_number: 전화번호 (없으면 null)
    
    예시:
    - GET /api/v1/users/phone/c478cd4c-5071-7060-2991-cc9b3bb59dff
    """
    logger.info(f"🔥 GET_PHONE_NUMBER REQUEST: user_id={user_id}")
    
    user_service = UserService(db)
    user = await user_service.get_user_by_id(user_id)
    
    if not user:
        logger.error(f"❌ User not found: user_id={user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_response(message="User not found", error_code="USER_NOT_FOUND")
        )
    
    logger.info(f"✅ Phone number retrieved: user_id={user_id}, phone={user.phone_number}")
    
    return success_response(
        data={
            "user_id": user.user_id,
            "phone_number": user.phone_number
        },
        message="Phone number retrieved successfully"
    )



@router.post("/fcm-token/{user_id}", response_model=dict)
async def update_fcm_token(
    user_id: str,
    token: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    FCM 토큰 업데이트
    
    Parameters:
    - user_id: 사용자 ID
    - token: Firebase Cloud Messaging 토큰
    
    Returns:
    - user_id: 사용자 ID
    - token: 업데이트된 FCM 토큰
    
    예시:
    - POST /api/v1/users/fcm-token/c478cd4c-5071-7060-2991-cc9b3bb59dff
    - Body: token=dGhpc19pc19hX3Rlc3RfdG9rZW4...
    """
    logger.info(f"🔥 UPDATE_FCM_TOKEN REQUEST: user_id={user_id}")
    logger.info(f"📱 Token (first 20 chars): {token[:20]}...")
    
    user_service = UserService(db)
    user = await user_service.update_fcm_token(user_id, token)
    
    if not user:
        logger.error(f"❌ User not found: user_id={user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_response(message="User not found", error_code="USER_NOT_FOUND")
        )
    
    logger.info(f"✅ FCM token updated: user_id={user_id}")
    
    return success_response(
        data={
            "user_id": user.user_id,
            "token": user.token
        },
        message="FCM token updated successfully"
    )


@router.post("/status/{user_id}", response_model=dict)
async def update_my_status(
    user_id: str,
    status: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    본인의 일일 상태 업데이트
    
    Parameters:
    - user_id: 사용자 ID
    - status: 상태 메시지
    
    예시:
    - POST /api/v1/users/status/user123
    - Body: status=오늘 기분이 좋아요!
    """
    logger.info(f"🔥 UPDATE_STATUS REQUEST: user_id={user_id}, status={status}")
    
    from app.services.dynamodb_service import dynamodb_service
    
    # 사용자 존재 확인
    user_service = UserService(db)
    user = await user_service.get_user_by_id(user_id)
    if not user:
        logger.error(f"❌ User not found: user_id={user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_response(message="User not found", error_code="USER_NOT_FOUND")
        )
    
    # Status 업데이트
    success = await dynamodb_service.update_my_daily_status(user_id, status)
    
    if not success:
        logger.error(f"❌ Status update failed: user_id={user_id}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_response(message="Failed to update status", error_code="STATUS_UPDATE_ERROR")
        )
    
    logger.info(f"✅ Status updated: user_id={user_id}")
    
    return success_response(
        data={"user_id": user_id, "daily_status": status},
        message="Status updated successfully"
    )


@router.get("/status/{user_id}", response_model=dict)
async def get_my_status(
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    본인의 일일 상태 조회
    
    Parameters:
    - user_id: 사용자 ID
    
    예시:
    - GET /api/v1/users/status/user123
    """
    logger.info(f"🔥 GET_STATUS REQUEST: user_id={user_id}")
    
    from app.services.dynamodb_service import dynamodb_service
    
    # 사용자 존재 확인
    user_service = UserService(db)
    user = await user_service.get_user_by_id(user_id)
    if not user:
        logger.error(f"❌ User not found: user_id={user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_response(message="User not found", error_code="USER_NOT_FOUND")
        )
    
    # Status 조회
    daily_status = await dynamodb_service.get_my_daily_status(user_id)
    
    logger.info(f"✅ Status retrieved: user_id={user_id}, status={daily_status}")
    
    return success_response(
        data={"user_id": user_id, "daily_status": daily_status or ""},
        message="Status retrieved successfully"
    )



@router.delete("/{user_id}", response_model=dict)
async def delete_user_account(
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    사용자 계정 완전 삭제
    
    다음 항목들이 모두 삭제됩니다:
    - RDS: 사용자 정보
    - DynamoDB: 모든 친구 관계 (양방향)
    - S3: 프로필 이미지, 야옹 소리, train voice, 챌린지 이미지 등
    
    Parameters:
    - user_id: 삭제할 사용자 ID
    
    예시:
    - DELETE /api/v1/users/b4589ddc-a001-7001-77aa-c2c3f3fd6a98
    """
    logger.info(f"🔥 DELETE_USER REQUEST: user_id={user_id}")
    
    user_service = UserService(db)
    success = await user_service.delete_user(user_id)
    
    if not success:
        logger.error(f"❌ User deletion failed: user_id={user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_response(message="User not found or deletion failed", error_code="USER_DELETE_ERROR")
        )
    
    logger.info(f"✅ User deleted successfully: user_id={user_id}")
    
    return success_response(
        data={"user_id": user_id, "deleted": True},
        message="User account completely deleted"
    )
