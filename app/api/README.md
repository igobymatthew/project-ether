# Backend Services

This directory contains the two backend services for the application.

## Services

-   **Main Backend (`main`)**: The main application logic, including the `genai-processors` pipeline.
-   **TTS Service (`tts`)**: A dedicated service for Text-to-Speech using `chatterbox-tts`.

## Running the Services

To run the application, you need to run both services in separate terminals.

### 1. Install Dependencies

First, install the dependencies for each service.

**For the Main Backend:**

```bash
pip install -r app/api/main/requirements.txt
```

**For the TTS Service:**

```bash
pip install -r app/api/tts/requirements.txt
```

*Note: It is highly recommended to use separate virtual environments for each service to avoid dependency conflicts.*

### 2. Run the Services

**To run the Main Backend (on port 8000):**

```bash
uvicorn app.api.main.main:app --host 0.0.0.0 --port 8000
```

**To run the TTS Service (on port 8001):**

```bash
uvicorn app.api.tts.main:app --host 0.0.0.0 --port 8001
```

The main backend is configured to communicate with the TTS service on port 8001. If you change the port for the TTS service, you will need to update the `tts_service_url` in `app/api/main/orchestrator/local_processors.py`.
