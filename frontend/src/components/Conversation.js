// import { useState, useRef } from "react";
// import "./../conversation.css";

// export default function Conversation() {
//   const [messages, setMessages] = useState([]);
//   const [recording, setRecording] = useState(false);
//   const [loading, setLoading] = useState(false);
//   const [playingAudio, setPlayingAudio] = useState(false);
//   const mediaRecorderRef = useRef(null);
//   const audioChunksRef = useRef([]);
//   const streamRef = useRef(null);
//   const audioRef = useRef(null);
//   const [stopChat, setStopChat] = useState(false);

//   // Convert audio blob to WAV format
//   const convertToWav = async (blob) => {
//     const audioContext = new (window.AudioContext || window.webkitAudioContext)();
//     const arrayBuffer = await blob.arrayBuffer();
//     const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);
    
//     const wavBuffer = audioBufferToWav(audioBuffer);
//     return new Blob([wavBuffer], { type: 'audio/wav' });
//   };

//   const audioBufferToWav = (audioBuffer) => {
//     const numChannels = audioBuffer.numberOfChannels;
//     const sampleRate = audioBuffer.sampleRate;
//     const format = 1;
//     const bitDepth = 16;
    
//     const bytesPerSample = bitDepth / 8;
//     const blockAlign = numChannels * bytesPerSample;
    
//     const data = [];
//     for (let i = 0; i < audioBuffer.numberOfChannels; i++) {
//       data.push(audioBuffer.getChannelData(i));
//     }
    
//     const interleaved = interleave(data);
//     const dataLength = interleaved.length * bytesPerSample;
//     const buffer = new ArrayBuffer(44 + dataLength);
//     const view = new DataView(buffer);
    
//     writeString(view, 0, 'RIFF');
//     view.setUint32(4, 36 + dataLength, true);
//     writeString(view, 8, 'WAVE');
//     writeString(view, 12, 'fmt ');
//     view.setUint32(16, 16, true);
//     view.setUint16(20, format, true);
//     view.setUint16(22, numChannels, true);
//     view.setUint32(24, sampleRate, true);
//     view.setUint32(28, sampleRate * blockAlign, true);
//     view.setUint16(32, blockAlign, true);
//     view.setUint16(34, bitDepth, true);
//     writeString(view, 36, 'data');
//     view.setUint32(40, dataLength, true);
    
//     floatTo16BitPCM(view, 44, interleaved);
    
//     return buffer;
//   };

//   const interleave = (channelData) => {
//     const length = channelData[0].length;
//     const result = new Float32Array(length * channelData.length);
//     let offset = 0;
//     for (let i = 0; i < length; i++) {
//       for (let channel = 0; channel < channelData.length; channel++) {
//         result[offset++] = channelData[channel][i];
//       }
//     }
//     return result;
//   };

//   const writeString = (view, offset, string) => {
//     for (let i = 0; i < string.length; i++) {
//       view.setUint8(offset + i, string.charCodeAt(i));
//     }
//   };

//   const floatTo16BitPCM = (view, offset, input) => {
//     for (let i = 0; i < input.length; i++, offset += 2) {
//       const s = Math.max(-1, Math.min(1, input[i]));
//       view.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7FFF, true);
//     }
//   };

//   const playAudioResponse = async (audioUrl) => {
//     try {
//       setPlayingAudio(true);
      
//       if (audioRef.current) {
//         audioRef.current.pause();
//         audioRef.current = null;
//       }

//       console.log("Audio URL to play:", audioUrl);
//       const audio = new Audio(`http://localhost:8000/conversation/audio/${audioUrl}`);
//       console.log("Audio URL:", audio);
//       audioRef.current = audio;

//       audio.onended = () => {
//         setPlayingAudio(false);
//       };

//       audio.onerror = (err) => {
//         console.error("Audio playback error:", err);
//         setPlayingAudio(false);
//         setMessages((prev) => [
//           ...prev,
//           { type: "error", text: "Failed to play audio response" }
//         ]);
//       };

//       await audio.play();
//       console.log("Playing audio response:", audioUrl);
//     } catch (error) {
//       console.error("Error playing audio:", error);
//       setPlayingAudio(false);
//     }
//   };

