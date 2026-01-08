import React, { useState, useEffect, useRef } from 'react';
import { FiPlus, FiMic, FiBarChart2 } from 'react-icons/fi';
import './App.css';
import VoiceMode from './VoiceMode.jsx';

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [showLanding, setShowLanding] = useState(true);
  const [isVoiceMode, setIsVoiceMode] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [isVeraTyping, setIsVeraTyping] = useState(false);
  const messagesEndRef = useRef(null);
  const recognitionRef = useRef(null);

  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      const recognition = new SpeechRecognition();
      recognition.continuous = true;
      recognition.interimResults = true;
      recognition.lang = 'en-US';

      recognition.onstart = () => setIsListening(true);
      recognition.onend = () => {
        setIsListening(false);
        setTranscript('');
      };

      recognition.onresult = (event) => {
        let interimTranscript = '';
        let finalTranscript = '';

        for (let i = event.resultIndex; i < event.results.length; ++i) {
          if (event.results[i].isFinal) {
            finalTranscript += event.results[i][0].transcript;
          } else {
            interimTranscript += event.results[i][0].transcript;
          }
        }

        setTranscript(interimTranscript);

        if (finalTranscript) {
            if (isVoiceMode) {
                sendMessage(finalTranscript.trim());
            } else {
                setInput(finalTranscript.trim());
            }
        }
      };

      recognitionRef.current = recognition;
    } else {
      console.log("Speech recognition not supported in this browser.");
    }

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
    };
  }, [isVoiceMode]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    if (!showLanding || isVeraTyping) {
      scrollToBottom();
    }
  }, [messages, showLanding, isVeraTyping]);

  const startConversation = () => {
    if (showLanding) {
      setShowLanding(false);
    }
  };

  const handleInputChange = (e) => {
    setInput(e.target.value);
    if (e.target.value.length > 0 && showLanding) {
      startConversation();
    }
  };

  const sendMessage = async (messageText) => {
    const text = (messageText || input).trim();
    if (!text) return;

    startConversation();

    const userMessage = { sender: 'user', text };
    setMessages((prevMessages) => [...prevMessages, userMessage]);
    setInput('');
    setIsVeraTyping(true);

    try {
      const response = await fetch('http://localhost:5000/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text }),
      });

      if (!response.ok) throw new Error('Network response was not ok');

      const data = await response.json();
      const veraMessage = { sender: 'vera', text: data.reply };
      setMessages((prevMessages) => [...prevMessages, veraMessage]);

    } catch (error) {
      console.error("Error sending message:", error);
      const errorMessage = { sender: 'vera', text: "Sorry, I'm having trouble connecting. Please try again later." };
      setMessages((prevMessages) => [...prevMessages, errorMessage]);
    } finally {
        setIsVeraTyping(false);
    }
  };

  const handleMicClick = () => {
    if (recognitionRef.current) {
      startConversation();
      if (isListening) {
        recognitionRef.current.stop();
      } else {
        recognitionRef.current.start();
      }
    }
  };

  const handleLiveSessionClick = () => {
    setIsVoiceMode(true);
    if (recognitionRef.current) {
      recognitionRef.current.start();
    }
  };

  const closeVoiceMode = () => {
    setIsVoiceMode(false);
    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }
  };

  return (
    <div className="App">
      <VoiceMode isActive={isVoiceMode} onClose={closeVoiceMode} transcript={transcript} />

      <div className={`landing-state ${!showLanding ? 'hidden' : ''}`}>
        <h1 className="landing-title">What are you working on?</h1>
      </div>

      <div className={`messages ${!showLanding ? 'visible' : ''}`}>
        {messages.map((msg, index) => (
          <div key={index} className={`message ${msg.sender}`}>
            {msg.text}
          </div>
        ))}
        {isVeraTyping && (
            <div className="message vera">
                <div className="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {!isVoiceMode && (
        <div className="command-bar">
          <button className="icon-button">
            <FiPlus />
          </button>
          <input
            type="text"
            value={input}
            onChange={handleInputChange}
            onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
            placeholder={isVeraTyping ? "Vera is thinking..." : "Ask anything"}
            disabled={isVeraTyping}
          />
          <button className={`icon-button ${isListening ? 'listening' : ''}`} onClick={handleMicClick} disabled={isVeraTyping}>
            <FiMic />
          </button>
          <button className="live-session-button" onClick={handleLiveSessionClick} disabled={isVeraTyping}>
            <FiBarChart2 style={{ transform: 'rotate(90deg)' }} />
          </button>
        </div>
      )}
    </div>
  );
}

export default App;
