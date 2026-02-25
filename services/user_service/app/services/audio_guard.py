"""
Audio Guardrail for Meow Audio Upload
======================================
회원가입 시 냐옹 음성 업로드에서 무음/불량 파일 및 언어 발화를
동기(10초 이내)로 차단하고, 저장 음성 품질을 통일한다.

Pipeline:
  0) 표준화 (16kHz mono, onset 기반 3초 추출)
  1) 오디오 품질 가드레일 (길이/무음/클리핑)
  2) STT (Transcribe Streaming — 항상 실행)
  3) 텍스트 판정 (meow-lexicon / 문장성 / LLM / 빈 텍스트)
  4) 품질 개선 (볼륨 정규화 / 무음 트리밍)

Returns:
  항상 dict — HTTPException을 raise하지 않음.
  status: "OK" | "FAIL"
  reason: Reason Code
  metrics: 디버깅/튜닝용 수치
"""

import io
import re
import logging
import numpy as np
from typing import Tuple, Dict, Any, Optional
from pydub import AudioSegment

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════
# Constants
# ═══════════════════════════════════════════════════════════════════════

SAMPLE_RATE = 16000
CHANNELS = 1
FRAME_MS = 10
FRAME_SAMPLES = int(SAMPLE_RATE * FRAME_MS / 1000)  # 160 samples

# Duration
MAX_DURATION_S = 4.0
MIN_DURATION_S = 0.3   # 0.3초 미만 → FAIL

# Quality thresholds
SILENCE_RMS_THRESHOLD = 0.01
CLIPPING_SAMPLE_THRESHOLD = 0.99
CLIPPING_RATIO_THRESHOLD = 0.05

# Onset detection
ONSET_NOISE_PERCENTILE = 20   # 하위 20% → 배경 소음
ONSET_MULTIPLIER = 2.8     # 소음 × 2.8 = onset threshold
ONSET_MIN_CONSECUTIVE = 2    # 2프레임(≈60ms) 연속

MAX_WAIT_S = 5.0          # 5초 안에 발화 없으면 FAIL
PRE_ROLL_MS = 700        # “사람 발화 앞 0.5초 ok”
VOICE_PRESENT_THR = 0.004 # 발화 존재 판정용 (튜닝 포인트)        

# Text judgment
SENTENCE_MAX_NORMALIZED_LEN = 12  # >= 12 → 즉시 FAIL

# Volume normalization
TARGET_DBFS = -20.0
TRIM_SILENCE_THRESH_DB = -55
TRIM_MARGIN_MS = 80
MIN_KEEP_HEAD_MS = 200
MIN_TRIM_MS = 300

# ── Meow lexicon regex (정규화 후 텍스트에 적용) ────────────────────
_MEOW_TOKEN = r'(?:(?:냐|야|먀)(?:아*)(?:옹|오)|미(?:야+)(?:아*)(?:옹|오)|냥+)'
MEOW_PATTERN = re.compile(rf'^(?:{_MEOW_TOKEN})+$')


# ═══════════════════════════════════════════════════════════════════════
# AudioGuard
# ═══════════════════════════════════════════════════════════════════════


