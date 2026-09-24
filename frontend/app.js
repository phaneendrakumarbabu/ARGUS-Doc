/**
 * ADFF - Agentic AI Document Tampering Detection & Forensic Analysis
 * Ultra-Modern Forensic UI/UX Controller
 */

// Application State
const state = {
  currentReport: null,
  currentView: 'overlay', // 'overlay' | 'heatmap' | 'split' | 'original'
  currentEvidenceType: 'interpretations', // 'interpretations' | 'observations'
  zoomLevel: 1.0,
  selectedRegionIndex: null,
  opacityLevel: 0.85,
  magnifierActive: false,
  splitPosition: 50, // 0 to 100 percent
  isDraggingSplit: false,
  verifiedSteps: new Set()
};

// DOM Elements Cache
const elements = {
  // Theme & Navigation
  themeToggleBtn: document.getElementById('theme-toggle-btn'),
  themeIconSun: document.getElementById('theme-icon-sun'),
  themeIconMoon: document.getElementById('theme-icon-moon'),
  btnKeyboardHelp: document.getElementById('btn-keyboard-help'),
  shortcutsModal: document.getElementById('shortcuts-modal'),
  btnCloseShortcuts: document.getElementById('btn-close-shortcuts'),

  // Header & Inputs
  sampleSelect: document.getElementById('sample-select'),
  btnRunSample: document.getElementById('btn-run-sample'),
  fileUploadInput: document.getElementById('file-upload-input'),
  dropzone: document.getElementById('dropzone'),
  currentFileBadge: document.getElementById('current-file-badge'),
  currentFileName: document.getElementById('current-file-name'),
  currentFileSize: document.getElementById('current-file-size'),

  // Pipeline Stepper
  pipelineNodes: document.querySelectorAll('.pipeline-node'),
  pipelineStatusText: document.getElementById('pipeline-status-text'),
  agentModeBadge: document.getElementById('agent-mode-badge'),
  
  // Viewer
  tabBtns: document.querySelectorAll('.tab-btn'),
  opacityControl: document.getElementById('opacity-control'),
  opacitySlider: document.getElementById('opacity-slider'),
  opacityValText: document.getElementById('opacity-val-text'),
  btnLoupeToggle: document.getElementById('btn-loupe-toggle'),
  btnZoomIn: document.getElementById('btn-zoom-in'),
  btnZoomOut: document.getElementById('btn-zoom-out'),
  btnZoomReset: document.getElementById('btn-zoom-reset'),
  docStatsStrip: document.getElementById('doc-stats-strip'),
  statGenre: document.getElementById('stat-genre'),
  statDocId: document.getElementById('stat-doc-id'),
  statAnomalyCount: document.getElementById('stat-anomaly-count'),
  statMode: document.getElementById('stat-mode'),

  // Viewport Stages
  canvasViewport: document.getElementById('canvas-viewport'),
  viewportEmpty: document.getElementById('viewport-empty'),
  imageStage: document.getElementById('image-stage'),
  forensicImage: document.getElementById('forensic-image'),
  forensicBlendedHeatmap: document.getElementById('forensic-blended-heatmap'),
  interactiveOverlay: document.getElementById('interactive-overlay'),

  // Split Stage
  splitStage: document.getElementById('split-stage'),
  splitContainer: document.getElementById('split-container'),
  splitImgBefore: document.getElementById('split-img-before'),
  splitImgAfter: document.getElementById('split-img-after'),
  splitAfterLayer: document.getElementById('split-after-layer'),
  splitDivider: document.getElementById('split-divider'),

  // Magnifier Loupe
  magnifierLoupe: document.getElementById('magnifier-loupe'),
  loupeCanvas: document.getElementById('loupe-canvas'),
  loupeHud: document.getElementById('loupe-hud'),

  // Spinner
  spinnerOverlay: document.getElementById('spinner-overlay'),
  spinnerStatusText: document.getElementById('spinner-status-text'),
  
  // Regions Bar
  regionsBar: document.getElementById('regions-bar'),
  regionCount: document.getElementById('region-count'),
  regionsChips: document.getElementById('regions-chips'),

  // Timeline
  timelineList: document.getElementById('timeline-list'),
  traceStepCount: document.getElementById('trace-step-count'),

  // Triage Card
  triageCategory: document.getElementById('manipulation-category'),
  riskBadge: document.getElementById('risk-badge'),
  riskLevelLabel: document.getElementById('risk-level-label'),
  riskScoreNum: document.getElementById('risk-score-num'),
  scoreFill: document.getElementById('score-fill'),
  scoreProgressbar: document.getElementById('score-progressbar'),
  scoreSeverityTag: document.getElementById('score-severity-tag'),
  docMetaSummary: document.getElementById('doc-meta-summary'),
  metaDocId: document.getElementById('meta-doc-id'),
  metaDocType: document.getElementById('meta-doc-type'),
  metaAnalysisDate: document.getElementById('meta-analysis-date'),

  // Forensic Pillars Breakdown
  forensicPillars: document.getElementById('forensic-pillars'),
  pillarMetaVal: document.getElementById('pillar-meta-val'),
  pillarMetaFill: document.getElementById('pillar-meta-fill'),
  pillarElaVal: document.getElementById('pillar-ela-val'),
  pillarElaFill: document.getElementById('pillar-ela-fill'),
  pillarNoiseVal: document.getElementById('pillar-noise-val'),
  pillarNoiseFill: document.getElementById('pillar-noise-fill'),
  pillarTypoVal: document.getElementById('pillar-typo-val'),
  pillarTypoFill: document.getElementById('pillar-typo-fill'),

  // Conflicts
  conflictAlert: document.getElementById('conflict-alert'),
  conflictText: document.getElementById('conflict-text'),

  // Evidence
  evTabBtns: document.querySelectorAll('.ev-tab-btn'),
  evidenceList: document.getElementById('evidence-list'),
  evidenceCount: document.getElementById('evidence-count'),

  // Verification Checklist & Sign-off
  verificationChecklist: document.getElementById('verification-checklist'),
  checklistProgressBadge: document.getElementById('checklist-progress-badge'),
  investigatorSignoff: document.getElementById('investigator-signoff'),
  investigatorName: document.getElementById('investigator-name'),
  btnSignDocket: document.getElementById('btn-sign-docket'),
  signoffStatus: document.getElementById('signoff-status'),

  // Export Actions & Modals
  btnExportJson: document.getElementById('btn-export-json'),
  btnExportMd: document.getElementById('btn-export-md'),
  btnViewMeta: document.getElementById('btn-view-meta'),
  metaModal: document.getElementById('meta-modal'),
  btnCloseModal: document.getElementById('btn-close-modal'),
  modalMetaGrid: document.getElementById('modal-meta-grid'),
  modalRawJson: document.getElementById('modal-raw-json'),

  // Toast
  toast: document.getElementById('toast'),
  toastMessage: document.getElementById('toast-message')
};

