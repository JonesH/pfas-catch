import { useState, useEffect, useRef } from 'react';

// Hook for managing molecule data fetching
const useMoleculeData = () => {
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [data, setData] = useState([null, null, null]);

  const fetchMoleculeData = async (inputText) => {
    if (!inputText.trim()) return;

    setLoading(true);
    setError(null);

    try {
      // 1) Get the list of SMILES
      const res = await fetch(
        `http://127.0.0.1:8003/smiles?text=${encodeURIComponent(inputText)}`,
        { method: "POST" }
      );

      if (!res.ok) throw new Error(`Failed to get SMILES: ${res.status}`);

      const smilesList = await res.json();
      if (!smilesList || !smilesList.length) {
        throw new Error("No molecules found");
      }

      const smiles = smilesList[0];

      // 2) Fetch the 2D image as blob
      console.log('Fetching 2D image for SMILES:', smiles);

      let render2DRes;
      let imageUrl = null;

      try {
        render2DRes = await fetch('http://127.0.0.1:8003/render2d', {
          method: 'POST',
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
          body: `smiles=${encodeURIComponent(smiles)}`
        });

        if (!render2DRes.ok) {
          render2DRes = await fetch(`http://127.0.0.1:8003/render2d?smiles=${encodeURIComponent(smiles)}`, {
            method: 'POST'
          });
        }

        if (!render2DRes.ok) {
          render2DRes = await fetch('http://127.0.0.1:8003/render2d', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ smiles: smiles })
          });
        }

        if (render2DRes.ok) {
          const imageBlob = await render2DRes.blob();
          if (imageBlob.size > 0) {
            imageUrl = URL.createObjectURL(imageBlob);
          } else {
            throw new Error("Received empty image blob");
          }
        } else {
          const errorText = await render2DRes.text();
          console.error('2D API Error:', errorText);
          throw new Error(`Failed to get 2D image: ${render2DRes.status}`);
        }
      } catch (imgError) {
        console.error('2D rendering failed:', imgError);
      }

      // 3) Fetch the 3D MOL2 file as blob
      let mol2Data = null;
      try {
        const render3DRes = await fetch(`http://127.0.0.1:8003/render3d?smiles=${encodeURIComponent(smiles)}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
          body: `smiles=${encodeURIComponent(smiles)}`
        });

        if (render3DRes.ok) {
          const mol2Blob = await render3DRes.blob();
          if (mol2Blob.size > 0) {
            // Store the blob text data instead of URL
            mol2Data = await mol2Blob.text();
            console.log('MOL2 data received:', mol2Data.substring(0, 200) + '...'); // Debug log
          } else {
            throw new Error("Received empty MOL2 blob");
          }
        } else {
          const errorText = await render3DRes.text();
          console.error('3D API Error:', errorText);
          throw new Error(`Failed to get 3D file: ${render3DRes.status}`);
        }
      } catch (mol2Error) {
        console.error('3D MOL2 rendering failed:', mol2Error);
      }

      setData([imageUrl, mol2Data, smiles]);

    } catch (err) {
      console.error('Fetch error:', err);
      setError(err.message || "Failed to fetch molecule data");
      setData([null, null, null]);
    } finally {
      setLoading(false);
    }
  };

  return {
    input,
    setInput,
    loading,
    error,
    data,
    fetchMoleculeData
  };
};

// Color scheme configuration
const colorSchemes = {
  1: {
    bg: 'bg-purple-100',
    text: 'text-purple-800',
    border: 'border-purple-200',
    button: 'bg-purple-600 hover:bg-purple-700',
    input: 'border-purple-300 focus:ring-purple-500',
    loading: 'border-purple-600'
  },
  2: {
    bg: 'bg-green-100',
    text: 'text-green-800',
    border: 'border-green-200',
    button: 'bg-green-600 hover:bg-green-700',
    input: 'border-green-300 focus:ring-green-500',
    loading: 'border-green-600'
  }
};

// Loading Spinner Component
const LoadingSpinner = ({ colorClass }) => (
  <div className="text-center">
    <div className={`animate-spin rounded-full h-8 w-8 border-b-2 ${colorClass} mb-2 mx-auto`}></div>
    <span>Loading...</span>
  </div>
);

// 3D Viewer Component - FIXED VERSION
const Mol3DViewer = ({ mol2Data, sectionNum }) => {
  const viewerRef = useRef(null);
  const containerRef = useRef(null);
  const [scriptLoaded, setScriptLoaded] = useState(false);
  const [viewerReady, setViewerReady] = useState(false);

  // Load 3Dmol.js script
  useEffect(() => {
    if (window.$3Dmol) {
      setScriptLoaded(true);
      return;
    }

    if (document.querySelector('script[src*="3Dmol"]')) {
      // Script is loading, wait for it
      const checkScript = () => {
        if (window.$3Dmol) {
          setScriptLoaded(true);
        } else {
          setTimeout(checkScript, 100);
        }
      };
      checkScript();
      return;
    }

    const script = document.createElement('script');
    script.src = 'https://cdnjs.cloudflare.com/ajax/libs/3Dmol/2.0.4/3Dmol-min.js';
    script.async = true;
    script.onload = () => {
      console.log('3Dmol.js loaded successfully');
      setScriptLoaded(true);
    };
    script.onerror = () => {
      console.error('Failed to load 3Dmol.js');
    };
    document.head.appendChild(script);
  }, []);

  // Initialize viewer when both script and data are ready
  useEffect(() => {
    if (scriptLoaded && mol2Data && containerRef.current && !viewerReady) {
      console.log('Initializing 3D viewer with MOL2 data:', mol2Data.substring(0, 100) + '...');
      initializeViewer();
    }
  }, [scriptLoaded, mol2Data, viewerReady]);

  const initializeViewer = () => {
    if (!containerRef.current || !window.$3Dmol || !mol2Data) {
      console.log('Viewer initialization conditions not met');
      return;
    }

    try {
      // Clear previous viewer
      if (viewerRef.current) {
        viewerRef.current.clear();
      }
      containerRef.current.innerHTML = '';

      console.log('Creating 3Dmol viewer...');

      // Create new viewer
      const viewer = window.$3Dmol.createViewer(containerRef.current, {
        backgroundColor: 'white',
        width: 300,
        height: 200
      });

      console.log('Adding MOL2 model...');

      // Add the MOL2 data
      viewer.addModel(mol2Data, 'mol2');

      // Set style
      viewer.setStyle({}, {
        stick: { radius: 0.1 },
        sphere: { scale: 0.3 }
      });

      // Zoom and render
      viewer.zoomTo();
      viewer.render();

      viewerRef.current = viewer;
      setViewerReady(true);

      console.log('3D viewer initialized successfully');
    } catch (error) {
      console.error('3D viewer initialization failed:', error);
    }
  };

  // Reset viewer when mol2Data changes
  useEffect(() => {
    if (!mol2Data) {
      setViewerReady(false);
    }
  }, [mol2Data]);

  if (!scriptLoaded) {
    return (
      <div className="w-full h-48 bg-gray-100 rounded border flex items-center justify-center">
        <span className="text-gray-500">Loading 3D viewer...</span>
      </div>
    );
  }

  if (!mol2Data) {
    return (
      <div className="w-full h-48 bg-gray-100 rounded border flex items-center justify-center">
        <span className="text-gray-500">No 3D data available</span>
      </div>
    );
  }

  return (
    <div className="relative">
      <div
        ref={containerRef}
        className="w-full h-48 bg-white rounded border"
        style={{ minHeight: '200px' }}
      />
      {!viewerReady && (
        <div className="absolute inset-0 flex items-center justify-center bg-white bg-opacity-75">
          <span className="text-gray-500">Rendering 3D structure...</span>
        </div>
      )}
    </div>
  );
};

// Voice Recognition Button Component
const VoiceButton = ({ onTranscript, disabled, colors }) => {
  const [isListening, setIsListening] = useState(false);
  const [voiceSupported, setVoiceSupported] = useState(false);
  const recognitionRef = useRef(null);

  useEffect(() => {
    // Check if voice recognition is supported
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    setVoiceSupported(!!SpeechRecognition);
  }, []);

  const startVoiceInput = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert("Your browser doesn't support voice recognition. Please try Chrome or Edge.");
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = 'en-US';
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;
    recognition.continuous = false;

    recognitionRef.current = recognition;
    setIsListening(true);

    recognition.onstart = () => {
      console.log('Voice recognition started');
    };

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      console.log('Voice input received:', transcript);
      onTranscript(transcript);
      setIsListening(false);
    };

    recognition.onerror = (event) => {
      console.error('Voice recognition error:', event.error);
      setIsListening(false);
      let errorMessage = 'Voice recognition failed';
      switch (event.error) {
        case 'no-speech':
          errorMessage = 'No speech detected. Please try again.';
          break;
        case 'audio-capture':
          errorMessage = 'No microphone found. Please check your microphone.';
          break;
        case 'not-allowed':
          errorMessage = 'Microphone access denied. Please allow microphone access.';
          break;
        case 'network':
          errorMessage = 'Network error. Please check your connection.';
          break;
        default:
          errorMessage = `Voice recognition error: ${event.error}`;
      }
      alert(errorMessage);
    };

    recognition.onend = () => {
      setIsListening(false);
      recognitionRef.current = null;
    };

    try {
      recognition.start();
    } catch (error) {
      console.error('Failed to start voice recognition:', error);
      setIsListening(false);
      alert('Failed to start voice recognition. Please try again.');
    }
  };

  const stopVoiceInput = () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }
    setIsListening(false);
  };

  const handleVoiceClick = () => {
    if (isListening) {
      stopVoiceInput();
    } else {
      startVoiceInput();
    }
  };

  if (!voiceSupported) {
    return (
      <button
        disabled
        className="bg-gray-400 text-white px-3 py-2 rounded transition disabled:opacity-50 flex items-center text-sm min-w-24 justify-center"
        title="Voice recognition not supported in this browser"
      >
        <svg className="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M10 2a3 3 0 00-3 3v4a3 3 0 006 0V5a3 3 0 00-3-3zM3.5 9.5a.5.5 0 01.5-.5h1a.5.5 0 01.5.5 5.5 5.5 0 0011 0 .5.5 0 01.5-.5h1a.5.5 0 01.5.5 6.5 6.5 0 01-6 6.459V17.5h2.5a.5.5 0 010 1h-6a.5.5 0 010-1H10v-1.541A6.5 6.5 0 013.5 9.5z" clipRule="evenodd" />
        </svg>
        Voice
      </button>
    );
  }

  return (
    <button
      onClick={handleVoiceClick}
      disabled={disabled}
      className={`${isListening ? 'bg-red-600 hover:bg-red-700' : colors.button} text-white px-3 py-2 rounded transition disabled:opacity-50 flex items-center text-sm min-w-24 justify-center`}
    >
      {isListening ? (
        <>
          <div className="w-4 h-4 bg-white rounded-full animate-pulse mr-2"></div>
          Listening...
        </>
      ) : (
        <>
          <svg className="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 2a3 3 0 00-3 3v4a3 3 0 006 0V5a3 3 0 00-3-3zM3.5 9.5a.5.5 0 01.5-.5h1a.5.5 0 01.5.5 5.5 5.5 0 0011 0 .5.5 0 01.5-.5h1a.5.5 0 01.5.5 6.5 6.5 0 01-6 6.459V17.5h2.5a.5.5 0 010 1h-6a.5.5 0 010-1H10v-1.541A6.5 6.5 0 013.5 9.5z" clipRule="evenodd" />
          </svg>
          Voice
        </>
      )}
    </button>
  );
};

// Molecule Input Component - Updated with speech recognition
const MoleculeInput = ({
  sectionNum,
  input,
  setInput,
  loading,
  error,
  onSubmit
}) => {
  const colors = colorSchemes[sectionNum];

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      onSubmit();
    }
  };

  const handleVoiceTranscript = (transcript) => {
    setInput(transcript);
    // Auto-submit after voice input
    setTimeout(() => {
      if (transcript.trim()) {
        onSubmit(transcript);
      }
    }, 500);
  };

  return (
    <div className="mb-6">
      <h3 className={`text-lg font-semibold ${colors.text} mb-2`}>
        Input:
      </h3>
      <div className="flex gap-2">
        <input
          type="text"
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Enter molecule description or use voice..."
          className={`flex-1 p-2 border ${colors.input} rounded-md focus:outline-none focus:ring-2`}
          disabled={loading}
        />
        <VoiceButton
          onTranscript={handleVoiceTranscript}
          disabled={loading}
          colors={colors}
        />
      </div>
      <p className="text-xs text-gray-500 mt-1">
        Press Enter to search or use the voice button for speech recognition
      </p>
      {error && (
        <p className="text-red-600 text-sm mt-1">{error}</p>
      )}
    </div>
  );
};

// 2D Structure Display Component
const Structure2D = ({
  sectionNum,
  loading,
  error,
  imageUrl,
  smiles
}) => {
  const colors = colorSchemes[sectionNum];

  return (
    <div className={`${colors.bg} rounded-lg shadow-lg p-4`}>
      <h3 className={`text-lg font-semibold ${colors.text} mb-3`}>
        2D Molecule Structure
      </h3>
      <div className={`bg-white rounded border-2 ${colors.border} min-h-64 flex items-center justify-center`}>
        {loading ? (
          <div className={colors.text}>
            <LoadingSpinner colorClass={colors.loading} />
          </div>
        ) : error ? (
          <p className="text-red-600 text-center px-4">{error}</p>
        ) : imageUrl ? (
          <div className="text-center p-2">
            <img
              src={imageUrl}
              alt="2D Molecule Structure"
              className="max-w-full max-h-48 object-contain rounded mb-2"
              onError={(e) => {
                console.error('Image failed to load:', imageUrl);
              }}
            />
            {smiles && (
              <p className="text-xs text-gray-500 break-all px-2">
                SMILES: {smiles}
              </p>
            )}
          </div>
        ) : (
          <p className={`${colors.text} text-center px-4`}>
            Enter text above to generate 2D structure
          </p>
        )}
      </div>
    </div>
  );
};

// 3D Structure Display Component
const Structure3D = ({
  sectionNum,
  loading,
  error,
  mol2Data,
  smiles
}) => {
  const colors = colorSchemes[sectionNum];

  const downloadMol2File = () => {
    if (mol2Data) {
      const blob = new Blob([mol2Data], { type: 'chemical/x-mol2' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `sample_${sectionNum}_3d_structure.mol2`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    }
  };

  return (
    <div className={`${colors.bg} rounded-lg shadow-lg p-4`}>
      <h3 className={`text-lg font-semibold ${colors.text} mb-3`}>
        Sample {sectionNum} - 3D Molecule Structure
      </h3>
      <div className={`bg-white rounded border-2 ${colors.border} min-h-64 flex items-center justify-center`}>
        {loading ? (
          <div className={colors.text}>
            <LoadingSpinner colorClass={colors.loading} />
          </div>
        ) : error ? (
          <p className="text-red-600 text-center px-4">{error}</p>
        ) : mol2Data ? (
          <div className="text-center p-2 w-full">
            <div className="mb-4">
              <Mol3DViewer mol2Data={mol2Data} sectionNum={sectionNum} />
            </div>
            <button
              onClick={downloadMol2File}
              className={`${colors.button} text-white px-4 py-2 rounded transition text-sm`}
            >
              Download MOL2 File
            </button>
            {smiles && (
              <p className="text-xs text-gray-400 mt-2 break-all px-2">
                SMILES: {smiles}
              </p>
            )}
          </div>
        ) : (
          <p className={`${colors.text} text-center px-4`}>
            3D structure will appear here
          </p>
        )}
      </div>
    </div>
  );
};

// Results Summary Table Component
const ResultsTable = ({ sample1Data, sample2Data }) => {
  const getStatusIcon = (loading, error, hasData) => {
    if (loading) return '🔄';
    if (error) return '❌';
    if (hasData) return '✅';
    return '⏸️';
  };

  const get2DIcon = (imageUrl) => imageUrl ? '📊' : '-';
  const get3DIcon = (mol2Data) => mol2Data ? '🧬' : '-';

  return (
    <div className="mt-6">
      <h3 className="text-lg font-semibold mb-2">Results Summary</h3>
      <div className="overflow-x-auto">
        <table className="w-full border-collapse border border-gray-300 text-sm">
          <thead>
            <tr className="bg-gray-50">
              <th className="border border-gray-300 px-2 py-1 text-left">Sample</th>
              <th className="border border-gray-300 px-2 py-1">Status</th>
              <th className="border border-gray-300 px-2 py-1">2D</th>
              <th className="border border-gray-300 px-2 py-1">3D</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td className="border border-gray-300 px-2 py-1 font-medium">Water impurities</td>
              <td className="border border-gray-300 px-2 py-1 text-center">
                {getStatusIcon(sample1Data.loading, sample1Data.error, sample1Data.data[0])}
              </td>
              <td className="border border-gray-300 px-2 py-1 text-center">
                {get2DIcon(sample1Data.data[0])}
              </td>
              <td className="border border-gray-300 px-2 py-1 text-center">
                {get3DIcon(sample1Data.data[1])}
              </td>
            </tr>
            <tr>
              <td className="border border-gray-300 px-2 py-1 font-medium">PFAS Component</td>
              <td className="border border-gray-300 px-2 py-1 text-center">
                {getStatusIcon(sample2Data.loading, sample2Data.error, sample2Data.data[0])}
              </td>
              <td className="border border-gray-300 px-2 py-1 text-center">
                {get2DIcon(sample2Data.data[0])}
              </td>
              <td className="border border-gray-300 px-2 py-1 text-center">
                {get3DIcon(sample2Data.data[1])}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
};

// Control Panel Component
const ControlPanel = ({ sample1Data, sample2Data }) => {
  return (
    <div className="w-1/3 bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-xl font-semibold mb-4">Molecule Analysis</h2>

      <MoleculeInput
        sectionNum={1}
        input={sample1Data.input}
        setInput={sample1Data.setInput}
        loading={sample1Data.loading}
        error={sample1Data.error}
        onSubmit={(text) => sample1Data.fetchMoleculeData(text || sample1Data.input)}
      />

      <MoleculeInput
        sectionNum={2}
        input={sample2Data.input}
        setInput={sample2Data.setInput}
        loading={sample2Data.loading}
        error={sample2Data.error}
        onSubmit={(text) => sample2Data.fetchMoleculeData(text || sample2Data.input)}
      />

      <ResultsTable sample1Data={sample1Data} sample2Data={sample2Data} />
    </div>
  );
};

// Visualization Panel Component
const VisualizationPanel = ({ sample1Data, sample2Data }) => {
  return (
    <div className="flex-1 grid grid-cols-2 gap-4">
      <Structure2D
        sectionNum={1}
        loading={sample1Data.loading}
        error={sample1Data.error}
        imageUrl={sample1Data.data[0]}
        smiles={sample1Data.data[2]}
      />

      <Structure3D
        sectionNum={1}
        loading={sample1Data.loading}
        error={sample1Data.error}
        mol2Data={sample1Data.data[1]}
        smiles={sample1Data.data[2]}
      />

      <Structure2D
        sectionNum={2}
        loading={sample2Data.loading}
        error={sample2Data.error}
        imageUrl={sample2Data.data[0]}
        smiles={sample2Data.data[2]}
      />

      <Structure3D
        sectionNum={2}
        loading={sample2Data.loading}
        error={sample2Data.error}
        mol2Data={sample2Data.data[1]}
        smiles={sample2Data.data[2]}
      />
    </div>
  );
};

// Main App Component
function App() {
  const sample1Data = useMoleculeData();
  const sample2Data = useMoleculeData();

  return (
    <div className="h-screen bg-gray-100 p-6">
      <h1 className="text-3xl font-bold text-black mb-6 text-center">Match PFAS Catch</h1>

      <div className="flex gap-6 h-full">
        <ControlPanel sample1Data={sample1Data} sample2Data={sample2Data} />
        <VisualizationPanel sample1Data={sample1Data} sample2Data={sample2Data} />
      </div>
    </div>
  );
}

export default App;