// import React, { useState } from "react";
// import axios from "axios";
// import { AiOutlineUpload, AiOutlineLoading3Quarters } from "react-icons/ai";
// import "../index.css";

// function DocumentTranslator() {
//   const [file, setFile] = useState(null);
//   const [sourceLang, setSourceLang] = useState("");
//   const [targetLang, setTargetLang] = useState("");
//   const [loading, setLoading] = useState(false);
//   const [result, setResult] = useState(null);
//   const [error, setError] = useState(null);

//   const handleSubmit = async (e) => {
//     e.preventDefault();
//     if (!file || !sourceLang || !targetLang) {
//       alert("Please select a file and languages!");
//       return;
//     }

//     const formData = new FormData();
//     formData.append("file", file);
//     formData.append("source_lang", sourceLang);
//     formData.append("target_lang", targetLang);

//     try {
//       setLoading(true);
//       setError(null);
//       setResult(null);
//       const res = await axios.post("http://127.0.0.1:8000/document/document-translator", formData, {
//         headers: { "Content-Type": "multipart/form-data" },
//       });
//       setResult(res.data);
//     } catch (err) {
//       setError(err.response?.data?.detail || "Upload failed");
//     } finally {
//       setLoading(false);
//     }
//   };

//   return (
//     <div className="w-full max-w-lg bg-white rounded-3xl shadow-lg p-8">
//       <form onSubmit={handleSubmit} className="flex flex-col gap-6">
//         <label className="block">
//           <span className="text-gray-700 font-semibold">Select File</span>
//           <div className="mt-2 flex items-center border-dashed border-2 border-gray-300 rounded-xl p-4 cursor-pointer hover:border-blue-400 transition">
//             <AiOutlineUpload size={24} className="text-gray-400 mr-3" />
//             <span className="text-gray-500">{file ? file.name : "Click to upload or drag file here"}</span>
//             <input
//               type="file"
//               onChange={(e) => setFile(e.target.files[0])}
//               className="absolute w-full h-full opacity-0 cursor-pointer"
//             />
//           </div>
//         </label>

//         <div className="flex gap-4">
//           <div className="flex-1">
//             <label className="block">
//               <span className="text-gray-700 font-semibold">Source Language</span>
//               <input
//                 type="text"
//                 placeholder="e.g., en"
//                 value={sourceLang}
//                 onChange={(e) => setSourceLang(e.target.value)}
//                 className="mt-2 block w-full border border-gray-300 rounded-lg p-3 focus:ring-2 focus:ring-blue-400 focus:outline-none"
//               />
//             </label>
//           </div>

//           <div className="flex-1">
//             <label className="block">
//               <span className="text-gray-700 font-semibold">Target Language</span>
//               <input
//                 type="text"
//                 placeholder="e.g., hi"
//                 value={targetLang}
//                 onChange={(e) => setTargetLang(e.target.value)}
//                 className="mt-2 block w-full border border-gray-300 rounded-lg p-3 focus:ring-2 focus:ring-blue-400 focus:outline-none"
//               />
//             </label>
//           </div>
//         </div>

//         <button
//           type="submit"
//           disabled={loading}
//           className="flex items-center justify-center bg-blue-600 text-white py-3 rounded-xl font-semibold hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
//         >
//           {loading ? (
//             <>
//               <AiOutlineLoading3Quarters className="animate-spin mr-2" />
//               Processing...
//             </>
//           ) : (
//             "Translate"
//           )}
//         </button>
//       </form>

//       {error && <p className="text-red-600 mt-4 text-center">{error}</p>}

//       {result && (
//         <div className="mt-8">
//           <h2 className="text-2xl font-semibold text-gray-800 mb-2">Result</h2>
//           <div className="bg-gray-100 p-4 rounded-lg whitespace-pre-wrap max-h-96 overflow-auto">
//             {result.translated_text || result.translated_pages?.join("\n\n")}
//           </div>
//           {result.output_file && (
//             <a
//               href={`http://127.0.0.1:8000/document/download/${result.output_file}`}
//               target="_blank"
//               rel="noopener noreferrer"
//               className="block mt-4 text-blue-600 font-medium underline"
//             >
//               Download Translated File
//             </a>
//           )}
//         </div>
//       )}
//     </div>
//   );
// }

// export default DocumentTranslator;

import React, { useState } from "react";
import axios from "axios";
import { AiOutlineUpload, AiOutlineLoading3Quarters } from "react-icons/ai";
import "./../index.css";