let toastTimeout = null;

// Initialization
document.addEventListener('DOMContentLoaded', () => {
  initTheme();
  setupEventListeners();
  setupKeyboardShortcuts();
  setupSplitSlider();
  setupMagnifierLoupe();
});

// --------------------------------------------------------------------------
// Theme Management (Light / Dark Mode)
// --------------------------------------------------------------------------
function initTheme() {
  const savedTheme = localStorage.getItem('adff-theme');
  const isDark = savedTheme !== 'light'; // Default to sleek dark cybernetic
  applyTheme(isDark);

  if (elements.themeToggleBtn) {
    elements.themeToggleBtn.addEventListener('click', () => {
      const currentlyDark = document.documentElement.classList.contains('dark');
      applyTheme(!currentlyDark);
      showToast(!currentlyDark ? 'Dark forensic console enabled' : 'Light laboratory theme enabled');
    });
  }
}

function applyTheme(isDark) {
  if (isDark) {
    document.documentElement.classList.add('dark');
    if (elements.themeIconSun) elements.themeIconSun.style.display = 'none';
    if (elements.themeIconMoon) elements.themeIconMoon.style.display = 'block';
    localStorage.setItem('adff-theme', 'dark');
  } else {
    document.documentElement.classList.remove('dark');
    if (elements.themeIconSun) elements.themeIconSun.style.display = 'block';
    if (elements.themeIconMoon) elements.themeIconMoon.style.display = 'none';
    localStorage.setItem('adff-theme', 'light');
  }
}

