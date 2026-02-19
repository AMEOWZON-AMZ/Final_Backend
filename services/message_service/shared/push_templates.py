import random

MESSAGE_PUSH_TEMPLATES = [
    ("🐱 새 쪽지가 도착했어요", "고양이가 전해준 말: {message}"),
    ("💌 쪽지 도착", "누군가 이렇게 말했어요: {message}"),
    ("📮 받은 편지함 업데이트", "새로운 쪽지가 왔어요: {message}"),
    ("🐾 친구의 한 마디", "도착한 메시지: {message}"),
    ("🌙 조용히 도착한 편지", "이런 말이 도착했어요: {message}"),
    ("✨ 새로운 안부", "쪽지 내용: {message}"),
    ("🎀 당신을 향한 한 줄", "받은 메시지: {message}"),
    ("🐈 고양이 배달 완료", "전달된 말: {message}"),
    ("💭 누군가 당신을 떠올렸어요", "메시지 미리보기: {message}"),
    ("📬 새 메시지 알림", "읽지 않은 쪽지: {message}"),
]


HEART_PUSH_TEMPLATES = [
    ("❤️ 하트가 도착했어요", "{nickname}님이 하트를 보냈어요"),
    ("🐱 고양이가 하트를 들고 왔어요", "{nickname}님이 마음을 전했어요"),
    ("💖 따뜻한 신호 도착", "{nickname}님이 당신을 응원해요"),
    ("🐾 작은 응원", "{nickname}님이 하트를 남겼어요"),
    ("🌷 안부 하트", "{nickname}님이 조용히 하트를 보냈어요"),
    ("💓 친구의 하트", "{nickname}님이 당신을 떠올렸어요"),
    ("✨ 오늘의 응원", "{nickname}님이 마음을 보냈어요"),
    ("🎀 마음 전달 완료", "{nickname}님이 하트를 전했어요"),
    ("🐈 고양이 배달 알림", "{nickname}님에게서 하트가 도착했어요"),
    ("💗 따뜻한 알림", "{nickname}님이 작은 마음을 남겼어요"),
]



def _message_preview(message_body: str) -> str:
    text = (message_body or "").strip()
    if not text:
        return "(no content)"
    if len(text) > 80:
        return f"{text[:77]}..."
    return text


def random_message_push_text(message_body: str) -> tuple[str, str]:
    title, body_template = random.choice(MESSAGE_PUSH_TEMPLATES)
    return title, body_template.format(message=_message_preview(message_body))


def random_heart_push_text() -> tuple[str, str]:
    return random.choice(HEART_PUSH_TEMPLATES)
