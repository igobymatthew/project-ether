# Project Ether

An experimental audio-LLM playground for simulating lively group calls.

## Capabilities

Project Ether simulates a group call with fictional characters.

-   **Expressive, natural voices**: Characters speak with natural-sounding voices.
-   **Real-time conversation**: Interact with characters in real-time.
-   **Background audio**: Includes background sounds for a more immersive experience.
-   **Dynamic conversations**: The conversation can shift between different speakers.

## How to Run

1.  **Clone the repository**
    ```bash
    git clone https://github.com/yourusername/project-ether.git
    cd project-ether
    ```

2.  **Set up the Python environment**
    ```bash
    python -m venv .venv
    source .venv/bin/activate   # On Windows, use: .venv\Scripts\activate
    pip install -r requirements.txt
    ```
    *Note: The required packages include large libraries for audio processing. The first time you run the backend, a model of about 1GB will be downloaded. The application will be ready to use once the download is complete.*

3.  **Generate character agents**
    ```bash
    python scripts/make_agents.py
    ```

4.  **Run the backend server**
    ```bash
    uvicorn app.backend.main:app --reload --port 8000
    ```
    You can check if the backend is running by visiting `http://localhost:8000/`.

5.  **Run the frontend**

    In a new terminal, run the following command:
    ```bash
    python -m http.server --directory app/frontend 8080
    ```
    Then, open your browser and go to `http://localhost:8080/index.html`.

## Usage

-   **Start Call**: Click the "Dial" button to connect and start the simulation.
-   **Interact**: Type a message in the input box to have a character respond.
-   **Switch Speakers**: Try asking to speak to a different character, for example, "Can I talk to my brother?".
-   **Adjust Volume**: Use the slider to change the volume of the background audio.
-   **End Call**: Click the "End Call" button to stop the simulation.