// --------------------------------------------------------------------------
// Event Listeners & Binding
// --------------------------------------------------------------------------
function setupEventListeners() {
  // Sample Selection & Execution
  elements.sampleSelect.addEventListener('change', () => {
    elements.btnRunSample.disabled = !elements.sampleSelect.value;
  });

  elements.btnRunSample.addEventListener('click', () => {
    const selected = elements.sampleSelect.value;
    if (selected) {
      runSampleAnalysis(selected);
    }
  });

  // File Upload
  elements.fileUploadInput.addEventListener('change', (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFileUpload(e.target.files[0]);
    }
  });

  // Drag and Drop Zone
  elements.dropzone.addEventListener('click', () => elements.fileUploadInput.click());
  elements.dropzone.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      elements.fileUploadInput.click();
    }
  });
  
  ['dragenter', 'dragover'].forEach(event => {
    elements.dropzone.addEventListener(event, (e) => {
      e.preventDefault();
      elements.dropzone.classList.add('drag-over');
    });
  });

  ['dragleave', 'drop'].forEach(event => {
    elements.dropzone.addEventListener(event, (e) => {
      e.preventDefault();
      elements.dropzone.classList.remove('drag-over');
    });
  });

  elements.dropzone.addEventListener('drop', (e) => {
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileUpload(e.dataTransfer.files[0]);
    }
  });

  // View Mode Tabs
  elements.tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      elements.tabBtns.forEach(b => {
        b.classList.remove('active');
        b.setAttribute('aria-selected', 'false');
      });
      btn.classList.add('active');
      btn.setAttribute('aria-selected', 'true');
      state.currentView = btn.dataset.view;
      updateImageView();
    });
  });

  // Opacity Slider
  elements.opacitySlider.addEventListener('input', (e) => {
    state.opacityLevel = e.target.value / 100;
    elements.opacityValText.textContent = `${e.target.value}%`;
    if (elements.forensicBlendedHeatmap) {
      elements.forensicBlendedHeatmap.style.opacity = state.opacityLevel;
    }
  });

  // Magnifier Toggle
  elements.btnLoupeToggle.addEventListener('click', () => {
    state.magnifierActive = !state.magnifierActive;
    elements.btnLoupeToggle.classList.toggle('active', state.magnifierActive);
    elements.btnLoupeToggle.style.color = state.magnifierActive ? 'var(--accent)' : '';
    showToast(state.magnifierActive ? '2.5x Loupe active: Hover image to inspect' : 'Loupe deactivated');
    if (!state.magnifierActive) {
      elements.magnifierLoupe.style.display = 'none';
    }
  });

  // Zoom Controls
  elements.btnZoomIn.addEventListener('click', () => {
    state.zoomLevel = Math.min(2.5, state.zoomLevel + 0.2);
    applyZoom();
  });

  elements.btnZoomOut.addEventListener('click', () => {
    state.zoomLevel = Math.max(0.5, state.zoomLevel - 0.2);
    applyZoom();
  });

  elements.btnZoomReset.addEventListener('click', () => {
    state.zoomLevel = 1.0;
    applyZoom();
  });

  // Evidence Tabs
  elements.evTabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      elements.evTabBtns.forEach(b => {
        b.classList.remove('active');
        b.setAttribute('aria-selected', 'false');
      });
      btn.classList.add('active');
      btn.setAttribute('aria-selected', 'true');
      state.currentEvidenceType = btn.dataset.evType;
      renderEvidence();
    });
  });

  // Investigator Sign-off
  elements.btnSignDocket.addEventListener('click', () => {
    const name = elements.investigatorName.value.trim();
    if (!name) {
      showToast('Please enter investigator name or badge #');
      return;
    }
    const timestamp = new Date().toISOString().replace('T', ' ').slice(0, 19) + ' UTC';
    elements.signoffStatus.textContent = `Approved & Signed by ${name} at ${timestamp}`;
    elements.signoffStatus.style.color = 'var(--risk-low)';
    showToast(`Docket signed by ${name}`);
  });

  // Export JSON (§8)
  elements.btnExportJson.addEventListener('click', () => {
    if (!state.currentReport) return;
    const jsonStr = JSON.stringify(state.currentReport, null, 2);
    downloadFile(jsonStr, `ADFF_Forensic_Report_${state.currentReport.document_id}.json`, 'application/json');
    showToast('Forensic report JSON exported.');
  });

  // Export Markdown Docket
  elements.btnExportMd.addEventListener('click', () => {
    if (!state.currentReport) return;
    const mdContent = generateMarkdownDocket(state.currentReport);
    downloadFile(mdContent, `ADFF_Forensic_Docket_${state.currentReport.document_id}.md`, 'text/markdown');
    showToast('Investigator Markdown Docket exported.');
  });

  // View File Metadata Modal
  elements.btnViewMeta.addEventListener('click', () => {
    if (!state.currentReport) return;
    populateMetaModal(state.currentReport);
    elements.metaModal.showModal();
  });

  elements.btnCloseModal.addEventListener('click', () => {
    elements.metaModal.close();
  });

  // Keyboard Shortcuts Modal
  elements.btnKeyboardHelp.addEventListener('click', () => {
    elements.shortcutsModal.showModal();
  });

  elements.btnCloseShortcuts.addEventListener('click', () => {
    elements.shortcutsModal.close();
  });
}

function applyZoom() {
  elements.imageStage.style.transform = `scale(${state.zoomLevel})`;
}

function downloadFile(content, fileName, mimeType) {
  const blob = new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = fileName;
  a.click();
  URL.revokeObjectURL(url);
}

// --------------------------------------------------------------------------
// Split Curtain Comparison Slider
// --------------------------------------------------------------------------
function setupSplitSlider() {
  const container = elements.splitContainer;
  const divider = elements.splitDivider;
  if (!container || !divider) return;

  const onMove = (clientX) => {
    const rect = container.getBoundingClientRect();
    if (rect.width <= 0) return;
    let offsetX = clientX - rect.left;
    let percentage = (offsetX / rect.width) * 100;
    percentage = Math.max(5, Math.min(95, percentage));
    
    state.splitPosition = percentage;
    container.style.setProperty('--split-pos', `${percentage}%`);
    divider.style.left = `${percentage}%`;
    divider.setAttribute('aria-valuenow', Math.round(percentage));
  };

  const startDrag = (e) => {
    state.isDraggingSplit = true;
    const clientX = e.clientX || (e.touches && e.touches[0].clientX);
    if (clientX) onMove(clientX);
  };

  const stopDrag = () => {
    state.isDraggingSplit = false;
  };

  const duringDrag = (e) => {
    if (!state.isDraggingSplit) return;
    const clientX = e.clientX || (e.touches && e.touches[0].clientX);
    if (clientX) onMove(clientX);
  };

  divider.addEventListener('mousedown', startDrag);
  window.addEventListener('mousemove', duringDrag);
  window.addEventListener('mouseup', stopDrag);

  divider.addEventListener('touchstart', startDrag, { passive: true });
  window.addEventListener('touchmove', duringDrag, { passive: true });
  window.addEventListener('touchend', stopDrag);
}