class AudioGuard:
    """냐옹 음성 업로드 가드레일 파이프라인."""

    # ──────────────────────────────────────────────────────────────
    # Public API
    # ──────────────────────────────────────────────────────────────

    def process(self, raw_bytes: bytes, filename: str) -> Dict[str, Any]:
        """
        메인 진입점. 항상 구조화된 dict를 반환한다 (예외를 raise하지 않음).

        Returns:
            {
                "status":         "OK" | "FAIL",
                "reason":         Reason Code (e.g. OK_MEOW_LEXICON, FAIL_SILENCE),
                "metrics":        { dur_total_s, onset_ms, speech_dur_s,
                                    rms, clip_ratio, stt_text_len },
                "stt_text":       정규화된 STT 텍스트 (없으면 None),
                "audio_bytes":    처리된 WAV bytes  (OK일 때만),
                "content_type":   "audio/wav"       (OK일 때만),
                "file_extension": "wav"             (OK일 때만),
            }
        """
        metrics: Dict[str, Any] = {
            "dur_total_s": 0.0,
            "onset_ms": -1,
            "speech_dur_s": 0.0,
            "rms": 0.0,
            "clip_ratio": 0.0,
            "stt_text_len": 0,
        }

        logger.info(
            f"AudioGuard.process() start — "
            f"file={filename}, size={len(raw_bytes)} bytes"
        )
        logger.info("🎵 [AUDIO_GUARD] Step 0: Starting audio validation")

        # ── Step 0: 디코딩 ─────────────────────────────────────
        logger.info(f"🎵 [AUDIO_GUARD] Step 0.1: Decoding audio file (format: {filename.rsplit('.', 1)[-1] if '.' in filename else 'unknown'})")
        try:
            ext = (
                filename.rsplit('.', 1)[-1].lower()
                if '.' in filename else ''
            )
            fmt_map = {
                'mp3': 'mp3', 'wav': 'wav',
                'mp4': 'mp4', 'm4a': 'mp4',
            }
            audio = AudioSegment.from_file(
                io.BytesIO(raw_bytes), format=fmt_map.get(ext)
            )
        except Exception as e:
            logger.error(f"❌ [AUDIO_GUARD] Audio decoding failed: {e}")
            return self._fail("FAIL_DECODE", metrics)

        logger.info(f"✅ [AUDIO_GUARD] Step 0.2: Audio decoded successfully")
        
        # 16kHz mono + 16-bit(PCM16)로 강제 (중요: RMS/클리핑/온셋 스케일 안정화)
        logger.info(f"🎵 [AUDIO_GUARD] Step 0.3: Converting to 16kHz mono PCM16")
        audio = (
            audio.set_frame_rate(SAMPLE_RATE)
                 .set_channels(CHANNELS)
                 .set_sample_width(2)
        )
        raw_samples = np.array(
            audio.get_array_of_samples(), dtype=np.float32
        ) / 32768.0
        metrics["dur_total_s"] = round(len(raw_samples) / SAMPLE_RATE, 3)
        logger.info(f"✅ [AUDIO_GUARD] Audio normalized: duration={metrics['dur_total_s']}s, samples={len(raw_samples)}")

        # ── Step 0': Onset 검출 + 3초 추출 ─────────────────────
        logger.info(f"🎵 [AUDIO_GUARD] Step 1: Detecting speech onset (max wait: {MAX_WAIT_S}s)")
        wait_samples = int(MAX_WAIT_S * SAMPLE_RATE)
        scan = raw_samples[:min(len(raw_samples), wait_samples)]

        n_frames = len(scan) // FRAME_SAMPLES
        if n_frames <= 0:
            return self._fail("FAIL_TOO_SHORT", metrics)

        # frame rms + peak (초성은 peak가 잘 잡힘)
        frame_rms = np.empty(n_frames, dtype=np.float32)
        frame_peak = np.empty(n_frames, dtype=np.float32)

        for i in range(n_frames):
            fr = scan[i*FRAME_SAMPLES:(i+1)*FRAME_SAMPLES]
            frame_rms[i] = np.sqrt(np.mean(fr**2))
            frame_peak[i] = np.max(np.abs(fr))

        # noise 추정: 하위 30% median 기반 (좀 더 robust)
        k = max(1, int(0.3 * n_frames))
        rms_sorted = np.sort(frame_rms)
        peak_sorted = np.sort(frame_peak)

        noise_rms = float(np.median(rms_sorted[:k]))
        noise_peak = float(np.median(peak_sorted[:k]))

        # 감지 임계값: 너무 빡세지 않게 (초성 살리기)
        thr_rms_hi  = max(noise_rms * 1.8, 0.0015)
        thr_peak_hi = max(noise_peak * 2.0, 0.010)

        thr_rms_lo  = max(noise_rms * 1.2, 0.0010)
        thr_peak_lo = max(noise_peak * 1.3, 0.006)

        # 1) 먼저 "확실한 발화" 프레임 찾기 (hi)
        hit = None
        for i in range(n_frames):
            if (frame_rms[i] >= thr_rms_hi) or (frame_peak[i] >= thr_peak_hi):
                hit = i
                break

        if hit is None:
            # 5초 내에 발화 없음
            metrics["onset_ms"] = -1
            logger.warning(f"⚠️ [AUDIO_GUARD] No speech detected within {MAX_WAIT_S}s")
            return self._fail("FAIL_NO_SPEECH_WITHIN_5S", metrics)

        # 2) backtrack: lo 기준으로 앞 프레임까지 끌어오기 (초성 보호)
        j = hit
        while j > 0 and ((frame_rms[j-1] >= thr_rms_lo) or (frame_peak[j-1] >= thr_peak_lo)):
            j -= 1

        logger.info(f"✅ [AUDIO_GUARD] Speech onset detected at frame {hit} (backtracked to {j})")
        
        onset_idx = j * FRAME_SAMPLES

        # 3) pre-roll 적용
        pre_roll = int(SAMPLE_RATE * PRE_ROLL_MS / 1000)
        start_idx = max(0, onset_idx - pre_roll)

        metrics["onset_ms"] = round(start_idx / SAMPLE_RATE * 1000, 1)

        max_samples = int(MAX_DURATION_S * SAMPLE_RATE)
        samples = raw_samples[start_idx:start_idx + max_samples]
        metrics["speech_dur_s"] = round(len(samples) / SAMPLE_RATE, 3)

        # 디버그용으로 threshold도 metrics에 넣어두면 튜닝 쉬움
        metrics["thr_rms_hi"] = round(thr_rms_hi, 5)
        metrics["thr_peak_hi"] = round(thr_peak_hi, 5)
        metrics["hit_frame"] = int(hit)
        metrics["backtracked_frame"] = int(j)
        
        logger.info(f"✅ [AUDIO_GUARD] Speech clip extracted: onset={metrics['onset_ms']}ms, duration={metrics['speech_dur_s']}s")
        
        # ── Step 1: 품질 가드레일 ──────────────────────────────
        logger.info(f"🎵 [AUDIO_GUARD] Step 2: Checking audio quality")
        fail_reason = self._check_quality(samples, metrics)
        if fail_reason:
            logger.warning(f"⚠️ [AUDIO_GUARD] Quality check failed: {fail_reason}")
            return self._fail(fail_reason, metrics)
        
        logger.info(f"✅ [AUDIO_GUARD] Quality check passed: RMS={metrics.get('rms', 0):.4f}, clip_ratio={metrics.get('clip_ratio', 0):.4f}")

        # ── Step 2: STT (항상 실행) ────────────────────────────
        logger.info(f"🎵 [AUDIO_GUARD] Step 3: Running STT (Speech-to-Text)")
        raw_text = self._run_stt(samples)
        logger.info(f"✅ [AUDIO_GUARD] STT completed: text='{raw_text if raw_text else '(empty)'}'")

        # ── Step 3: 텍스트 판정 ────────────────────────────────
        logger.info(f"🎵 [AUDIO_GUARD] Step 4: Validating text content")
        clip_start_ms = int(start_idx / SAMPLE_RATE * 1000)
        clip_end_ms = clip_start_ms + int(MAX_DURATION_S * 1000)
        clip_audio = audio[clip_start_ms:clip_end_ms]

        result = self._judge_text(raw_text, clip_audio, metrics)
        logger.info(f"🎵 [AUDIO_GUARD] Validation complete: status={result['status']}, reason={result['reason']}")
        return result

    # ──────────────────────────────────────────────────────────────
    # Response builders
    # ──────────────────────────────────────────────────────────────

    def _fail(
        self, reason: str, metrics: Dict, stt_text: str = None
    ) -> Dict[str, Any]:
        out = {
            "status": "FAIL",
            "reason": reason,
            "metrics": metrics,
            "stt_text": stt_text,
        }
        out["user_notice"] = self._user_notice(out)
        logger.info(f"FAIL: {reason} | metrics={metrics}")
        return out

    def _ok(
        self, reason: str, audio: AudioSegment,
        metrics: Dict, stt_text: str = None
    ) -> Dict[str, Any]:
        audio = self._normalize_volume(audio)
        audio = self._trim_silence(audio)

        buf = io.BytesIO()
        audio.export(buf, format="wav")
        wav_bytes = buf.getvalue()

        out = {
            "status": "OK",
            "reason": reason,
            "metrics": metrics,
            "stt_text": stt_text,
            "audio_bytes": wav_bytes,
            "content_type": "audio/wav",
            "file_extension": "wav",
        }
        out["user_notice"] = self._user_notice(out)

        logger.info(
            f"OK: {reason} | stt='{stt_text}' | metrics={metrics} | output={len(wav_bytes)}B"
        )
        return out

    # ──────────────────────────────────────────────────────────────
    # Step 0: Onset 검출
    # ──────────────────────────────────────────────────────────────

    def _find_onset(self, samples: np.ndarray) -> Optional[int]:
        """
        발화 시작점(onset) 검출.

        전략:
        1) 10ms frame RMS + Peak 계산
        2) 하위 energy 기반 noise level 추정
        3) High threshold로 발화 탐지
        4) Low threshold로 backtrack (초성 보호)

        Returns:
            onset sample index (int) or None
        """

        if len(samples) < FRAME_SAMPLES:
            return None

        n_frames = len(samples) // FRAME_SAMPLES
        if n_frames <= 0:
            return None

        # ─────────────────────────
        # frame energy 계산
        # ─────────────────────────
        frame_rms = np.empty(n_frames, dtype=np.float32)
        frame_peak = np.empty(n_frames, dtype=np.float32)

        for i in range(n_frames):
            fr = samples[i*FRAME_SAMPLES:(i+1)*FRAME_SAMPLES]
            frame_rms[i] = np.sqrt(np.mean(fr**2))
            frame_peak[i] = np.max(np.abs(fr))

        # ─────────────────────────
        # noise level 추정 (robust)
        # ─────────────────────────
        k = max(1, int(0.3 * n_frames))  # 하위 30%

        noise_rms = float(np.median(np.sort(frame_rms)[:k]))
        noise_peak = float(np.median(np.sort(frame_peak)[:k]))

        # ─────────────────────────
        # adaptive threshold
        # ─────────────────────────
        thr_rms_hi  = max(noise_rms * 1.8, 0.0015)
        thr_peak_hi = max(noise_peak * 2.0, 0.010)

        thr_rms_lo  = max(noise_rms * 1.2, 0.0010)
        thr_peak_lo = max(noise_peak * 1.3, 0.006)

        # ─────────────────────────
        # 1️⃣ 확실한 발화 찾기
        # ─────────────────────────
        hit = None
        for i in range(n_frames):
            if (frame_rms[i] >= thr_rms_hi) or (frame_peak[i] >= thr_peak_hi):
                hit = i
                break

        if hit is None:
            return None  # 발화 없음

        # ─────────────────────────
        # 2️⃣ backtrack (초성 보호)
        # ─────────────────────────
        j = hit
        while j > 0 and (
            (frame_rms[j-1] >= thr_rms_lo) or
            (frame_peak[j-1] >= thr_peak_lo)
        ):
            j -= 1

        onset_sample = j * FRAME_SAMPLES
        return onset_sample
            
    # ──────────────────────────────────────────────────────────────
    # Step 1: 품질 가드레일
    # ──────────────────────────────────────────────────────────────

    def _check_quality(
        self, samples: np.ndarray, metrics: Dict
    ) -> Optional[str]:
        """품질 체크. 실패 시 FAIL reason 반환, 통과 시 None."""
        # ① 길이 체크 (0.3초 미만 → FAIL)
        duration = len(samples) / SAMPLE_RATE
        if duration < MIN_DURATION_S:
            logger.warning(f"너무 짧음: {duration:.2f}s < {MIN_DURATION_S}s")
            return "FAIL_TOO_SHORT"

        # ② 무음 체크 (RMS < 0.01 → FAIL)
        rms = float(np.sqrt(np.mean(samples ** 2)))
        metrics["rms"] = round(rms, 4)
        if rms < SILENCE_RMS_THRESHOLD:
            logger.warning(f"무음: RMS={rms:.4f}")
            return "FAIL_SILENCE"

        # ③ 클리핑 체크 (>5% → FAIL)
        clip_ratio = 0.0
        if len(samples) > 0:
            clip_ratio = float(
                np.sum(np.abs(samples) > CLIPPING_SAMPLE_THRESHOLD)
                / len(samples)
            )
        metrics["clip_ratio"] = round(clip_ratio, 4)
        if clip_ratio > CLIPPING_RATIO_THRESHOLD:
            logger.warning(f"클리핑: {clip_ratio:.2%}")
            return "FAIL_CLIPPING"

        return None  # 통과

    # ──────────────────────────────────────────────────────────────
    # Step 2: STT
    # ──────────────────────────────────────────────────────────────

    def _run_stt(self, samples: np.ndarray) -> Optional[str]:
        """Transcribe Streaming 호출. 실패 시 None 반환."""
        pcm_int16 = (
            (samples * 32767).clip(-32768, 32767).astype(np.int16)
        )
        pcm_bytes = pcm_int16.tobytes()

        try:
            from app.services.transcribe_service import transcribe_service
            result = transcribe_service.transcribe_pcm(
                pcm_bytes, SAMPLE_RATE
            )
            return result
        except Exception as e:
            logger.debug(f"STT 예외 (무시됨): {e}")
            return None

    # ──────────────────────────────────────────────────────────────
    # Step 3: 텍스트 판정
    # ──────────────────────────────────────────────────────────────

    def _judge_text(
        self, raw_text: Optional[str],
        audio: AudioSegment, metrics: Dict
    ) -> Dict[str, Any]:

        # 기본: LLM 사용 여부 디폴트
        metrics["llm_used"] = False
        metrics["llm_verdict"] = None
        metrics["llm_error"] = None

        # ── (D) STT 빈 텍스트 / 실패 ──
        if not raw_text or not raw_text.strip():
            metrics["stt_text_len"] = 0
            # STT가 없지만 소리는 있음(품질 가드레일 통과) → 버튼 사운드로 OK
            return self._ok("OK_STT_EMPTY", audio, metrics, stt_text=None)

        logger.info(f"STT 원본: '{raw_text}'")

        # 텍스트 정규화
        normalized = self._normalize_text(raw_text)
        metrics["stt_text_len"] = len(normalized)
        logger.info(f"정규화: '{normalized}' (len={len(normalized)})")

        # 정규화 후 빈 문자열 (특수문자만 있었던 경우)
        if not normalized:
            return self._ok("OK_STT_EMPTY", audio, metrics, stt_text=None)

        # 숫자만이면 (ASR 오인식) → 버튼 사운드로 OK
        if normalized.isdigit():
            return self._ok("OK_STT_EMPTY", audio, metrics, stt_text=None)

        # ── (A) Meow-lexicon → OK ──
        if self._is_meow_lexicon(normalized):
            return self._ok("OK_MEOW_LEXICON", audio, metrics, normalized)

        # ── (B) 명백한 문장성 → 즉시 FAIL ──
        if self._is_sentence_like(raw_text, normalized):
            return self._fail("FAIL_TEXT_SENTENCE", metrics, normalized)

        # ── (C) 나머지 전부 → LLM 판정 ──
        logger.info(f"애매한 텍스트 (len={len(normalized)}) → LLM 판정 시도")

        metrics["llm_used"] = True
        try:
            from app.services.audio_llm_service import audio_llm_service
            verdict = audio_llm_service.judge(normalized, raw_text)
            metrics["llm_verdict"] = verdict

            if verdict == "ALLOW":
                # ✅ 여기서 OK_NON_LINGUISTIC 말고 "텍스트 허용" reason으로 분리
                return self._ok("OK_TEXT_ALLOWED", audio, metrics, normalized)
            else:
                # ✅ FAIL_LLM 말고 "금지표현" 의미로 reason 분리
                return self._fail("FAIL_BANNED_TEXT", metrics, normalized)

        except Exception as e:
            # LLM 실패 시 정책 결정:
            # 1) fail-close(보수): FAIL_LLM
            # 2) fail-open(개방): OK_TEXT_ALLOWED
            # 지금은 네 목적상 fail-close 유지할게 (원하면 바꿔줄게)
            metrics["llm_error"] = str(e)
            logger.warning(f"LLM 실패: {e} → FAIL_LLM")
            return self._fail("FAIL_LLM", metrics, normalized)
    # ── 텍스트 판정 유틸 ───────────────────────────────────────

    @staticmethod
    def _normalize_text(text: str) -> str:
        """
        STT 텍스트 정규화.
        - 소문자화
        - 공백/특수문자 제거 (한글·영문·숫자만 유지)
        - 반복 글자 축약 (3회 이상 → 2회)
        """
        text = text.lower().strip()
        text = re.sub(r'[^가-힣a-z0-9]', '', text)
        text = re.sub(r'(.)\1{2,}', r'\1\1', text)
        return text

    @staticmethod
    def _is_meow_lexicon(normalized: str) -> bool:
        """정규화 텍스트가 전부 냐옹 패턴인지 확인."""
        if not normalized:
            return False
        return bool(MEOW_PATTERN.match(normalized))

    @staticmethod
    def _is_sentence_like(raw_text: str, normalized: str) -> bool:
        """
        강한 의미 발화만 문장으로 간주.
        단어 개수/구두점은 사용하지 않음.
        """

        # 너무 긴 발화 → 문장 가능성 높음
        if len(normalized) >= SENTENCE_MAX_NORMALIZED_LEN:
            return True

        return False

    # ──────────────────────────────────────────────────────────────
    # Step 4: 품질 개선
    # ──────────────────────────────────────────────────────────────

    def _normalize_volume(self, audio: AudioSegment) -> AudioSegment:
        """볼륨 정규화 (-20 dBFS 목표, 클리핑 방지)."""
        if audio.dBFS == float('-inf'):
            return audio

        change_db = TARGET_DBFS - audio.dBFS

        # 과증폭 → 클리핑 방지
        if change_db > 0:
            arr = np.array(
                audio.get_array_of_samples(), dtype=np.float32
            ) / (2 ** 15)
            peak = float(np.max(np.abs(arr)))
            if peak > 0:
                max_gain_db = 20 * np.log10(0.95 / peak)
                change_db = min(change_db, max_gain_db)

        normalized = audio.apply_gain(change_db)
        logger.info(
            f"볼륨 정규화: {audio.dBFS:.1f} → {normalized.dBFS:.1f} dBFS "
            f"({change_db:+.1f} dB)"
        )
        return normalized

    def _trim_silence(self, audio: AudioSegment) -> AudioSegment:
        """앞뒤 무음 제거 (초성 보호 패딩만 남기고, 긴 무음은 제거)."""
        from pydub.silence import detect_leading_silence

        lead_ms = detect_leading_silence(
            audio,
            silence_threshold=TRIM_SILENCE_THRESH_DB,
            chunk_size=10,
        )
        trail_ms = detect_leading_silence(
            audio.reverse(),
            silence_threshold=TRIM_SILENCE_THRESH_DB,
            chunk_size=10,
        )

        # 너무 짧은 무음은 트림하지 않음 (초성/자음 보호)
        if lead_ms < MIN_TRIM_MS:
            lead_ms = 0
        if trail_ms < MIN_TRIM_MS:
            trail_ms = 0

        # ✅ 핵심: 첫 발화 직전 "MIN_KEEP_HEAD_MS"만 남기고 앞무음 제거
        # 예: lead=1600ms면 start=1600-200=1400ms부터 자름
        start = max(0, lead_ms - MIN_KEEP_HEAD_MS)

        # 뒤는 margin을 조금 줘도 되고, 깔끔하게 자르고 싶으면 +0으로
        end = len(audio) - trail_ms
        end = min(end + TRIM_MARGIN_MS, len(audio))

        # 너무 짧아지는 것 방지
        end = max(end, start + 150)

        trimmed = audio[start:end]

        if len(trimmed) < len(audio):
            logger.info(
                f"무음 트리밍: {len(audio)}ms → {len(trimmed)}ms "
                f"(lead={lead_ms}ms, trail={trail_ms}ms, start={start}ms)"
            )
        return trimmed
    def _user_notice(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        사용자에게 노출할 메시지.
        - title: 토스트/다이얼로그 제목
        - message: 본문
        - action: 사용자가 바로 할 수 있는 조치
        - severity: "info" | "warning" | "error"
        """
        reason = result.get("reason", "UNKNOWN")

        # ✅ OK 케이스
        if result.get("status") == "OK":
            return {
                "severity": "info",
                "title": "등록 완료",
                "message": "냐옹! 소리가 등록됐다냥",
                "action": None,
            }

        # ❌ FAIL 케이스
        if reason == "FAIL_DECODE":
            return {
                "severity": "error",
                "title": "업로드 실패",
                "message": "다시 한번 녹음해달라냥",
                "action": None,
            }
        
        # 기본 FAIL 메시지
        return {
            "severity": "error",
            "title": "업로드 실패",
            "message": "다시 한번 녹음해달라냥",
            "action": None,
        }
# ═══════════════════════════════════════════════════════════════════════
# Global instance
# ═══════════════════════════════════════════════════════════════════════

audio_guard = AudioGuard()
