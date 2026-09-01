import React, { useState } from 'react';

function App() {
  const [file, setFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    setFile(selectedFile);
    setResult(null);
    if (selectedFile) setPreviewUrl(URL.createObjectURL(selectedFile));
  };

  const handleUpload = async () => {
    if (!file) return alert("Select a document to scan.");
    setLoading(true);
    const formData = new FormData();
    formData.append('file', file); 

    try {
      const response = await fetch('http://localhost:8000/api/analyze-document', { method: 'POST', body: formData });
      setResult(await response.json()); 
    } catch (error) {
      alert("Failed to connect to forensic backend.");
    } finally {
      setLoading(false);
    }
  };

  // Helper for glowing status colors
  const getStatusColor = (score) => score > 50 ? '#ef4444' : '#10b981'; 
  const getBoxShadow = (score) => score > 50 ? '0 0 20px rgba(239, 68, 68, 0.4)' : '0 0 20px rgba(16, 185, 129, 0.4)';

  return (
    <div style={{ backgroundColor: '#030712', minHeight: '100vh', color: '#e5e7eb', padding: '40px 20px', fontFamily: 'system-ui, sans-serif' }}>
      <div style={{ maxWidth: '1000px', margin: '0 auto' }}>
        
        {/* HEADER */}
        <div style={{ textAlign: 'center', marginBottom: '40px' }}>
          <h1 style={{ fontSize: '2.5rem', fontWeight: '900', margin: '0', color: '#38bdf8', letterSpacing: '3px', textTransform: 'uppercase' }}>
            Omni-Guard Document Forensics
          </h1>
          <p style={{ color: '#6b7280', fontSize: '1.1rem', marginTop: '10px' }}>Universal AI Detection for Forgeries & Tampering</p>
        </div>

        {/* SCANNER CONSOLE */}
        <div style={{ backgroundColor: '#111827', padding: '30px', borderRadius: '16px', border: '1px solid #1f2937', display: 'flex', gap: '20px', justifyContent: 'center', alignItems: 'center', marginBottom: '40px' }}>
          <input 
            type="file" accept="image/*" onChange={handleFileChange}
            style={{ padding: '12px', backgroundColor: '#1f2937', borderRadius: '8px', border: '1px dashed #374151', color: '#9ca3af', width: '300px' }} 
          />
          <button 
            onClick={handleUpload} disabled={loading || !file} 
            style={{ padding: '14px 35px', fontSize: '1.1rem', fontWeight: 'bold', backgroundColor: loading ? '#374151' : '#0284c7', color: 'white', border: 'none', borderRadius: '8px', cursor: loading ? 'not-allowed' : 'pointer', transition: 'all 0.3s', boxShadow: loading ? 'none' : '0 0 15px rgba(2, 132, 199, 0.5)' }}
          >
            {loading ? "INITIALIZING SCAN..." : "INITIATE FORENSIC SCAN"}
          </button>
        </div>

        {/* DASHBOARD RESULTS */}
        {result && (
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '30px' }}>
            
            {/* LEFT: IMAGE & MASTER SCORE */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
              <div style={{ 
                backgroundColor: '#111827', padding: '30px', borderRadius: '16px', border: `2px solid ${getStatusColor(result.risk_score)}`, 
                boxShadow: getBoxShadow(result.risk_score), textAlign: 'center', transition: 'all 0.5s'
              }}>
                <h3 style={{ margin: '0 0 10px 0', color: '#9ca3af', textTransform: 'uppercase', fontSize: '0.9rem' }}>Threat Assessment</h3>
                <div style={{ fontSize: '4rem', fontWeight: '900', color: getStatusColor(result.risk_score), lineHeight: '1' }}>
                  {result.risk_score}%
                </div>
                <div style={{ marginTop: '10px', fontSize: '1.2rem', fontWeight: 'bold', color: getStatusColor(result.risk_score) }}>
                  {result.risk_score > 50 ? "FORGERY DETECTED" : "DOCUMENT AUTHENTIC"}
                </div>
                <div style={{ marginTop: '15px', padding: '5px 10px', backgroundColor: '#1f2937', borderRadius: '6px', fontSize: '0.85rem', color: '#cbd5e1', display: 'inline-block' }}>
                  Detected Type: <strong>{result.document_type}</strong>
                </div>
              </div>

              {previewUrl && (
                <div style={{ backgroundColor: '#111827', padding: '15px', borderRadius: '16px', border: '1px solid #1f2937' }}>
                  <img src={previewUrl} alt="Scanned" style={{ width: '100%', borderRadius: '8px', filter: 'grayscale(20%) contrast(120%)' }} />
                </div>
              )}
            </div>

            {/* RIGHT: FORENSIC MODULES */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
              
              {/* Module 1: EXIF Metadata */}
              <div style={{ backgroundColor: '#111827', padding: '20px', borderRadius: '12px', borderLeft: result.forensics.metadata.tampering_suspected ? '4px solid #ef4444' : '4px solid #10b981' }}>
                <h4 style={{ margin: '0 0 10px 0', color: '#38bdf8' }}>MODULE 1: EXIF Metadata Analysis</h4>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.95rem' }}>
                  <span>Software Signature: <span style={{ color: '#cbd5e1' }}>{result.forensics.metadata.editing_software_detected}</span></span>
                  <span style={{ fontWeight: 'bold', color: result.forensics.metadata.tampering_suspected ? '#ef4444' : '#10b981' }}>
                    {result.forensics.metadata.tampering_suspected ? "⚠️ Editing Tools Found" : "✅ Clean"}
                  </span>
                </div>
              </div>

              {/* Module 2: ELA Pixels */}
              <div style={{ backgroundColor: '#111827', padding: '20px', borderRadius: '12px', borderLeft: result.forensics.ela.tampering_suspected ? '4px solid #ef4444' : '4px solid #10b981' }}>
                <h4 style={{ margin: '0 0 10px 0', color: '#38bdf8' }}>MODULE 2: Pixel Error Level Analysis (ELA)</h4>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.95rem' }}>
                  <span>Compression Variance: <span style={{ color: '#cbd5e1' }}>{result.forensics.ela.mean_error_score}</span></span>
                  <span style={{ fontWeight: 'bold', color: result.forensics.ela.tampering_suspected ? '#ef4444' : '#10b981' }}>
                    {result.forensics.ela.tampering_suspected ? "⚠️ Pixel Splicing Detected" : "✅ Natural Variance"}
                  </span>
                </div>
              </div>

              {/* Module 3: Logical OCR */}
              <div style={{ backgroundColor: '#111827', padding: '20px', borderRadius: '12px', borderLeft: (result.forensics.mrz.found && !result.forensics.mrz.valid) ? '4px solid #ef4444' : '4px solid #374151' }}>
                <h4 style={{ margin: '0 0 10px 0', color: '#38bdf8' }}>MODULE 3: Logical Verification</h4>
                <div style={{ fontSize: '0.95rem' }}>
                  {result.document_type === "Passport" ? (
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <span>ICAO 9303 Checksum:</span>
                      <span style={{ fontWeight: 'bold', color: result.forensics.mrz.valid ? '#10b981' : '#ef4444' }}>
                        {result.forensics.mrz.valid ? "✅ Check Digits Match" : "⚠️ Cryptographic Math Failed"}
                      </span>
                    </div>
                  ) : (
                    <span style={{ color: '#9ca3af', fontStyle: 'italic' }}>Skipped: Checksum rules do not apply to General Documents.</span>
                  )}
                </div>
              </div>

              {/* Module 4: Raw Text Dump */}
              <div style={{ backgroundColor: '#111827', padding: '20px', borderRadius: '12px', border: '1px solid #1f2937' }}>
                <h4 style={{ margin: '0 0 10px 0', color: '#6b7280' }}>EXTRACTED TEXT FRAGMENTS</h4>
                <pre style={{ margin: 0, color: '#059669', fontSize: '0.8rem', whiteSpace: 'pre-wrap', wordWrap: 'break-word', fontFamily: 'monospace' }}>
                  {result.forensics.ocr_preview || "[No legible text found]"}
                </pre>
              </div>

            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;