// --------------------------------------------------------------------------
// 2.5x Forensic Magnifier Loupe
// --------------------------------------------------------------------------
function setupMagnifierLoupe() {
  const stage = elements.imageStage;
  const loupe = elements.magnifierLoupe;
  const canvas = elements.loupeCanvas;
  if (!stage || !loupe || !canvas) return;
  const ctx = canvas.getContext('2d');

  stage.addEventListener('mousemove', (e) => {
    if (!state.magnifierActive || !elements.forensicImage.src) {
      loupe.style.display = 'none';
      return;
    }

    const rect = stage.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    if (x < 0 || y < 0 || x > rect.width || y > rect.height) {
      loupe.style.display = 'none';
      return;
    }

    loupe.style.display = 'block';
    loupe.style.left = `${e.clientX - 80}px`;
    loupe.style.top = `${e.clientY - 80}px`;

    // Draw 2.5x magnified view
    const zoom = 2.5;
    const img = elements.forensicImage;
    if (img.naturalWidth && img.naturalHeight) {
      const scaleX = img.naturalWidth / rect.width;
      const scaleY = img.naturalHeight / rect.height;
      const naturalX = x * scaleX;
      const naturalY = y * scaleY;

      ctx.clearRect(0, 0, 160, 160);
      ctx.drawImage(
        img,
        naturalX - 80 / zoom,
        naturalY - 80 / zoom,
        160 / zoom,
        160 / zoom,
        0,
        0,
        160,
        160
      );

      elements.loupeHud.textContent = `X: ${Math.round(naturalX)} | Y: ${Math.round(naturalY)}`;
    }
  });

  stage.addEventListener('mouseleave', () => {
    loupe.style.display = 'none';
  });
}

// --------------------------------------------------------------------------
// Keyboard Shortcuts
// --------------------------------------------------------------------------
function setupKeyboardShortcuts() {
  window.addEventListener('keydown', (e) => {
    // Avoid triggering while typing in inputs
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA' || e.target.tagName === 'SELECT') {
      return;
    }

    switch (e.key) {
      case '1':
        switchView('overlay');
        break;
      case '2':
        switchView('heatmap');
        break;
      case '3':
        switchView('original');
        break;
      case 's':
      case 'S':
        switchView('split');
        break;
      case 'm':
      case 'M':
        elements.btnLoupeToggle.click();
        break;
      case '+':
      case '=':
        elements.btnZoomIn.click();
        break;
      case '-':
      case '_':
        elements.btnZoomOut.click();
        break;
      case '0':
        elements.btnZoomReset.click();
        break;
      case '?':
        elements.shortcutsModal.showModal();
        break;
      case 'Escape':
        if (elements.metaModal.open) elements.metaModal.close();
        if (elements.shortcutsModal.open) elements.shortcutsModal.close();
        state.selectedRegionIndex = null;
        renderOverlayBBoxes();
        break;
    }
  });
}

function switchView(viewName) {
  elements.tabBtns.forEach(btn => {
    const isTarget = btn.dataset.view === viewName;
    btn.classList.toggle('active', isTarget);
    btn.setAttribute('aria-selected', isTarget ? 'true' : 'false');
  });
  state.currentView = viewName;
  updateImageView();
}

// --------------------------------------------------------------------------
// Sample & File Analysis Handlers
// --------------------------------------------------------------------------
async function handleFileUpload(file) {
  showLoading(true, `Ingesting and analyzing '${file.name}' across forensic agents...`);
  
  elements.currentFileBadge.style.display = 'inline-flex';
  elements.currentFileName.textContent = file.name;
  elements.currentFileSize.textContent = formatBytes(file.size);

  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await fetch('/api/analyze', {
      method: 'POST',
      body: formData
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || 'Analysis failed on server.');
    }

    const report = await response.json();
    displayReport(report);
    showToast(`Forensic analysis completed for ${file.name}`);
  } catch (err) {
    alert(`Forensic analysis error: ${err.message}`);
  } finally {
    showLoading(false);
  }
}

async function runSampleAnalysis(sampleId) {
  showLoading(true, `Executing adaptive control loop on synthetic case '${sampleId}'...`);

  try {
    const response = await fetch(`/api/analyze-sample/${sampleId}`, {
      method: 'POST'
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || 'Sample run failed.');
    }

    const report = await response.json();
    displayReport(report);
    showToast(`Benchmark case '${sampleId}' processed.`);
  } catch (err) {
    alert(`Sample analysis error: ${err.message}`);
  } finally {
    showLoading(false);
  }
}

// --------------------------------------------------------------------------
// Display Forensic Report Data
// --------------------------------------------------------------------------
function displayReport(report) {
  state.currentReport = report;
  state.selectedRegionIndex = null;
  state.zoomLevel = 1.0;
  state.verifiedSteps.clear();
  applyZoom();

  // Enable Export buttons
  elements.btnExportJson.disabled = false;
  elements.btnExportMd.disabled = false;
  elements.btnViewMeta.disabled = false;

  // 1. Pipeline Stepper
  updatePipelineStepper(report);

  // 2. Triage Summary Card & Forensic Pillars
  renderTriageHeader(report);
  renderForensicPillars(report);

  // 3. Timeline Decision Trace
  renderExecutionTimeline(report.execution_trace || []);

  // 4. Document Image Visualizer
  updateImageView();

  // 5. Suspicious Regions Chips
  renderSuspiciousRegions(report.suspicious_regions || []);

  // 6. Unresolved Conflicts
  renderConflicts(report.unresolved_conflicts || []);

  // 7. Evidence Matrix
  renderEvidence();

  // 8. Human Verification Steps
  renderVerificationChecklist(report.recommended_verification_steps || []);

  // 9. Document Quick Stats Strip
  renderDocStats(report);
}

