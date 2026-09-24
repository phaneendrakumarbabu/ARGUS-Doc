/**
 * ADFF - Agentic AI Document Tampering Detection & Forensic Analysis
 * Interactive Forensic Workstation Controller
 * Preserves Established Design System & UI/UX Standards
 */

// Application State
const state = {
  currentReport: null,
  currentView: 'overlay', // 'overlay' | 'heatmap' | 'original' | 'split'
  currentEvidenceType: 'interpretations', // 'interpretations' | 'observations'
  timelineFilter: 'all', // 'all' | 'decisions' | 'custody'
  zoomLevel: 1.0,
  selectedRegionIndex: null,
  searchQuery: '',
  evidenceFilter: '',
  activeModalTab: 'cases',
  cases: [],
  auditLog: [],
  verificationStatus: {}
};

// DOM Elements Cache
const elements = {
  // Theme Toggle
  themeToggleBtn: document.getElementById('theme-toggle-btn'),
  themeIconSun: document.getElementById('theme-icon-sun'),
  themeIconMoon: document.getElementById('theme-icon-moon'),

  // Header & Search
  globalSearchInput: document.getElementById('global-search-input'),
  searchClearBtn: document.getElementById('search-clear-btn'),
  btnOpenCases: document.getElementById('btn-open-cases'),
  sampleSelect: document.getElementById('sample-select'),
  btnRunSample: document.getElementById('btn-run-sample'),
  fileUploadInput: document.getElementById('file-upload-input'),

  // Left Sidebar: Ingestion & Timeline
  dropzone: document.getElementById('dropzone'),
  currentFileBadge: document.getElementById('current-file-badge'),
  currentFileName: document.getElementById('current-file-name'),
  currentFileSize: document.getElementById('current-file-size'),
  ingestShaBadge: document.getElementById('ingest-sha-badge'),
  ingestShaVal: document.getElementById('ingest-sha-val'),
  btnCopySha: document.getElementById('btn-copy-sha'),

  timelineList: document.getElementById('timeline-list'),
  traceStepCount: document.getElementById('trace-step-count'),
  btnFilterAll: document.getElementById('btn-filter-all'),
  btnFilterDecisions: document.getElementById('btn-filter-decisions'),
  btnFilterCustody: document.getElementById('btn-filter-custody'),

  // Center Viewer
  tabBtns: document.querySelectorAll('.tab-btn'),
  btnTabSplit: document.getElementById('btn-tab-split'),
  viewportEmpty: document.getElementById('viewport-empty'),
  canvasViewport: document.getElementById('canvas-viewport'),
  imageStage: document.getElementById('image-stage'),
  forensicImage: document.getElementById('forensic-image'),
  interactiveOverlay: document.getElementById('interactive-overlay'),
  splitStage: document.getElementById('split-stage'),
  splitBaseImage: document.getElementById('split-base-image'),
  splitHeatImage: document.getElementById('split-heat-image'),
  regionTooltip: document.getElementById('region-tooltip'),
  tooltipConf: document.getElementById('tooltip-conf'),
  tooltipCoords: document.getElementById('tooltip-coords'),
  tooltipReason: document.getElementById('tooltip-reason'),
  tooltipText: document.getElementById('tooltip-text'),

  spinnerOverlay: document.getElementById('spinner-overlay'),
  spinnerStatusText: document.getElementById('spinner-status-text'),
  btnZoomIn: document.getElementById('btn-zoom-in'),
  btnZoomOut: document.getElementById('btn-zoom-out'),
  btnZoomReset: document.getElementById('btn-zoom-reset'),
  zoomReadout: document.getElementById('zoom-readout'),

  // Regions Bar
  regionsBar: document.getElementById('regions-bar'),
  regionCount: document.getElementById('region-count'),
  regionsChips: document.getElementById('regions-chips'),

  // Right Docket Panel
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

  // AI Signals Breakdown
  signalsSection: document.getElementById('signals-section'),
  signalsClustersBadge: document.getElementById('signals-clusters-badge'),
  signalElaVal: document.getElementById('signal-ela-val'),
  signalNoiseVal: document.getElementById('signal-noise-val'),
  signalEdgeVal: document.getElementById('signal-edge-val'),
  signalTypoVal: document.getElementById('signal-typo-val'),

  // Grouped Forensic Metadata Inspector
  groupedMetaAccordion: document.getElementById('grouped-meta-accordion'),
  metaGroupHeaders: document.querySelectorAll('.meta-group-header'),
  metaGroupFilename: document.getElementById('meta-group-filename'),
  metaGroupFilesize: document.getElementById('meta-group-filesize'),
  metaGroupFiletype: document.getElementById('meta-group-filetype'),
  metaGroupSha: document.getElementById('meta-group-sha'),
  btnCopyMetaSha: document.getElementById('btn-copy-meta-sha'),
  metaGroupCreator: document.getElementById('meta-group-creator'),
  metaGroupProducer: document.getElementById('meta-group-producer'),
  metaGroupCreated: document.getElementById('meta-group-created'),
  metaGroupModified: document.getElementById('meta-group-modified'),
  metaGroupTemporalDesc: document.getElementById('meta-group-temporal-desc'),
  metaGroupIncremental: document.getElementById('meta-group-incremental'),
  metaGroupEof: document.getElementById('meta-group-eof'),
  metaGroupSoftware: document.getElementById('meta-group-software'),

  // Conflicts
  conflictAlert: document.getElementById('conflict-alert'),
  conflictText: document.getElementById('conflict-text'),

  // Evidence
  evTabBtns: document.querySelectorAll('.ev-tab-btn'),
  evidenceFilterInput: document.getElementById('evidence-filter-input'),
  evidenceList: document.getElementById('evidence-list'),
  evidenceCount: document.getElementById('evidence-count'),

  // Verification Checklist
  verificationChecklist: document.getElementById('verification-checklist'),

  // Export & Docket Actions
  btnExportJson: document.getElementById('btn-export-json'),
  btnCopyJson: document.getElementById('btn-copy-json'),
  btnDownloadDocket: document.getElementById('btn-download-docket'),
  btnPreviewDocket: document.getElementById('btn-preview-docket'),

  // Cases & Audit Modal
  casesModal: document.getElementById('cases-modal'),
  btnCloseCasesModal: document.getElementById('btn-close-cases-modal'),
  modalTabBtns: document.querySelectorAll('.modal-tab-btn'),
  modalTabCases: document.getElementById('modal-tab-cases'),
  modalTabAudit: document.getElementById('modal-tab-audit'),
  casesCountBadge: document.getElementById('cases-count-badge'),
  auditCountBadge: document.getElementById('audit-count-badge'),
  casesGridList: document.getElementById('cases-grid-list'),
  auditTableBody: document.getElementById('audit-table-body'),

  // Docket Preview Modal
  docketModal: document.getElementById('docket-modal'),
  btnCloseDocketModal: document.getElementById('btn-close-docket-modal'),
  docketPreviewContent: document.getElementById('docket-preview-content'),
  btnDownloadDocketMd: document.getElementById('btn-download-docket-md'),
  btnPrintDocket: document.getElementById('btnPrintDocket') || document.getElementById('btn-print-docket'),

  // Toast
  toast: document.getElementById('toast'),
  toastMessage: document.getElementById('toast-message')
};

