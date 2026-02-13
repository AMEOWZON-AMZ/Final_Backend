from fastapi import FastAPI
from pydantic import BaseModel
import firebase_admin
from firebase_admin import credentials, messaging

app = FastAPI()

# ✅ 서비스 계정 키 파일 경로 (파일명 맞춰서 수정 가능)
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

# ✅ 테스트용: user -> token 1개 저장(간단 버전)
TOKENS: dict[str, str] = {}


class RegisterReq(BaseModel):
    user: str   # 예: "phone" / "emu"
    token: str


class SendReq(BaseModel):
    to: str     # 예: "phone" / "emu"
    title: str
    body: str


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/register")
def register(req: RegisterReq):
    TOKENS[req.user] = req.token
    return {"ok": True, "user": req.user}


@app.post("/send")
def send(req: SendReq):
    token = TOKENS.get(req.to)
    if not token:
        return {"ok": False, "reason": f"no token for {req.to}", "known_users": list(TOKENS.keys())}

    msg = messaging.Message(
        notification=messaging.Notification(
            title=req.title,
            body=req.body,
        ),
        token=token,
    )

    message_id = messaging.send(msg)
    return {"ok": True, "message_id": message_id, "to": req.to}