function updatePipelineStepper(report) {
  const trace = report.execution_trace || [];
  const decisions = trace.map(t => t.decision);
  const executedAgents = new Set(trace.map(t => t.agent.toLowerCase().replace(/\s+/g, '_')));

  const hasEarlyStop = decisions.includes('EARLY_STOP');
  const hasReExam = decisions.includes('ADAPTIVE_REEXAMINATION_PASS');

  // Update Badge
  elements.agentModeBadge.className = 'agent-mode-badge';
  if (hasEarlyStop) {
    elements.agentModeBadge.textContent = 'Early Stop (Compute Saved)';
    elements.agentModeBadge.classList.add('badge-early-stop');
    elements.pipelineStatusText.textContent = 'Authentic baseline confirmed. Non-essential passes skipped.';
  } else if (hasReExam) {
    elements.agentModeBadge.textContent = 'Adaptive Re-examination';
    elements.agentModeBadge.classList.add('badge-deep-pass');
    elements.pipelineStatusText.textContent = 'Evidence conflict surfaced. Extra high-sensitivity pass executed.';
  } else {
    elements.agentModeBadge.textContent = 'Full Multi-Modal Pass';
    elements.pipelineStatusText.textContent = 'Standard multi-agent pipeline completed.';
  }

  // Update Individual Nodes
  elements.pipelineNodes.forEach((node, idx) => {
    node.className = 'pipeline-node';
    const agentKey = node.dataset.agent;

    if (hasEarlyStop && idx >= 5) {
      // Skipped due to early stop
      node.classList.add('node-skipped');
    } else if (hasReExam && (agentKey === 'image_forensics' || agentKey === 'evidence_reasoning')) {
      node.classList.add('node-reexam');
    } else {
      node.classList.add('node-completed');
    }
  });
}

function renderTriageHeader(report) {
  elements.triageCategory.textContent = report.likely_manipulation_category.replace(/-/g, ' ');

  // Risk Badge & Level
  const level = (report.risk_level || 'low').toLowerCase();
  elements.riskBadge.className = `risk-badge badge-${level}`;
  elements.riskLevelLabel.textContent = `${report.risk_level.toUpperCase()} RISK`;

  // Score Number & Progress Bar
  const score = Math.min(100, Math.max(0, report.risk_score || 0));
  elements.riskScoreNum.textContent = score.toFixed(1);
  elements.scoreFill.style.width = `${score}%`;
  if (elements.scoreProgressbar) {
    elements.scoreProgressbar.setAttribute('aria-valuenow', score.toFixed(1));
  }

  if (score < 35) {
    elements.scoreSeverityTag.textContent = 'Low Forensics Concern';
    elements.scoreSeverityTag.style.color = 'var(--risk-low)';
  } else if (score < 65) {
    elements.scoreSeverityTag.textContent = 'Moderate Discrepancies';
    elements.scoreSeverityTag.style.color = 'var(--risk-medium)';
  } else {
    elements.scoreSeverityTag.textContent = 'Significant Tampering Signs';
    elements.scoreSeverityTag.style.color = 'var(--risk-high)';
  }

  // Document metadata summary
  elements.docMetaSummary.style.display = 'grid';
  elements.metaDocId.textContent = report.document_id;
  elements.metaDocType.textContent = report.document_type || 'Questioned Document';
  elements.metaAnalysisDate.textContent = report.analysis_date ? (report.analysis_date.slice(0, 19).replace('T', ' ') + ' UTC') : '-';
}

function renderForensicPillars(report) {
  elements.forensicPillars.style.display = 'flex';
  const score = report.risk_score || 0;
  const regions = report.suspicious_regions || [];
  const conflicts = report.unresolved_conflicts || [];

  // Metadata Integrity
  const isSuspiciousMeta = conflicts.some(c => c.toLowerCase().includes('photoshop') || c.toLowerCase().includes('metadata'));
  const metaScore = isSuspiciousMeta ? 45 : (score < 30 ? 98 : 72);
  elements.pillarMetaVal.textContent = `${metaScore}%`;
  elements.pillarMetaFill.style.width = `${metaScore}%`;
  elements.pillarMetaFill.style.backgroundColor = metaScore > 75 ? 'var(--risk-low)' : 'var(--risk-medium)';

  // ELA Uniformity
  const elaRegions = regions.filter(r => r.source_method && r.source_method.includes('ela'));
  const elaScore = elaRegions.length > 0 ? Math.max(15, 100 - elaRegions.length * 35) : (score > 60 ? 30 : 96);
  elements.pillarElaVal.textContent = `${elaScore}%`;
  elements.pillarElaFill.style.width = `${elaScore}%`;
  elements.pillarElaFill.style.backgroundColor = elaScore > 70 ? 'var(--risk-low)' : 'var(--risk-high)';

  // Noise Consistency
  const noiseScore = report.likely_manipulation_category === 'splicing' ? 25 : (score > 60 ? 45 : 94);
  elements.pillarNoiseVal.textContent = `${noiseScore}%`;
  elements.pillarNoiseFill.style.width = `${noiseScore}%`;
  elements.pillarNoiseFill.style.backgroundColor = noiseScore > 70 ? 'var(--risk-low)' : 'var(--risk-high)';

  // Typography Alignment
  const typoScore = report.likely_manipulation_category === 'text-replacement' ? 20 : (score > 60 ? 55 : 99);
  elements.pillarTypoVal.textContent = `${typoScore}%`;
  elements.pillarTypoFill.style.width = `${typoScore}%`;
  elements.pillarTypoFill.style.backgroundColor = typoScore > 70 ? 'var(--risk-low)' : 'var(--risk-medium)';
}

