import io
import logging
import os
import re
import uuid
from datetime import datetime, timezone

import boto3
import open_clip
import torch
from botocore.exceptions import BotoCoreError, ClientError
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from PIL import Image, UnidentifiedImageError


app = FastAPI(title="vision-validate-service")
logger = logging.getLogger("vision_service")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")


S3_BUCKET = os.getenv("S3_BUCKET", "").strip()
S3_PREFIX = os.getenv("S3_PREFIX", "topics").strip("/") or "topics"
AWS_REGION = os.getenv("AWS_REGION", "ap-northeast-2").strip()
THRESHOLD = float(os.getenv("THRESHOLD", "0.22"))
MODEL_NAME = os.getenv("MODEL_NAME", "ViT-B-32").strip()
PRETRAINED = os.getenv("PRETRAINED", "laion2b_s34b_b79k").strip()
MAX_BYTES = int(os.getenv("MAX_BYTES", str(10 * 1024 * 1024)))

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
MODEL = None
PREPROCESS = None
TOKENIZER = None
S3_CLIENT = None


def _safe_topic(topic: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9-_ ]+", "", topic).strip().lower()
    cleaned = re.sub(r"\s+", "-", cleaned)
    return cleaned or "untitled-topic"


def _get_prompts(topic: str) -> list[str]:
    return [
        f"a photo of {topic}",
        f"a picture of {topic}",
        f"{topic} in a photo",
    ]


def _load_model_once() -> None:
    global MODEL, PREPROCESS, TOKENIZER
    model, _, preprocess = open_clip.create_model_and_transforms(
        MODEL_NAME,
        pretrained=PRETRAINED,
    )
    tokenizer = open_clip.get_tokenizer(MODEL_NAME)
    model = model.to(DEVICE)
    model.eval()
    MODEL = model
    PREPROCESS = preprocess
    TOKENIZER = tokenizer
    logger.info("CLIP model loaded model_name=%s pretrained=%s device=%s", MODEL_NAME, PRETRAINED, DEVICE)


def _init_s3_client() -> None:
    global S3_CLIENT
    kwargs = {"region_name": AWS_REGION} if AWS_REGION else {}
    S3_CLIENT = boto3.client("s3", **kwargs)


@app.on_event("startup")
def startup() -> None:
    _load_model_once()
    _init_s3_client()


@app.get("/health")
def health() -> dict:
    return {"ok": True}


def _to_rgb_jpeg(image_bytes: bytes) -> bytes:
    try:
        image = Image.open(io.BytesIO(image_bytes))
    except UnidentifiedImageError as exc:
        raise HTTPException(status_code=400, detail="이미지 파일만 업로드할 수 있습니다") from exc
    except OSError as exc:
        raise HTTPException(status_code=400, detail="손상된 이미지 파일입니다") from exc

    rgb = image.convert("RGB")
    output = io.BytesIO()
    rgb.save(output, format="JPEG", quality=95)
    return output.getvalue()


def _compute_similarity_score(image_jpeg_bytes: bytes, topic: str) -> float:
    image = Image.open(io.BytesIO(image_jpeg_bytes)).convert("RGB")
    image_tensor = PREPROCESS(image).unsqueeze(0).to(DEVICE)

    prompts = _get_prompts(topic)
    text_tokens = TOKENIZER(prompts).to(DEVICE)

    with torch.no_grad():
        image_features = MODEL.encode_image(image_tensor)
        text_features = MODEL.encode_text(text_tokens)
        image_features = image_features / image_features.norm(dim=-1, keepdim=True)
        text_features = text_features / text_features.norm(dim=-1, keepdim=True)
        similarities = image_features @ text_features.T

    return float(similarities.mean().item())


def _build_s3_key(topic: str) -> str:
    day = datetime.now(timezone.utc).date().isoformat()
    safe_topic = _safe_topic(topic)
    image_id = uuid.uuid4().hex
    return f"{S3_PREFIX}/{day}/{safe_topic}/{image_id}.jpg"


@app.post("/validate-upload")
async def validate_upload(file: UploadFile = File(...), topic: str = Form(...)) -> dict:
    # if not S3_BUCKET:
    #     raise HTTPException(status_code=500, detail="S3_BUCKET 환경변수가 필요합니다")

    if not topic or not topic.strip():
        raise HTTPException(status_code=400, detail="topic은 필수입니다")
    topic = topic.strip()

    if file.content_type and not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="이미지 파일만 업로드할 수 있습니다")

    raw = await file.read(MAX_BYTES + 1)
    if not raw:
        raise HTTPException(status_code=400, detail="빈 파일은 업로드할 수 없습니다")
    if len(raw) > MAX_BYTES:
        raise HTTPException(status_code=413, detail="파일 크기 제한을 초과했습니다")

    jpeg_bytes = _to_rgb_jpeg(raw)
    score = _compute_similarity_score(jpeg_bytes, topic)
    logger.info("validate topic=%s score=%.4f threshold=%.4f", topic, score, THRESHOLD)

    if score < THRESHOLD:
        return JSONResponse(
            status_code=422,
            content={
                "ok": False,
                "score": round(score, 4),
                "threshold": THRESHOLD,
                "message": "해당 사진은 오늘의 주제와 적합하지 않습니다",
            },
        )

    # s3_key = _build_s3_key(topic)
    # try:
    #     S3_CLIENT.put_object(
    #         Bucket=S3_BUCKET,
    #         Key=s3_key,
    #         Body=jpeg_bytes,
    #         ContentType="image/jpeg",
    #     )
    # except (ClientError, BotoCoreError) as exc:
    #     logger.exception("s3 upload failed key=%s", s3_key)
    #     return JSONResponse(
    #         status_code=502,
    #         content={
    #             "ok": False,
    #             "score": round(score, 4),
    #             "threshold": THRESHOLD,
    #             "message": "저장에 실패했습니다",
    #         },
    #     )
    # logger.info("upload success topic=%s score=%.4f threshold=%.4f s3_key=%s", topic, score, THRESHOLD, s3_key)

    logger.info("validate pass topic=%s score=%.4f threshold=%.4f", topic, score, THRESHOLD)
    return {
        "ok": True,
        "score": round(score, 4),
        "threshold": THRESHOLD,
        # "bucket": S3_BUCKET,
        # "key": s3_key,
        # "url": f"s3://{S3_BUCKET}/{s3_key}",
        "message": "주제 적합성 통과",
    }
