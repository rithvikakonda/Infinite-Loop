import { useState, useRef } from "react";
import "./../weather.css";

export default function Weather() {
  const [messages, setMessages] = useState([]);
  const [recording, setRecording] = useState(false);
  const [loading, setLoading] = useState(false);
  const [playingAudio, setPlayingAudio] = useState(false);
  const [weatherData, setWeatherData] = useState(null);

  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const streamRef = useRef(null);
  const audioRef = useRef(null);

  const LOCATION = {
    lat: "17.385044",
    lon: "78.486671",
    city: "Hyderabad",
    state: "Telangana",
  };

  // --------------------------
  // Audio playback function
  // --------------------------
  const playAudioResponse = async (audioFile) => {
    try {
      setPlayingAudio(true);

      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current = null;
      }

      // Fetch audio as Blob
      const response = await fetch(`http://localhost:8000/weather/outputs/${audioFile}`);
      if (!response.ok) throw new Error("Failed to fetch audio file");

      const audioBlob = await response.blob();
      const audioUrl = URL.createObjectURL(audioBlob);
      console.log("Playing audio from blob URL:", audioUrl);

      const audio = new Audio(audioUrl);
      audioRef.current = audio;

      audio.onended = () => setPlayingAudio(false);
      audio.onerror = (err) => {
        console.error("Audio playback error:", err);
        setPlayingAudio(false);
        setMessages((prev) => [...prev, { type: "error", text: "Failed to play audio response" }]);
      };

      await audio.play();
    } catch (err) {
      console.error("Error playing audio:", err);
      setPlayingAudio(false);
    }
  };

  // --------------------------
  // Microphone recording
  // --------------------------
  const startRecording = async () => {
    try {
      setRecording(true);
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;

      mediaRecorderRef.current = new MediaRecorder(stream);
      audioChunksRef.current = [];

      mediaRecorderRef.current.ondataavailable = (e) => {
        if (e.data.size > 0) audioChunksRef.current.push(e.data);
      };

      mediaRecorderRef.current.onstop = async () => {
        setLoading(true);
        try {
          const blob = new Blob(audioChunksRef.current, { type: "audio/webm" });

          const formData = new FormData();
          formData.append("file", blob, "voice.webm");
          formData.append("lang", "te");
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
              { type: "bot", text: data.answer_text },
            ]);

            // Parse weather data
            const weather = parseWeatherFromResponse(data.answer_text);
            if (weather) setWeatherData(weather);

            // Play audio if backend provides it
            if (data.audio_url) {
              await playAudioResponse(data.audio_url);
            }
          } else {
            setMessages((prev) => [
              ...prev,
              { type: "error", text: `Error: ${data.reply || "Unknown error"}` },
            ]);
          }
        } catch (error) {
          console.error("Error processing audio:", error);
          setMessages((prev) => [
            ...prev,
            { type: "error", text: `Error: ${error.message}` },
          ]);
        } finally {
          setLoading(false);
          if (streamRef.current) {
            streamRef.current.getTracks().forEach((track) => track.stop());
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

  // --------------------------
  // Weather parsing & icons
  // --------------------------
  const getWeatherIcon = (condition) => {
    const c = condition.toLowerCase();
    if (c.includes("clear")) return "☀️";
    if (c.includes("cloud") || c.includes("overcast")) return "☁️";
    if (c.includes("rain") || c.includes("drizzle")) return "🌧️";
    if (c.includes("snow")) return "❄️";
    if (c.includes("thunder")) return "⛈️";
    if (c.includes("fog")) return "🌫️";
    return "🌤️";
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
        precipitation: precipMatch ? parseFloat(precipMatch[1]) : null,
      };
    }
    return null;
  };

  // --------------------------
  // Render UI
  // --------------------------
  return (
    <div className="weather-container">
      <div className="weather-wrapper">
        <div className="location-banner">
          <div className="location-icon">📍</div>
          <div className="location-info">
            <h2 className="location-city">{LOCATION.city}</h2>
            <p className="location-state">{LOCATION.state}</p>
          </div>
        </div>

        {weatherData && (
          <div className="weather-card">
            <div className="weather-icon-large">{getWeatherIcon(weatherData.condition)}</div>
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

        <div className="chat-card">
          <div className="chat-header">
            <h1 className="chat-title">🌾 Weather Assistant</h1>
            <p className="chat-subtitle">Ask about weather in Telugu, Hindi or English</p>
          </div>

          <div className="chat-messages">
            {messages.length === 0 ? (
              <div className="empty-state">
                <p className="empty-state-title">
                  Press "Start Recording" to ask about weather
                </p>
              </div>
            ) : (
              messages.map((msg, idx) => (
                <div key={idx} className={`message-wrapper ${msg.type}`}>
                  <div className={`message-bubble ${msg.type}`}>{msg.text}</div>
                </div>
              ))
            )}
            {loading && <p>Getting weather information...</p>}
            {playingAudio && <p>🔊 Playing weather report...</p>}
          </div>

          <div className="controls">
            {!recording ? (
              <button
                onClick={startRecording}
                disabled={loading || playingAudio}
                className="btn btn-record"
              >
                🎤 Ask About Weather
              </button>
            ) : (
              <button onClick={stopRecording} className="btn btn-stop-recording">
                ⏹️ Stop Recording
              </button>
            )}
            {messages.length > 0 && (
              <button onClick={clearChat} disabled={loading} className="btn btn-clear">
                🗑️ Clear
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
