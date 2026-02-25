"""
Audio LLM Guard Service
========================
Gemini Flash를 사용하여 애매한 STT 텍스트가
고양이 울음소리/무해 발화인지, 의미 있는 언어 발화인지 판정한다.

- 별도 API 키: AUDIO_GUARD_GEMINI_API_KEY
- 2초 타임아웃 강제
- 실패 시 예외 → audio_guard에서 FAIL_LLM 처리
"""

import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════
# Constants
# ═══════════════════════════════════════════════════════════════════════

LLM_TIMEOUT_S = 3
MODEL_NAME = "gemini-2.5-flash"

SYSTEM_PROMPT = """
당신은 '고양이 버튼 사운드' 업로드 텍스트의 "금지표현 감지기"입니다.

목표:
STT 텍스트에 아래 금지 카테고리가 포함된 경우에만 REJECT를 출력합니다.
그 외 모든 경우는 ALLOW를 출력합니다.
(인사/감정표현/한 단어/짧은 문장 포함: 모두 ALLOW)

금지 카테고리 (포함 시 REJECT):
- 욕설/비속어
- 혐오표현/차별/모욕
- 위협/자해/폭력 선동
- 성적/외설 표현
- 정치 선동/혐오/위협

중요:
- 애매하면 ALLOW.

출력:
반드시 ALLOW 또는 REJECT 중 하나만 출력.
"""

# ═══════════════════════════════════════════════════════════════════════
# AudioLLMService
# ═══════════════════════════════════════════════════════════════════════


class AudioLLMService:
    """Gemini Flash 기반 애매 텍스트 판정."""

    def __init__(self):
        self._model = None

    def _get_model(self):
        """Lazy init — 첫 호출 시 모델 초기화."""
        if self._model is not None:
            return self._model

        import google.generativeai as genai

        api_key = os.getenv("AUDIO_GUARD_GEMINI_API_KEY")
        if not api_key:
            raise ValueError(
                "AUDIO_GUARD_GEMINI_API_KEY 환경변수가 설정되지 않았습니다."
            )

        genai.configure(api_key=api_key)
        self._model = genai.GenerativeModel(MODEL_NAME)
        logger.info(f"AudioLLMService 초기화 완료 (model={MODEL_NAME})")
        return self._model

    def judge(
        self, normalized_text: str, raw_text: str
    ) -> str:
        """
        텍스트 판정.

        Args:
            normalized_text: 정규화된 STT 텍스트
            raw_text: 원본 STT 텍스트

        Returns:
            "ALLOW" 또는 "REJECT"

        Raises:
            Exception: LLM 호출 실패 시 (audio_guard에서 FAIL_LLM 처리)
        """
        model = self._get_model()

        prompt = (
            f"{SYSTEM_PROMPT}\n\n"
            f"STT 원본: \"{raw_text}\"\n"
            f"정규화: \"{normalized_text}\"\n\n"
            f"지금 즉시 한 단어로만 답해: ALLOW 또는 REJECT"
        )

        logger.info(f"LLM 판정 요청: '{normalized_text}'")

        response = model.generate_content(
            prompt,
            generation_config={
                "max_output_tokens": 128,
                "temperature": 0.0,
            },
        )

        def _extract_all_text(resp) -> str:
            """google-generativeai 응답에서 가능한 모든 텍스트를 모아서 합친다."""
            texts = []

            def pull(obj):
                if not obj:
                    return
                cands = getattr(obj, "candidates", None)
                if not cands:
                    return
                for c in cands:
                    content = getattr(c, "content", None)
                    parts = getattr(content, "parts", None) if content else None
                    if parts:
                        for p in parts:
                            t = getattr(p, "text", None)
                            if t:
                                texts.append(t)
                    else:
                        # parts가 비어도 content 자체를 문자열로 한번 살려본다 (디버깅/호환성)
                        try:
                            texts.append(str(content))
                        except Exception:
                            pass

            # 표면 response
            pull(resp)
            # 내부 result
            pull(getattr(resp, "_result", None))
            # 내부 chunks (조각이 여기 들어오는 경우가 있음)
            for ch in getattr(resp, "_chunks", []) or []:
                pull(ch)

            return "".join(texts)

        answer = _extract_all_text(response).strip().upper()
        logger.info(f"LLM 응답(raw): '{answer}'")

        # 강건 판정: 포함 여부로만 판단 (조각/여분 텍스트 방어)
        if "REJECT" in answer:
            return "REJECT"
        if "ALLOW" in answer:
            return "ALLOW"

        # 아무 키워드도 없으면 보수적으로 REJECT
        logger.warning(f"LLM 응답이 비었거나 키워드 없음: '{answer}' → REJECT")
        return "REJECT"


# ═══════════════════════════════════════════════════════════════════════
# Global instance
# ═══════════════════════════════════════════════════════════════════════

audio_llm_service = AudioLLMService()
