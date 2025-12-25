import os
from flask import Flask, render_template_string, request, send_file, jsonify
import mido
from mido import Message, MidiFile, MidiTrack

app = Flask(__name__)

# 保存用の一時ディレクトリ
EXPORT_DIR = "exports"
if not os.path.exists(EXPORT_DIR):
    os.makedirs(EXPORT_DIR)

# HTML Template (VexFlowを使用した楽譜UI)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Python MIDI Editor</title>
    <script src="https://cdn.jsdelivr.net/npm/vexflow@4.2.2/build/cjs/vexflow.js"></script>
    <style>
        body { font-family: sans-serif; text-align: center; background: #f4f4f4; }
        #canvas-container { background: white; margin: 20px auto; padding: 20px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); width: fit-content; cursor: crosshair; }
        .controls { margin-top: 20px; }
        button { padding: 10px 20px; font-size: 16px; cursor: pointer; background: #007bff; color: white; border: none; border-radius: 5px; }
        button:hover { background: #0056b3; }
        #status { margin-top: 10px; color: #666; }
    </style>
</head>
<body>
    <h1>Simple Score MIDI Editor</h1>
    <div id="canvas-container"></div>
    <div class="controls">
        <button onclick="clearNotes()">Clear</button>
        <button onclick="exportMidi()">Export MIDI</button>
        <button onclick="playMidi()" id="playBtn">Play (Browser Preview)</button>
    </div>
    <p id="status">Click on the staff to add notes (C4 to B5).</p>

    <script>
        const { Renderer, Stave, StaveNote, Formatter, Voice } = Vex.Flow;
        let notes = [];
        const container = document.getElementById('canvas-container');

        // 描画関数
        function drawScore() {
            container.innerHTML = "";
            const renderer = new Renderer(container, Renderer.Backends.SVG);
            renderer.resize(600, 200);
            const context = renderer.getContext();
            const stave = new Stave(10, 40, 550);
            stave.addClef("treble").setContext(context).draw();

            if (notes.length > 0) {
                const staveNotes = notes.map(n => new StaveNote({ keys: [n], duration: "q" }));
                const voice = new Voice({ num_beats: notes.length, beat_value: 4 });
                voice.addTickables(staveNotes);
                new Formatter().joinVoices([voice]).format([voice], 500);
                voice.draw(context, stave);
            }
        }

        // クリックで音符追加
        container.addEventListener('mousedown', (e) => {
            const rect = container.getBoundingClientRect();
            const y = e.clientY - rect.top;
            
            // 簡易的な高さ判定 (C4〜B5)
            const pitches = ["b/5", "a/5", "g/5", "f/5", "e/5", "d/5", "c/5", "b/4", "a/4", "g/4", "f/4", "e/4", "d/4", "c/4"];
            const idx = Math.floor((y - 40) / 10);
            if (idx >= 0 && idx < pitches.length) {
                notes.push(pitches[idx]);
                drawScore();
            }
        });

        function clearNotes() { notes = []; drawScore(); }

        // MIDIエクスポート処理 (Pythonへ送信)
        async function exportMidi() {
            const response = await fetch('/save_midi', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ notes: notes })
            });
            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = "output.mid";
                a.click();
            }
        }

        // 簡易再生 (Web Audio API)
        function playMidi() {
            const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            const freqMap = { "c/4": 261.63, "d/4": 293.66, "e/4": 329.63, "f/4": 349.23, "g/4": 392.00, "a/4": 440.00, "b/4": 493.88, "c/5": 523.25, "d/5": 587.33, "e/5": 659.25, "f/5": 698.46, "g/5": 783.99, "a/5": 880.00, "b/5": 987.77 };
            
            notes.forEach((note, i) => {
                const osc = audioCtx.createOscillator();
                const gain = audioCtx.createGain();
                osc.type = 'sine';
                osc.frequency.setValueAtTime(freqMap[note], audioCtx.currentTime + i * 0.5);
                gain.gain.setValueAtTime(0.1, audioCtx.currentTime + i * 0.5);
                gain.gain.exponentialRampToValueAtTime(0.0001, audioCtx.currentTime + i * 0.5 + 0.4);
                osc.connect(gain);
                gain.connect(audioCtx.destination);
                osc.start(audioCtx.currentTime + i * 0.5);
                osc.stop(audioCtx.currentTime + i * 0.5 + 0.5);
            });
        }

        drawScore();
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/save_midi', methods=['POST'])
def save_midi():
    data = request.json
    ui_notes = data.get('notes', [])
    
    mid = MidiFile()
    track = MidiTrack()
    mid.tracks.append(track)
    
    # ノート変換用辞書
    note_to_midi = {
        "c/4": 60, "d/4": 62, "e/4": 64, "f/4": 65, "g/4": 67, "a/4": 69, "b/4": 71,
        "c/5": 72, "d/5": 74, "e/5": 76, "f/5": 77, "g/5": 79, "a/5": 81, "b/5": 83
    }

    track.append(Message('program_change', program=0, time=0))
    
    for n in ui_notes:
        midi_val = note_to_midi.get(n, 60)
        track.append(Message('note_on', note=midi_val, velocity=64, time=0))
        track.append(Message('note_off', note=midi_val, velocity=64, time=480))

    filepath = os.path.join(EXPORT_DIR, "output.mid")
    mid.save(filepath)
    return send_file(filepath, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
