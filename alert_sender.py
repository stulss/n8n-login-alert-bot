# alert_sender.py — 과제 1: 로그인 경보를 n8n Webhook 으로 전송하는 파이썬 전송기
"""
경보 목록을 만들어 n8n Webhook 으로 POST 한다.

실행:
    python alert_sender.py

사전 준비:
    .env.example 을 .env 로 복사한 뒤 STUDENT 와 N8N_WEBHOOK_URL 을 채운다.

기대 출력:
    [n8n] POST http://localhost:5678/webhook/... -> 200
"""
import os
import sys
from pathlib import Path

import requests  # pip install requests
from dotenv import load_dotenv

# ── 설정: 같은 폴더의 .env 에서 읽는다 (.env.example 참고) ──
load_dotenv(Path(__file__).resolve().parent / ".env", override=True)

STUDENT = os.getenv("STUDENT", "").strip()  # 채점 증적 — 본인 식별자
N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL", "").strip()
TIMEOUT = int(os.getenv("N8N_TIMEOUT", 10))  # 초

# 거부(레벨 10 이상)와 허용(레벨 10 미만)이 모두 섞이도록 구성한다.
# ip 는 예약 대역(1.2.3.x, 192.168.x.x)만 사용 — 실제 개인 서버로 보내지 않는다.
ALERTS = [
    {"ip": "1.2.3.114", "level": 10, "rule": "5712"},   # 레벨 10 -> 거부(High) 기대
    {"ip": "192.168.0.10", "level": 3, "rule": "5710"},  # 레벨 3  -> 허용(Low) 기대
]


def build_payload(student, alerts):
  return {"student": student, "alerts": alerts}


def send_to_n8n(url, payload):
  """n8n Webhook 으로 전송. 실패해도 프로그램이 죽지 않고 메시지만 출력한다."""
  try:
    res = requests.post(url, json=payload, timeout=TIMEOUT)
    print(f"[n8n] POST {url} -> {res.status_code}")
    if res.text:
      print(f"[n8n] response: {res.text[:300]}")
    return res.status_code
  except requests.RequestException as e:
    print(f"[n8n] 전송 실패: {e}", file=sys.stderr)
    return None


def main():
  missing = [
      name
      for name, value in (("STUDENT", STUDENT), ("N8N_WEBHOOK_URL", N8N_WEBHOOK_URL))
      if not value
  ]
  if missing:
    print(
        f"[설정 오류] .env 에 {', '.join(missing)} 값이 없습니다. "
        "`.env.example` 을 `.env` 로 복사한 뒤 채우세요.",
        file=sys.stderr,
    )
    return 1

  payload = build_payload(STUDENT, ALERTS)
  print(f"[alert_sender] student={STUDENT} alerts={len(ALERTS)}건 전송 시도")
  status = send_to_n8n(N8N_WEBHOOK_URL, payload)
  if status is None:
    return 1
  return 0 if status == 200 else 1


if __name__ == "__main__":
  sys.exit(main())