function renderDocStats(report) {
  elements.docStatsStrip.style.display = 'flex';
  elements.statGenre.textContent = report.document_type || 'Document';
  elements.statDocId.textContent = report.document_id.slice(0, 16) + '...';
  elements.statAnomalyCount.textContent = `${(report.suspicious_regions || []).length} Detected`;

  const decisions = (report.execution_trace || []).map(t => t.decision);
  if (decisions.includes('EARLY_STOP')) {
    elements.statMode.textContent = 'Early Stop';
  } else if (decisions.includes('ADAPTIVE_REEXAMINATION_PASS')) {
    elements.statMode.textContent = 'Adaptive Pass';
  } else {
    elements.statMode.textContent = 'Standard';
  }
}

function updateImageView() {
  if (!state.currentReport || !state.currentReport.page_artifacts || state.currentReport.page_artifacts.length === 0) {
    elements.viewportEmpty.style.display = 'flex';
    elements.imageStage.style.display = 'none';
    elements.splitStage.style.display = 'none';
    return;
  }

  elements.viewportEmpty.style.display = 'none';
  const artifacts = state.currentReport.page_artifacts[0];

  if (state.currentView === 'split') {
    // Show Split Stage
    elements.imageStage.style.display = 'none';
    elements.splitStage.style.display = 'flex';
    elements.splitImgBefore.src = artifacts.original_image;
    elements.splitImgAfter.src = artifacts.heatmap_image || artifacts.overlay_image;
    return;
  }

  // Normal Stage
  elements.splitStage.style.display = 'none';
  elements.imageStage.style.display = 'inline-block';

  let src = artifacts.original_image;
  elements.forensicBlendedHeatmap.style.display = 'none';

  if (state.currentView === 'overlay') {
    src = artifacts.overlay_image || artifacts.original_image;
  } else if (state.currentView === 'heatmap') {
    src = artifacts.heatmap_image;
  }

  elements.forensicImage.src = src;
  renderOverlayBBoxes();
}

function renderOverlayBBoxes() {
  if (!state.currentReport || state.currentView !== 'overlay') {
    elements.interactiveOverlay.innerHTML = '';
    return;
  }

  const regions = state.currentReport.suspicious_regions || [];
  elements.interactiveOverlay.innerHTML = '';

  const img = elements.forensicImage;
  if (!img.naturalWidth || !img.naturalHeight) {
    img.onload = renderOverlayBBoxes;
    return;
  }

  elements.interactiveOverlay.setAttribute('viewBox', `0 0 ${img.naturalWidth} ${img.naturalHeight}`);

  regions.forEach((reg, idx) => {
    const [x0, y0, x1, y1] = reg.bbox;
    const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
    rect.setAttribute('x', Math.min(x0, x1));
    rect.setAttribute('y', Math.min(y0, y1));
    rect.setAttribute('width', Math.abs(x1 - x0));
    rect.setAttribute('height', Math.abs(y1 - y0));
    rect.setAttribute('rx', '4');
    rect.setAttribute('class', `bbox-rect ${state.selectedRegionIndex === idx ? 'bbox-selected' : ''}`);

    rect.addEventListener('click', () => {
      selectRegion(idx);
    });

    elements.interactiveOverlay.appendChild(rect);
  });
}

function selectRegion(idx) {
  state.selectedRegionIndex = idx;
  renderOverlayBBoxes();

  // Scroll matching chip into view
  const chips = elements.regionsChips.querySelectorAll('.region-chip');
  chips.forEach((c, i) => {
    if (i === idx) {
      c.style.borderColor = 'var(--risk-high)';
      c.style.background = 'var(--risk-high-bg)';
      c.scrollIntoView({ behavior: 'smooth', inline: 'center', block: 'nearest' });
    } else {
      c.style.borderColor = 'var(--card-border)';
      c.style.background = 'var(--bg-secondary)';
    }
  });

  showToast(`Focused on Anomaly #${idx + 1}`);
}

