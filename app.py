"""
Backend sederhana buat web chat AI, membungkus package Python
unofficial 'perchance' (https://github.com/eeemoon/perchance)
supaya bisa dipanggil lewat REST API dari frontend (HTML/JS di Bolt.new dsb).

CATATAN PENTING:
- Ini pakai package UNOFFICIAL. Bisa berhenti berfungsi kapan saja
  kalau Perchance mengubah struktur internal mereka.
- Harus di-deploy ke server yang mendukung Python (Render, Railway,
  PythonAnywhere, dll) -- TIDAK bisa jalan di Bolt.new (Node.js only).
"""

import asyncio
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from perchance import TextGenerator

app = Flask(__name__)
CORS(app)  # supaya frontend dari domain lain (Bolt.new / hosting statis) boleh manggil


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/api/chat", methods=["POST"])
def chat():
    """
    Body JSON yang diharapkan:
    { "message": "teks pertanyaan user" }

    Balasan JSON:
    { "reply": "teks jawaban AI" }
    """
    data = request.get_json(silent=True) or {}
    prompt = (data.get("message") or "").strip()

    if not prompt:
        return jsonify({"error": "Field 'message' kosong"}), 400

    try:
        reply = asyncio.run(generate_reply(prompt))
        return jsonify({"reply": reply})
    except Exception as e:
        # Perchance unofficial API bisa gagal sewaktu-waktu (timeout, rate limit,
        # perubahan struktur di sisi mereka) -- selalu tangani errornya biar
        # frontend nggak nge-hang.
        return jsonify({"error": f"Gagal generate balasan: {str(e)}"}), 502


async def generate_reply(prompt: str) -> str:
    async with TextGenerator() as gen:
        chunks = []
        async for chunk in gen.stream(prompt):
            chunks.append(chunk)
        return "".join(chunks)


if __name__ == "__main__":
    # Untuk development lokal. Di production (Render/Railway), biasanya
    # dijalankan lewat gunicorn -- lihat Procfile / start command.
    app.run(host="0.0.0.0", port=5000, debug=True)
