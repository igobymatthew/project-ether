import asyncio
# from genai_processors import Processor
import whisper
import numpy as np
import httpx
from app.api.main.llm.lm_studio import LMStudio

# class LocalSTTProcessor(Processor):
#     """
#     A processor that uses a local Whisper model for Speech-to-Text conversion.
#     """
#     def __init__(self, model):
#         super().__init__()
#         self.model = model
#         self.audio_buffer = bytearray()

#     async def call(self, *args, **kwargs):
#         audio_chunk = args[0]
#         if audio_chunk:
#             self.audio_buffer.extend(audio_chunk)

#     async def process(self):
#         if not self.audio_buffer:
#             return

#         # Convert buffer to numpy array
#         audio_np = np.frombuffer(self.audio_buffer, dtype=np.int16).astype(np.float32) / 32768.0
#         self.audio_buffer = bytearray() # Clear buffer

#         if audio_np.size > 0:
#             result = self.model.transcribe(audio_np, fp16=False)
#             transcript = result["text"]
#             if transcript:
#                 await self.output.put(transcript)


# class LocalLLMProcessor(Processor):
#     """
#     A processor that sends text to a local LLM and streams the response.
#     """
#     def __init__(self):
#         super().__init__()
#         self.llm = LMStudio()

#     async def call(self, *args, **kwargs):
#         text = args[0]
#         response = self.llm.chat_completion(
#             messages=[{"role": "user", "content": text}],
#             max_tokens=150,
#             stream=True
#         )
#         for chunk in response:
#             content = chunk.choices[0].delta.content
#             if content:
#                 await self.output.put(content)


# class LocalTTSProcessor(Processor):
#     """
#     A processor that calls a remote TTS service to convert text to speech.
#     """
#     def __init__(self, tts_service_url="http://localhost:8001/synthesize"):
#         super().__init__()
#         self.tts_service_url = tts_service_url
#         self.client = httpx.AsyncClient()

#     async def call(self, *args, **kwargs):
#         text_chunk = args[0]
#         if text_chunk:
#             try:
#                 response = await self.client.post(
#                     self.tts_service_url,
#                     json={"text": text_chunk},
#                     timeout=20.0 # Set a timeout
#                 )
#                 response.raise_for_status()  # Raise an exception for bad status codes
#                 audio_bytes = response.content
#                 if audio_bytes:
#                     await self.output.put(audio_bytes)
#             except httpx.RequestError as e:
#                 # Handle connection errors, timeouts, etc.
#                 print(f"An error occurred while requesting {e.request.url!r}: {e}")
#             except Exception as e:
#                 print(f"An unexpected error occurred in LocalTTSProcessor: {e}")
