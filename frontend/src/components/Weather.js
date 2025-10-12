// import { useState, useRef } from "react";
// import "../weather.css";

// export default function Weather() {
//   const [messages, setMessages] = useState([]);
//   const [recording, setRecording] = useState(false);
//   const [loading, setLoading] = useState(false);
//   const [playingAudio, setPlayingAudio] = useState(false);
//   const [weatherData, setWeatherData] = useState(null);
//   const mediaRecorderRef = useRef(null);
//   const audioChunksRef = useRef([]);
//   const streamRef = useRef(null);
//   const audioRef = useRef(null);

//   // Hardcoded location - Change these values as needed
//   const LOCATION = {
//     lat: "17.385044",
//     lon: "78.486671",
//     city: "Hyderabad",
//     state: "Telangana"
//   };

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

//   const getWeatherIcon = (condition) => {
//     const conditionLower = condition.toLowerCase();
//     if (conditionLower.includes('clear')) return '☀️';
//     if (conditionLower.includes('cloud') || conditionLower.includes('overcast')) return '☁️';
//     if (conditionLower.includes('rain') || conditionLower.includes('drizzle')) return '🌧️';
//     if (conditionLower.includes('snow')) return '❄️';
//     if (conditionLower.includes('thunder')) return '⛈️';
//     if (conditionLower.includes('fog')) return '🌫️';
//     return '🌤️';
//   };

//   const parseWeatherFromResponse = (responseText) => {
//     const tempMatch = responseText.match(/(\d+)°C/);
//     const windMatch = responseText.match(/(\d+)\s*km\/h/);
//     const precipMatch = responseText.match(/(\d+\.?\d*)\s*mm/);
    
//     if (tempMatch) {
//       return {
//         temperature: parseInt(tempMatch[1]),
//         condition: responseText,
//         wind_speed: windMatch ? parseInt(windMatch[1]) : null,
//         precipitation: precipMatch ? parseFloat(precipMatch[1]) : null
//       };
//     }
//     return null;
//   };

//   const playAudioResponse = async (audioFile) => {
//     try {
//       setPlayingAudio(true);
      
//       if (audioRef.current) {
//         audioRef.current.pause();
//         audioRef.current = null;
//       }

//       // The backend returns just the filename, so we construct the full URL
//       const audioUrl = `http://localhost:8000/weather/${audioFile}`;
//       console.log("Playing audio from:", audioUrl);
      
//       const audio = new Audio(audioUrl);
//       audioRef.current = audio;

//       audio.onended = () => {
//         console.log("Audio playback finished");
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
//       console.log("Audio playing successfully");
//     } catch (error) {
//       console.error("Error playing audio:", error);
//       setPlayingAudio(false);
//     }
//   };

//   const startRecording = async () => {
//     try {
//       setRecording(true);
//       const stream = await navigator.mediaDevices.getUserMedia({ 
//         audio: { channelCount: 1, sampleRate: 16000 } 
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
//           formData.append("lat", LOCATION.lat);
//           formData.append("lon", LOCATION.lon);
//           formData.append("state", LOCATION.state);

//           const response = await fetch("http://localhost:8000/weather/handle_farmer_query", {
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

//             // Try to parse weather data from response
//             const weather = parseWeatherFromResponse(data.answer_text);
//             if (weather) {
//               setWeatherData(weather);
//             }
            
//             // Play audio response - backend returns path like "outputs/filename.wav"
//             if (data.audio_file) {
//               console.log("Received audio file:", data.audio_file);
//               await playAudioResponse(data.audio_file);
//             } else {
//               console.warn("No audio file in response");
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

//   const clearChat = () => {
//     setMessages([]);
//     setWeatherData(null);
//   };

//   return (
//     <div className="weather-container">
//       <div className="weather-wrapper">
//         {/* Location Banner */}
//         <div className="location-banner">
//           <div className="location-icon">📍</div>
//           <div className="location-info">
//             <h2 className="location-city">{LOCATION.city}</h2>
//             <p className="location-state">{LOCATION.state}</p>
//           </div>
//         </div>

