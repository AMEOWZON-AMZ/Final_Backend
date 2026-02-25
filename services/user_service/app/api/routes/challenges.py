"""
챌린지 API 라우트
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional
from app.core.database import get_db
from app.services.challenge_service import challenge_service
from app.services.s3_service import s3_service
from app.schemas.challenge import (
    ChallengeDayCreate,
    ChallengeDayResponse,
    ChallengeDayDetailResponse,
    SubmissionResponse,
    UserChallengeHistoryResponse,
    ChallengeMapResponse,
    FriendSubmissionInfo
)
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/", response_model=ChallengeDayResponse, status_code=201)
async def create_challenge_day(
    challenge_data: ChallengeDayCreate,
    db: Session = Depends(get_db)
):
    """
    새 챌린지 생성 (관리자용)
    
    - challenge_date: 챌린지 날짜 (YYYY-MM-DD)
    - title: 챌린지 제목
    - description: 챌린지 설명 (선택)
    """
    try:
        challenge = challenge_service.create_challenge_day(db, challenge_data)
        return challenge
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create challenge: {e}")
        raise HTTPException(status_code=500, detail="Failed to create challenge")


@router.get("/date/{target_date}", response_model=ChallengeDayDetailResponse)
async def get_challenge_by_date(
    target_date: date,
    user_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    특정 날짜의 챌린지 조회
    
    - target_date: 조회할 날짜 (YYYY-MM-DD)
    - user_id: 사용자 ID (선택, 제공 시 제출 여부 포함)
    
    응답:
    - id: 챌린지 ID
    - date: 챌린지 날짜
    - title: 챌린지 제목
    - description: 챌린지 설명
    - is_active: 오늘 날짜인지 여부 (true면 제출 가능)
    - user_submission: 사용자 제출 정보 (user_id 제공 시)
    """
    try:
        challenge_detail = challenge_service.get_challenge_by_date(db, target_date, user_id)
        return challenge_detail
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get challenge: {e}")
        raise HTTPException(status_code=500, detail="Failed to get challenge")


@router.post("/{challenge_day_id}/submit", response_model=SubmissionResponse, status_code=201)
async def submit_challenge(
    challenge_day_id: int,
    user_id: str = Form(...),
    image: UploadFile = File(...),
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None),
    altitude: Optional[float] = Form(None),
    db: Session = Depends(get_db)
):
    """
    챌린지 사진 제출 (오늘 날짜만 가능)
    
    Parameters:
    - challenge_day_id: 챌린지 ID
    - user_id: 사용자 ID (Form)
    - image: 이미지 파일 (File)
    - latitude: 위도 (Form, 선택적) - 앱에서 직접 전송
    - longitude: 경도 (Form, 선택적) - 앱에서 직접 전송
    - altitude: 고도 (Form, 선택적) - 앱에서 직접 전송
    
    제약사항:
    - 오늘 날짜 챌린지만 제출 가능
    - 한 챌린지당 1회만 제출 가능
    - 이미지 파일만 허용
    
    GPS 우선순위:
    1. 앱에서 전송한 위치 (latitude, longitude) - 가장 정확
    2. 이미지 EXIF GPS - 백업용
    3. GPS 없음 - 제출은 가능
    """
    try:
        # 파일 정보 로깅
        logger.info(f"🔍 Submit challenge - challenge_id: {challenge_day_id}, user_id: {user_id}")
        logger.info(f"🔍 File - filename: {image.filename}, content_type: '{image.content_type}'")
        
        # 앱에서 전송한 위치 확인
        app_provided_gps = latitude is not None and longitude is not None
        if app_provided_gps:
            logger.info(f"📍 App provided GPS: lat={latitude}, lon={longitude}")
        
        # 챌린지 정보 조회 (날짜 확인용)
        from app.models.challenge import ChallengeDay
        challenge = db.query(ChallengeDay).filter(ChallengeDay.id == challenge_day_id).first()
        if not challenge:
            raise HTTPException(status_code=404, detail="Challenge not found")
        
        # S3에 이미지 업로드 (EXIF GPS 추출 시도)
        challenge_date_str = challenge.challenge_date.strftime("%Y-%m-%d")
        image_url, exif_gps_data = await s3_service.upload_challenge_image(image, user_id, challenge_date_str)
        
        # GPS 데이터 결정 (우선순위: 앱 전송 > EXIF)
        final_latitude = latitude if app_provided_gps else (exif_gps_data['latitude'] if exif_gps_data else None)
        final_longitude = longitude if app_provided_gps else (exif_gps_data['longitude'] if exif_gps_data else None)
        final_altitude = altitude if altitude is not None else (exif_gps_data.get('altitude') if exif_gps_data else None)
        
        # GPS 소스 로깅
        if app_provided_gps:
            logger.info(f"📍 Using app-provided GPS: lat={final_latitude}, lon={final_longitude}")
        elif exif_gps_data:
            logger.info(f"📍 Using EXIF GPS: lat={final_latitude}, lon={final_longitude}")
        else:
            logger.info(f"📍 No GPS data available")
        
        # DB에 제출 기록 저장 (GPS 포함)
        submission = challenge_service.submit_challenge(
            db=db,
            challenge_day_id=challenge_day_id,
            user_id=user_id,
            image_url=image_url,
            latitude=final_latitude,
            longitude=final_longitude,
            altitude=final_altitude
        )
        
        return submission
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to submit challenge: {e}")
        raise HTTPException(status_code=500, detail="Failed to submit challenge")


