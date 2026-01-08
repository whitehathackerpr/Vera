import React, { useState, useEffect } from 'react';
import { FiX } from 'react-icons/fi';
import './VoiceMode.css';

const VoiceMode = ({ isActive, onClose, transcript }) => {
  const [showTranscript, setShowTranscript] = useState(false);

  useEffect(() => {
    let timer;
    if (transcript) {
      setShowTranscript(true);
      timer = setTimeout(() => setShowTranscript(false), 2000); // Fades out after 2s
    }
    return () => clearTimeout(timer);
  }, [transcript]);


  // Create an array to map over for the bars
  const bars = Array.from({ length: 15 });

  return (
    <div className={`voice-mode-overlay ${isActive ? 'active' : ''}`}>
      <button className="close-button" onClick={onClose}>
        <FiX />
      </button>

      <div className="waveform-container">
        {bars.map((_, index) => (
          <div key={index} className="waveform-bar"></div>
        ))}
      </div>

      <div className="listening-text">
        <h2>Vera Listening</h2>
        <p>Speak naturally...</p>
      </div>

      <div className="transcript-container">
          <p className={`transcript-fade ${showTranscript ? '' : 'opacity-0'}`}>
              {transcript}
          </p>
      </div>
    </div>
  );
};

export default VoiceMode;
