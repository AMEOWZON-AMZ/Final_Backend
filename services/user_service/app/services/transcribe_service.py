import asyncio
import logging
import traceback
from typing import Optional
import concurrent.futures as cf

from amazon_transcribe.client import TranscribeStreamingClient
from amazon_transcribe.handlers import TranscriptResultStreamHandler
from amazon_transcribe.model import TranscriptEvent

from app.core.config import settings

logger = logging.getLogger(__name__)

LANGUAGE_CODE = "ko-KR"
MEDIA_ENCODING = "pcm"
CHUNK_SIZE = 1024 * 8
TRANSCRIBE_TIMEOUT_S = 8
REGION = settings.AWS_REGION  # ap-northeast-2

# ✅ 전역 executor (요청마다 만들지 않기)
_EXECUTOR = cf.ThreadPoolExecutor(max_workers=4)


class _ResultHandler(TranscriptResultStreamHandler):
    def __init__(self, output_stream):
        super().__init__(output_stream)
        self.final_texts: list[str] = []

    async def handle_transcript_event(self, transcript_event: TranscriptEvent):
        for result in transcript_event.transcript.results:
            if not result.is_partial:
                for alt in result.alternatives:
                    text = (alt.transcript or "").strip()
                    if text:
                        self.final_texts.append(text)


class TranscribeService:
    def transcribe_pcm(self, pcm_bytes: bytes, sample_rate: int = 16000) -> Optional[str]:
        """
        동기 진입점. FastAPI async 루프 안에서도 안전하게 동작.
        전체 타임아웃은 여기서만 강제(디버깅 단순화).
        """
        try:
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = None

            if loop and loop.is_running():
                # async 환경 → 별도 스레드에서 새 event loop로 실행
                fut = _EXECUTOR.submit(self._run_in_new_loop, pcm_bytes, sample_rate)
                return fut.result(timeout=TRANSCRIBE_TIMEOUT_S)
            else:
                # sync 환경 → 현재 스레드에서 event loop 실행
                return asyncio.run(self._transcribe_async(pcm_bytes, sample_rate))

        except cf.TimeoutError:
            logger.warning(f"🎤 [TRANSCRIBE] Timeout after {TRANSCRIBE_TIMEOUT_S}s")
            return None
        except Exception as e:
            logger.error("Transcribe 호출 실패: %r", e)
            logger.error("Traceback:\n%s", traceback.format_exc())
            return None

    def _run_in_new_loop(self, pcm_bytes: bytes, sample_rate: int) -> Optional[str]:
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(self._transcribe_async(pcm_bytes, sample_rate))
        finally:
            loop.close()

    async def _transcribe_async(self, pcm_bytes: bytes, sample_rate: int) -> Optional[str]:
        # ✅ 여기서는 timeout을 추가로 걸지 않음 (outer에서만 관리)
        return await self._stream_transcribe(pcm_bytes, sample_rate)

    async def _stream_transcribe(self, pcm_bytes: bytes, sample_rate: int) -> Optional[str]:
        client = TranscribeStreamingClient(region=REGION)

        stream = await client.start_stream_transcription(
            language_code=LANGUAGE_CODE,
            media_sample_rate_hz=sample_rate,
            media_encoding=MEDIA_ENCODING,
        )

        async def send_chunks():
            offset = 0
            while offset < len(pcm_bytes):
                chunk = pcm_bytes[offset:offset + CHUNK_SIZE]
                await stream.input_stream.send_audio_event(audio_chunk=chunk)
                offset += CHUNK_SIZE
            await stream.input_stream.end_stream()

        handler = _ResultHandler(stream.output_stream)

        await asyncio.gather(send_chunks(), handler.handle_events())

        if handler.final_texts:
            full_text = " ".join(handler.final_texts)
            logger.info("Transcribe 결과: '%s' (%d segments)", full_text, len(handler.final_texts))
            return full_text

        logger.info("Transcribe: 텍스트 없음 (빈 결과)")
        return None


transcribe_service = TranscribeService()