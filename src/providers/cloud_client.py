"""Cloud LLM Client supporting OpenAI, Anthropic, and Google Gemini with graceful fallback."""

import json
import os
from typing import Dict, Any, Optional
from src.providers.base_client import BaseLLMClient
from src.providers.mock_client import MockSimulatedLLMClient

class CloudLLMClient(BaseLLMClient):
    """Integrates with Cloud LLM APIs (OpenAI / Anthropic / Gemini)."""

    def __init__(self, provider: str = "openai", api_key: str = "", model: Optional[str] = None):
        self.provider = provider.lower()
        self.api_key = api_key or os.getenv(f"{self.provider.upper()}_API_KEY", "")
        self.model = model
        self.fallback = MockSimulatedLLMClient()

    def generate(self, prompt: str, system_prompt: str = "", temperature: float = 0.0) -> str:
        if not self.api_key:
            return self.fallback.generate(prompt, system_prompt, temperature)

        try:
            if self.provider == "openai":
                from openai import OpenAI
                client = OpenAI(api_key=self.api_key)
                response = client.chat.completions.create(
                    model=self.model or "gpt-4o",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=temperature
                )
                return response.choices[0].message.content or ""

            elif self.provider == "anthropic":
                import anthropic
                client = anthropic.Anthropic(api_key=self.api_key)
                response = client.messages.create(
                    model=self.model or "claude-3-5-sonnet-20241022",
                    system=system_prompt,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temperature,
                    max_tokens=4096
                )
                return response.content[0].text

            elif self.provider == "gemini":
                # Direct REST call using X-goog-api-key
                import urllib.request
                import json
                model_name = self.model or "gemini-3.8-flash"
                if not model_name.startswith("models/"):
                    endpoint_model = f"models/{model_name}"
                else:
                    endpoint_model = model_name
                url = f"https://generativelanguage.googleapis.com/v1beta/{endpoint_model}:generateContent"
                payload = {
                    "contents": [{"parts": [{"text": f"{system_prompt}\n\n{prompt}".strip()}]}],
                    "generationConfig": {"temperature": temperature}
                }
                req = urllib.request.Request(
                    url,
                    data=json.dumps(payload).encode("utf-8"),
                    headers={"Content-Type": "application/json", "X-goog-api-key": self.api_key}
                )
                with urllib.request.urlopen(req, timeout=10.0) as resp:
                    res_data = json.loads(resp.read().decode("utf-8"))
                    candidates = res_data.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        if parts:
                            return parts[0].get("text", "").strip()
                return ""

        except Exception as e:
            # Graceful fallback to deterministic mock if API call fails or quota exceeded
            print(f"[Warning] Cloud LLM ({self.provider}) error: {e}. Falling back to deterministic client.")
            return self.fallback.generate(prompt, system_prompt, temperature)

        return self.fallback.generate(prompt, system_prompt, temperature)

    def generate_json(self, prompt: str, system_prompt: str = "") -> Dict[str, Any]:
        text_resp = self.generate(
            prompt=f"{prompt}\n\nIMPORTANT: Respond with pure JSON only, without markdown wrapping.",
            system_prompt=system_prompt,
            temperature=0.0
        )
        try:
            # Try to strip markdown ```json ... ``` blocks
            cleaned = text_resp.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("\n", 1)[1]
                if cleaned.endswith("```"):
                    cleaned = cleaned.rsplit("```", 1)[0]
            return json.loads(cleaned)
        except Exception:
            return self.fallback.generate_json(prompt, system_prompt)
