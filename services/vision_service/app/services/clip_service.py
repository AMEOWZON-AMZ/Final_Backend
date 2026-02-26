import io

import open_clip
import torch
from PIL import Image, UnidentifiedImageError

from app.core.config import settings


def _prompts(topic: str) -> list[str]:
    return [
        f"a photo of {topic}",
        f"a picture of {topic}",
        f"{topic} in a photo",
    ]


class ClipService:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        model, _, preprocess = open_clip.create_model_and_transforms(
            settings.model_name,
            pretrained=settings.pretrained,
        )
        self.model = model.to(self.device)
        self.model.eval()
        self.preprocess = preprocess
        self.tokenizer = open_clip.get_tokenizer(settings.model_name)

    @staticmethod
    def normalize_image(image_bytes: bytes) -> bytes:
        try:
            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        except (UnidentifiedImageError, OSError) as exc:
            raise ValueError("Only valid image files can be uploaded") from exc

        output = io.BytesIO()
        image.save(output, format="JPEG", quality=95)
        return output.getvalue()

    def score_topic(self, image_bytes: bytes, topic: str) -> float:
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        image_tensor = self.preprocess(image).unsqueeze(0).to(self.device)
        prompts = _prompts(topic)
        text_tokens = self.tokenizer(prompts).to(self.device)
        with torch.no_grad():
            image_features = self.model.encode_image(image_tensor)
            text_features = self.model.encode_text(text_tokens)
            image_features = image_features / image_features.norm(dim=-1, keepdim=True)
            text_features = text_features / text_features.norm(dim=-1, keepdim=True)
            sims = (image_features @ text_features.T).squeeze(0)
        return float(sims.max().item())
