// import React, { useState } from "react";
// import "./index.css";

// export default function App() {
//   const [video, setVideo] = useState(null);
//   const [sourceLang, setSourceLang] = useState("english");
//   const [targetLang, setTargetLang] = useState("hindi");
//   const [loading, setLoading] = useState(false);
//   const [result, setResult] = useState("");
//   const [audioUrl, setAudioUrl] = useState("");

//   const handleUpload = async () => {
//     if (!video) {
//       alert("Please select a video!");
//       return;
//     }

//     setLoading(true);
//     const formData = new FormData();
//     formData.append("video_file", video);
//     formData.append("source_lang", sourceLang);
//     formData.append("target_lang", targetLang);
//     console.log("Uploading video:", video.name, "Source:", sourceLang, "Target:", targetLang);
//     try {
//       const res = await fetch("http://127.0.0.1:8000/video-to-translate-and-speak", {
//         method: "POST",
//         body: formData,
//       });
//       const data = await res.json();

//       setResult(data.translated_text || JSON.stringify(data));

//       if (data.audio_base64) {
//         // Convert base64 to Blob and URL
//         const audioBlob = new Blob(
//           [Uint8Array.from(atob(data.audio_base64), c => c.charCodeAt(0))],
//           { type: "audio/wav" }
//         );
//         const url = URL.createObjectURL(audioBlob);
//         setAudioUrl(url);
//       }
//     } catch (err) {
//       setResult("Error: " + err.message);
//     } finally {
//       setLoading(false);
//     }
//   };

//   return (
//     <div className="container">
//       <h1>🎬 Video Translation App</h1>

//       <div className="input-group">
//         <label>🎞️ Select Video:</label>
//         <input type="file" accept="video/*" onChange={(e) => setVideo(e.target.files[0])} />
//       </div>

//       <div className="input-group">
//         <label>🌐 Source Language:</label>
//         <select value={sourceLang} onChange={(e) => setSourceLang(e.target.value)}>
//           <option value="english">English</option>
//           <option value="hindi">Hindi</option>
//           <option value="telugu">Telugu</option>
//           <option value="tamil">Tamil</option>
//           <option value="bengali">Bengali</option>
//         </select>
//       </div>

//       <div className="input-group">
//         <label>🎯 Target Language:</label>
//         <select value={targetLang} onChange={(e) => setTargetLang(e.target.value)}>
//           <option value="hindi">Hindi</option>
//           <option value="telugu">Telugu</option>
//           <option value="tamil">Tamil</option>
//           <option value="bengali">Bengali</option>
//           <option value="english">English</option>
//         </select>
//       </div>

//       <button onClick={handleUpload} disabled={loading}>
//         {loading ? "Processing..." : "Upload & Translate"}
//       </button>

//       {audioUrl && (
//         <div className="audio-box">
//           <h3>🔊 Translated Audio</h3>
//           <audio controls src={audioUrl}></audio>
//           <br />
//           <a href={audioUrl} download="translated_audio.wav" className="download-btn">
//             ⬇️ Download Audio
//           </a>
//         </div>
//       )}
//       {result && (
//         <div className="result-box">
//           <strong>Translated Text:</strong>
//           <p>{result}</p>
//         </div>
//       )}

//     </div>
//   );
// }

import React from "react";
import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import VideoTranslator from "./components/VideoTranslator";
import DocumentTranslator from "./components/DocumentTranslator";
import Conversation from "./components/Conversation";
import Weather from "./components/Weather";
import SpeechToSpeech from "./components/SpeechToSpeech";

function Home() {
  return (
    <div className="container">
      <h1>🏠 Welcome to My App</h1>
      <p>Use this app to translate and dub videos into other languages.</p>
      <Link to="/translate" className="btn">Go to Video Translator</Link><br /><br />
      <Link to="/document" className="btn">Go to Document Translator</Link><br /><br />
      <Link to="/conversation" className="btn">Go to Conversation</Link><br /><br />
      <Link to="/weather" className="btn">Go to Weather Report</Link><br /><br />
      <Link to="/speech" className="btn">Go to Speech-to-Speech</Link>
    </div>
  );
}

export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/translate" element={<VideoTranslator />} />
        <Route path="/document" element={<DocumentTranslator />} />
        <Route path="/conversation" element={<Conversation />} />
        <Route path="/weather" element={<Weather />} />
        <Route path="/speech" element={<SpeechToSpeech />} />
      </Routes>
    </Router>
  );
}