function TranslatorApp() {
  const [file, setFile] = useState(null);
  const [video, setVideo] = useState(null);
  const [sourceLang, setSourceLang] = useState("");
  const [targetLang, setTargetLang] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [audioUrl, setAudioUrl] = useState(null);
  const [error, setError] = useState(null);

  const handleDocumentUpload = async (e) => {
    e.preventDefault();
    if (!file || !sourceLang || !targetLang) {
      alert("Please select a file and languages!");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);
    formData.append("source_lang", sourceLang);
    formData.append("target_lang", targetLang);

    try {
      setLoading(true);
      setError(null);
      setResult(null);
      const res = await axios.post(
        "http://127.0.0.1:8000/document/document-translator",
        formData,
        { headers: { "Content-Type": "multipart/form-data" } }
      );
      setResult(res.data.translated_text || res.data.translated_pages?.join("\n\n"));
    } catch (err) {
      setError(err.response?.data?.detail || "Upload failed");
    } finally {
      setLoading(false);
    }
  };

  const handleVideoUpload = async () => {
    if (!video || !sourceLang || !targetLang) {
      alert("Please select a video and languages!");
      return;
    }

    const formData = new FormData();
    formData.append("video", video);
    formData.append("source_lang", sourceLang);
    formData.append("target_lang", targetLang);

    try {
      setLoading(true);
      setError(null);
      setResult(null);
      setAudioUrl(null);

      const res = await axios.post(
        "http://127.0.0.1:8000/video/video-translator",
        formData,
        { headers: { "Content-Type": "multipart/form-data" }, responseType: "blob" }
      );

      const url = window.URL.createObjectURL(new Blob([res.data], { type: "audio/wav" }));
      setAudioUrl(url);
    } catch (err) {
      setError(err.response?.data?.detail || "Video translation failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <h1>🎬 Translator App</h1>

      {/* Document Translator */}
      <form onSubmit={handleDocumentUpload}>
        <label>
          📄 Select Document:
          <input type="file" onChange={(e) => setFile(e.target.files[0])} />
        </label>

        <label>
          🌐 Source Language:
          <select value={sourceLang} onChange={(e) => setSourceLang(e.target.value)}>
            <option value="">Select</option>
            <option value="english">English</option>
            <option value="hindi">Hindi</option>
            <option value="telugu">Telugu</option>
            <option value="tamil">Tamil</option>
            <option value="bengali">Bengali</option>
          </select><br />
        </label>

        <label>
          🎯 Target Language:
          <select value={targetLang} onChange={(e) => setTargetLang(e.target.value)}>
            <option value="">Select</option>
            <option value="hindi">Hindi</option>
            <option value="telugu">Telugu</option>
            <option value="tamil">Tamil</option>
            <option value="bengali">Bengali</option>
            <option value="english">English</option>
          </select>
        </label>

        <button type="submit" disabled={loading}>
          {loading ? (
            <>
              <AiOutlineLoading3Quarters className="loading-icon" />
              Processing...
            </>
          ) : (
            "Translate Document"
          )}
        </button>
      </form>

      {/* Video Translator */}
      {/* <label>
        🎞️ Select Video:
        <input type="file" accept="video/*" onChange={(e) => setVideo(e.target.files[0])} />
      </label> */}

      {/* <label> */}
        {/* 🌐 Source Language:
        <select value={sourceLang} onChange={(e) => setSourceLang(e.target.value)}>
          <option value="">Select</option>
          <option value="english">English</option>
          <option value="hindi">Hindi</option>
          <option value="telugu">Telugu</option>
          <option value="tamil">Tamil</option>
          <option value="bengali">Bengali</option>
        </select>
      </label>

      <label>
        🎯 Target Language:
        <select value={targetLang} onChange={(e) => setTargetLang(e.target.value)}>
          <option value="">Select</option>
          <option value="hindi">Hindi</option>
          <option value="telugu">Telugu</option>
          <option value="tamil">Tamil</option>
          <option value="bengali">Bengali</option>
          <option value="english">English</option>
        </select>
      </label> */}

      {/* <button onClick={handleVideoUpload} disabled={loading}>
        {loading ? "Processing..." : "Upload & Translate Video"}
      </button> */}

      {/* Display error */}
      {/* {error && <p className="text-red-600 mt-4 text-center">{error}</p>} */}

      {/* Document Translation Result */}
      {/* {result && (
        <div className="result-box">
          <strong>Translated Text:</strong>
          <p>{result}</p>
        </div>
      )} */}

      {/* Video Translation Audio */}
      {/* {audioUrl && (
        <div className="result-box">
          <strong>🔊 Translated Audio:</strong>
          <audio controls src={audioUrl}></audio>
          <br />
          <a href={audioUrl} download="translated_audio.wav" className="download-link">
            ⬇️ Download Audio
          </a>
        </div>
      )} */}
    </div>
  );
}

export default TranslatorApp;