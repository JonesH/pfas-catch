"""Main file rendering the APIs"""

from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles


from src.utils import (
    get_best_adsorber_pfas_table,
    get_filename,
    get_molecules,
    get_smiles,
)

app = FastAPI()

HTML_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Match PFAS Catch</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/3Dmol/2.0.4/3Dmol-min.js"></script>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 {
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
        }
        .section {
            padding: 30px;
            border-bottom: 1px solid #eee;
        }
        .section:last-child {
            border-bottom: none;
        }
        .section h2 {
            color: #333;
            margin-bottom: 20px;
            font-size: 1.8em;
            font-weight: 400;
        }
        .input-section {
            background: #f8f9fa;
        }
        .input-group {
            display: flex;
            gap: 15px;
            align-items: center;
            flex-wrap: wrap;
        }
        input[type="text"] {
            flex: 1;
            min-width: 300px;
            padding: 15px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 16px;
            transition: border-color 0.3s;
        }
        input[type="text"]:focus {
            outline: none;
            border-color: #4facfe;
        }
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            transition: transform 0.2s;
        }
        .btn:hover {
            transform: translateY(-2px);
        }
        .btn-voice {
            background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
            color: white;
            border: none;
            padding: 15px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            transition: all 0.3s;
            display: flex;
            align-items: center;
            gap: 8px;
            min-width: 120px;
            justify-content: center;
        }
        .btn-voice:hover {
            transform: translateY(-2px);
        }
        .btn-voice.recording {
            background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
            animation: pulse 1.5s infinite;
        }
        .btn-voice.processing {
            background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%);
        }
        @keyframes pulse {
            0% { box-shadow: 0 0 0 0 rgba(231, 76, 60, 0.7); }
            70% { box-shadow: 0 0 0 10px rgba(231, 76, 60, 0); }
            100% { box-shadow: 0 0 0 0 rgba(231, 76, 60, 0); }
        }
        .voice-status {
            margin-top: 10px;
            padding: 10px;
            border-radius: 5px;
            font-size: 14px;
            text-align: center;
        }
        .voice-status.listening {
            background: #fff3cd;
            color: #856404;
            border: 1px solid #ffeaa7;
        }
        .voice-status.processing {
            background: #d1ecf1;
            color: #0c5460;
            border: 1px solid #bee5eb;
        }
        .voice-status.error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        .molecule-container {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-top: 20px;
        }
        .molecule-viewer {
            border: 2px solid #eee;
            border-radius: 10px;
            overflow: hidden;
            background: #f8f9fa;
        }
        .molecule-title {
            background: #667eea;
            color: white;
            padding: 15px;
            margin: 0;
            font-size: 1.2em;
            text-align: center;
        }
        .viewer-2d {
            text-align: center;
            padding: 20px;
        }
        .viewer-2d img {
            max-width: 100%;
            height: auto;
            border-radius: 8px;
        }
        .viewer-3d {
            width: 100%;
            height: 400px;
            position: relative;
        }
        .adsorber-section {
            background: #f1f8ff;
        }
        .adsorber-info {
            background: #e8f4f8;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .best-adsorber {
            font-size: 1.3em;
            color: #2c5aa0;
            font-weight: 600;
            margin-bottom: 10px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            background: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        th, td {
            padding: 15px;
            text-align: left;
            border-bottom: 1px solid #eee;
        }
        th {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            font-weight: 500;
        }
        tr:hover {
            background: #f8f9fa;
        }
        .loading {
            text-align: center;
            padding: 40px;
            color: #666;
        }
        .error {
            background: #fee;
            color: #c33;
            padding: 15px;
            border-radius: 8px;
            margin-top: 15px;
        }
        @media (max-width: 768px) {
            .molecule-container {
                grid-template-columns: 1fr;
            }
            .input-group {
                flex-direction: column;
                align-items: stretch;
            }
            input[type="text"] {
                min-width: auto;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Match PFAS Catch</h1>
            <p>Analyze PFAS molecules and find optimal adsorbers</p>
        </div>

        <!-- Input Section -->
        <div class="section input-section">
            <h2>🔍 Analysis Input</h2>
            <form id="analysisForm">
                <div class="input-group">
                    <input type="text" id="queryInput" placeholder="Enter PFAS compound (e.g., per fluoro butanoic acid)" required>
                    <button type="submit" class="btn">Analyze</button>
                    <button type="button" id="voiceBtn" class="btn-voice">
                        <span id="voiceIcon">🎤</span>
                        <span id="voiceText">Voice</span>
                    </button>
                </div>
                <div id="voiceStatus" class="voice-status" style="display: none;"></div>
            </form>
        </div>

        <!-- Results Container -->
        <div id="resultsContainer" style="display: none;">
            <!-- PFAS Molecule Section -->
            <div class="section">
                <h2>🧬 PFAS Molecule</h2>
                <div class="molecule-container">
                    <div class="molecule-viewer">
                        <h3 class="molecule-title">2D Structure</h3>
                        <div class="viewer-2d">
                            <img id="pfas2d" src="" alt="PFAS 2D Structure">
                        </div>
                    </div>
                    <div class="molecule-viewer">
                        <h3 class="molecule-title">3D Structure</h3>
                        <div id="pfas3d" class="viewer-3d"></div>
                    </div>
                </div>
            </div>

            <!-- Adsorber Section -->
            <div class="section adsorber-section">
                <h2>🎯 Best Adsorber</h2>
                <div class="adsorber-info">
                    <div class="best-adsorber" id="bestAdsorberName"></div>
                    <p>This adsorber shows the highest binding affinity for the target PFAS molecule.</p>
                </div>
                <div class="molecule-container">
                    <div class="molecule-viewer">
                        <h3 class="molecule-title">2D Structure</h3>
                        <div class="viewer-2d">
                            <img id="adsorber2d" src="" alt="Adsorber 2D Structure">
                        </div>
                    </div>
                    <div class="molecule-viewer">
                        <h3 class="molecule-title">3D Structure</h3>
                        <div id="adsorber3d" class="viewer-3d"></div>
                    </div>
                </div>
            </div>

            <!-- Results Table Section -->
            <div class="section">
                <h2>📊 Binding Analysis Results</h2>
                <table id="resultsTable">
                    <thead>
                        <tr>
                            <th>PFAS</th>
                            <th>ADSORBER Variant</th>
                            <th>Binding Distance (nm)</th>
                            <th>Binding Free Energy (kJ/mol)</th>
                            <th>Dissociation Constant (M)</th>
                        </tr>
                    </thead>
                    <tbody></tbody>
                </table>
            </div>
        </div>

        <!-- Loading/Error States -->
        <div id="loadingState" class="loading" style="display: none;">
            <p>🔬 Analyzing compound...</p>
        </div>
        <div id="errorState" class="error" style="display: none;"></div>
    </div>

    <script>
        // Speech Recognition Setup
        let recognition = null;
        let isListening = false;

        // Check if speech recognition is supported
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            recognition = new SpeechRecognition();
            
            recognition.continuous = false;
            recognition.interimResults = false;
            recognition.lang = 'en-US';
            
            recognition.onstart = function() {
                isListening = true;
                updateVoiceButton('listening');
                showVoiceStatus('Listening... Speak now!', 'listening');
            };
            
            recognition.onresult = function(event) {
                const transcript = event.results[0][0].transcript;
                document.getElementById('queryInput').value = transcript;
                showVoiceStatus(`Heard: "${transcript}"`, 'processing');
                setTimeout(() => hideVoiceStatus(), 3000);
            };
            
            recognition.onerror = function(event) {
                console.error('Speech recognition error:', event.error);
                let errorMessage = 'Speech recognition error occurred.';
                
                switch(event.error) {
                    case 'no-speech':
                        errorMessage = 'No speech detected. Please try again.';
                        break;
                    case 'audio-capture':
                        errorMessage = 'Microphone not available. Please check permissions.';
                        break;
                    case 'not-allowed':
                        errorMessage = 'Microphone access denied. Please enable microphone permissions.';
                        break;
                    case 'network':
                        errorMessage = 'Network error. Please check your connection.';
                        break;
                }
                
                showVoiceStatus(errorMessage, 'error');
                setTimeout(() => hideVoiceStatus(), 5000);
            };
            
            recognition.onend = function() {
                isListening = false;
                updateVoiceButton('idle');
            };
        }

        // Voice button event listener
        document.getElementById('voiceBtn').addEventListener('click', function() {
            if (!recognition) {
                showVoiceStatus('Speech recognition not supported in this browser.', 'error');
                setTimeout(() => hideVoiceStatus(), 3000);
                return;
            }

            if (isListening) {
                recognition.stop();
            } else {
                recognition.start();
            }
        });

        function updateVoiceButton(state) {
            const voiceBtn = document.getElementById('voiceBtn');
            const voiceIcon = document.getElementById('voiceIcon');
            const voiceText = document.getElementById('voiceText');
            
            voiceBtn.className = 'btn-voice';
            
            switch(state) {
                case 'listening':
                    voiceBtn.classList.add('recording');
                    voiceIcon.textContent = '🔴';
                    voiceText.textContent = 'Listening...';
                    break;
                case 'processing':
                    voiceBtn.classList.add('processing');
                    voiceIcon.textContent = '⏳';
                    voiceText.textContent = 'Processing...';
                    break;
                default:
                    voiceIcon.textContent = '🎤';
                    voiceText.textContent = 'Voice';
            }
        }

        function showVoiceStatus(message, type) {
            const statusEl = document.getElementById('voiceStatus');
            statusEl.textContent = message;
            statusEl.className = `voice-status ${type}`;
            statusEl.style.display = 'block';
        }

        function hideVoiceStatus() {
            document.getElementById('voiceStatus').style.display = 'none';
        }

        // Form submission logic
        document.getElementById('analysisForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const query = document.getElementById('queryInput').value.trim();
            if (!query) return;

            // Show loading state
            document.getElementById('loadingState').style.display = 'block';
            document.getElementById('resultsContainer').style.display = 'none';
            document.getElementById('errorState').style.display = 'none';

            try {
                const response = await fetch('/text2imagefiles', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                    },
                    body: `query=${encodeURIComponent(query)}`
                });

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const data = await response.json();
                displayResults(data);

            } catch (error) {
                console.error('Error:', error);
                document.getElementById('errorState').textContent = 'Error analyzing compound: ' + error.message;
                document.getElementById('errorState').style.display = 'block';
            } finally {
                document.getElementById('loadingState').style.display = 'none';
            }
        });

        function displayResults(data) {
            // Display PFAS 2D image
            if (data.images_2d && data.images_2d.length > 0) {
                document.getElementById('pfas2d').src = data.images_2d[0].path;
            }

            // Display PFAS 3D structure
            if (data.images_3d && data.images_3d.length > 0) {
                load3DMolecule('pfas3d', data.images_3d[0].path);
            }

            // Display best adsorber info
            document.getElementById('bestAdsorberName').textContent = data.best_adsorber || 'Unknown';

            // Display adsorber 2D image
            if (data.images_adsorbers && data.images_adsorbers.length > 0) {
                document.getElementById('adsorber2d').src = data.images_adsorbers[0].path;
            }

            // Display adsorber 3D structure
            if (data.mol2_files_adsorbers && data.mol2_files_adsorbers.length > 0) {
                load3DMolecule('adsorber3d', data.mol2_files_adsorbers[0].path);
            }

            // Populate results table
            populateTable(data.pfas_table || []);

            // Show results
            document.getElementById('resultsContainer').style.display = 'block';
        }

        function load3DMolecule(elementId, mol2Path) {
            const element = document.getElementById(elementId);
            element.innerHTML = ''; // Clear previous content
            
            const viewer = $3Dmol.createViewer(element, {
                defaultcolors: $3Dmol.elementColors.Jmol
            });

            fetch(mol2Path)
                .then(response => response.text())
                .then(data => {
                    viewer.addModel(data, 'mol2');
                    viewer.setStyle({}, {stick: {radius: 0.2}, sphere: {scale: 0.3}});
                    viewer.zoomTo();
                    viewer.render();
                })
                .catch(error => {
                    console.error('Error loading 3D molecule:', error);
                    element.innerHTML = '<p style="padding: 20px; text-align: center; color: #666;">Unable to load 3D structure</p>';
                });
        }

        function populateTable(tableData) {
            const tbody = document.querySelector('#resultsTable tbody');
            tbody.innerHTML = '';

            tableData.forEach(row => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${row.PFAS}</td>
                    <td>${row.ADSORBER_variant}</td>
                    <td>${row.Binding_distance_nm}</td>
                    <td>${row.Binding_free_energy_kJ_mol}</td>
                    <td>${row.Dissociation_constant_M}</td>
                `;
                tbody.appendChild(tr);
            });
        }
    </script>
</body>
</html>
    """

# Mount static files (for serving images and mol2 files)
app.mount("/images", StaticFiles(directory="images"), name="images")


@app.get("/")
def get_pfas_match_root():
    """Base API for PFAS to Adsorber match"""
    return {"PFAS": "ADSORBER-adsorber"}


@app.get("/app", response_class=HTMLResponse)
async def render_pfas_analysis_page():
    """Render the main PFAS analysis page"""
    html_content = HTML_content
    return HTMLResponse(content=html_content, status_code=200)


@app.post("/smiles")
async def get_smiles_from_text(text: str):
    """Get the SMILES representation from the given text description of the molecule"""
    molecule_names = get_molecules(text)
    return [get_smiles(molecule_name) for molecule_name in molecule_names]


@app.post("/render2d")
async def get_2d_render_from_smiles(smiles: str) -> FileResponse:
    """Returns an image from a give smiles text"""
    filename = get_filename(smiles) + ".jpg"  # Assuming the images are in PNG format
    file_path = Path("images") / filename
    return FileResponse(file_path, media_type="image/jpg")


@app.post("/render3d")
async def get_3d_render_from_smiles(smiles: str) -> FileResponse:
    """Returns a 3D renderable mol2 file from a given smiles text"""
    filename = get_filename(smiles) + "_gaff.mol2"
    file_path = Path("images") / filename
    return FileResponse(file_path, media_type="text/mol2")


@app.post("/text2imagefiles")
async def get_images_from_text(request: Request):
    """Returns a list of image files from the text description of the molecule"""
    # Get form data
    form_data = await request.form()
    query = form_data.get("query", "")
    if not query:
        return {"error": "No query provided"}
    molecule_names = get_molecules(query)
    images = []
    mol2_files = []
    images_adsorbers = []
    mol2_files_adsorbers = []
    pfas_table_dict = {}
    adsorber_name = ""
    for molecule_name in molecule_names:
        smiles = get_smiles(molecule_name)
        filename = get_filename(smiles) + ".jpg"
        file_path = Path("images") / filename
        images.append(FileResponse(file_path, media_type="image/jpg"))

        mol2_filename = get_filename(smiles) + "_gaff.mol2"
        mol2_file_path = Path("images") / mol2_filename
        mol2_files.append(FileResponse(mol2_file_path, media_type="text/mol2"))
        if "per-fluoro" in molecule_name:
            # if the molecule is a PFAS
            # Fetch the binding table for the PFAS
            pfas_table_dict = get_best_adsorber_pfas_table(molecule_name)
            adsorber_name = "ADSORBER_" + pfas_table_dict[0].get("ADSORBER_variant")
            image_adsorber = adsorber_name + ".jpg"
            image_adsorber_path = Path("images") / image_adsorber
            images_adsorbers.append(
                FileResponse(image_adsorber_path, media_type="image/jpg")
            )
            mol2_adsorber = adsorber_name + "_gaff.mol2"
            mol2_adsorber_path = Path("images") / mol2_adsorber
            mol2_files_adsorbers.append(
                FileResponse(mol2_adsorber_path, media_type="text/mol2")
            )

    # output_text = f"Generated images for: {', '.join(molecule_names)}"
    # _ = await text_to_speech(output_text)
    return {
        "images_2d": images,
        "images_3d": mol2_files,
        "best_adsorber": adsorber_name,
        "images_adsorbers": images_adsorbers,
        "mol2_files_adsorbers": mol2_files_adsorbers,
        "pfas_table": pfas_table_dict,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app)
