import json
import logging
from typing import Dict, List
from litellm import acompletion
import tiktoken

from app.config.settings import settings

logger = logging.getLogger("course_scraper.llm_html_parser")

class LlmHtmlParser:
    def __init__(self):
        self.model = settings.LLM_MODEL
        self.encoding = tiktoken.get_encoding("cl100k_base")  # Mistral uses cl100k_base encoding
        self.max_tokens = 2500  # Mistral has 8k context, leave room for prompt and response
        
    def _count_tokens(self, text: str) -> int:
        """Count the number of tokens in a text string using Mistral's encoding"""
        return len(self.encoding.encode(text))
    
    def _split_html_into_chunks(self, html: str) -> List[str]:
        """Split HTML into chunks that fit within token limits"""
        chunks = []
        current_chunk = []
        current_token_count = 0
        
        # Split by closing tags to maintain HTML structure
        elements = html.split('>')
        
        for element in elements:
            if not element.strip():
                continue
                
            element = element + '>'  # Add back the delimiter
            element_tokens = self._count_tokens(element)
            
            if current_token_count + element_tokens > self.max_tokens:
                # Current chunk is full, start a new one
                if current_chunk:
                    chunks.append(''.join(current_chunk))
                current_chunk = [element]
                current_token_count = element_tokens
            else:
                current_chunk.append(element)
                current_token_count += element_tokens
        
        # Add the last chunk if it exists
        if current_chunk:
            chunks.append(''.join(current_chunk))
            
        return chunks

    def _create_messages(self, html: str, prompts: List[str], expect_array: bool = False, is_chunk: bool = False, chunk_index: int = 0, total_chunks: int = 1) -> List[Dict]:
        """Create message list for LLM prompt"""
        system_msg = (
            "You are a precise HTML parser that extracts information from HTML content. "
            f"Always return valid JSON {'arrays containing objects' if expect_array else 'object'} "
            "with the exact specified fields. If a field is not found, use null instead of empty string."
        )
        
        if is_chunk:
            system_msg += (
                f" This is chunk {chunk_index + 1} of {total_chunks}. "
                "Process this chunk independently and return any complete information found. "
                "Partial or incomplete information should be omitted."
            )
        
        messages = [{"role": "system", "content": system_msg}]
        messages.extend([{"role": "user", "content": prompt} for prompt in prompts])
        messages.append({"role": "user", "content": f"HTML content:\n{html}"})
        return messages

    async def _parse_html_chunk(self, html: str, prompts: List[str], expect_array: bool = False, chunk_index: int = 0, total_chunks: int = 1) -> Dict | List[Dict]:
        """Parse a single chunk of HTML"""
        try:
            html_preview = html[:100] + "..." if len(html) > 100 else html
            logger.info(f"Processing chunk {chunk_index + 1}/{total_chunks}, Preview: {html_preview}")
            
            response = await acompletion(
                model=self.model,
                messages=self._create_messages(html, prompts, expect_array, True, chunk_index, total_chunks),
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
            
            preview = str(parsed_data)[:50] + "..." if len(str(parsed_data)) > 50 else str(parsed_data)
            logger.info(f"Chunk {chunk_index + 1} Response: {preview}")
            
            return parsed_data
        except Exception as e:
            logger.error(f"Error parsing HTML chunk {chunk_index + 1}: {str(e)}")
            return [] if expect_array else {}

    async def _parse_html(self, html: str, prompts: List[str], expect_array: bool = False) -> Dict | List[Dict]:
        """Generic HTML parsing method that handles both single objects and lists"""
        try:
            # Check if HTML needs to be chunked
            total_tokens = self._count_tokens(html)
            if total_tokens > self.max_tokens:
                logger.info(f"HTML content too large ({total_tokens} tokens), splitting into chunks")
                chunks = self._split_html_into_chunks(html)
                logger.info(f"Split into {len(chunks)} chunks")
                
                # Process each chunk
                results = []
                for i, chunk in enumerate(chunks):
                    chunk_result = await self._parse_html_chunk(chunk, prompts, expect_array, i, len(chunks))
                    if expect_array:
                        results.extend(chunk_result)
                    else:
                        # For dictionaries, merge the results
                        results.append(chunk_result)
                
                if expect_array:
                    return results
                else:
                    # Merge dictionaries, later values overwrite earlier ones
                    final_result = {}
                    for r in results:
                        final_result.update(r)
                    return final_result
            else:
                # If HTML is small enough, process it directly
                return await self._parse_html_chunk(html, prompts, expect_array)
                
        except Exception as e:
            logger.error(f"Error parsing HTML with Mistral: {str(e)}")
            return [] if expect_array else {}

    async def parse_html_to_json(self, html: str, prompts: List[str]) -> Dict:
        """Parse HTML content into a JSON object using LLM"""
        return await self._parse_html(html, prompts)

    async def parse_html_to_json_list(self, html: str, prompts: List[str]) -> List[Dict]:
        """Parse HTML content into a list of JSON objects using LLM"""
        return await self._parse_html(html, prompts, expect_array=True) 