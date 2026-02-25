"""
챌린지 서비스
비즈니스 로직 처리
"""
from sqlalchemy.orm import Session
from sqlalchemy import desc, text
from datetime import date, datetime
from typing import Optional, List, Dict
from fastapi import HTTPException
from app.models.challenge import ChallengeDay, ChallengeSubmission
from app.schemas.challenge import (
    ChallengeDayCreate,
    ChallengeDayDetailResponse,
    UserSubmissionInfo,
    SubmissionResponse,
    UserChallengeHistory,
    UserChallengeHistoryResponse
)
import logging
import os
import calendar

logger = logging.getLogger(__name__)

# 타임존 처리 (Python 3.9+ zoneinfo, fallback to pytz)
try:
    from zoneinfo import ZoneInfo
    KST = ZoneInfo("Asia/Seoul")
except ImportError:
    import pytz
    KST = pytz.timezone("Asia/Seoul")


def get_today_kst() -> date:
    """
    한국 시간 기준 오늘 날짜 반환
    
    중요: EC2는 UTC 시간대일 수 있으므로 명시적으로 KST 사용
    예: UTC 2026-02-15 15:00 → KST 2026-02-16 00:00
    """
    return datetime.now(KST).date()


class ChallengeService:
    """챌린지 관련 비즈니스 로직"""
    
    @staticmethod
    def generate_challenges_with_gemini(year: int, month: int) -> List[tuple]:
        """
        Gemini API로 월간 챌린지 생성
        
        Args:
            year: 연도 (예: 2026)
            month: 월 (1-12)
        
        Returns:
            [(date, title, description), ...]
        """
        try:
            import google.generativeai as genai
            
            # Gemini API 설정
            GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
            if not GEMINI_API_KEY:
                raise ValueError("GEMINI_API_KEY not found in environment variables")
            
            genai.configure(api_key=GEMINI_API_KEY)
            
            # 해당 월의 일수 계산
            days_in_month = calendar.monthrange(year, month)[1]
            
            # 월 이름 (한글)
            month_names = {
                1: "1월 (겨울)", 2: "2월 (겨울)", 3: "3월 (봄)", 4: "4월 (봄)",
                5: "5월 (봄)", 6: "6월 (여름)", 7: "7월 (여름)", 8: "8월 (여름)",
                9: "9월 (가을)", 10: "10월 (가을)", 11: "11월 (가을)", 12: "12월 (겨울)"
            }
            
            # Gemini 프롬프트
            prompt = f"""
당신은 일상 사진 챌린지 기획자입니다.
{year}년 {month_names.get(month, f'{month}월')}의 일일 사진 챌린지를 {days_in_month}개 생성해주세요.

요구사항:
1. 일상에서 쉽게 찾을 수 있는 대상 (건물, 사물, 풍경, 동물 등)
2. 창의적이고 재미있는 주제
3. 매일 다른 주제 (중복 없음)
4. 간단한 제목 (2-6글자)
5. 짧은 설명 (10-25글자, "~을 찍어보세요" 형식)

예시:
소화기 | 오늘 마주친 소화기를 찍어보세요
엘리베이터 버튼 | 엘리베이터 버튼을 찍어보세요
현관 발판 | 현관 앞 발판을 찍어보세요
버스 번호 | 오늘 탄 버스 번호를 찍어보세요
전동 킥보드 | 길가에 세워진 킥보드를 찾아보세요

형식:
각 줄마다 "제목 | 설명" 형식으로 정확히 {days_in_month}개를 생성해주세요.
번호나 날짜는 붙이지 마세요.
"""
            
            # Gemini API 호출
            model = genai.GenerativeModel('gemini-2.5-flash')
            response = model.generate_content(prompt)
            
            # 응답 로깅
            logger.info(f"Gemini API Response received for {year}-{month:02d}")
            
            # 응답 파싱
            challenges = []
            lines = response.text.strip().split('\n')
            
            for i, line in enumerate(lines, start=1):
                if i > days_in_month:
                    break
                
                if '|' in line:
                    # 불필요한 문자 제거 (번호, 별표 등)
                    line = line.strip()
                    for prefix in ['*', '-', '•', '1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.']:
                        if line.startswith(prefix):
                            line = line[len(prefix):].strip()
                    
                    parts = line.split('|')
                    title = parts[0].strip()
                    description = parts[1].strip() if len(parts) > 1 else ""
                    
                    challenge_date = date(year, month, i)
                    challenges.append((challenge_date, title, description))
            
            logger.info(f"Successfully parsed {len(challenges)} challenges for {year}-{month:02d}")
            return challenges
            
        except ImportError:
            raise ImportError("google-generativeai package not installed")
        except Exception as e:
            logger.error(f"Failed to generate challenges with Gemini: {str(e)}")
            raise Exception(f"Failed to generate challenges with Gemini: {str(e)}")
    
    @staticmethod
    def generate_next_month_challenges(db: Session) -> Dict:
        """
        다음 달 챌린지 생성
        
        Returns:
            {"year": int, "month": int, "inserted": int, "skipped": int, "total": int}
        """
        today = datetime.now()
        
        # 다음 달 계산
        if today.month == 12:
            next_year = today.year + 1
            next_month = 1
        else:
            next_year = today.year
            next_month = today.month + 1
        
        logger.info(f"Generating challenges for {next_year}-{next_month:02d}")
        
        # Gemini로 챌린지 생성
        challenges = ChallengeService.generate_challenges_with_gemini(next_year, next_month)
        
        if not challenges:
            raise Exception("No challenges generated")
        
        # DB에 삽입
        inserted_count = 0
        skipped_count = 0
        
        for challenge_date, title, description in challenges:
            try:
                # PostgreSQL: ON CONFLICT DO NOTHING 사용
                result = db.execute(text("""
                    INSERT INTO challenge_days (challenge_date, title, description)
                    VALUES (:date, :title, :description)
                    ON CONFLICT (challenge_date) DO NOTHING
                    RETURNING id
                """), {
                    "date": challenge_date,
                    "title": title,
                    "description": description
                })
                
                if result.rowcount > 0:
                    inserted_count += 1
                    logger.info(f"Inserted challenge: {challenge_date} - {title}")
                else:
                    skipped_count += 1
                    logger.info(f"Skipped (already exists): {challenge_date}")
                    
            except Exception as e:
                logger.error(f"Failed to insert challenge for {challenge_date}: {e}")
                skipped_count += 1
        
        db.commit()
        
        logger.info(f"Challenge generation complete: {inserted_count} inserted, {skipped_count} skipped")
        
        return {
            "year": next_year,
            "month": next_month,
            "inserted": inserted_count,
            "skipped": skipped_count,
            "total": len(challenges)
        }
    
    @staticmethod
    def create_challenge_day(db: Session, challenge_data: ChallengeDayCreate) -> ChallengeDay:
        """새 챌린지 생성 (관리자용)"""
        # 해당 날짜에 이미 챌린지가 있는지 확인
        existing = db.query(ChallengeDay).filter(
            ChallengeDay.challenge_date == challenge_data.challenge_date
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Challenge already exists for date {challenge_data.challenge_date}"
            )
        
        # 새 챌린지 생성
        new_challenge = ChallengeDay(
            challenge_date=challenge_data.challenge_date,
            title=challenge_data.title,
            description=challenge_data.description
        )
        
        db.add(new_challenge)
        db.commit()
        db.refresh(new_challenge)
        
        logger.info(f"Challenge created: {new_challenge.id} for {challenge_data.challenge_date}")
        return new_challenge
    
    @staticmethod
    def get_challenge_by_date(db: Session, target_date: date, user_id: Optional[str] = None) -> ChallengeDayDetailResponse:
        """특정 날짜의 챌린지 조회"""
        # 챌린지 조회
        challenge = db.query(ChallengeDay).filter(
            ChallengeDay.challenge_date == target_date
        ).first()
        
        if not challenge:
            raise HTTPException(
                status_code=404,
                detail=f"No challenge found for date {target_date}"
            )
        
        # 오늘 날짜인지 확인 (한국 시간 기준)
        today_kst = get_today_kst()
        is_active = (target_date == today_kst)
        
        logger.info(f"Challenge date: {target_date}, Today (KST): {today_kst}, is_active: {is_active}")
        
        # 사용자 제출 정보 조회
        user_submission = None
        if user_id:
            submission = db.query(ChallengeSubmission).filter(
                ChallengeSubmission.challenge_day_id == challenge.id,
                ChallengeSubmission.user_id == user_id
            ).first()
            
            if submission:
                user_submission = UserSubmissionInfo(
                    submitted=True,
                    image_url=submission.image_url,
                    submitted_at=submission.created_at
                )
            else:
                user_submission = UserSubmissionInfo(submitted=False)
        
        return ChallengeDayDetailResponse(
            id=challenge.id,
            date=challenge.challenge_date,
            title=challenge.title,
            description=challenge.description,
            is_active=is_active,
            user_submission=user_submission
        )
    
    @staticmethod
    def submit_challenge(
        db: Session,
        challenge_day_id: int,
        user_id: str,
        image_url: str,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        altitude: Optional[float] = None
    ) -> SubmissionResponse:
        """챌린지 제출 (GPS 좌표 포함) - 여러 장 제출 가능"""
        # 챌린지 존재 확인
        challenge = db.query(ChallengeDay).filter(
            ChallengeDay.id == challenge_day_id
        ).first()
        
        if not challenge:
            raise HTTPException(status_code=404, detail="Challenge not found")
        
        # 오늘 날짜 챌린지인지 확인 (한국 시간 기준)
        today_kst = get_today_kst()
        if challenge.challenge_date != today_kst:
            raise HTTPException(
                status_code=400,
                detail=f"Can only submit to today's challenge. Today (KST): {today_kst}, Challenge date: {challenge.challenge_date}"
            )
        
        # GPS 정보 유무 확인
        has_gps = latitude is not None and longitude is not None
        
        # 새 제출 생성 (여러 장 제출 가능)
        new_submission = ChallengeSubmission(
            challenge_day_id=challenge_day_id,
            user_id=user_id,
            image_url=image_url,
            latitude=latitude,
            longitude=longitude,
            altitude=altitude,
            has_gps=has_gps
        )
        
        db.add(new_submission)
        db.commit()
        db.refresh(new_submission)
        
        logger.info(f"Challenge submission created: {new_submission.id}, GPS: {has_gps}")
        return SubmissionResponse(
            id=new_submission.id,
            challenge_day_id=new_submission.challenge_day_id,
            user_id=new_submission.user_id,
            image_url=new_submission.image_url,
            latitude=new_submission.latitude,
            longitude=new_submission.longitude,
            altitude=new_submission.altitude,
            has_gps=new_submission.has_gps,
            created_at=new_submission.created_at
        )
    
    @staticmethod
    def get_user_challenge_history(
        db: Session,
        user_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> UserChallengeHistoryResponse:
        """사용자 챌린지 참여 이력 조회"""
        # 제출 목록 조회 (최신순)
        submissions = db.query(ChallengeSubmission, ChallengeDay).join(
            ChallengeDay,
            ChallengeSubmission.challenge_day_id == ChallengeDay.id
        ).filter(
            ChallengeSubmission.user_id == user_id
        ).order_by(
            desc(ChallengeSubmission.created_at)
        ).limit(limit).offset(offset).all()
        
        # 전체 개수
        total = db.query(ChallengeSubmission).filter(
            ChallengeSubmission.user_id == user_id
        ).count()
        
        # 응답 생성
        history_list = [
            UserChallengeHistory(
                challenge_day_id=submission.challenge_day_id,
                date=challenge.challenge_date,
                title=challenge.title,
                image_url=submission.image_url,
                submitted_at=submission.created_at
            )
            for submission, challenge in submissions
        ]
        
        return UserChallengeHistoryResponse(
            total=total,
            submissions=history_list
        )


    @staticmethod
    def get_submissions_with_gps(
        db: Session,
        challenge_date: date,
        user_ids: Optional[List[str]] = None
    ) -> List[ChallengeSubmission]:
        """
        GPS 좌표가 있는 제출만 조회 (지도용)
        
        Args:
            db: 데이터베이스 세션
            challenge_date: 챌린지 날짜
            user_ids: 필터링할 사용자 ID 목록 (친구 목록 등)
        
        Returns:
            GPS 정보가 있는 제출 목록
        """
        # 챌린지 조회
        challenge = db.query(ChallengeDay).filter(
            ChallengeDay.challenge_date == challenge_date
        ).first()
        
        if not challenge:
            return []
        
        # GPS 있는 제출 조회
        query = db.query(ChallengeSubmission).filter(
            ChallengeSubmission.challenge_day_id == challenge.id,
            ChallengeSubmission.has_gps == True
        )
        
        # 특정 사용자들만 필터링 (친구 목록 등)
        if user_ids:
            query = query.filter(ChallengeSubmission.user_id.in_(user_ids))
        
        submissions = query.all()
        
        logger.info(f"Found {len(submissions)} submissions with GPS for date {challenge_date}")
        return submissions


# 전역 서비스 인스턴스
challenge_service = ChallengeService()