//         {/* Weather Card (if available) */}
//         {weatherData && (
//           <div className="weather-card">
//             <div className="weather-icon-large">
//               {getWeatherIcon(weatherData.condition)}
//             </div>
//             <div className="weather-temp">{weatherData.temperature}°C</div>
//             <div className="weather-condition-text">{weatherData.condition}</div>
//             {(weatherData.wind_speed || weatherData.precipitation !== null) && (
//               <div className="weather-details">
//                 {weatherData.precipitation !== null && (
//                   <div className="weather-detail-item">
//                     <span className="weather-detail-icon">💧</span>
//                     <span>Rain: {weatherData.precipitation}mm</span>
//                   </div>
//                 )}
//                 {weatherData.wind_speed && (
//                   <div className="weather-detail-item">
//                     <span className="weather-detail-icon">💨</span>
//                     <span>Wind: {weatherData.wind_speed} km/h</span>
//                   </div>
//                 )}
//               </div>
//             )}
//           </div>
//         )}

//         {/* Chat Card */}
//         <div className="chat-card">
//           <div className="chat-header">
//             <h1 className="chat-title">🌾 Weather Assistant</h1>
//             <p className="chat-subtitle">Ask about weather in Telugu, Hindi or English</p>
//           </div>

//           <div className="chat-messages">
//             {messages.length === 0 ? (
//               <div className="empty-state">
//                 <p className="empty-state-title">Press "Start Recording" to ask about weather</p>
//                 <p className="empty-state-subtitle">
//                   Examples: "What's the weather today?" • "Will it rain tomorrow?" • "Weather for next Monday"
//                 </p>
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
//                 <p className="loading-text">Getting weather information...</p>
//               </div>
//             )}
//             {playingAudio && (
//               <div className="audio-playing-container">
//                 <div className="audio-playing-indicator">
//                   <span className="audio-icon">🔊</span>
//                   <p className="audio-playing-text">Playing weather report...</p>
//                 </div>
//               </div>
//             )}
//           </div>

//           <div className="controls">
//             {!recording ? (
//               <button
//                 onClick={startRecording}
//                 disabled={loading || playingAudio}
//                 className="btn btn-record"
//               >
//                 🎤 Ask About Weather
//               </button>
//             ) : (
//               <button
//                 onClick={stopRecording}
//                 className="btn btn-stop-recording"
//               >
//                 ⏹️ Stop Recording
//               </button>
//             )}
//             {messages.length > 0 && (
//               <button
//                 onClick={clearChat}
//                 disabled={loading}
//                 className="btn btn-clear"
//               >
//                 🗑️ Clear
//               </button>
//             )}
//           </div>
//         </div>
//       </div>
//     </div>
//   );
// }

import { useState, useRef } from "react";
import "./../weather.css";

