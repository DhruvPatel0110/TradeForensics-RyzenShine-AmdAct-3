"""
TradeForensics — Smoke Test Script for LLM Connection
Team: RyzenShine | AMD Developer Hackathon ACT III
"""

import sys
import time
import json
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.app.core.config import settings
from backend.app.llm.client import get_llm_client, GroqLLMClient, MockLLMClient

def test_connection():
    print("=" * 70)
    print("TRADEFORENSICS — LLM CONNECTIVITY SMOKE TEST")
    print(f"Project: {settings.PROJECT_NAME} | Team: {settings.TEAM_NAME}")
    print("=" * 70)
    print(f"[Config] Configured Provider: {settings.LLM_PROVIDER}")
    print(f"[Config] Groq Model:         {settings.GROQ_MODEL}")
    
    masked_key = (
        settings.GROQ_API_KEY[:6] + "..." + settings.GROQ_API_KEY[-4:]
        if len(settings.GROQ_API_KEY) > 10 and not settings.GROQ_API_KEY.startswith("gsk_placeholder")
        else "Not Set / Placeholder"
    )
    print(f"[Config] Groq API Key:       {masked_key}")
    print("-" * 70)

    client = get_llm_client()
    client_name = client.__class__.__name__
    print(f"[Status] Active Client:      {client_name}")

    test_prompt = (
        "Analyze the following evidence and return a JSON diagnosis:\n"
        "Category: 'relogios_presentes' (Watches & Gifts)\n"
        "Total Orders: 540\n"
        "Late Delivery Rate: 29.5% (Store Baseline: 12.1%)\n"
        "Top Customer Complaint Theme: 'Logistics / Package Damaged'\n"
        "Key Review Quote: 'O relogio veio quebrado e a caixa amassada.'"
    )

    print("\n[Action] Sending diagnostic probe request...")
    start_time = time.time()
    try:
        result = client.generate_json(test_prompt)
        elapsed = time.time() - start_time
        print(f"[Success] Response received in {elapsed:.2f} seconds!")
        print("\n--- Parsed JSON Output ---")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        print("---------------------------")
        
        if isinstance(client, MockLLMClient):
            print("\n[NOTE] Currently running in deterministic Mock mode.")
            print("To activate live Groq API inference:")
            print("1. Get your free key at: https://console.groq.com")
            print("2. Paste it in e:\\amd-dev-hktn\\.env (GROQ_API_KEY=gsk_...)")
            print("3. Re-run: python scripts/test_groq_connection.py")
        else:
            print("\n[SUCCESS] Live Groq API inference is fully operational!")
            
    except Exception as e:
        print(f"[ERROR] Inference test failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_connection()
