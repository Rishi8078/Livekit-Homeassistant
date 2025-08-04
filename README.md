# LiveKit AI Assistant for Home Assistant

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A voice-controlled AI personal assistant built with **LiveKit Agents** that integrates seamlessly with **Home Assistant** via the **Model Context Protocol (MCP)**. This agent, codenamed "Friday," provides real-time voice interaction, smart home control, and access to external information.


## 🌟 Features

-   **🎙️ Real-time Voice Interaction**: Uses Google's Realtime Model for natural and responsive voice conversations.
-   **🏡 Full Smart Home Control**: Deep integration with Home Assistant using MCP for controlling lights, scenes, sensors, and more.
-   **🌤️ Real-time Information**: Fetches current weather, performs web searches, and provides time information for any location.
-   **🔇 Noise Cancellation**: Includes background noise reduction for clearer voice commands.
-   **🌐 Multi-language Support**: Automatically detects the user's language and responds accordingly.
-   **🩺 System Health Checks**: Built-in diagnostics to verify connections to all services.

---

## 🔧 Prerequisites

-   Python 3.9+
-   A running Home Assistant instance with the MCP server add-on enabled.
-   A LiveKit account and API credentials.
-   Google Cloud credentials for speech-to-text and text-to-speech services.

---

## 🚀 Installation & Setup

1.  **Clone the Repository**:
    ```bash
    git clone [https://github.com/Rishi8078/Livekit-Homeassistant.git](https://github.com/Rishi8078/Livekit-Homeassistant.git)
    cd livekit-home-assistant-agent
    ```

2.  **Create and Activate a Virtual Environment**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables**:
    Create a `.env` file in the root of the project and add the following configuration.

    ```env
    # LiveKit Configuration
    LIVEKIT_URL=YOUR_LIVEKIT_URL
    LIVEKIT_API_KEY=YOUR_API_KEY
    LIVEKIT_API_SECRET=YOUR_API_SECRET

    # Google Cloud Configuration
    # Make sure this points to your service account JSON file
    GOOGLE_APPLICATION_CREDENTIALS=path/to/your/credentials.json

    # Home Assistant MCP Configuration
    HOME_ASSISTANT_MCP_URL=https://your-ha-instance/mcp_server/sse
    HOME_ASSISTANT_TOKEN=YOUR_LONG_LIVED_ACCESS_TOKEN
    
    ```

---

## 🏠 Home Assistant MCP Setup

This agent uses the **Model Context Protocol (MCP)** for a powerful, real-time connection to Home Assistant.

1.  **Install the MCP Server Add-on**: Find and install the "MCP Server" add-on from the Home Assistant Add-on Store.
2.  **Configure the Add-on**: Set it up with your Home Assistant URL and a long-lived access token.
3.  **Get the SSE Endpoint**: Once the add-on is running, copy the SSE endpoint URL.
4.  **Create a Long-Lived Access Token**:
    -   In Home Assistant, go to your user profile page.
    -   Scroll down to "Long-Lived Access Tokens" and click "Create Token".
    -   Name it (e.g., "LiveKit Agent") and copy the generated token.
5.  **Update your `.env` file** with the `HOME_ASSISTANT_MCP_URL` and `HOME_ASSISTANT_TOKEN`.

---

## ▶️ Usage

1.  **Run the Health Check**: Before starting, it's a good idea to run the health check to ensure all connections are working.
    ```bash
    python health_check.py
    ```

2.  **Start the Agent**:
    ```bash
    python agent.py console
    ```

3.  **Interact with the Agent**:
    Once the agent is running and connected to a LiveKit room, you can start interacting with it using its wake word.

    -   *"Friday, what's the weather in London?"*
    -   *"Hey Friday, turn on the living room lights."*
    -   *"Friday, set the bedroom light to blue."*
    -   *"Hey Friday, activate the movie time scene."*

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue to discuss your ideas.

1.  Fork the repository.
2.  Create your feature branch (`git checkout -b feature/AmazingFeature`).
3.  Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4.  Push to the branch (`git push origin feature/AmazingFeature`).
5.  Open a Pull Request.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
