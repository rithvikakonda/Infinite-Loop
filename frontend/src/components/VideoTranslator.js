// import React, { useState } from "react";
// import { motion } from "framer-motion";
// import { Upload, Play, Loader2 } from "lucide-react";

// export default function VideoTranslator() {
//   const [video, setVideo] = useState(null);
//   const [targetLang, setTargetLang] = useState("hi");
//   const [ttsGender, setTtsGender] = useState("female");
//   const [loading, setLoading] = useState(false);
//   const [result, setResult] = useState(null);

//   const handleUpload = (e) => {
//     setVideo(e.target.files[0]);
//   };

//   const handleSubmit = async () => {
//     if (!video) {
//       alert("Please upload a video first!");
//       return;
//     }

//     const formData = new FormData();
//     formData.append("video_file", video);
//     formData.append("target_lang", targetLang);
//     formData.append("tts_gender", ttsGender);

//     try {
//       setLoading(true);
//       setResult(null);

//       const res = await fetch("http://127.0.0.1:8000/video-to-translate-and-speak", {
//         method: "POST",
//         body: formData,
//       });

//       const data = await res.json();
//       if (!res.ok) throw new Error(data.detail || "Translation failed");
//       setResult(data);
//     } catch (err) {
//       alert("Error: " + err.message);
//     } finally {
//       setLoading(false);
//     }
//   };

//   return (
//     <motion.div
//       className="max-w-2xl mx-auto mt-12 bg-white shadow-lg rounded-2xl p-6 space-y-6 border border-gray-100"
//       initial={{ opacity: 0, y: 20 }}
//       animate={{ opacity: 1, y: 0 }}
//       transition={{ duration: 0.4 }}
//     >
//       <h1 className="text-2xl font-bold text-center text-gray-800">
//         🎬 Video Translator & Voice Generator
//       </h1>

//       <div className="flex flex-col space-y-3">
//         <label className="font-semibold">Upload a video (max 20 sec)</label>
//         <input
//           type="file"
//           accept="video/*"
//           onChange={handleUpload}
//           className="border border-gray-300 rounded-lg p-2"
//         />
//       </div>

//       <div className="grid grid-cols-2 gap-4">
//         <div>
//           <label className="font-semibold">Target Language</label>
//           <select
//             value={targetLang}
//             onChange={(e) => setTargetLang(e.target.value)}
//             className="w-full border border-gray-300 rounded-lg p-2"
//           >
//             <option value="hi">Hindi</option>
//             <option value="ta">Tamil</option>
//             <option value="te">Telugu</option>
//             <option value="bn">Bengali</option>
//             <option value="ml">Malayalam</option>
//           </select>
//         </div>

//         <div>
//           <label className="font-semibold">Voice Gender</label>
//           <select
//             value={ttsGender}
//             onChange={(e) => setTtsGender(e.target.value)}
//             className="w-full border border-gray-300 rounded-lg p-2"
//           >
//             <option value="female">Female</option>
//             <option value="male">Male</option>
//           </select>
//         </div>
//       </div>

//       <button
//         onClick={handleSubmit}
//         disabled={loading}
//         className="flex items-center justify-center gap-2 w-full bg-blue-600 text-white py-2 rounded-lg font-medium hover:bg-blue-700 transition"
//       >
//         {loading ? (
//           <>
//             <Loader2 className="animate-spin" /> Processing...
//           </>
//         ) : (
//           <>
//             <Upload /> Upload & Translate
//           </>
//         )}
//       </button>

//       {result && (
//         <motion.div
//           className="mt-6 bg-gray-50 rounded-lg p-4 border border-gray-200 space-y-3"
//           initial={{ opacity: 0 }}
//           animate={{ opacity: 1 }}
//         >
//           <h2 className="font-semibold text-gray-700">Result:</h2>
//           <p className="text-sm">
//             <strong>Original:</strong> {result.source_text}
//           </p>
//           <p className="text-sm">
//             <strong>Translated:</strong> {result.translated_text}
//           </p>

//           {result.merged_audio_file && (
//             <div className="mt-4 flex flex-col items-center">
//               <audio controls className="w-full">
//                 <source src={result.merged_audio_file} type="audio/wav" />
//               </audio>
//               <p className="text-sm text-gray-500 mt-1 flex items-center gap-1">
//                 <Play size={16} /> TTS audio generated ({result.tts_chunks} chunks)
//               </p>
//             </div>
//           )}
//         </motion.div>
//       )}
//     </motion.div>
//   );
// }

import React, { useState } from "react";
import "../index.css";

export default function VideoTranslator() {
  const [video, setVideo] = useState(null);
  const [sourceLang, setSourceLang] = useState("english");
  const [targetLang, setTargetLang] = useState("hindi");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState("");
  const [audioUrl, setAudioUrl] = useState("");

  const handleUpload = async () => {
    if (!video) {
      alert("Please select a video!");
      return;
    }

    setLoading(true);
    const formData = new FormData();
    formData.append("video_file", video);
    formData.append("source_lang", sourceLang);
    formData.append("target_lang", targetLang);

    console.log("Uploading video:", video.name, "Source:", sourceLang, "Target:", targetLang);

    try {
      const res = await fetch("http://127.0.0.1:8000/translate/video-to-translate-and-speak", {
        method: "POST",
        body: formData,
      });
      const data = await res.json();

      setResult(data.translated_text || JSON.stringify(data));

      if (data.audio_base64) {
        const audioBlob = new Blob(
          [Uint8Array.from(atob(data.audio_base64), c => c.charCodeAt(0))],
          { type: "audio/wav" }
        );
        const url = URL.createObjectURL(audioBlob);
        setAudioUrl(url);
      }
    } catch (err) {
      setResult("Error: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <h1>🎬 Video Translation App</h1>

      <div className="input-group">
        <label>🎞️ Select Video:</label>
        <input type="file" accept="video/*" onChange={(e) => setVideo(e.target.files[0])} />
      </div>

      <div className="input-group">
        <label>🌐 Source Language:</label>
        <select value={sourceLang} onChange={(e) => setSourceLang(e.target.value)}>
          <option value="english">English</option>
          <option value="hindi">Hindi</option>
          <option value="telugu">Telugu</option>
          <option value="tamil">Tamil</option>
          <option value="bengali">Bengali</option>
        </select>
      </div>

      <div className="input-group">
        <label>🎯 Target Language:</label>
        <select value={targetLang} onChange={(e) => setTargetLang(e.target.value)}>
          <option value="hindi">Hindi</option>
          <option value="telugu">Telugu</option>
          <option value="tamil">Tamil</option>
          <option value="bengali">Bengali</option>
          <option value="english">English</option>
        </select>
      </div>

      <button onClick={handleUpload} disabled={loading}>
        {loading ? "Processing..." : "Upload & Translate"}
      </button>

      {audioUrl && (
        <div className="audio-box">
          <h3>🔊 Translated Audio</h3>
          <audio controls src={audioUrl}></audio>
          <br />
          <a href={audioUrl} download="translated_audio.wav" className="download-btn">
            ⬇️ Download Audio
          </a>
        </div>
      )}

      {result && (
        <div className="result-box">
          <strong>Translated Text:</strong>
          <p>{result}</p>
        </div>
      )}
    </div>
  );
}

