/**
 * ADFF - Agentic AI Document Tampering Detection & Forensic Analysis
 * Interactive Frontend Controller
 * Conforms strictly to Design System Tokens & 10/10 UI/UX Standards
 */

// Application State
const state = {
  currentReport: null,
  currentView: 'overlay', // 'overlay' | 'heatmap' | 'original'
  currentEvidenceType: 'interpretations', // 'interpretations' | 'observations'
  zoomLevel: 1.0,
  selectedRegionIndex: null
};

// DOM Elements Cache
const elements = {
  // Theme Toggle
  themeToggleBtn: document.getElementById('theme-toggle-btn'),
  themeIconSun: document.getElementById('theme-icon-sun'),
  themeIconMoon: document.getElementById('theme-icon-moon'),

  // Header & Inputs
  sampleSelect: document.getElementById('sample-select'),
  btnRunSample: document.getElementById('btn-run-sample'),
  fileUploadInput: document.getElementById('file-upload-input'),
  dropzone: document.getElementById('dropzone'),
  currentFileBadge: document.getElementById('current-file-badge'),
  currentFileName: document.getElementById('current-file-name'),
  currentFileSize: document.getElementById('current-file-size'),
  
  // Viewer
  tabBtns: document.querySelectorAll('.tab-btn'),
  viewportEmpty: document.getElementById('viewport-empty'),
  imageStage: document.getElementById('image-stage'),
  forensicImage: document.getElementById('forensic-image'),
  interactiveOverlay: document.getElementById('interactive-overlay'),
  spinnerOverlay: document.getElementById('spinner-overlay'),
  spinnerStatusText: document.getElementById('spinner-status-text'),
  btnZoomIn: document.getElementById('btn-zoom-in'),
  btnZoomOut: document.getElementById('btn-zoom-out'),
  btnZoomReset: document.getElementById('btn-zoom-reset'),
  
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
  docMetaSummary: document.getElementById('doc-meta-summary'),
  metaDocId: document.getElementById('meta-doc-id'),
  metaDocType: document.getElementById('meta-doc-type'),
  metaAnalysisDate: document.getElementById('meta-analysis-date'),

  // Conflicts
  conflictAlert: document.getElementById('conflict-alert'),
  conflictText: document.getElementById('conflict-text'),

  // Evidence
  evTabBtns: document.querySelectorAll('.ev-tab-btn'),
  evidenceList: document.getElementById('evidence-list'),
  evidenceCount: document.getElementById('evidence-count'),

  // Verification
  verificationChecklist: document.getElementById('verification-checklist'),

  // Actions
  btnExportJson: document.getElementById('btn-export-json'),
  btnCopyJson: document.getElementById('btn-copy-json'),

  // Toast
  toast: document.getElementById('toast'),
  toastMessage: document.getElementById('toast-message')
};

// Toast notification timeout reference
let toastTimeout = null;

// Initialization
document.addEventListener('DOMContentLoaded', () => {
  initTheme();
  setupEventListeners();
  loadSampleMetadata();
});

