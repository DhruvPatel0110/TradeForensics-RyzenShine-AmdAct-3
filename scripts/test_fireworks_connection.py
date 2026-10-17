"""
TradeForensics — Fireworks AI / AMD Instinct Hardware Connection Smoke Test
Verifies that the Fireworks LLM client initializes, handles schema formatting,
and executes inference (live or simulated AMD Instinct fallback) cleanly.
"""

import sys
import json
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.app.core.config import settings
from backend.app.llm.fireworks_client import FireworksLLMClient

def main():
    print("=" * 70)
    print("TradeForensics — AMD Instinct Hardware Bridge Verification")
    print(f"Target Cluster: Fireworks AI / AMD Instinct MI300X Accelerators")
    print(f"Target Model: {settings.FIREWORKS_MODEL}")
    print(f"Base URL: {settings.FIREWORKS_BASE_URL}")
    print("=" * 70)

    client = FireworksLLMClient()
    test_prompt = (
        "ISSUE: Seller 1ca7077d has +47.2% negative reviews in Southeast corridor.\n"
        "Late delivery rate: 22.4% (vs 8.1% baseline). Sample size: 115 orders.\n"
        "Provide a structured operational action plan matching the JSON schema."
    )

    print("\n[1/2] Dispatching prompt to AMD Instinct inference client...")
    res = client.generate_json(test_prompt)

    print("\n[2/2] Validating returned JSON structure:")
    print("-" * 50)
    print(json.dumps(res, indent=2, ensure_ascii=False))
    print("-" * 50)

    # Assert basic required fields
    assert "summary" in res, "Missing 'summary' in response"
    assert "severity" in res, "Missing 'severity' in response"
    assert "recommended_actions" in res, "Missing 'recommended_actions' in response"
    
    print("\nSUCCESS: AMD Instinct LLM Client verified with valid structured output.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
