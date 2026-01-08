# Frontend Blueprint: Vera AI Assistant

## 1. Overview

This document outlines the architecture and design of the Vera AI Assistant's frontend. The frontend is a modern, single-page application (SPA) built with React. It provides a beautiful, user-friendly, and animated chat interface for interacting with the Vera AI, which is served by a separate Python (Flask) backend.

The user interface is designed to be intuitive and engaging, featuring real-time messaging, voice input, and text-to-speech output.

## 2. Technology Stack

- **Framework:** [React](https://react.dev/) (`v19`) bootstrapped with [Vite](https://vitejs.dev/).
- **Language:** JavaScript (ES6+) with JSX.
- **Build Tool:** Vite (`rolldown-vite`) for fast development and optimized builds.
- **Styling:**
    - Plain CSS with modern features (Flexbox, Custom Properties).
    - Google Fonts for typography (`Poppins`).
    - Keyframe animations for a dynamic user experience.
- **Icons:** [React Icons](https://react-icons.github.io/react-icons/) (`v5`) for a clean and consistent icon set.
- **Browser APIs:**
    - **Web Speech API (`SpeechRecognition`):** For capturing user voice input.
    - **Web Speech API (`SpeechSynthesis`):** For speaking Vera's responses aloud.
    - **Fetch API:** For communicating with the backend server.

## 3. Project Structure

The `frontend` directory is organized as follows:

```
frontend/
├── public/              # Static assets (e.g., favicon)
├── src/
│   ├── App.css          # Core stylesheet for the application component
│   ├── App.jsx          # The single, primary React component
│   └── main.jsx         # Application entry point
├── .gitignore
├── BLUEPRINT.md         # This document
├── package.json         # Project metadata, scripts, and dependencies
└── vite.config.js       # Vite build and development configuration
```

## 4. Component Architecture (`App.jsx`)

The entire frontend is encapsulated within a single, powerful component: `App.jsx`.

### State Management (`useState`)

- `messages (Array)`: Stores the complete chat history. Each item is an object like `{ sender: 'user' | 'vera', text: '...' }`.
- `input (String)`: Manages the current value of the message input field.
- `isListening (Boolean)`: Tracks whether the microphone is currently active for speech recognition.

### Refs (`useRef`)

- `messagesEndRef`: Attached to a `div` at the bottom of the message list to enable smooth auto-scrolling to the newest message.
- `recognitionRef`: Holds the persistent instance of the `SpeechRecognition` object.

### Core Logic & Functions

- **`sendMessage(messageText)`**:
    1.  Validates and trims the user's input (`messageText` or the current `input` state).
    2.  Immediately updates the `messages` state with the user's message for a responsive feel.
    3.  Sends the message to the backend via a `POST` request to `http://localhost:5000/ask`.
    4.  On receiving a successful response, it updates the `messages` state with Vera's reply.
    5.  Initiates the browser's `SpeechSynthesis` API to read Vera's reply aloud.
    6.  Includes error handling to display a user-friendly message in the chat if the backend call fails.

- **`handleMicClick()`**: Toggles the `SpeechRecognition` service on or off.

- **`useEffect` Hooks**:
    1.  **On Mount**: Initializes the `SpeechRecognition` API and its event listeners (`onstart`, `onend`, `onresult`).
    2.  **On `[messages]` Change**: Calls `scrollToBottom()` to ensure the view stays focused on the latest message.

## 5. Styling (`App.css`)

The UI/UX is designed to be modern, fluid, and visually appealing.

- **Theme:** A dark, "glassmorphism" design with a vibrant gradient background. The chat container is semi-transparent with a blurred backdrop, giving it a floating appearance.
- **CSS Custom Properties (Variables):** A clear color palette is defined at the `:root` for easy theming and maintenance.
- **Animations:**
    - `@keyframes message-appear`: New messages gracefully fade and scale into view.
    - `@keyframes pulse`: The microphone icon gently pulses with a red glow when active, providing clear visual feedback to the user.
- **Layout:** Flexbox is used extensively to create a robust and responsive layout.

## 6. API Integration

- **Endpoint:** The frontend communicates exclusively with the backend's `/ask` endpoint.
- **Method:** `POST`
- **Request Body:** A JSON object: `{ "message": "The user's input" }`
- **Response Body:** A JSON object: `{ "reply": "Vera's response" }`

This decoupled approach allows the frontend and backend to be developed, deployed, and scaled independently.