function renderSuspiciousRegions(regions) {
  elements.regionCount.textContent = regions.length;

  if (regions.length === 0) {
    elements.regionsBar.style.display = 'none';
    return;
  }

  elements.regionsBar.style.display = 'flex';
  elements.regionsChips.innerHTML = '';

  regions.forEach((reg, idx) => {
    const chip = document.createElement('div');
    chip.className = 'region-chip';
    chip.tabIndex = 0;
    chip.setAttribute('role', 'button');
    const confPercent = Math.round(reg.confidence * 100);

    chip.innerHTML = `
      <div class="region-chip-top">
        <span class="region-conf-badge">${confPercent}% Conf</span>
        <span class="region-coord">[${reg.bbox.join(', ')}]</span>
      </div>
      <p class="region-reason" title="${reg.reason}">${reg.associated_text ? `"${reg.associated_text}" — ` : ''}${reg.reason}</p>
    `;

    chip.addEventListener('click', () => selectRegion(idx));
    chip.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        selectRegion(idx);
      }
    });

    elements.regionsChips.appendChild(chip);
  });
}

function renderConflicts(conflicts) {
  if (conflicts && conflicts.length > 0) {
    elements.conflictAlert.style.display = 'flex';
    elements.conflictText.textContent = conflicts.join(' | ');
  } else {
    elements.conflictAlert.style.display = 'none';
  }
}

function renderExecutionTimeline(trace) {
  elements.traceStepCount.textContent = `${trace.length} Steps`;
  elements.timelineList.innerHTML = '';

  if (trace.length === 0) {
    elements.timelineList.innerHTML = '<div class="timeline-empty-state"><p>No execution steps recorded.</p></div>';
    return;
  }

  trace.forEach((entry) => {
    const item = document.createElement('div');
    item.className = 'timeline-item';

    let decisionClass = 'tag-proceed';
    let nodeClass = '';
    if (entry.decision === 'EARLY_STOP') {
      decisionClass = 'tag-early-stop';
      nodeClass = 'decision-early-stop';
    } else if (entry.decision === 'ADAPTIVE_REEXAMINATION_PASS') {
      decisionClass = 'tag-deep-pass';
      nodeClass = 'decision-deep-pass';
    } else if (entry.decision === 'COMPLETE') {
      decisionClass = 'tag-complete';
    }

    item.innerHTML = `
      <div class="timeline-node ${nodeClass}">${entry.step}</div>
      <div class="timeline-content">
        <div class="timeline-header-row">
          <span class="timeline-agent-name">${entry.agent}</span>
          <span class="timeline-decision-tag ${decisionClass}">${entry.decision.replace(/_/g, ' ')}</span>
        </div>
        <p class="timeline-rationale">${entry.rationale}</p>
      </div>
    `;

    elements.timelineList.appendChild(item);
  });
}

function renderEvidence() {
  if (!state.currentReport || !state.currentReport.evidence) {
    elements.evidenceList.innerHTML = '<div class="empty-evidence-text">Evidence lineage will appear here once forensic analysis completes.</div>';
    elements.evidenceCount.textContent = '0 items';
    return;
  }

  const items = state.currentReport.evidence.filter(e => {
    return state.currentEvidenceType === 'interpretations' 
      ? e.type === 'interpretation'
      : e.type === 'observation';
  });

  elements.evidenceCount.textContent = `${items.length} items`;
  elements.evidenceList.innerHTML = '';

  if (items.length === 0) {
    elements.evidenceList.innerHTML = `<div class="empty-evidence-text">No ${state.currentEvidenceType} recorded.</div>`;
    return;
  }

  items.forEach(ev => {
    const card = document.createElement('div');
    card.className = 'evidence-item-card';

    let citationsHtml = '';
    if (ev.supported_by && ev.supported_by.length > 0) {
      citationsHtml = `
        <div class="evidence-citation-chips">
          <span style="font-size: 0.65rem; color: var(--text-muted);">Citing:</span>
          ${ev.supported_by.map(id => `<span class="citation-chip" data-cite="${id}">[${id}]</span>`).join('')}
        </div>
      `;
    }

    card.innerHTML = `
      <p>
        <span class="evidence-id-tag">[${ev.id || 'EVID'}]</span>
        ${ev.text}
      </p>
      ${citationsHtml}
    `;

    // Click on citation chip to switch to observations and highlight
    card.querySelectorAll('.citation-chip').forEach(chip => {
      chip.addEventListener('click', (e) => {
        e.stopPropagation();
        const targetId = chip.dataset.cite;
        switchToObservation(targetId);
      });
    });

    elements.evidenceList.appendChild(card);
  });
}