@router.get("/users/{user_id}/history", response_model=UserChallengeHistoryResponse)
async def get_user_challenge_history(
    user_id: str,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """
    사용자 챌린지 참여 이력 조회
    
    - user_id: 사용자 ID
    - limit: 조회 개수 (기본 50)
    - offset: 시작 위치 (기본 0)
    
    응답:
    - total: 전체 참여 개수
    - submissions: 제출 목록 (최신순)
    """
    try:
        history = challenge_service.get_user_challenge_history(db, user_id, limit, offset)
        return history
    except Exception as e:
        logger.error(f"Failed to get user challenge history: {e}")
        raise HTTPException(status_code=500, detail="Failed to get challenge history")


@router.get("/date/{target_date}/friends", response_model=dict)
async def get_challenge_friends_images(
    target_date: date,
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    특정 날짜 챌린지의 제출 이미지 조회 (본인 + 친구들)
    
    - target_date: 조회할 날짜 (YYYY-MM-DD)
    - user_id: 현재 사용자 ID (쿼리 파라미터)
    
    응답:
    - challenge: 챌린지 제목
    - date: 챌린지 날짜
    - images: 제출된 이미지 URL 목록 (본인 + 친구들)
    - friends: 제출자 상세 정보 (user_id, nickname, image_url, submitted_at)
    """
    try:
        from app.models.challenge import ChallengeDay, ChallengeSubmission
        from app.models.user import User
        import boto3
        from app.core.config import settings
        
        # 1. 챌린지 조회
        challenge = db.query(ChallengeDay).filter(
            ChallengeDay.challenge_date == target_date
        ).first()
        
        if not challenge:
            raise HTTPException(status_code=404, detail="Challenge not found for this date")
        
        # 2. DynamoDB에서 친구 목록 조회
        dynamodb = boto3.resource('dynamodb', region_name=settings.AWS_REGION)
        friends_table = dynamodb.Table('user_friends')
        
        try:
            # Query로 user_id의 모든 친구 관계 조회
            from boto3.dynamodb.conditions import Key
            response = friends_table.query(
                KeyConditionExpression=Key('user_id').eq(user_id)
            )
            # friend_user_id 목록 추출
            friend_ids = [item['friend_user_id'] for item in response.get('Items', [])]
            logger.info(f"DynamoDB query for user {user_id}: found {len(friend_ids)} friends")
            logger.info(f"Friend IDs: {friend_ids}")
        except Exception as e:
            logger.warning(f"Failed to get friends from DynamoDB: {e}")
            friend_ids = []
        
        # 자기 자신도 포함 (본인 제출도 보이도록)
        all_user_ids = friend_ids + [user_id]
        logger.info(f"Including user's own submission. Total user_ids: {len(all_user_ids)}")
        
        # 3. 친구들 + 본인의 제출 이미지 조회
        logger.info(f"Querying submissions for challenge_id={challenge.id}, user_ids={all_user_ids}")
        submissions = db.query(ChallengeSubmission, User).join(
            User,
            ChallengeSubmission.user_id == User.user_id
        ).filter(
            ChallengeSubmission.challenge_day_id == challenge.id,
            ChallengeSubmission.user_id.in_(all_user_ids) if all_user_ids else False
        ).all()
        logger.info(f"Found {len(submissions)} submissions")
        
        # 4. Presigned URL 생성 (1시간 유효)
        from app.services.s3_service import s3_service
        
        images = []
        friends = []
        for submission, user in submissions:
            # S3 presigned URL 생성
            presigned_url = s3_service.generate_presigned_url(submission.image_url, expiration=3600)
            images.append(presigned_url)
            friends.append({
                "user_id": submission.user_id,
                "nickname": user.nickname,
                "image_url": presigned_url,
                "submitted_at": submission.created_at.isoformat(),
                "is_me": submission.user_id == user_id  # 본인 제출 여부 표시
            })
        
        return {
            "challenge": challenge.title,
            "date": challenge.challenge_date.isoformat(),
            "images": images,
            "friends": friends  # 본인 + 친구들 제출 목록
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get challenge friends images: {e}")
        raise HTTPException(status_code=500, detail="Failed to get friends images")


@router.post("/generate-next-month", response_model=dict)
async def generate_next_month_challenges_api(
    db: Session = Depends(get_db)
):
    """
    다음 달 챌린지 생성 (관리자 전용)
    
    Gemini API를 사용하여 다음 달의 일일 챌린지를 자동 생성합니다.
    
    - 매달 1일에 실행 권장
    - Gemini API로 창의적인 챌린지 생성
    - 중복 날짜는 자동으로 스킵
    
    응답:
    - year: 생성된 챌린지의 연도
    - month: 생성된 챌린지의 월
    - inserted: 새로 삽입된 챌린지 수
    - skipped: 이미 존재하여 스킵된 챌린지 수
    - total: 생성 시도한 총 챌린지 수
    """
    try:
        logger.info("🎯 Starting Gemini challenge generation...")
        
        # 챌린지 생성
        result = challenge_service.generate_next_month_challenges(db)
        
        logger.info(f"✅ Generated {result['inserted']} challenges for {result['year']}-{result['month']:02d}")
        
        return {
            "success": True,
            "message": f"Successfully generated {result['inserted']} challenges for {result['year']}-{result['month']:02d}",
            "data": result
        }
        
    except ImportError as e:
        logger.error(f"❌ Import error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="google-generativeai package not installed"
        )
    except ValueError as e:
        logger.error(f"❌ Configuration error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="GEMINI_API_KEY not configured"
        )
    except Exception as e:
        logger.error(f"❌ Failed to generate challenges: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate challenges: {str(e)}"
        )



@router.get("/map", response_model=ChallengeMapResponse)
async def get_challenge_map(
    date: str = Query(..., description="Challenge date (YYYY-MM-DD)"),
    user_id: Optional[str] = Query(None, description="User ID for friend filtering"),
    db: Session = Depends(get_db)
):
    """
    챌린지 지도 데이터 조회 (GPS 있는 제출만)
    
    - date: 챌린지 날짜 (YYYY-MM-DD)
    - user_id: 사용자 ID (친구 필터링용, 선택적)
    
    Returns:
        GPS 좌표가 있는 제출 목록 (지도 표시용)
    """
    try:
        from datetime import date as date_type
        challenge_date = date_type.fromisoformat(date)
        
        # 챌린지 정보 조회
        from app.models.challenge import ChallengeDay
        challenge = db.query(ChallengeDay).filter(
            ChallengeDay.challenge_date == challenge_date
        ).first()
        
        if not challenge:
            raise HTTPException(status_code=404, detail="Challenge not found for this date")
        
        # 친구 목록 가져오기 (user_id가 있으면)
        friend_ids = None
        if user_id:
            from app.services.dynamodb_service import dynamodb_service
            friends = await dynamodb_service.get_accepted_friends(user_id)
            friend_ids = [f['friend_user_id'] for f in friends]
            friend_ids.append(user_id)  # 본인도 포함
        
        # GPS 있는 제출 조회
        submissions = challenge_service.get_submissions_with_gps(
            db=db,
            challenge_date=challenge_date,
            user_ids=friend_ids
        )
        
        # 사용자 정보 조회 및 응답 생성
        from app.services.user_service import UserService
        user_service = UserService(db)
        submission_infos = []
        
        for sub in submissions:
            try:
                user = await user_service.get_user_by_id(sub.user_id)
                submission_infos.append(
                    FriendSubmissionInfo(
                        user_id=sub.user_id,
                        nickname=user.nickname if user else "Unknown",
                        image_url=sub.image_url,
                        latitude=float(sub.latitude) if sub.latitude else None,
                        longitude=float(sub.longitude) if sub.longitude else None,
                        altitude=float(sub.altitude) if sub.altitude else None,
                        has_gps=sub.has_gps,
                        submitted_at=sub.created_at
                    )
                )
            except Exception as e:
                logger.warning(f"Failed to get user info for {sub.user_id}: {e}")
                continue
        
        return ChallengeMapResponse(
            challenge_id=challenge.id,
            title=challenge.title,
            date=challenge.challenge_date,
            submissions=submission_infos
        )
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get challenge map: {e}")
        raise HTTPException(status_code=500, detail="Failed to get challenge map")