export default function Weather() {
  const [messages, setMessages] = useState([]);
  const [recording, setRecording] = useState(false);
  const [loading, setLoading] = useState(false);
  const [playingAudio, setPlayingAudio] = useState(false);
  const [weatherData, setWeatherData] = useState(null);
  // NEW STATE for selected language
  const [selectedLanguage, setSelectedLanguage] = useState("en"); // Default to English
  
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const streamRef = useRef(null);
  const audioRef = useRef(null);

  // Hardcoded location - Change these values as needed
  const LOCATION = {
    lat: "17.385044",
    lon: "78.486671",
    city: "Hyderabad",
    state: "Telangana"
  };

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

  const getWeatherIcon = (condition) => {
    const conditionLower = condition.toLowerCase();
    if (conditionLower.includes('clear')) return '☀️';
    if (conditionLower.includes('cloud') || conditionLower.includes('overcast')) return '☁️';
    if (conditionLower.includes('rain') || conditionLower.includes('drizzle')) return '🌧️';
    if (conditionLower.includes('snow')) return '❄️';
    if (conditionLower.includes('thunder')) return '⛈️';
    if (conditionLower.includes('fog')) return '🌫️';
    return '🌤️';
  };

  const parseWeatherFromResponse = (responseText) => {
    const tempMatch = responseText.match(/(\d+)°C/);
    const windMatch = responseText.match(/(\d+)\s*km\/h/);
    const precipMatch = responseText.match(/(\d+\.?\d*)\s*mm/);
    
    if (tempMatch) {
      return {
        temperature: parseInt(tempMatch[1]),
        condition: responseText,
        wind_speed: windMatch ? parseInt(windMatch[1]) : null,
        precipitation: precipMatch ? parseFloat(precipMatch[1]) : null
      };
    }
    return null;
  };

  const playAudioResponse = async (audioFile) => {
    try {
      setPlayingAudio(true);
      
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current = null;
      }

      // The backend returns just the filename, so we construct the full URL
      const audioUrl = `http://localhost:8000/weather/${audioFile}`;
      console.log("Playing audio from:", audioUrl);
      
      const audio = new Audio(audioUrl);
      audioRef.current = audio;

      audio.onended = () => {
        console.log("Audio playback finished");
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
      console.log("Audio playing successfully");
    } catch (error) {
      console.error("Error playing audio:", error);
      setPlayingAudio(false);
    }
  };

  const startRecording = async () => {
    try {
      setRecording(true);
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: { channelCount: 1, sampleRate: 16000 } 
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
          // UPDATED: Use selectedLanguage state
          formData.append("lang", selectedLanguage);
          formData.append("gender", "male");
          formData.append("lat", LOCATION.lat);
          formData.append("lon", LOCATION.lon);
          formData.append("state", LOCATION.state);

          const response = await fetch("http://localhost:8000/weather/handle_farmer_query", {
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

            // Try to parse weather data from response
            const weather = parseWeatherFromResponse(data.answer_text);
            if (weather) {
              setWeatherData(weather);
            }
            
            // Play audio response - backend returns path like "outputs/filename.wav"
            if (data.audio_file) {
              console.log("Received audio file:", data.audio_file);
              await playAudioResponse(data.audio_file);
            } else {
              console.warn("No audio file in response");
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
      alert("Error accessing microphone: " + error.message);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== "inactive") {
      setRecording(false);
      mediaRecorderRef.current.stop();
    }
  };

  const clearChat = () => {
    setMessages([]);
    setWeatherData(null);
  };
  
  // Language configuration - NOW INCLUDING ALL 22 LANGUAGES
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
    // Clear chat when language changes for a fresh start
    clearChat();
  };

  return (
    <div className="weather-container">
      <div className="weather-wrapper">
        {/* Location Banner */}
        <div className="location-banner">
          <div className="location-icon">📍</div>
          <div className="location-info">
            <h2 className="location-city">{LOCATION.city}</h2>
            <p className="location-state">{LOCATION.state}</p>
          </div>
        </div>

        {/* Weather Card (if available) */}
        {weatherData && (
          <div className="weather-card">
            <div className="weather-icon-large">
              {getWeatherIcon(weatherData.condition)}
            </div>
            <div className="weather-temp">{weatherData.temperature}°C</div>
            <div className="weather-condition-text">{weatherData.condition}</div>
            {(weatherData.wind_speed || weatherData.precipitation !== null) && (
              <div className="weather-details">
                {weatherData.precipitation !== null && (
                  <div className="weather-detail-item">
                    <span className="weather-detail-icon">💧</span>
                    <span>Rain: {weatherData.precipitation}mm</span>
                  </div>
                )}
                {weatherData.wind_speed && (
                  <div className="weather-detail-item">
                    <span className="weather-detail-icon">💨</span>
                    <span>Wind: {weatherData.wind_speed} km/h</span>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* Chat Card */}
        <div className="chat-card">
          <div className="chat-header">
            <h1 className="chat-title">🌾 Weather Assistant</h1>
            <p className="chat-subtitle">Ask about weather in any supported language</p>
          </div>

          {/* NEW: Language Selection */}
          <div className="language-selector">
            <p className="language-prompt">Choose your language:</p>
            {/* Removed Tailwind classes here as they belong in CSS or a separate utility */}
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
          {/* END NEW: Language Selection */}

          <div className="chat-messages">
            {messages.length === 0 ? (
              <div className="empty-state">
                <p className="empty-state-title">Press "Ask About Weather" to start</p>
                <p className="empty-state-subtitle">
                  Examples: "What's the weather today?" • "Weather on 28th September" • "Weather after 2 days"
                </p>
                <p className="empty-state-language">
                  Current Language: **{languages.find(l => l.code === selectedLanguage)?.name}**
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
                <p className="loading-text">Getting weather information...</p>
              </div>
            )}
            {playingAudio && (
              <div className="audio-playing-container">
                <div className="audio-playing-indicator">
                  <span className="audio-icon">🔊</span>
                  <p className="audio-playing-text">Playing weather report...</p>
                </div>
              </div>
            )}
          </div>

          <div className="controls">
            {!recording ? (
              <button
                onClick={startRecording}
                disabled={loading || playingAudio}
                className="btn btn-record"
              >
                🎤 Ask About Weather in **{languages.find(l => l.code === selectedLanguage)?.name}**
              </button>
            ) : (
              <button
                onClick={stopRecording}
                className="btn btn-stop-recording"
              >
                ⏹️ Stop Recording
              </button>
            )}
            {messages.length > 0 && (
              <button
                onClick={clearChat}
                disabled={loading}
                className="btn btn-clear"
              >
                🗑️ Clear
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}