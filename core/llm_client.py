"""HuggingFace Inference API LLM Client."""

import os
from typing import Optional, Dict, Any, List
import asyncio
from huggingface_hub import InferenceClient
from tenacity import retry, stop_after_attempt, wait_exponential
import logging

logger = logging.getLogger(__name__)


class HuggingFaceLLMClient:
    """Wrapper for HuggingFace Inference API with retry logic."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "meta-llama/Llama-3.1-70B-Instruct",
        max_tokens: int = 2048,
        temperature: float = 0.7,
    ):
        self.api_key = api_key or os.getenv("HUGGINGFACE_API_KEY")
        if not self.api_key:
            raise ValueError("HuggingFace API key not found. Set HUGGINGFACE_API_KEY env var.")
        
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.client = InferenceClient(token=self.api_key)
        
        logger.info(f"Initialized HuggingFace LLM client with model: {model}")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs
    ) -> str:
        """Generate text completion with retry logic.
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            max_tokens: Max tokens to generate (overrides default)
            temperature: Sampling temperature (overrides default)
            **kwargs: Additional parameters for HF Inference API
            
        Returns:
            Generated text
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = self.client.chat_completion(
                messages=messages,
                model=self.model,
                max_tokens=max_tokens or self.max_tokens,
                temperature=temperature or self.temperature,
                **kwargs
            )
            
            generated_text = response.choices[0].message.content
            logger.debug(f"Generated {len(generated_text)} characters")
            return generated_text
            
        except Exception as e:
            logger.error(f"HuggingFace API error: {str(e)}")
            raise
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    async def generate_async(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs
    ) -> str:
        """Async version of generate."""
        # HuggingFace InferenceClient doesn't have native async support
        # Run in executor to avoid blocking
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: self.generate(prompt, system_prompt, max_tokens, temperature, **kwargs)
        )
    
    def generate_structured(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        response_format: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> str:
        """Generate with structured output (JSON mode).
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            response_format: JSON schema for structured output
            **kwargs: Additional parameters
            
        Returns:
            Generated text (should be valid JSON if response_format is provided)
        """
        # Add JSON formatting instruction to prompt
        if response_format:
            prompt += "\n\nRespond with valid JSON only. No markdown formatting."
        
        return self.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            **kwargs
        )
    
    def batch_generate(
        self,
        prompts: List[str],
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> List[str]:
        """Generate completions for multiple prompts.
        
        Args:
            prompts: List of prompts
            system_prompt: Optional system prompt for all
            **kwargs: Additional parameters
            
        Returns:
            List of generated texts
        """
        results = []
        for prompt in prompts:
            try:
                result = self.generate(prompt, system_prompt, **kwargs)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to generate for prompt: {prompt[:50]}... Error: {str(e)}")
                results.append(f"ERROR: {str(e)}")
        
        return results
    
    async def batch_generate_async(
        self,
        prompts: List[str],
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> List[str]:
        """Async batch generation."""
        tasks = [
            self.generate_async(prompt, system_prompt, **kwargs)
            for prompt in prompts
        ]
        return await asyncio.gather(*tasks, return_exceptions=True)
