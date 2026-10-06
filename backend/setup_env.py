"""Helper script for configuring .env interactively."""

import os
import re
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent
ENV_FILE = BACKEND_DIR / ".env"
EXAMPLE_FILE = BACKEND_DIR / ".env.example"


def check_and_prompt_api_key() -> None:
    # 1. Ensure .env exists
    if not ENV_FILE.exists():
        if EXAMPLE_FILE.exists():
            content = EXAMPLE_FILE.read_text(encoding="utf-8")
            ENV_FILE.write_text(content, encoding="utf-8")
            print("[+] Da tao file .env tu .env.example")
        else:
            ENV_FILE.write_text("GEMINI_API_KEY=\nLLM_PROVIDER=gemini\n", encoding="utf-8")

    # 2. Check current API key
    content = ENV_FILE.read_text(encoding="utf-8")
    match = re.search(r"^GEMINI_API_KEY=(.*)$", content, re.MULTILINE)
    current_key = match.group(1).strip() if match else ""

    is_missing = not current_key or "your-gemini-api-key" in current_key.lower()

    if is_missing:
        print("\n" + "=" * 60)
        print(" [!] CHUA CAU HINH GEMINI API KEY")
        print("=" * 60)
        print("Lay API key mien phi tai: https://aistudio.google.com/apikey")
        print()
        try:
            user_key = input(">> Vui long dan GEMINI_API_KEY cua ban (hoac an Enter de bo qua): ").strip()
        except (EOFError, KeyboardInterrupt):
            user_key = ""

        if user_key:
            if "GEMINI_API_KEY=" in content:
                content = re.sub(
                    r"^GEMINI_API_KEY=.*$",
                    f"GEMINI_API_KEY={user_key}",
                    content,
                    flags=re.MULTILINE,
                )
            else:
                content += f"\nGEMINI_API_KEY={user_key}\n"
            ENV_FILE.write_text(content, encoding="utf-8")
            print("[+] Da luu GEMINI_API_KEY vao file .env thanh cong!\n")
        else:
            print("[i] Bo qua. Ban co the sua file backend\\.env sau.\n")
    else:
        print(f"[+] GEMINI_API_KEY da duoc cau hinh (ket thuc bang ...{current_key[-4:] if len(current_key) >= 4 else '***'}).")


if __name__ == "__main__":
    check_and_prompt_api_key()