//   const startRecording = async () => {
//     try {
//       setRecording(true);
//       const stream = await navigator.mediaDevices.getUserMedia({ 
//         audio: {
//           channelCount: 1,
//           sampleRate: 16000
//         } 
//       });
//       streamRef.current = stream;
      
//       const options = { mimeType: 'audio/webm' };
//       mediaRecorderRef.current = new MediaRecorder(stream, options);
//       audioChunksRef.current = [];

//       mediaRecorderRef.current.ondataavailable = (e) => {
//         if (e.data.size > 0) {
//           audioChunksRef.current.push(e.data);
//         }
//       };

//       mediaRecorderRef.current.onstop = async () => {
//         setLoading(true);
//         try {
//           const blob = new Blob(audioChunksRef.current, { type: "audio/webm" });
//           const wavBlob = await convertToWav(blob);
          
//           const formData = new FormData();
//           formData.append("file", wavBlob, "voice.wav");
//           formData.append("lang", "te");
//           formData.append("gender", "male");

//           const response = await fetch("http://localhost:8000/conversation/handle_farmer_query", {
//             method: "POST",
//             body: formData,
//           });

//           const data = await response.json();
          
//           if (data.success) {
//             setMessages((prev) => [
//               ...prev,
//               { type: "user", text: data.query_text },
//               { type: "bot", text: data.answer_text }
//             ]);
            
//             if (data.audio_url) {
//               await playAudioResponse(data.audio_url);
//             }
//           } else {
//             setMessages((prev) => [
//               ...prev,
//               { type: "error", text: `Error: ${data.reply || "Unknown error"}` }
//             ]);
//           }
//         } catch (error) {
//           console.error("Error processing audio:", error);
//           setMessages((prev) => [
//             ...prev,
//             { type: "error", text: `Error: ${error.message}` }
//           ]);
//         } finally {
//           setLoading(false);
//           if (streamRef.current) {
//             streamRef.current.getTracks().forEach(track => track.stop());
//           }
//         }
//       };

//       mediaRecorderRef.current.start();
//     } catch (error) {
//       console.error("Error starting recording:", error);
//       setRecording(false);
//       alert("Error accessing microphone: " + error.message);
//     }
//   };

//   const stopRecording = () => {
//     if (mediaRecorderRef.current && mediaRecorderRef.current.state !== "inactive") {
//       setRecording(false);
//       mediaRecorderRef.current.stop();
//     }
//   };

//   const handleStopChat = async () => {
//     setStopChat(true);
    
//     if (audioRef.current) {
//       audioRef.current.pause();
//       audioRef.current = null;
//     }
//     setPlayingAudio(false);

//     if (streamRef.current) {
//       streamRef.current.getTracks().forEach(track => track.stop());
//     }

//     try {
//       await fetch("http://localhost:8000/conversation/clear_history", {
//         method: "POST",
//       });
//     } catch (error) {
//       console.error("Error clearing history:", error);
//     }

//     setMessages((prev) => [...prev, { type: "system", text: "Chat stopped. History cleared." }]);
//   };

//   const clearChat = () => {
//     setMessages([]);
//     setStopChat(false);
//   };

//   return (
//     <div className="app-container">
//       <div className="app-wrapper">
//         <div className="chat-card">
//           <div className="chat-header">
//             <h1 className="chat-title">🌾 Farmer Assistant</h1>
//             <p className="chat-subtitle">Voice-enabled agricultural advisor</p>
//           </div>

//           <div className="chat-messages">
//             {messages.length === 0 ? (
//               <div className="empty-state">
//                 <p className="empty-state-title">Press "Start Recording" to ask a question</p>
//                 <p className="empty-state-subtitle">Speak in Telugu, Hindi, or English</p>
//               </div>
//             ) : (
//               messages.map((msg, idx) => (
//                 <div key={idx} className={`message-wrapper ${msg.type}`}>
//                   <div className={`message-bubble ${msg.type}`}>
//                     {msg.text}
//                   </div>
//                 </div>
//               ))
//             )}
//             {loading && (
//               <div className="loading-container">
//                 <div className="spinner"></div>
//                 <p className="loading-text">Processing your question...</p>
//               </div>
//             )}
//             {playingAudio && (
//               <div className="audio-playing-container">
//                 <div className="audio-playing-indicator">
//                   <span className="audio-icon">🔊</span>
//                   <p className="audio-playing-text">Playing audio response...</p>
//                 </div>
//               </div>
//             )}
//           </div>