// --------------------------------------------------------------------------
// Theme Management (Light / Dark Mode)
// --------------------------------------------------------------------------
function initTheme() {
  const savedTheme = localStorage.getItem('adff-theme');
  // Default to light theme (matching official reference UI) unless user toggled dark
  const isDark = savedTheme === 'dark';

  applyTheme(isDark);

  if (elements.themeToggleBtn) {
    elements.themeToggleBtn.addEventListener('click', () => {
      const currentlyDark = document.documentElement.classList.contains('dark');
      applyTheme(!currentlyDark);
      showToast(!currentlyDark ? 'Dark theme enabled' : 'Light theme enabled');
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
  // Sample Run
  if (elements.btnRunSample) {
    elements.btnRunSample.disabled = false;
    elements.btnRunSample.addEventListener('click', () => {
      const selected = elements.sampleSelect.value || 'edited_amount_invoice';
      runSampleAnalysis(selected);
    });
  }

  if (elements.sampleSelect) {
    elements.sampleSelect.addEventListener('change', () => {
      if (elements.btnRunSample) {
        elements.btnRunSample.disabled = false;
      }
    });
  }

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

  // View Mode Tabs (Suspicious Overlay, Thermal Heatmap, Base Document)
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

  // Evidence Tabs (Interpretations vs Observations)
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

  // Export JSON (§8)
  elements.btnExportJson.addEventListener('click', () => {
    if (!state.currentReport) return;
    const jsonStr = JSON.stringify(state.currentReport, null, 2);
    const blob = new Blob([jsonStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `ADFF_Report_${state.currentReport.document_id}.json`;
    a.click();
    URL.revokeObjectURL(url);
    showToast('Forensic report JSON exported.');
  });

  // Copy JSON
  elements.btnCopyJson.addEventListener('click', () => {
    if (!state.currentReport) return;
    const jsonStr = JSON.stringify(state.currentReport, null, 2);
    navigator.clipboard.writeText(jsonStr).then(() => {
      showToast('Forensic report copied to clipboard.');
    }).catch(() => {
      showToast('Could not copy report to clipboard.');
    });
  });
}

function applyZoom() {
  elements.imageStage.style.transform = `scale(${state.zoomLevel})`;
}

// --------------------------------------------------------------------------
// Sample Metadata & Analysis Handlers
// --------------------------------------------------------------------------
async function loadSampleMetadata() {
  try {
    const res = await fetch('/api/samples');
    if (res.ok) {
      const samples = await res.json();
      // Metadata loaded successfully
    }
  } catch (err) {
    console.warn('Could not load samples metadata', err);
  }
}

async function handleFileUpload(file) {
  showLoading(true, `Ingesting and analyzing '${file.name}'...`);
  
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
    showToast(`Analysis complete for ${file.name}`);
  } catch (err) {
    alert(`Forensic analysis error: ${err.message}`);
  } finally {
    showLoading(false);
  }
}

async function runSampleAnalysis(sampleId) {
  showLoading(true, `Orchestrating adaptive analysis on sample '${sampleId}'...`);

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
  applyZoom();

  // Enable Export buttons
  elements.btnExportJson.disabled = false;
  elements.btnCopyJson.disabled = false;

  // 1. Triage Summary Card
  renderTriageHeader(report);

  // 2. Timeline Decision Trace
  renderExecutionTimeline(report.execution_trace || []);

  // 3. Document Image Visualizer
  updateImageView();

  // 4. Suspicious Regions Chips
  renderSuspiciousRegions(report.suspicious_regions || []);

  // 5. Unresolved Conflicts
  renderConflicts(report.unresolved_conflicts || []);

  // 6. Evidence Matrix
  renderEvidence();

  // 7. Human Verification Steps
  renderVerificationChecklist(report.recommended_verification_steps || []);
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

  // Document metadata summary
  elements.docMetaSummary.style.display = 'grid';
  elements.metaDocId.textContent = report.document_id;
  elements.metaDocType.textContent = report.document_type || 'Questioned Document';
  elements.metaAnalysisDate.textContent = report.analysis_date ? (report.analysis_date.slice(0, 19).replace('T', ' ') + ' UTC') : '-';
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

function updateImageView() {
  if (!state.currentReport || !state.currentReport.page_artifacts || state.currentReport.page_artifacts.length === 0) {
    elements.viewportEmpty.style.display = 'block';
    elements.imageStage.style.display = 'none';
    return;
  }

  elements.viewportEmpty.style.display = 'none';
  elements.imageStage.style.display = 'inline-block';

  const artifacts = state.currentReport.page_artifacts[0];
  let src = artifacts.original_image;

  if (state.currentView === 'overlay') {
    src = artifacts.overlay_image || artifacts.original_image;
  } else if (state.currentView === 'heatmap') {
    src = artifacts.heatmap_image;
  }

  elements.forensicImage.src = src;
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
    chip.setAttribute('aria-label', `Suspicious region: ${reg.reason}`);
    const confPercent = Math.round(reg.confidence * 100);

    chip.innerHTML = `
      <div class="region-chip-top">
        <span class="region-conf-badge">${confPercent}% Conf</span>
        <span class="region-coord">[${reg.bbox.join(', ')}]</span>
      </div>
      <p class="region-reason" title="${reg.reason}">${reg.associated_text ? `"${reg.associated_text}" — ` : ''}${reg.reason}</p>
    `;

    const selectChip = () => {
      document.querySelectorAll('.region-chip').forEach(c => {
        c.style.borderColor = 'var(--border)';
        c.style.backgroundColor = 'var(--card)';
      });
      chip.style.borderColor = 'var(--ring)';
      chip.style.backgroundColor = 'var(--accent)';
      state.selectedRegionIndex = idx;
    };

    chip.addEventListener('click', selectChip);
    chip.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        selectChip();
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

function renderEvidence() {
  if (!state.currentReport || !state.currentReport.evidence) {
    elements.evidenceList.innerHTML = '<div class="empty-evidence-text">Evidence lineage will appear here once forensic analysis completes.</div>';
    elements.evidenceCount.textContent = '0 items';
    return;
  }

  const items = state.currentReport.evidence.filter(e => {
    if (state.currentEvidenceType === 'interpretations') {
      return e.type === 'interpretation';
    } else {
      return e.type === 'observation';
    }
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
          <span style="font-size: 0.65rem; color: var(--muted-foreground);">Supported by:</span>
          ${ev.supported_by.map(id => `<span class="citation-chip">${id}</span>`).join('')}
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

    elements.evidenceList.appendChild(card);
  });
}

function renderVerificationChecklist(steps) {
  elements.verificationChecklist.innerHTML = '';

  if (!steps || steps.length === 0) {
    elements.verificationChecklist.innerHTML = '<li class="empty-check-item">Standard baseline verification recommended.</li>';
    return;
  }

  steps.forEach((step, idx) => {
    const li = document.createElement('li');
    li.className = 'checklist-item';
    li.innerHTML = `
      <span class="checklist-num" aria-hidden="true">${idx + 1}</span>
      <span>${step}</span>
    `;
    elements.verificationChecklist.appendChild(li);
  });
}

// --------------------------------------------------------------------------
// Utility Feedback Helpers
// --------------------------------------------------------------------------
function showToast(message) {
  if (!elements.toast || !elements.toastMessage) return;
  
  if (toastTimeout) {
    clearTimeout(toastTimeout);
  }

  elements.toastMessage.textContent = message;
  elements.toast.style.display = 'flex';

  toastTimeout = setTimeout(() => {
    elements.toast.style.display = 'none';
  }, 2500);
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
