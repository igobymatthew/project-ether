import asyncio
from genai_processors import बड़ीसोच, Processor
import whisper
import torch
import numpy as np
from app.backend.llm.lm_studio import LMStudio
from chatterbox_tts import ChatterboxTTS

class LocalSTTProcessor(Processor):
    """
    A processor that uses a local Whisper model for Speech-to-Text conversion.
    """
    def __init__(self, model):
        super().__init__()
        self.model = model
        self.audio_buffer = bytearray()

    async def call(self, *args, **kwargs):
        audio_chunk = args[0]
        if audio_chunk:
            self.audio_buffer.extend(audio_chunk)

    async def process(self):
        if not self.audio_buffer:
            return

        # Convert buffer to numpy array
        audio_np = np.frombuffer(self.audio_buffer, dtype=np.int16).astype(np.float32) / 32768.0
        self.audio_buffer = bytearray() # Clear buffer

        if audio_np.size > 0:
            result = self.model.transcribe(audio_np, fp16=False)
            transcript = result["text"]
            if transcript:
                await self.output.put(transcript)


class LocalLLMProcessor(Processor):
    """
    A processor that sends text to a local LLM and streams the response.
    """
    def __init__(self):
        super().__init__()
        self.llm = LMStudio()

    async def call(self, *args, **kwargs):
        text = args[0]
        response = self.llm.chat_completion(
            messages=[{"role": "user", "content": text}],
            max_tokens=150,
            stream=True
        )
        for chunk in response:
            content = chunk.choices[0].delta.content
            if content:
                await self.output.put(content)


class LocalTTSProcessor(Processor):
    """
    A processor that uses ChatterboxTTS to convert text to speech audio stream.
    """
    def __init__(self, tts_model: ChatterboxTTS):
        super().__init__()
        self.tts_model = tts_model

    async def call(self, *args, **kwargs):
        text_chunk = args[0]
        if text_chunk:
            # Generate audio waveform from text
            wav = self.tts_model.generate_stream(text_chunk)
            if wav is not None:
                # The output from chatterbox is a tensor, convert to bytes
                audio_bytes = self.wav_to_bytes(wav)
                await self.output.put(audio_bytes)

    def wav_to_bytes(self, wav_tensor):
        # Assuming the waveform is mono
        wav_tensor = (wav_tensor * 32767).to(torch.int16)
        return wav_tensor.cpu().numpy().tobytes()
