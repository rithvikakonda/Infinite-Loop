import React, { useState } from "react";

export default function TextToSpeech() {
  const [text, setText] = useState("");
  const [lang, setLang] = useState("en");
  const [gender, setGender] = useState("female");
  const [audioSrc, setAudioSrc] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setAudioSrc(null);

    try {
      const formData = new FormData();
      formData.append("text", text);
      formData.append("target_lang", lang);
      formData.append("tts_gender", gender);

      // Change this URL if your FastAPI runs elsewhere (Render, etc.)
      const res = await fetch("http://127.0.0.1:8000/tts/text-to-speech", {
        method: "POST",
        body: formData,
      });

      if (!res.ok) throw new Error(`HTTP ${res.status}`);

      const data = await res.json();

      // Convert base64 to playable audio source
      const audioUrl = `data:audio/wav;base64,${data.audio_base64}`;
      setAudioSrc(audioUrl);
    } catch (err) {
      console.error("TTS Error:", err);
      setError("Something went wrong while generating audio.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col items-center p-6">
      <h1 className="text-3xl font-bold mb-4 text-gray-800">🗣️ Text to Speech</h1>

      <form
        onSubmit={handleSubmit}
        className="bg-white p-6 rounded-2xl shadow-md w-full max-w-lg"
      >
        <textarea
          className="w-full p-3 border rounded-lg mb-4"
          rows="4"
          placeholder="Enter your text here..."
          value={text}
          onChange={(e) => setText(e.target.value)}
          required
        />

        <div className="flex gap-3 mb-4">
          <select
            className="flex-1 p-2 border rounded-lg"
            value={lang}
            onChange={(e) => setLang(e.target.value)}
          >
            <option value="en">English</option>
            <option value="hi">Hindi</option>
            <option value="es">Spanish</option>
            <option value="fr">French</option>
            <option value="de">German</option>
          </select>

          <select
            className="flex-1 p-2 border rounded-lg"
            value={gender}
            onChange={(e) => setGender(e.target.value)}
          >
            <option value="female">Female</option>
            <option value="male">Male</option>
          </select>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="bg-blue-600 text-white w-full py-2 rounded-lg hover:bg-blue-700 transition"
        >
          {loading ? "Generating..." : "Convert to Speech"}
        </button>
      </form>

      {error && <p className="text-red-500 mt-4">{error}</p>}

      {audioSrc && (
        <div className="mt-6">
          <h2 className="text-lg font-semibold mb-2">🔊 Preview</h2>
          <audio controls src={audioSrc} className="w-full max-w-md" />
        </div>
      )}
    </div>
  );
}
