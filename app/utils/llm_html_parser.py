import json
import logging
from typing import Dict, List
from litellm import acompletion

from app.config.settings import settings

logger = logging.getLogger("course_scraper.llm_html_parser")

class LlmHtmlParser:
    def __init__(self):
        self.model = settings.LLM_MODEL

    def _create_messages(self, html: str, prompts: List[str], expect_array: bool = False) -> List[Dict]:
        """Create message list for LLM prompt"""
        system_msg = (
            "You are a precise HTML parser that extracts information from HTML content. "
            f"Always return valid JSON {'arrays containing objects' if expect_array else 'object'} "
            "with the exact specified fields. If a field is not found, use null instead of empty string."
        )
        
        messages = [{"role": "system", "content": system_msg}]
        messages.extend([{"role": "user", "content": prompt} for prompt in prompts])
        messages.append({"role": "user", "content": f"HTML content:\n{html}"})
        return messages

    async def _parse_html(self, html: str, prompts: List[str], expect_array: bool = False) -> Dict | List[Dict]:
        """Generic HTML parsing method that handles both single objects and lists"""
        try:
            response = await acompletion(
                model=self.model,
                messages=self._create_messages(html, prompts, expect_array),
                response_format={"type": "json_object"},
                temperature=0,
                max_tokens=4000,
                api_key=settings.MISTRAL_API_KEY,
                api_base="https://api.mistral.ai/v1"
            )
            
            parsed_data = json.loads(response.choices[0].message.content)
            expected_type = list if expect_array else dict
            if not isinstance(parsed_data, expected_type):
                raise Exception(f"Unexpected response format: {type(parsed_data)}")
            
            return parsed_data
        except Exception as e:
            logger.error(f"Error parsing HTML with Mistral: {str(e)}")
            return [] if expect_array else {}

    async def parse_html_to_json(self, html: str, prompts: List[str]) -> Dict:
        """Parse HTML content into a JSON object using GPT-4"""
        return await self._parse_html(html, prompts)

    async def parse_html_to_json_list(self, html: str, prompts: List[str]) -> List[Dict]:
        """Parse HTML content into a list of JSON objects using GPT-4"""
        return await self._parse_html(html, prompts, expect_array=True) 