//           {!stopChat && (
//             <div className="controls">
//               {!recording ? (
//                 <button
//                   onClick={startRecording}
//                   disabled={loading || playingAudio}
//                   className="btn btn-record"
//                 >
//                   🎤 Start Recording
//                 </button>
//               ) : (
//                 <button
//                   onClick={stopRecording}
//                   className="btn btn-stop-recording"
//                 >
//                   ⏹️ Stop Recording
//                 </button>
//               )}
//               <button
//                 onClick={handleStopChat}
//                 disabled={loading}
//                 className="btn btn-stop-chat"
//               >
//                 🛑 Stop Chat
//               </button>
//             </div>
//           )}

//           {stopChat && (
//             <div className="stop-chat-section">
//               <p className="stop-chat-message">Chat has been stopped</p>
//               <button onClick={clearChat} className="btn btn-restart">
//                 🔄 Start New Chat
//               </button>
//             </div>
//           )}
//         </div>
//       </div>
//     </div>
//   );
// }

import { useState, useRef } from "react";
import "./../conversation.css";

export default function App() {
  const [messages, setMessages] = useState([]);
  const [recording, setRecording] = useState(false);
  const [loading, setLoading] = useState(false);
  const [playingAudio, setPlayingAudio] = useState(false);
  const [stopChat, setStopChat] = useState(false);
  // State for selected language, defaulted to English (en)
  const [selectedLanguage, setSelectedLanguage] = useState("en"); 

  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const streamRef = useRef(null);
  const audioRef = useRef(null);
  
  // --- Language configuration (22 Languages) ---
  const languages = [
    { code: "en", name: "English" },
    { code: "hi", name: "Hindi (हिंदी)" },
    { code: "bn", name: "Bengali (বাংলা)" },
    { code: "mr", name: "Marathi (मराठी)" },
    { code: "gu", name: "Gujarati (ગુજરાતી)" },
    { code: "or", name: "Odia (ଓଡ଼ିଆ)" },
    { code: "pa", name: "Punjabi (ਪੰਜਾਬੀ)" },
    { code: "as", name: "Assamese (অসমীয়া)" },
    { code: "te", name: "Telugu (తెలుగు)" },
    { code: "kn", name: "Kannada (ಕನ್ನಡ)" },
    { code: "ta", name: "Tamil (தமிழ்)" },
    { code: "ml", name: "Malayalam (മലയാളം)" },
    { code: "ur", name: "Urdu (اُردُو)" },
    { code: "sa", name: "Sanskrit (संस्कृतम्)" },
    { code: "brx", name: "Bodo (बर')" },
    { code: "doi", name: "Dogri (डोगरी)" },
    { code: "ks", name: "Kashmiri (کٲشُر)" },
    { code: "gom", name: "Goan Konkani (कोंकणी)" },
    { code: "mai", name: "Maithili (मैथिली)" },
    { code: "ne", name: "Nepali (नेपाली)" },
    { code: "sat", name: "Santali (ᱥᱟᱱᱛᱟᱲᱤ)" },
    { code: "sd", name: "Sindhi (سنڌي)" },
  ];

  const handleLanguageChange = (code) => {
    setSelectedLanguage(code);
    clearChat();
  };
  // --- End Language configuration ---


  // Convert audio blob to WAV format
  const convertToWav = async (blob) => {
    const audioContext = new (window.AudioContext || window.webkitAudioContext)();
    const arrayBuffer = await blob.arrayBuffer();
    const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);
    
    const wavBuffer = audioBufferToWav(audioBuffer);
    return new Blob([wavBuffer], { type: 'audio/wav' });
  };

  const audioBufferToWav = (audioBuffer) => {
    const numChannels = audioBuffer.numberOfChannels;
    const sampleRate = audioBuffer.sampleRate;
    const format = 1;
    const bitDepth = 16;
    
    const bytesPerSample = bitDepth / 8;
    const blockAlign = numChannels * bytesPerSample;
    
    const data = [];
    for (let i = 0; i < audioBuffer.numberOfChannels; i++) {
      data.push(audioBuffer.getChannelData(i));
    }
    
    const interleaved = interleave(data);
    const dataLength = interleaved.length * bytesPerSample;
    const buffer = new ArrayBuffer(44 + dataLength);
    const view = new DataView(buffer);
    
    writeString(view, 0, 'RIFF');
    view.setUint32(4, 36 + dataLength, true);
    writeString(view, 8, 'WAVE');
    writeString(view, 12, 'fmt ');
    view.setUint32(16, 16, true);
    view.setUint16(20, format, true);
    view.setUint16(22, numChannels, true);
    view.setUint32(24, sampleRate, true);
    view.setUint32(28, sampleRate * blockAlign, true);
    view.setUint16(32, blockAlign, true);
    view.setUint16(34, bitDepth, true);
    writeString(view, 36, 'data');
    view.setUint32(40, dataLength, true);
    
    floatTo16BitPCM(view, 44, interleaved);
    
    return buffer;
  };

  const interleave = (channelData) => {
    const length = channelData[0].length;
    const result = new Float32Array(length * channelData.length);
    let offset = 0;
    for (let i = 0; i < length; i++) {
      for (let channel = 0; channel < channelData.length; channel++) {
        result[offset++] = channelData[channel][i];
      }
    }
    return result;
  };

  const writeString = (view, offset, string) => {
    for (let i = 0; i < string.length; i++) {
      view.setUint8(offset + i, string.charCodeAt(i));
    }
  };

  const floatTo16BitPCM = (view, offset, input) => {
    for (let i = 0; i < input.length; i++, offset += 2) {
      const s = Math.max(-1, Math.min(1, input[i]));
      view.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7FFF, true);
    }
  };

  const playAudioResponse = async (audioFile) => {
    try {
      setPlayingAudio(true);
      
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current = null;
      }

      // Backend returns "outputs/filename.wav", so we split to get the filename for the GET route
      const filename = audioFile.split('/').pop();

      const audio = new Audio(`http://localhost:8000/conversation/outputs/${filename}`);
      audioRef.current = audio;

      audio.onended = () => {
        setPlayingAudio(false);
      };

      audio.onerror = (err) => {
        console.error("Audio playback error:", err);
        setPlayingAudio(false);
        setMessages((prev) => [
          ...prev,
          { type: "error", text: "Failed to play audio response" }
        ]);
      };

      await audio.play();
      console.log("Playing audio response:", filename);
    } catch (error) {
      console.error("Error playing audio:", error);
      setPlayingAudio(false);
    }
  };

  const startRecording = async () => {
    try {
      setRecording(true);
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          channelCount: 1,
          sampleRate: 16000
        } 
      });
      streamRef.current = stream;
      
      const options = { mimeType: 'audio/webm' };
      mediaRecorderRef.current = new MediaRecorder(stream, options);
      audioChunksRef.current = [];

      mediaRecorderRef.current.ondataavailable = (e) => {
        if (e.data.size > 0) {
          audioChunksRef.current.push(e.data);
        }
      };

      mediaRecorderRef.current.onstop = async () => {
        setLoading(true);
        try {
          const blob = new Blob(audioChunksRef.current, { type: "audio/webm" });
          const wavBlob = await convertToWav(blob);
          
          const formData = new FormData();
          formData.append("file", wavBlob, "voice.wav");
          formData.append("lang", selectedLanguage); // Use selected language
          formData.append("gender", "male");
          // Assuming default location for this specific chat, update if needed
          formData.append("lat", "17.385044");
          formData.append("lon", "78.486671");
          formData.append("state", "Telangana");


          const response = await fetch("http://localhost:8000/conversation/handle_farmer_query", {
            method: "POST",
            body: formData,
          });

          const data = await response.json();
          
          if (data.success) {
            setMessages((prev) => [
              ...prev,
              { type: "user", text: data.query_text },
              { type: "bot", text: data.answer_text }
            ]);
            
            if (data.audio_file) { // Changed from audio_url to audio_file based on backend update
              await playAudioResponse(data.audio_file);
            }
          } else {
            setMessages((prev) => [
              ...prev,
              { type: "error", text: `Error: ${data.reply || "Unknown error"}` }
            ]);
          }
        } catch (error) {
          console.error("Error processing audio:", error);
          setMessages((prev) => [
            ...prev,
            { type: "error", text: `Error: ${error.message}` }
          ]);
        } finally {
          setLoading(false);
          if (streamRef.current) {
            streamRef.current.getTracks().forEach(track => track.stop());
          }
        }
      };

      mediaRecorderRef.current.start();
    } catch (error) {
      console.error("Error starting recording:", error);
      setRecording(false);
      // NOTE: Using a custom message box instead of alert() is recommended in a real app
      alert("Error accessing microphone: " + error.message);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== "inactive") {
      setRecording(false);
      mediaRecorderRef.current.stop();
    }
  };

  const handleStopChat = async () => {
    setStopChat(true);
    
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current = null;
    }
    setPlayingAudio(false);

    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
    }

    try {
      await fetch("http://localhost:8000/conversation/clear_history", {
        method: "POST",
      });
    } catch (error) {
      console.error("Error clearing history:", error);
    }

    setMessages((prev) => [...prev, { type: "system", text: "Chat stopped. History cleared." }]);
  };

  const clearChat = () => {
    setMessages([]);
    setStopChat(false);
  };

  const getCurrentLanguageName = () => {
    return languages.find(l => l.code === selectedLanguage)?.name;
  };

  return (
    <div className="app-container">
      <div className="app-wrapper">
        <div className="chat-card">
          <div className="chat-header">
            <h1 className="chat-title">🌾 Farmer Assistant</h1>
            <p className="chat-subtitle">Voice-enabled agricultural advisor</p>
          </div>

          {/* Language Selector */}
          <div className="language-selector">
            <p className="language-prompt">Choose your language:</p>
            <div className="language-buttons">
              {languages.map((lang) => (
                <button
                  key={lang.code}
                  className={`btn-lang ${selectedLanguage === lang.code ? 'active' : ''}`}
                  onClick={() => handleLanguageChange(lang.code)}
                  disabled={loading || recording || playingAudio}
                >
                  {lang.name}
                </button>
              ))}
            </div>
          </div>
          {/* End Language Selector */}

          <div className="chat-messages">
            {messages.length === 0 ? (
              <div className="empty-state">
                <p className="empty-state-title">Press "Ask Question" to start</p>
                <p className="empty-state-subtitle">
                  Current Language: **{getCurrentLanguageName()}**
                </p>
              </div>
            ) : (
              messages.map((msg, idx) => (
                <div key={idx} className={`message-wrapper ${msg.type}`}>
                  <div className={`message-bubble ${msg.type}`}>
                    {msg.text}
                  </div>
                </div>
              ))
            )}
            {loading && (
              <div className="loading-container">
                <div className="spinner"></div>
                <p className="loading-text">Processing your question...</p>
              </div>
            )}
            {playingAudio && (
              <div className="audio-playing-container">
                <div className="audio-playing-indicator">
                  <span className="audio-icon">🔊</span>
                  <p className="audio-playing-text">Playing audio response...</p>
                </div>
              </div>
            )}
          </div>

          {!stopChat && (
            <div className="controls">
              {!recording ? (
                <button
                  onClick={startRecording}
                  disabled={loading || playingAudio}
                  className="btn btn-record"
                >
                  🎤 Ask Question in **{getCurrentLanguageName()}**
                </button>
              ) : (
                <button
                  onClick={stopRecording}
                  className="btn btn-stop-recording"
                >
                  ⏹️ Stop Recording
                </button>
              )}
              <button
                onClick={handleStopChat}
                disabled={loading}
                className="btn btn-stop-chat"
              >
                🛑 Stop Chat
              </button>
            </div>
          )}

          {stopChat && (
            <div className="stop-chat-section">
              <p className="stop-chat-message">Chat has been stopped</p>
              <button onClick={clearChat} className="btn btn-restart">
                🔄 Start New Chat
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}