function switchToObservation(targetId) {
  state.currentEvidenceType = 'observations';
  elements.evTabBtns.forEach(b => {
    const isObs = b.dataset.evType === 'observations';
    b.classList.toggle('active', isObs);
    b.setAttribute('aria-selected', isObs ? 'true' : 'false');
  });
  renderEvidence();

  // Highlight specific observation
  setTimeout(() => {
    const cards = elements.evidenceList.querySelectorAll('.evidence-item-card');
    cards.forEach(c => {
      if (c.textContent.includes(`[${targetId}]`)) {
        c.style.borderColor = 'var(--accent)';
        c.style.background = 'var(--accent-glow)';
        c.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    });
  }, 50);
}

function renderVerificationChecklist(steps) {
  elements.verificationChecklist.innerHTML = '';
  elements.investigatorSignoff.style.display = steps.length > 0 ? 'flex' : 'none';

  if (!steps || steps.length === 0) {
    elements.verificationChecklist.innerHTML = '<li class="empty-check-item">Standard baseline verification recommended.</li>';
    elements.checklistProgressBadge.textContent = '0 / 0';
    return;
  }

  elements.checklistProgressBadge.textContent = `0 / ${steps.length}`;

  steps.forEach((step, idx) => {
    const li = document.createElement('li');
    li.className = 'checklist-item';
    li.dataset.index = idx;

    li.innerHTML = `
      <input type="checkbox" class="checklist-checkbox" id="chk-${idx}">
      <label for="chk-${idx}">${step}</label>
    `;

    const checkbox = li.querySelector('.checklist-checkbox');
    checkbox.addEventListener('change', () => {
      if (checkbox.checked) {
        state.verifiedSteps.add(idx);
        li.classList.add('verified');
      } else {
        state.verifiedSteps.delete(idx);
        li.classList.remove('verified');
      }
      elements.checklistProgressBadge.textContent = `${state.verifiedSteps.size} / ${steps.length}`;
    });

    elements.verificationChecklist.appendChild(li);
  });
}

function populateMetaModal(report) {
  elements.modalMetaGrid.innerHTML = `
    <div class="meta-card-cell">
      <span class="meta-card-title">Document ID</span>
      <span class="meta-card-val">${report.document_id}</span>
    </div>
    <div class="meta-card-cell">
      <span class="meta-card-title">Genre / Type</span>
      <span class="meta-card-val">${report.document_type || 'Questioned Document'}</span>
    </div>
    <div class="meta-card-cell">
      <span class="meta-card-title">Analysis Timestamp</span>
      <span class="meta-card-val">${report.analysis_date || '-'}</span>
    </div>
    <div class="meta-card-cell">
      <span class="meta-card-title">Triage Classification</span>
      <span class="meta-card-val">${report.risk_level.toUpperCase()} (${report.risk_score} / 100)</span>
    </div>
    <div class="meta-card-cell">
      <span class="meta-card-title">Manipulation Modality</span>
      <span class="meta-card-val">${report.likely_manipulation_category}</span>
    </div>
    <div class="meta-card-cell">
      <span class="meta-card-title">Methods Executed</span>
      <span class="meta-card-val">${(report.methods_executed || []).length} Specialized Agents</span>
    </div>
  `;

  elements.modalRawJson.textContent = JSON.stringify(report, null, 2);
}

function generateMarkdownDocket(report) {
  return `# ADFF FORENSIC INVESTIGATION DOCKET
**Document ID**: \`${report.document_id}\`  
**Analysis Date**: ${report.analysis_date}  
**Document Genre**: ${report.document_type || 'Questioned Document'}  
**Overall Triage**: **${report.risk_level.toUpperCase()} RISK** (Score: ${report.risk_score}/100)  
**Likely Manipulation Modality**: \`${report.likely_manipulation_category}\`  

---

## 1. Executive Summary & Findings
${report.disclaimer}

- **Total Localized Anomalies**: ${(report.suspicious_regions || []).length}
- **Methods Executed**: ${(report.methods_executed || []).join(', ')}
- **Unresolved Conflicts**: ${(report.unresolved_conflicts || []).length > 0 ? report.unresolved_conflicts.join('; ') : 'None'}

---

## 2. Localized Anomaly Regions
| # | Bounding Box [x0, y0, x1, y1] | Confidence | Reason | Associated Text |
|---|---|---|---|---|
${(report.suspicious_regions || []).map((r, i) => `| ${i + 1} | \`[${r.bbox.join(', ')}]\` | ${(r.confidence * 100).toFixed(0)}% | ${r.reason} | ${r.associated_text ? `\`${r.associated_text}\`` : '-'} |`).join('\n')}

---

## 3. Evidence Matrix
### Observations [OBS]
${(report.evidence || []).filter(e => e.type === 'observation').map(e => `- **[${e.id}]**: ${e.text}`).join('\n')}

### Interpretations [INT]
${(report.evidence || []).filter(e => e.type === 'interpretation').map(e => `- **[${e.id}]**: ${e.text} ${e.supported_by ? `*(Citing: ${e.supported_by.join(', ')})*` : ''}`).join('\n')}

---

## 4. Investigator Verification Checklist
${(report.recommended_verification_steps || []).map((s, i) => `- [ ] ${s}`).join('\n')}

---

## 5. Orchestrator Autonomous Decision Trace
${(report.execution_trace || []).map(t => `${t.step}. **${t.agent}** [${t.decision}]: ${t.rationale}`).join('\n')}

*Generated by ADFF Multi-Agent Forensic Platform.*
`;
}

// --------------------------------------------------------------------------
// Utility Helpers
// --------------------------------------------------------------------------
function showToast(message) {
  if (!elements.toast || !elements.toastMessage) return;
  if (toastTimeout) clearTimeout(toastTimeout);

  elements.toastMessage.textContent = message;
  elements.toast.style.display = 'flex';

  toastTimeout = setTimeout(() => {
    elements.toast.style.display = 'none';
  }, 2800);
}

function showLoading(isLoading, text = '') {
  if (isLoading) {
    elements.spinnerOverlay.style.display = 'flex';
    elements.spinnerStatusText.textContent = text;
  } else {
    elements.spinnerOverlay.style.display = 'none';
  }
}

function formatBytes(bytes, decimals = 1) {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}
