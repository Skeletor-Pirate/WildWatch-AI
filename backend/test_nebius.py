import os
import sys
import asyncio
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

NEBIUS_API_KEY = os.getenv("NEBIUS_API_KEY", "")
NEBIUS_BASE_URL = os.getenv("NEBIUS_BASE_URL", "https://api.tokenfactory.nebius.com/v1/")
VLM_MODEL_ID = os.getenv("VLM_MODEL_ID", "meta-llama/Llama-3.2-11B-Vision-Instruct")
LLM_MODEL_ID = os.getenv("LLM_MODEL_ID", "meta-llama/Llama-3.1-70B-Instruct")

async def test_nebius_connection():
    print("=" * 65)
    print("           NEBIUS AI CLOUD CONNECTION DIAGNOSTIC")
    print("=" * 65)
    print(f"Base URL : {NEBIUS_BASE_URL}")
    print(f"LLM Model: {LLM_MODEL_ID}")
    print(f"VLM Model: {VLM_MODEL_ID}")

    if not NEBIUS_API_KEY or NEBIUS_API_KEY == "your_nebius_api_key_here":
        print("\n[!] ERROR: No valid NEBIUS_API_KEY found in your .env file!")
        print("    1. Sign up at https://studio.nebius.ai/")
        print("    2. Generate an API Key under Account -> API Keys")
        print("    3. Paste it into .env as NEBIUS_API_KEY=your_key")
        return

    masked_key = NEBIUS_API_KEY[:6] + "..." + NEBIUS_API_KEY[-4:]
    print(f"API Key  : {masked_key}")
    print("\n[1/2] Testing Text LLM Agent Endpoint...")

    client = AsyncOpenAI(base_url=NEBIUS_BASE_URL, api_key=NEBIUS_API_KEY)

    try:
        response = await client.chat.completions.create(
            model=LLM_MODEL_ID,
            messages=[
                {"role": "system", "content": "You are WildWatch AI."},
                {"role": "user", "content": "Respond with 'CONNECTED' and your model architecture."}
            ],
            max_tokens=50,
            temperature=0.1
        )
        reply = response.choices[0].message.content.strip()
        print(f"  [+] LLM Success! Response: {reply}")
    except Exception as e:
        print(f"  [-] LLM Test Failed: {e}")

    print("\n[2/2] Testing Vision (VLM) Model Endpoint with sample image...")
    # Public sample image of wildlife
    sample_image_url = "https://raw.githubusercontent.com/pjreddie/darknet/master/data/horses.jpg"

    try:
        vlm_resp = await client.chat.completions.create(
            model=VLM_MODEL_ID,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "What animals are in this image? Answer in 5 words or less."},
                        {"type": "image_url", "image_url": {"url": sample_image_url}}
                    ]
                }
            ],
            max_tokens=50,
            temperature=0.1
        )
        vlm_reply = vlm_resp.choices[0].message.content.strip()
        print(f"  [+] VLM Success! Response: {vlm_reply}")
        print("\n>>> ALL NEBIUS CLOUD ENDPOINTS ARE OPERATIONAL AND READY!")
    except Exception as e:
        print(f"  [-] VLM Test Failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_nebius_connection())