// Toast notification timeout reference
let toastTimeout = null;

// --------------------------------------------------------------------------
// Initialization
// --------------------------------------------------------------------------
document.addEventListener('DOMContentLoaded', () => {
  initTheme();
  setupEventListeners();
  loadSampleMetadata();
  fetchCasesAndAudit();
});

// --------------------------------------------------------------------------
// Theme Management (Light / Dark Mode)
// --------------------------------------------------------------------------
function initTheme() {
  const savedTheme = localStorage.getItem('adff-theme');
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
  // Global Forensic Search
  if (elements.globalSearchInput) {
    elements.globalSearchInput.addEventListener('input', (e) => {
      state.searchQuery = (e.target.value || '').trim().toLowerCase();
      if (elements.searchClearBtn) {
        elements.searchClearBtn.style.display = state.searchQuery ? 'inline' : 'none';
      }
      applyGlobalSearch();
    });
  }

  if (elements.searchClearBtn) {
    elements.searchClearBtn.addEventListener('click', () => {
      elements.globalSearchInput.value = '';
      state.searchQuery = '';
      elements.searchClearBtn.style.display = 'none';
      applyGlobalSearch();
    });
  }

  // Cases Modal open/close
  if (elements.btnOpenCases) {
    elements.btnOpenCases.addEventListener('click', () => {
      openCasesModal();
    });
  }

  if (elements.btnCloseCasesModal) {
    elements.btnCloseCasesModal.addEventListener('click', () => {
      elements.casesModal.style.display = 'none';
    });
  }

  elements.casesModal.addEventListener('click', (e) => {
    if (e.target === elements.casesModal) {
      elements.casesModal.style.display = 'none';
    }
  });

  // Modal Tab switching (Cases vs Audit)
  elements.modalTabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      elements.modalTabBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const tab = btn.dataset.modalTab;
      state.activeModalTab = tab;
      if (tab === 'cases') {
        elements.modalTabCases.style.display = 'flex';
        elements.modalTabAudit.style.display = 'none';
      } else {
        elements.modalTabCases.style.display = 'none';
        elements.modalTabAudit.style.display = 'flex';
      }
    });
  });

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

  // Copy SHA Buttons
  if (elements.btnCopySha) {
    elements.btnCopySha.addEventListener('click', (e) => {
      e.stopPropagation();
      const hash = elements.ingestShaVal.textContent;
      if (hash && hash !== '...') {
        navigator.clipboard.writeText(hash).then(() => showToast('SHA-256 copied to clipboard.'));
      }
    });
  }

  if (elements.btnCopyMetaSha) {
    elements.btnCopyMetaSha.addEventListener('click', () => {
      const hash = elements.metaGroupSha.textContent;
      if (hash && hash !== '-') {
        navigator.clipboard.writeText(hash).then(() => showToast('SHA-256 copied to clipboard.'));
      }
    });
  }

  // Timeline Filter Buttons
  const timelineFilters = [elements.btnFilterAll, elements.btnFilterDecisions, elements.btnFilterCustody];
  timelineFilters.forEach(btn => {
    if (!btn) return;
    btn.addEventListener('click', () => {
      timelineFilters.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      state.timelineFilter = btn.dataset.filter;
      if (state.currentReport) {
        renderExecutionTimeline(state.currentReport.execution_trace || [], state.currentReport.chain_of_custody || []);
      }
    });
  });

  // View Mode Tabs (Suspicious Overlay, Thermal Heatmap, Base Document, Split)
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
    state.zoomLevel = Math.min(3.0, +(state.zoomLevel + 0.25).toFixed(2));
    applyZoom();
  });

  elements.btnZoomOut.addEventListener('click', () => {
    state.zoomLevel = Math.max(0.5, +(state.zoomLevel - 0.25).toFixed(2));
    applyZoom();
  });

  elements.btnZoomReset.addEventListener('click', () => {
    state.zoomLevel = 1.0;
    applyZoom();
  });

  // Mouse wheel zoom on canvas
  if (elements.canvasViewport) {
    elements.canvasViewport.addEventListener('wheel', (e) => {
      if (e.ctrlKey || e.metaKey) {
        e.preventDefault();
        if (e.deltaY < 0) {
          state.zoomLevel = Math.min(3.0, +(state.zoomLevel + 0.15).toFixed(2));
        } else {
          state.zoomLevel = Math.max(0.5, +(state.zoomLevel - 0.15).toFixed(2));
        }
        applyZoom();
      }
    }, { passive: false });
  }

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

  // Evidence Filter Input
  if (elements.evidenceFilterInput) {
    elements.evidenceFilterInput.addEventListener('input', (e) => {
      state.evidenceFilter = (e.target.value || '').trim().toLowerCase();
      renderEvidence();
    });
  }

  // Metadata Group Accordions
  elements.metaGroupHeaders.forEach(header => {
    header.addEventListener('click', () => {
      const group = header.dataset.group;
      const body = document.getElementById(`meta-group-${group}`);
      const icon = header.querySelector('.meta-group-icon');
      if (body) {
        const isHidden = body.style.display === 'none';
        body.style.display = isHidden ? 'flex' : 'none';
        if (icon) icon.textContent = isHidden ? '▾' : '▸';
      }
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
    a.download = `ADFF_Forensic_Report_${state.currentReport.document_id}.json`;
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

  // Download Docket Markdown
  if (elements.btnDownloadDocket) {
    elements.btnDownloadDocket.addEventListener('click', () => {
      downloadDocketFile();
    });
  }

  // Preview Docket
  if (elements.btnPreviewDocket) {
    elements.btnPreviewDocket.addEventListener('click', () => {
      openDocketModal();
    });
  }

  if (elements.btnCloseDocketModal) {
    elements.btnCloseDocketModal.addEventListener('click', () => {
      elements.docketModal.style.display = 'none';
    });
  }

  elements.docketModal.addEventListener('click', (e) => {
    if (e.target === elements.docketModal) {
      elements.docketModal.style.display = 'none';
    }
  });

  if (elements.btnDownloadDocketMd) {
    elements.btnDownloadDocketMd.addEventListener('click', () => {
      downloadDocketFile();
    });
  }

  if (elements.btnPrintDocket) {
    elements.btnPrintDocket.addEventListener('click', () => {
      window.print();
    });
  }
}

function applyZoom() {
  if (elements.imageStage) {
    elements.imageStage.style.transform = `scale(${state.zoomLevel})`;
  }
  if (elements.zoomReadout) {
    elements.zoomReadout.textContent = `${Math.round(state.zoomLevel * 100)}%`;
  }
}

// --------------------------------------------------------------------------
// Sample Metadata & Analysis Handlers
// --------------------------------------------------------------------------
async function loadSampleMetadata() {
  try {
    const res = await fetch('/api/samples');
    if (res.ok) {
      const samples = await res.json();
      // Metadata loaded
    }
  } catch (err) {
    console.warn('Could not load samples metadata', err);
  }
}

async function fetchCasesAndAudit() {
  try {
    const [casesRes, auditRes] = await Promise.all([
      fetch('/api/cases'),
      fetch('/api/audit-log')
    ]);

    if (casesRes.ok) {
      state.cases = await casesRes.json();
      if (elements.casesCountBadge) elements.casesCountBadge.textContent = state.cases.length;
    }

    if (auditRes.ok) {
      state.auditLog = await auditRes.json();
      if (elements.auditCountBadge) elements.auditCountBadge.textContent = state.auditLog.length;
    }
  } catch (err) {
    console.warn('Could not fetch cases/audit', err);
  }
}

async function handleFileUpload(file) {
  showLoading(true, `Ingesting and computing SHA-256 for '${file.name}'...`);
  
  elements.currentFileBadge.style.display = 'inline-flex';
  elements.currentFileName.textContent = file.name;
  elements.currentFileSize.textContent = formatBytes(file.size);

  const formData = new FormData();
  formData.append('file', file);

  try {
    // Stage 1
    updateLoadingStep(`[1/4] Validating document stream & computing SHA-256...`);
    const response = await fetch('/api/analyze', {
      method: 'POST',
      body: formData
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || 'Analysis failed on server.');
    }

    updateLoadingStep(`[3/4] Synthesizing multi-agent forensic evidence...`);
    const report = await response.json();
    displayReport(report);
    showToast(`Analysis complete for ${file.name}`);
    fetchCasesAndAudit(); // Refresh audit trail
  } catch (err) {
    alert(`Forensic analysis error: ${err.message}`);
  } finally {
    showLoading(false);
  }
}

async function runSampleAnalysis(sampleId) {
  showLoading(true, `Orchestrating adaptive analysis on sample '${sampleId}'...`);

  try {
    updateLoadingStep(`[1/3] Loading benchmark document & checking baseline...`);
    const response = await fetch(`/api/analyze-sample/${sampleId}`, {
      method: 'POST'
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || 'Sample run failed.');
    }

    updateLoadingStep(`[3/3] Compiling forensic report and audit trail...`);
    const report = await response.json();
    displayReport(report);
    showToast(`Benchmark case '${sampleId}' processed.`);
    fetchCasesAndAudit(); // Refresh audit trail
  } catch (err) {
    alert(`Sample analysis error: ${err.message}`);
  } finally {
    showLoading(false);
  }
}

function updateLoadingStep(msg) {
  if (elements.spinnerStatusText) {
    elements.spinnerStatusText.textContent = msg;
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
  if (elements.btnDownloadDocket) elements.btnDownloadDocket.disabled = false;
  if (elements.btnPreviewDocket) elements.btnPreviewDocket.disabled = false;

  // Ingestion hash pill
  if (report.document_metadata && report.document_metadata.sha256) {
    elements.ingestShaBadge.style.display = 'inline-flex';
    elements.ingestShaVal.textContent = report.document_metadata.sha256.slice(0, 16) + '...';
    elements.ingestShaVal.title = report.document_metadata.sha256;
  } else {
    elements.ingestShaBadge.style.display = 'none';
  }

  // 1. Triage Summary Card & Grouped Metadata
  renderTriageHeader(report);

  // 2. Timeline Decision Trace & Chain of Custody
  renderExecutionTimeline(report.execution_trace || [], report.chain_of_custody || []);

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

  // AI Forensic Signals Breakdown
  if (report.forensic_signals) {
    elements.signalsSection.style.display = 'block';
    const s = report.forensic_signals;
    elements.signalsClustersBadge.textContent = `${s.anomalous_clusters_count || 0} Clusters`;
    elements.signalElaVal.textContent = `${s.ela_anomaly_score || 0.0}%`;
    elements.signalNoiseVal.textContent = `${s.noise_inconsistency_score || 0.0}%`;
    elements.signalEdgeVal.textContent = `${s.edge_discontinuity_score || 0.0}%`;
    elements.signalTypoVal.textContent = `${s.typography_anomalies_count || 0}`;
  } else {
    elements.signalsSection.style.display = 'none';
  }

  // Grouped Forensic Metadata Inspector (Level 4)
  if (report.document_metadata) {
    elements.groupedMetaAccordion.style.display = 'flex';
    const m = report.document_metadata;
    elements.metaGroupFilename.textContent = m.file_name || '-';
    elements.metaGroupFilesize.textContent = m.file_size ? formatBytes(m.file_size) : '-';
    elements.metaGroupFiletype.textContent = m.file_type || '-';
    elements.metaGroupSha.textContent = m.sha256 ? (m.sha256.slice(0, 12) + '...') : '-';
    elements.metaGroupSha.title = m.sha256 || '';

    elements.metaGroupCreator.textContent = m.creator || 'None';
    elements.metaGroupProducer.textContent = m.producer || 'None';
    elements.metaGroupCreated.textContent = m.creation_date || 'N/A';
    elements.metaGroupModified.textContent = m.mod_date || 'N/A';
    elements.metaGroupTemporalDesc.textContent = m.time_difference_desc || (m.is_modified_post_creation ? 'Modified post-creation' : 'Verified authentic');

    elements.metaGroupIncremental.textContent = m.has_incremental_updates ? 'Yes (Detected)' : 'No';
    elements.metaGroupEof.textContent = m.eof_marker_count != null ? m.eof_marker_count : '1';
    elements.metaGroupSoftware.textContent = (m.software_flags && m.software_flags.length > 0) ? m.software_flags.join(', ') : 'None flagged';
  } else {
    elements.groupedMetaAccordion.style.display = 'none';
  }
}

function renderExecutionTimeline(trace, chainOfCustody) {
  elements.traceStepCount.textContent = `${trace.length} Steps`;
  elements.timelineList.innerHTML = '';

  // Branch 1: Chain of Custody View
  if (state.timelineFilter === 'custody') {
    if (!chainOfCustody || chainOfCustody.length === 0) {
      elements.timelineList.innerHTML = '<div class="timeline-empty-state"><p>Chain of custody recorded upon document ingestion.</p></div>';
      return;
    }

    chainOfCustody.forEach(c => {
      const item = document.createElement('div');
      item.className = 'custody-item';
      item.innerHTML = `
        <div class="custody-step-badge">${c.step}</div>
        <div class="custody-body" style="flex: 1;">
          <div class="custody-header">
            <span class="custody-phase">${c.phase}</span>
            <span class="custody-actor">${c.actor}</span>
          </div>
          <p class="custody-desc">${c.description}</p>
          <span style="font-size: 0.625rem; color: var(--muted-foreground); font-family: var(--font-mono);">${c.timestamp}</span>
        </div>
      `;
      elements.timelineList.appendChild(item);
    });
    return;
  }

  // Branch 2: Execution Trace
  let filteredTrace = trace;
  if (state.timelineFilter === 'decisions') {
    filteredTrace = trace.filter(t => t.decision !== 'PROCEED');
  }

  if (filteredTrace.length === 0) {
    elements.timelineList.innerHTML = '<div class="timeline-empty-state"><p>No execution steps matching filter.</p></div>';
    return;
  }

  filteredTrace.forEach((entry) => {
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
        <span style="font-size: 0.625rem; color: var(--muted-foreground); font-family: var(--font-mono); display: block; margin-top: 2px;">${entry.timestamp || ''}</span>
      </div>
    `;

    elements.timelineList.appendChild(item);
  });
}

function updateImageView() {
  if (!state.currentReport || !state.currentReport.page_artifacts || state.currentReport.page_artifacts.length === 0) {
    elements.viewportEmpty.style.display = 'block';
    elements.imageStage.style.display = 'none';
    if (elements.splitStage) elements.splitStage.style.display = 'none';
    return;
  }

  elements.viewportEmpty.style.display = 'none';
  const artifacts = state.currentReport.page_artifacts[0];

  // Split Comparison Mode
  if (state.currentView === 'split') {
    elements.imageStage.style.display = 'none';
    if (elements.splitStage) {
      elements.splitStage.style.display = 'flex';
      elements.splitBaseImage.src = artifacts.original_image;
      elements.splitHeatImage.src = artifacts.heatmap_image;
    }
    return;
  }

  // Standard Modes
  if (elements.splitStage) elements.splitStage.style.display = 'none';
  elements.imageStage.style.display = 'inline-block';

  let src = artifacts.original_image;
  if (state.currentView === 'overlay') {
    src = artifacts.overlay_image || artifacts.original_image;
  } else if (state.currentView === 'heatmap') {
    src = artifacts.heatmap_image;
  }

  elements.forensicImage.onload = () => {
    renderSvgOverlay();
  };
  elements.forensicImage.src = src;
}

function renderSvgOverlay() {
  const overlay = elements.interactiveOverlay;
  if (!overlay) return;
  overlay.innerHTML = '';

  const img = elements.forensicImage;
  const regions = (state.currentReport && state.currentReport.suspicious_regions) || [];

  if (regions.length === 0 || !img.naturalWidth || !img.naturalHeight) {
    return;
  }

  overlay.setAttribute('viewBox', `0 0 ${img.naturalWidth} ${img.naturalHeight}`);

  regions.forEach((reg, idx) => {
    const [x0, y0, x1, y1] = reg.bbox;
    const w = Math.max(1, x1 - x0);
    const h = Math.max(1, y1 - y0);

    const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
    rect.setAttribute('x', x0);
    rect.setAttribute('y', y0);
    rect.setAttribute('width', w);
    rect.setAttribute('height', h);
    rect.setAttribute('fill', 'rgba(200, 122, 122, 0.22)');
    rect.setAttribute('stroke', '#c87a7a');
    rect.setAttribute('stroke-width', '2.5');
    rect.setAttribute('rx', '4');

    if (state.selectedRegionIndex === idx) {
      rect.classList.add('selected');
      rect.setAttribute('stroke', 'var(--primary)');
      rect.setAttribute('fill', 'rgba(243, 234, 200, 0.35)');
    }

    rect.addEventListener('mouseenter', (e) => {
      showRegionTooltip(reg, rect);
    });

    rect.addEventListener('mouseleave', () => {
      hideRegionTooltip();
    });

    rect.addEventListener('click', () => {
      selectRegion(idx);
    });

    overlay.appendChild(rect);
  });
}

function showRegionTooltip(reg, targetElement) {
  const tip = elements.regionTooltip;
  if (!tip) return;

  const confPercent = Math.round(reg.confidence * 100);
  elements.tooltipConf.textContent = `${confPercent}% Conf`;
  elements.tooltipCoords.textContent = `[${reg.bbox.join(', ')}]`;
  elements.tooltipReason.textContent = reg.reason || 'Anomalous region';

  if (reg.associated_text) {
    elements.tooltipText.style.display = 'block';
    elements.tooltipText.textContent = `OCR: "${reg.associated_text}"`;
  } else {
    elements.tooltipText.style.display = 'none';
  }

  tip.style.display = 'block';

  // Position relative to viewport
  const rectBox = targetElement.getBoundingClientRect();
  const viewportBox = elements.canvasViewport.getBoundingClientRect();

  const top = rectBox.top - viewportBox.top + elements.canvasViewport.scrollTop - 75;
  const left = rectBox.left - viewportBox.left + elements.canvasViewport.scrollLeft;

  tip.style.top = `${Math.max(10, top)}px`;
  tip.style.left = `${Math.max(10, left)}px`;
}

function hideRegionTooltip() {
  if (elements.regionTooltip) {
    elements.regionTooltip.style.display = 'none';
  }
}

function selectRegion(idx) {
  state.selectedRegionIndex = idx;
  const regions = (state.currentReport && state.currentReport.suspicious_regions) || [];
  const reg = regions[idx];

  // Update chip styling
  document.querySelectorAll('.region-chip').forEach((c, i) => {
    if (i === idx) {
      c.style.borderColor = 'var(--ring)';
      c.style.backgroundColor = 'var(--accent)';
      c.scrollIntoView({ behavior: 'smooth', inline: 'center', block: 'nearest' });
    } else {
      c.style.borderColor = 'var(--border)';
      c.style.backgroundColor = 'var(--card)';
    }
  });

  renderSvgOverlay();

  if (reg) {
    showToast(`Focused on region [${reg.bbox.join(', ')}]`);
  }
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

function renderEvidence() {
  if (!state.currentReport || !state.currentReport.evidence) {
    elements.evidenceList.innerHTML = '<div class="empty-evidence-text">Evidence lineage will appear here once forensic analysis completes.</div>';
    elements.evidenceCount.textContent = '0 items';
    return;
  }

  const query = state.evidenceFilter || state.searchQuery;

  const items = state.currentReport.evidence.filter(e => {
    const matchesType = state.currentEvidenceType === 'interpretations' ? e.type === 'interpretation' : e.type === 'observation';
    if (!matchesType) return false;
    if (!query) return true;
    const textMatch = e.text.toLowerCase().includes(query);
    const idMatch = (e.id || '').toLowerCase().includes(query);
    const citMatch = (e.supported_by || []).some(c => c.toLowerCase().includes(query));
    return textMatch || idMatch || citMatch;
  });

  elements.evidenceCount.textContent = `${items.length} items`;
  elements.evidenceList.innerHTML = '';

  if (items.length === 0) {
    elements.evidenceList.innerHTML = `<div class="empty-evidence-text">No ${state.currentEvidenceType} matching current query.</div>`;
    return;
  }

  items.forEach(ev => {
    const card = document.createElement('div');
    card.className = 'evidence-item-card';
    card.id = `ev-card-${ev.id || ''}`;

    let citationsHtml = '';
    if (ev.supported_by && ev.supported_by.length > 0) {
      citationsHtml = `
        <div class="evidence-citation-chips">
          <span style="font-size: 0.65rem; color: var(--muted-foreground);">Supported by:</span>
          ${ev.supported_by.map(id => `<span class="citation-chip" role="button" tabindex="0" title="Click to view ${id}">${id}</span>`).join('')}
        </div>
      `;
    }

    // Severity estimation based on confidence and keywords
    let severityTag = 'Informational';
    let severityClass = 'badge-info';
    const lower = ev.text.toLowerCase();
    if (lower.includes('critical') || lower.includes('forgery') || lower.includes('splic') || (ev.confidence && ev.confidence >= 0.85)) {
      severityTag = 'High';
      severityClass = 'badge-high';
    } else if (lower.includes('discrepancy') || lower.includes('inconsistency') || lower.includes('modified') || (ev.confidence && ev.confidence >= 0.6)) {
      severityTag = 'Medium';
      severityClass = 'badge-medium';
    } else if (lower.includes('authentic') || lower.includes('uniform') || lower.includes('consistent')) {
      severityTag = 'Verified';
      severityClass = 'badge-verified';
    }

    card.innerHTML = `
      <div class="evidence-header-line">
        <div>
          <span class="evidence-id-tag">[${ev.id || 'EVID'}]</span>
          <span class="badge ${severityClass}">${severityTag}</span>
        </div>
        ${ev.source_agent ? `<span style="font-size: 0.625rem; color: var(--muted-foreground);">${ev.source_agent}</span>` : ''}
      </div>
      <p style="margin-top: 2px;">${ev.text}</p>
      ${citationsHtml}
    `;

    // Clickable citation chips
    card.querySelectorAll('.citation-chip').forEach(chip => {
      chip.addEventListener('click', (e) => {
        e.stopPropagation();
        const citId = chip.textContent.trim();
        jumpToEvidenceItem(citId);
      });
    });

    elements.evidenceList.appendChild(card);
  });
}

function jumpToEvidenceItem(targetId) {
  // If target is OBS, switch to observations tab
  if (targetId.startsWith('OBS')) {
    elements.evTabBtns.forEach(b => {
      const isObs = b.dataset.evType === 'observations';
      b.classList.toggle('active', isObs);
      b.setAttribute('aria-selected', isObs ? 'true' : 'false');
    });
    state.currentEvidenceType = 'observations';
    renderEvidence();
  }

  setTimeout(() => {
    const card = document.getElementById(`ev-card-${targetId}`);
    if (card) {
      card.scrollIntoView({ behavior: 'smooth', block: 'center' });
      card.style.borderColor = 'var(--ring)';
      card.style.backgroundColor = 'var(--accent)';
      setTimeout(() => {
        card.style.borderColor = 'var(--border)';
        card.style.backgroundColor = 'var(--background)';
      }, 2000);
      showToast(`Navigated to evidence item [${targetId}]`);
    } else {
      showToast(`Evidence item [${targetId}] cited.`);
    }
  }, 50);
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
    const isChecked = !!state.verificationStatus[idx];
    if (isChecked) li.classList.add('completed');

    li.innerHTML = `
      <input type="checkbox" class="checklist-checkbox" id="check-step-${idx}" ${isChecked ? 'checked' : ''} aria-label="Mark verification step completed">
      <span class="checklist-num" aria-hidden="true">${idx + 1}</span>
      <span>${step}</span>
    `;

    const checkbox = li.querySelector('.checklist-checkbox');
    checkbox.addEventListener('change', (e) => {
      state.verificationStatus[idx] = e.target.checked;
      li.classList.toggle('completed', e.target.checked);
      showToast(e.target.checked ? `Step ${idx + 1} marked complete.` : `Step ${idx + 1} unmarked.`);
    });

    elements.verificationChecklist.appendChild(li);
  });
}

// --------------------------------------------------------------------------
// Global Search Filter
// --------------------------------------------------------------------------
function applyGlobalSearch() {
  const query = state.searchQuery;

  // Filter evidence
  renderEvidence();

  // Highlight matching regions in chips
  const chips = document.querySelectorAll('.region-chip');
  chips.forEach(chip => {
    if (!query) {
      chip.style.opacity = '1';
    } else {
      const text = chip.textContent.toLowerCase();
      chip.style.opacity = text.includes(query) ? '1' : '0.35';
    }
  });

  // Filter execution trace
  if (state.currentReport) {
    renderExecutionTimeline(state.currentReport.execution_trace || [], state.currentReport.chain_of_custody || []);
  }
}

// --------------------------------------------------------------------------
// Cases & Audit Modal Handlers
// --------------------------------------------------------------------------
function openCasesModal() {
  elements.casesModal.style.display = 'flex';
  renderCasesList();
  renderAuditTable();
}

function renderCasesList() {
  elements.casesGridList.innerHTML = '';
  if (state.cases.length === 0) {
    elements.casesGridList.innerHTML = '<p class="empty-evidence-text">No active cases registered.</p>';
    return;
  }

  state.cases.forEach(c => {
    const card = document.createElement('div');
    card.className = 'case-card';

    const riskBadgeClass = `badge-${(c.risk_level || 'low').toLowerCase()}`;

    card.innerHTML = `
      <div class="case-card-header">
        <div>
          <span style="font-family: var(--font-mono); font-size: 0.6875rem; font-weight: 700; color: var(--primary);">${c.id}</span>
          <h3 class="case-card-title">${c.title}</h3>
        </div>
        <div style="display: flex; gap: var(--space-2); align-items: center;">
          <span class="badge ${riskBadgeClass}">${c.risk_level.toUpperCase()} (${c.risk_score})</span>
          <span class="badge badge-subtle">${c.status}</span>
        </div>
      </div>
      <p class="case-desc">${c.description}</p>
      <div class="case-card-meta">
        <span><strong>Category:</strong> ${c.category}</span>
        <span><strong>Investigator:</strong> ${c.investigator}</span>
        <span><strong>Findings:</strong> ${c.findings_count}</span>
        <span><strong>Created:</strong> ${c.created_at}</span>
      </div>
      <div style="margin-top: var(--space-2); display: flex; justify-content: flex-end;">
        <button class="btn btn-secondary btn-sm btn-load-case" data-sample-id="${c.sample_id}">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polygon points="5 3 19 12 5 21 5 3"/>
          </svg>
          Load Case into Workspace
        </button>
      </div>
    `;

    card.querySelector('.btn-load-case').addEventListener('click', () => {
      elements.casesModal.style.display = 'none';
      runSampleAnalysis(c.sample_id);
    });

    elements.casesGridList.appendChild(card);
  });
}

function renderAuditTable() {
  elements.auditTableBody.innerHTML = '';
  if (state.auditLog.length === 0) {
    elements.auditTableBody.innerHTML = '<tr><td colspan="7" style="text-align: center; color: var(--muted-foreground);">No audit trail recorded.</td></tr>';
    return;
  }

  state.auditLog.forEach(a => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td style="font-family: var(--font-mono); font-weight: 700; color: var(--primary);">${a.id}</td>
      <td style="font-family: var(--font-mono); white-space: nowrap;">${a.timestamp}</td>
      <td><strong>${a.actor}</strong></td>
      <td>${a.action}</td>
      <td style="font-family: var(--font-mono);">${a.target}</td>
      <td><span class="badge badge-subtle">${a.status}</span></td>
      <td style="font-family: var(--font-mono); color: var(--muted-foreground);">${a.checksum}</td>
    `;
    elements.auditTableBody.appendChild(tr);
  });
}

// --------------------------------------------------------------------------
// Docket Preview & Markdown Download Handlers
// --------------------------------------------------------------------------
async function openDocketModal() {
  if (!state.currentReport) return;
  elements.docketModal.style.display = 'flex';
  elements.docketPreviewContent.textContent = 'Fetching court-ready forensic docket...';

  try {
    const res = await fetch(`/api/reports/${state.currentReport.document_id}/docket`);
    if (res.ok) {
      const text = await res.text();
      elements.docketPreviewContent.textContent = text;
    } else {
      elements.docketPreviewContent.textContent = 'Forensic docket not yet generated for this session.';
    }
  } catch (err) {
    elements.docketPreviewContent.textContent = `Error loading docket: ${err.message}`;
  }
}

async function downloadDocketFile() {
  if (!state.currentReport) return;
  try {
    const res = await fetch(`/api/reports/${state.currentReport.document_id}/docket`);
    if (res.ok) {
      const text = await res.text();
      const blob = new Blob([text], { type: 'text/markdown' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `ADFF_Docket_${state.currentReport.document_id}.md`;
      a.click();
      URL.revokeObjectURL(url);
      showToast('Forensic examination docket (.md) downloaded.');
    } else {
      showToast('Docket file not available for download.');
    }
  } catch (err) {
    showToast('Failed to download docket.');
  }
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
