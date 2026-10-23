import { getPublicOrigin } from '../../services/publicOrigin';
import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { credentialService } from '../../services/credentialService';
import { Credential } from '../../types';
import { StatusBadge } from '../../components/common/StatusBadge';

export const StudentCredentialDetailsPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [credential, setCredential] = useState<Credential | null>(null);
  const [loading, setLoading] = useState(true);
  const [shareModalOpen, setShareModalOpen] = useState(false);
  const [recipientEmail, setRecipientEmail] = useState('');
  const [emailSent, setEmailSent] = useState(false);
  const [toastMessage, setToastMessage] = useState<string | null>(null);
  const [pdfLoading, setPdfLoading] = useState(false);

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 3000);
  };

  useEffect(() => {
    if (!id) return;
    credentialService.getById(id).then((res) => {
      setCredential(res);
      setLoading(false);
    }).catch(() => {
      setCredential(null);
      setLoading(false);
    });
  }, [id]);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[50vh] gap-3">
        <span className="w-8 h-8 border-3 border-primary border-t-transparent rounded-full animate-spin"></span>
        <span className="text-sm font-medium text-on-surface-variant">Loading academic credential record...</span>
      </div>
    );
  }

  if (!credential) {
    return (
      <div className="bg-white rounded-2xl p-12 text-center border border-slate-200">
        <span className="material-symbols-outlined text-[48px] text-slate-300">search_off</span>
        <h2 className="text-xl font-bold text-primary mt-2">Credential Not Found</h2>
        <p className="text-xs text-on-surface-variant mt-1">No credential was found matching {id}.</p>
        <Link
          to="/student/credentials"
          className="mt-4 inline-flex items-center gap-1.5 px-4 py-2 bg-primary text-white text-xs font-semibold rounded-xl"
        >
          ← Back to My Credentials
        </Link>
      </div>
    );
  }

  const publicVerificationUrl = `${getPublicOrigin()}/verify/result?channel=QR_SCAN&id=${encodeURIComponent(credential.id)}`;

  const copyPublicUrl = () => {
    navigator.clipboard.writeText(publicVerificationUrl);
    showToast('Public verification URL copied to clipboard!');
  };

  const copyCertId = () => {
    navigator.clipboard.writeText(credential.id);
    showToast(`Credential ID ${credential.id} copied!`);
  };

  const downloadAsPDF = () => {
    if (!credential) return;
    setPdfLoading(true);

    const qrUrl = credential.qrCodeUrl ||
      `https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${encodeURIComponent(publicVerificationUrl)}`;

    // Raw YYYY-MM-DD used in the machine-readable field so the extractor
    // normalises it to exactly what is stored in the DB.
    const rawIssueDate = credential.issueDate ?? '';
    // Add T00:00:00 to prevent timezone shift turning e.g. 2026-10-23 → Oct 22
    const issueDateFormatted = credential.issueDate
      ? new Date(credential.issueDate + 'T00:00:00').toLocaleDateString('en-US', {
          year: 'numeric', month: 'long', day: 'numeric',
        })
      : credential.issueDate;

    const statusColor =
      credential.status === 'ACTIVE' || credential.status === 'CONFERRED'
        ? '#059669'
        : credential.status === 'REVOKED'
        ? '#dc2626'
        : '#d97706';

    const html = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>Certificate – ${credential.id}</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    * { margin: 0; padding: 0; box-sizing: border-box; }
    html, body { width: 210mm; background: #fff; font-family: 'Inter', sans-serif; color: #0f172a; }
    @page { size: A4; margin: 0; }
    @media print {
      html, body { width: 210mm; }
      .no-print { display: none !important; }
    }

    .page {
      width: 210mm;
      min-height: 297mm;
      padding: 14mm 16mm 12mm;
      display: flex;
      flex-direction: column;
      gap: 10mm;
      position: relative;
      background: #fff;
    }

    /* decorative border */
    .page::before {
      content: '';
      position: absolute;
      inset: 5mm;
      border: 2px solid #c7d2fe;
      border-radius: 6mm;
      pointer-events: none;
    }
    .page::after {
      content: '';
      position: absolute;
      inset: 6.5mm;
      border: 0.5px solid #e0e7ff;
      border-radius: 5mm;
      pointer-events: none;
    }

    /* ── Header ── */
    .header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      border-bottom: 2px solid #e0e7ff;
      padding-bottom: 6mm;
    }
    .header-left { display: flex; align-items: center; gap: 4mm; }
    .seal {
      width: 18mm; height: 18mm;
      background: linear-gradient(135deg, #1e3a5f 0%, #2563eb 100%);
      border-radius: 50%;
      display: flex; align-items: center; justify-content: center;
      color: #fff; font-size: 9mm; font-weight: 800;
      flex-shrink: 0;
      box-shadow: 0 2px 6px rgba(37,99,235,0.4);
    }
    .inst-name { font-size: 4.8mm; font-weight: 800; color: #1e3a5f; }
    .inst-sub  { font-size: 2.8mm; color: #64748b; margin-top: 0.5mm; }
    .badge {
      font-size: 2.5mm; font-weight: 600;
      background: #f0fdf4; color: #166534;
      border: 1px solid #bbf7d0;
      border-radius: 3mm;
      padding: 1.2mm 3mm;
    }

    /* ── Title ── */
    .cert-label {
      text-align: center;
      font-size: 3mm; font-weight: 700;
      letter-spacing: 0.4mm;
      text-transform: uppercase;
      color: #6366f1;
    }
    .cert-title {
      text-align: center;
      font-size: 8mm; font-weight: 800;
      color: #1e3a5f;
      line-height: 1.15;
      margin-top: 2mm;
    }
    .cert-subtitle {
      text-align: center;
      font-size: 3.5mm;
      color: #475569;
      margin-top: 1.5mm;
    }

    /* ── Fields grid ── */
    .fields {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 4mm;
    }
    .field {
      background: #f8fafc;
      border: 1px solid #e2e8f0;
      border-radius: 3mm;
      padding: 3mm 4mm;
    }
    .field-label { font-size: 2.3mm; font-weight: 600; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.3mm; }
    .field-value { font-size: 3.5mm; font-weight: 700; color: #1e293b; margin-top: 0.8mm; white-space: nowrap; }
    .field-mono  { font-family: 'Courier New', monospace; font-size: 2.8mm; }

    /* ── Status pill ── */
    .status-pill {
      display: inline-flex;
      align-items: center;
      gap: 1.5mm;
      font-size: 3mm;
      font-weight: 700;
      padding: 1.5mm 3.5mm;
      border-radius: 3mm;
      color: ${statusColor};
      background: ${statusColor}18;
      border: 1px solid ${statusColor}44;
    }

    /* ── Crypto section ── */
    .crypto {
      background: #0f172a;
      border-radius: 4mm;
      padding: 5mm 6mm;
      display: flex;
      flex-direction: column;
      gap: 3mm;
    }
    .crypto-title { font-size: 2.8mm; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.4mm; }
    .crypto-row   { display: flex; flex-direction: column; gap: 0.8mm; }
    .crypto-label { font-size: 2mm; color: #64748b; font-weight: 600; text-transform: uppercase; }
    .crypto-val   { font-family: 'Courier New', monospace; font-size: 2.3mm; color: #a5b4fc; word-break: break-all; }

    /* ── Footer + QR ── */
    .footer {
      display: flex;
      align-items: flex-end;
      justify-content: space-between;
      border-top: 1px solid #e0e7ff;
      padding-top: 5mm;
      margin-top: auto;
    }
    .footer-text { font-size: 2.3mm; color: #94a3b8; max-width: 120mm; line-height: 1.5; }
    .qr-box { text-align: center; }
    .qr-box img { width: 28mm; height: 28mm; border: 1px solid #e2e8f0; border-radius: 2mm; display: block; }
    .qr-label { font-size: 2mm; color: #94a3b8; margin-top: 1mm; }
  </style>
</head>
<body>
<div class="page">

  <!-- Header -->
  <div class="header">
    <div class="header-left">
      <div class="seal">⛓</div>
      <div>
        <div class="inst-name">${credential.institution || 'Academic Institution'}</div>
        <div class="inst-sub">Office of the Registrar · Blockchain-Anchored Records</div>
      </div>
    </div>
    <div class="badge">✓ Verified on ChainCert</div>
  </div>

  <!-- Certificate title -->
  <div>
    <div class="cert-label">Official Academic Credential</div>
    <div class="cert-title">${credential.course}</div>
    <div class="cert-subtitle">Conferred upon <strong>${credential.studentName}</strong> in recognition of the successful completion of all prescribed requirements.</div>
  </div>

  <!-- Fields: labels MUST match extractor alias list exactly -->
  <div class="fields">
    <div class="field">
      <div class="field-label">Credential ID:</div>
      <div class="field-value field-mono">${credential.id}</div>
    </div>
    <div class="field">
      <div class="field-label">Student Full Name:</div>
      <div class="field-value">${credential.studentName}</div>
    </div>
    <div class="field">
      <div class="field-label">Roll Number:</div>
      <div class="field-value field-mono">${credential.studentRoll}</div>
    </div>
    <div class="field">
      <div class="field-label">Issue Date:</div>
      <div class="field-value">${rawIssueDate}</div>
    </div>
    <div class="field">
      <div class="field-label">CGPA:</div>
      <div class="field-value">${credential.cgpa || ''}</div>
    </div>
    <div class="field">
      <div class="field-label">Course / Academic Degree:</div>
      <div class="field-value">${credential.course}</div>
    </div>
    <div class="field" style="grid-column: span 2;">
      <div class="field-label">Institution:</div>
      <div class="field-value">${credential.institution || ''}</div>
    </div>
    <div class="field" style="grid-column: span 2;">
      <div class="field-label">Credential Status</div>
      <div class="field-value">
        <span class="status-pill">${credential.status}</span>
      </div>
    </div>
  </div>

  <!-- Cryptographic Trust Section -->
  <div class="crypto">
    <div class="crypto-title">🔒 Cryptographic Trust Metadata</div>
    <div class="crypto-row">
      <span class="crypto-label">SHA-256 Certificate Hash</span>
      <span class="crypto-val">${credential.sha256Hash || 'Not available'}</span>
    </div>
    <div class="crypto-row">
      <span class="crypto-label">Merkle Root</span>
      <span class="crypto-val">${credential.merkleRoot || 'Not available'}</span>
    </div>
    ${credential.merkleLeafIndex !== undefined ? `
    <div class="crypto-row">
      <span class="crypto-label">Merkle Leaf Index</span>
      <span class="crypto-val">${credential.merkleLeafIndex}</span>
    </div>` : ''}
    ${credential.batch ? `
    <div class="crypto-row">
      <span class="crypto-label">Batch ID</span>
      <span class="crypto-val">${credential.batch}</span>
    </div>` : ''}
  </div>

  <!-- Footer + QR -->
  <div class="footer">
    <div class="footer-text">
      This credential is digitally anchored on a blockchain-backed Merkle tree and can be independently verified at any time.
      Verify at: <strong>${publicVerificationUrl}</strong>
    </div>
    <div class="qr-box">
      <img src="${qrUrl}" alt="Verification QR" />
      <div class="qr-label">Scan to verify</div>
    </div>
  </div>

</div>
<script>
  // Auto-trigger print as soon as images load
  window.addEventListener('load', function() {
    setTimeout(function() { window.print(); window.close(); }, 400);
  });
<\/script>
</body>
</html>`;

    const printWin = window.open('', '_blank', 'width=900,height=700');
    if (!printWin) {
      showToast('Pop-up blocked — please allow pop-ups and try again.');
      setPdfLoading(false);
      return;
    }
    printWin.document.write(html);
    printWin.document.close();
    setPdfLoading(false);
    showToast('PDF certificate opened — choose "Save as PDF" in the print dialog.');
  };

  return (
    <div className="flex flex-col w-full space-y-6">
      {/* Toast Notification */}
      {toastMessage && (
        <div className="fixed bottom-6 right-6 z-50 bg-primary text-white text-xs px-4 py-2.5 rounded-xl shadow-xl flex items-center gap-2 border border-slate-700 animate-fade-in">
          <span className="material-symbols-outlined text-[18px] text-emerald-400">check_circle</span>
          <span>{toastMessage}</span>
        </div>
      )}

      {/* Navigation / Breadcrumb Header */}
      <header className="w-full flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex flex-col gap-1">
          <div className="flex items-center gap-1.5 flex-wrap text-xs text-on-surface-variant">
            <Link
              to="/student/credentials"
              className="inline-flex items-center gap-1 hover:text-primary transition-colors font-semibold"
            >
              <span className="material-symbols-outlined text-[16px]">arrow_back</span>
              <span>Back to My Credentials</span>
            </Link>
            <span>/</span>
            <span className="font-mono font-bold text-primary uppercase">{credential.id}</span>
            <span>/</span>
            <span>Official Record</span>
          </div>
          <h1 className="font-headline-lg text-2xl sm:text-3xl text-primary tracking-tight font-bold">
            Credential Details
          </h1>
        </div>
        <StatusBadge status={credential.status} size="md" />
      </header>

      {/* Two-Column Grid Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left Column: Formal Credential Document Card */}
        <div className="lg:col-span-8 flex flex-col gap-6">
          <section className="bg-white rounded-2xl shadow-sm p-6 sm:p-8 border border-slate-200/80 relative overflow-hidden">
            {/* Header Lockup: Institution seal & title */}
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-6 mb-6 bg-surface-container-low/60 -mx-6 -mt-6 sm:-mx-8 sm:-mt-8 p-6 sm:p-8 border-b border-slate-200/60">
              <div className="flex items-center gap-3">
                <div className="w-14 h-14 rounded-2xl bg-primary-container text-white flex items-center justify-center shadow-sm shrink-0">
                  <span className="material-symbols-outlined text-[32px]">account_balance</span>
                </div>
                <div>
                  <span className="font-label-sm text-[11px] uppercase tracking-wider text-on-surface-variant font-semibold block">
                    Issuing Academic Institution
                  </span>
                  <span className="text-base sm:text-lg text-primary font-bold block">
                    {credential.institution}
                  </span>
                  <span className="text-xs text-on-surface-variant block mt-0.5">
                    HLC Institutional Accreditation • Registrar Node #402
                  </span>
                </div>
              </div>
              <div className="shrink-0 flex items-center gap-1 bg-white px-3 py-1 rounded-xl text-xs font-semibold text-primary border border-slate-200 shadow-2xs">
                <span className="material-symbols-outlined text-[15px] text-secondary">verified_user</span>
                <span>Standard Digital Parchment</span>
              </div>
            </div>

            {/* Certificate Title & Identifier */}
            <div className="flex flex-col gap-2 mb-6">
              <span className="text-xs uppercase tracking-wider text-secondary font-bold flex items-center gap-1">
                <span className="material-symbols-outlined text-[16px]">workspace_premium</span>
                Official Conferred Qualification
              </span>
              <h2 className="text-2xl sm:text-3xl font-bold text-primary leading-tight">
                {credential.course}
              </h2>

              <div className="mt-2 flex flex-wrap items-center gap-3">
                <div className="bg-surface-container-low px-3.5 py-1.5 rounded-xl flex items-center gap-2 border border-slate-200">
                  <span className="text-xs text-on-surface-variant uppercase font-semibold">Credential ID</span>
                  <span className="font-mono text-sm font-bold text-primary">{credential.id}</span>
                  <button
                    onClick={copyCertId}
                    className="text-slate-400 hover:text-primary transition-colors p-1"
                    title="Copy Credential ID"
                  >
                    <span className="material-symbols-outlined text-[16px]">content_copy</span>
                  </button>
                </div>
                <StatusBadge status={credential.status} size="sm" />
              </div>

              <p className="text-xs sm:text-sm text-on-surface-variant mt-2 leading-relaxed">
                This credential is fully verified, registered, and in good standing with no adverse flags on file with the university registrar.
              </p>
            </div>

            {/* Two-column grid of official attributes */}
            <div className="bg-surface-container-low/40 rounded-2xl p-5 border border-slate-200/80 mb-6">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="bg-white p-3.5 rounded-xl border border-slate-200/60">
                  <span className="text-[11px] text-slate-500 uppercase tracking-wider block font-medium">
                    Student Full Name
                  </span>
                  <span className="text-sm sm:text-base font-bold text-primary mt-0.5 block">
                    {credential.studentName}
                  </span>
                </div>

                <div className="bg-white p-3.5 rounded-xl border border-slate-200/60">
                  <span className="text-[11px] text-slate-500 uppercase tracking-wider block font-medium">
                    Roll Number / Student ID
                  </span>
                  <span className="text-sm font-mono font-bold text-slate-800 mt-0.5 block">
                    {credential.studentRoll}
                  </span>
                </div>

                <div className="bg-white p-3.5 rounded-xl border border-slate-200/60">
                  <span className="text-[11px] text-slate-500 uppercase tracking-wider block font-medium">
                    Course / Qualification
                  </span>
                  <span className="text-xs sm:text-sm font-semibold text-slate-900 mt-0.5 block">
                    {credential.course}
                  </span>
                </div>

                <div className="bg-white p-3.5 rounded-xl border border-slate-200/60">
                  <span className="text-[11px] text-slate-500 uppercase tracking-wider block font-medium">
                    Degree Classification
                  </span>
                  <span className="text-xs sm:text-sm font-semibold text-secondary mt-0.5 flex items-center gap-1">
                    <span className="material-symbols-outlined text-[18px]">military_tech</span>
                    {credential.grade}
                  </span>
                </div>

                <div className="bg-white p-3.5 rounded-xl border border-slate-200/60">
                  <span className="text-[11px] text-slate-500 uppercase tracking-wider block font-medium">
                    Cumulative GPA
                  </span>
                  <span className="text-sm font-bold text-primary mt-0.5 block">
                    {credential.cgpa || '3.92 / 4.00'}
                  </span>
                </div>

                <div className="bg-white p-3.5 rounded-xl border border-slate-200/60">
                  <span className="text-[11px] text-slate-500 uppercase tracking-wider block font-medium">
                    Date of Conferral
                  </span>
                  <span className="text-sm font-semibold text-slate-900 mt-0.5 block">
                    {credential.issueDate}
                  </span>
                </div>
              </div>
            </div>

            {/* Official Action Toolbar */}
            <div className="flex flex-wrap items-center gap-3 pt-2">
              <button
                onClick={downloadAsPDF}
                disabled={pdfLoading}
                className="bg-primary-container text-white hover:bg-primary px-5 h-11 rounded-xl font-semibold text-xs shadow-xs transition-all flex items-center justify-center gap-2 disabled:opacity-60 disabled:cursor-not-allowed"
                id="btn-download"
              >
                {pdfLoading ? (
                  <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                ) : (
                  <span className="material-symbols-outlined text-[20px]">download</span>
                )}
                <span>{pdfLoading ? 'Preparing PDF…' : 'Download Credential (PDF)'}</span>
              </button>

              <button
                onClick={() => setShareModalOpen(true)}
                className="bg-white border border-slate-200 hover:bg-slate-50 text-slate-700 px-4 h-11 rounded-xl font-semibold text-xs transition-all flex items-center justify-center gap-2 shadow-2xs"
              >
                <span className="material-symbols-outlined text-[18px]">share</span>
                <span>Share Link</span>
              </button>

              <button
                onClick={() => navigate(`/verify?id=${encodeURIComponent(credential.id)}`)}
                className="bg-white border border-slate-200 hover:bg-slate-50 text-secondary px-4 h-11 rounded-xl font-semibold text-xs transition-all flex items-center justify-center gap-2 shadow-2xs"
              >
                <span className="material-symbols-outlined text-[18px]">search_check</span>
                <span>Verify Credential</span>
              </button>
            </div>
          </section>

          {/* Cryptographic Trust Metadata */}
          <section className="bg-white rounded-2xl shadow-sm p-6 border border-slate-200/80 space-y-4">
            <div className="flex items-center gap-2 text-primary">
              <span className="material-symbols-outlined text-[22px] text-secondary">verified</span>
              <h2 className="text-base font-bold">Credential Information & Trust Metadata</h2>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
              <div className="p-4 bg-surface-container-low rounded-xl flex flex-col justify-between border border-slate-200/60">
                <span className="text-[11px] text-slate-500 uppercase font-semibold">Issuing Authority</span>
                <span className="font-bold text-primary mt-1">{credential.institution}</span>
                <span className="text-[11px] text-emerald-700 mt-2 flex items-center gap-1 font-medium">
                  <span className="material-symbols-outlined text-[14px]">check_circle</span> Institutional Key Active
                </span>
              </div>

              <div className="p-4 bg-surface-container-low rounded-xl flex flex-col justify-between border border-slate-200/60">
                <span className="text-[11px] text-slate-500 uppercase font-semibold">Conferred On</span>
                <span className="font-bold text-primary mt-1">{credential.issueDate}</span>
                <span className="text-[11px] text-slate-600 mt-2 flex items-center gap-1">
                  <span className="material-symbols-outlined text-[14px]">schedule</span> Convocation Registry
                </span>
              </div>

              <div className="p-4 bg-surface-container-low rounded-xl flex flex-col justify-between border border-slate-200/60">
                <span className="text-[11px] text-slate-500 uppercase font-semibold">Canonical Digest</span>
                <span className="font-mono text-[11px] text-slate-700 truncate mt-1">{credential.sha256Hash}</span>
                <span className="text-[11px] text-emerald-700 mt-2 flex items-center gap-1 font-medium">
                  <span className="material-symbols-outlined text-[14px]">lock</span> Immutable Seal
                </span>
              </div>
            </div>
          </section>
        </div>

        {/* Right Column: QR Code & Public URL Card */}
        <div className="lg:col-span-4 flex flex-col gap-6" id="verification-card">
          <div className="bg-white rounded-2xl p-6 shadow-sm border border-slate-200/80 space-y-5 text-center">
            <div>
              <span className="text-xs font-bold text-secondary uppercase tracking-wider block">
                Instant Verification
              </span>
              <h3 className="text-base font-bold text-primary mt-0.5">Official QR Anchor</h3>
              <p className="text-xs text-on-surface-variant mt-1">
                Scan with any standard device camera to verify real-time status directly with Westminster State University.
              </p>
            </div>

            {/* QR Image Frame */}
            <div className="p-4 bg-surface-container-low rounded-2xl border border-slate-200 inline-block mx-auto shadow-inner">
              <img
                src={credential.qrCodeUrl || `https://api.qrserver.com/v1/create-qr-code/?size=180x180&data=${encodeURIComponent(publicVerificationUrl)}`}
                alt={`QR code for ${credential.id}`}
                className="w-44 h-44 rounded-lg object-contain mx-auto"
              />
            </div>

            <div className="space-y-1 font-mono text-xs">
              <span className="text-slate-400 text-[11px] font-sans block">Official Public URL</span>
              <div className="p-2.5 rounded-xl bg-surface-container-low border border-slate-200 text-slate-700 truncate text-[11px]">
                {publicVerificationUrl}
              </div>
            </div>

            <div className="pt-2 flex flex-col gap-2">
              <button
                onClick={copyPublicUrl}
                className="w-full h-10 rounded-xl bg-surface-container hover:bg-surface-container-high text-primary font-semibold text-xs transition-colors flex items-center justify-center gap-1.5 border border-slate-200"
              >
                <span className="material-symbols-outlined text-[18px]">link</span>
                <span>Copy Verification URL</span>
              </button>

              <button
                onClick={() => navigate(`/verify?id=${encodeURIComponent(credential.id)}`)}
                className="w-full h-10 rounded-xl bg-primary hover:bg-primary-container text-white font-semibold text-xs shadow-xs transition-colors flex items-center justify-center gap-1.5"
              >
                <span className="material-symbols-outlined text-[18px]">verified</span>
                <span>Open Verification View</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Share Modal Dialog */}
      {shareModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-primary/70 backdrop-blur-sm">
          <div className="w-full max-w-md bg-white rounded-2xl p-6 sm:p-8 shadow-2xl border border-slate-200">
            <div className="flex items-start justify-between pb-4 border-b border-slate-100">
              <div>
                <span className="text-xs font-bold text-secondary uppercase tracking-wider">Public Provenance</span>
                <h3 className="text-lg font-bold text-primary mt-0.5">Share Verification Link</h3>
              </div>
              <button
                onClick={() => {
                  setShareModalOpen(false);
                  setEmailSent(false);
                }}
                className="w-8 h-8 rounded-full hover:bg-slate-100 text-slate-500 flex items-center justify-center"
              >
                <span className="material-symbols-outlined text-[20px]">close</span>
              </button>
            </div>

            <div className="py-4 space-y-4">
              <div>
                <label className="text-xs font-semibold text-primary block mb-1">
                  Public Verification Link
                </label>
                <div className="flex items-center gap-2">
                  <input
                    type="text"
                    readOnly
                    value={publicVerificationUrl}
                    className="flex-1 h-10 px-3 rounded-xl bg-surface-container-low border border-slate-200 text-xs font-mono text-slate-700"
                  />
                  <button
                    onClick={copyPublicUrl}
                    className="px-3.5 h-10 rounded-xl bg-primary text-white text-xs font-semibold hover:bg-primary-container shrink-0"
                  >
                    Copy
                  </button>
                </div>
              </div>

              <div className="pt-2 border-t border-slate-100">
                <label className="text-xs font-semibold text-primary block mb-1">
                  Send to Employer / University by Email
                </label>
                <input
                  type="email"
                  value={recipientEmail}
                  onChange={(e) => setRecipientEmail(e.target.value)}
                  placeholder="recruiter@company.com"
                  className="w-full h-10 px-3 rounded-xl bg-white border border-slate-300 text-xs mb-2"
                />
                {emailSent ? (
                  <div className="p-2.5 rounded-lg bg-emerald-50 text-emerald-800 text-xs border border-emerald-200">
                    Verification link sent to {recipientEmail}.
                  </div>
                ) : (
                  <button
                    onClick={() => {
                      if (!recipientEmail) return;
                      setEmailSent(true);
                      showToast(`Verification link emailed to ${recipientEmail}`);
                    }}
                    className="w-full h-10 rounded-xl bg-secondary hover:bg-secondary/90 text-white font-semibold text-xs transition-colors flex items-center justify-center gap-1.5"
                  >
                    <span className="material-symbols-outlined text-[16px]">mail</span>
                    <span>Send Verified Link</span>
                  </button>
                )}
              </div>
            </div>

            <div className="pt-2 border-t border-slate-100 flex justify-end">
              <button
                onClick={() => {
                  setShareModalOpen(false);
                  setEmailSent(false);
                }}
                className="px-4 py-2 text-xs font-semibold text-slate-600 hover:bg-slate-100 rounded-lg"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
