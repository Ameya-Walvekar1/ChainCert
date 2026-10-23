import React, { useState, useEffect } from 'react';
import { verificationService } from '../../services/verificationService';
import { auditService } from '../../services/auditService';
import { VerificationResult, VerificationHistoryItem } from '../../types';
import { VerificationBadge } from '../../components/common/VerificationBadge';

export const InstitutionVerificationPage: React.FC = () => {
  const [certId, setCertId] = useState('CC-2024-89042-ENG');
  const [result, setResult] = useState<VerificationResult | null>(null);
  const [isVerifying, setIsVerifying] = useState(false);
  const [history, setHistory] = useState<VerificationHistoryItem[]>([]);

  useEffect(() => {
    auditService.getVerificationHistory().then(setHistory);
    // Initial verification display
    handleVerify('CC-2024-89042-ENG');
  }, []);

  const handleVerify = async (queryId?: string) => {
    const idToVerify = queryId || certId;
    if (!idToVerify.trim()) return;

    setIsVerifying(true);
    setResult(null);

    try {
      const res = await verificationService.verifyById(idToVerify, 'ID_LOOKUP');
      setResult(res);
    } finally {
      setIsVerifying(false);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setIsVerifying(true);
      setResult(null);
      try {
        const res = await verificationService.verifyUploadedFile(file);
        setResult(res);
      } finally {
        setIsVerifying(false);
      }
    }
  };

  return (
    <div className="flex flex-col w-full space-y-6">
      {/* Simulation Ribbon / Quick State Switcher */}
      <div className="p-3 bg-surface-container-low rounded-2xl flex flex-wrap items-center justify-between gap-3 border border-slate-200/60 shadow-xs">
        <div className="flex items-center gap-2 pl-1">
          <span className="material-symbols-outlined text-[18px] text-on-surface-variant">tune</span>
          <span className="font-label-sm text-xs uppercase tracking-wider text-on-surface-variant font-semibold">
            Test State:
          </span>
        </div>
        <div className="flex flex-wrap items-center gap-1.5" id="state-selector-tabs">
          <button
            onClick={() => setResult(null)}
            className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition-all ${
              !result && !isVerifying
                ? 'bg-primary text-white shadow-xs'
                : 'text-on-surface-variant hover:bg-surface-container'
            }`}
          >
            1. Idle
          </button>
          <button
            onClick={() => handleVerify('CC-2024-89042-ENG')}
            className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition-all ${
              result?.state === 'GENUINE'
                ? 'bg-emerald-600 text-white shadow-xs'
                : 'text-emerald-700 bg-emerald-50 hover:bg-emerald-100'
            }`}
          >
            2. Genuine
          </button>
          <button
            onClick={() => handleVerify('CC-TAMPERED-SAMPLE')}
            className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition-all ${
              result?.state === 'TAMPERED'
                ? 'bg-rose-600 text-white shadow-xs'
                : 'text-rose-700 bg-rose-50 hover:bg-rose-100'
            }`}
          >
            3. Tampered
          </button>
          <button
            onClick={() => handleVerify('CC-2024-55120-MED')}
            className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition-all ${
              result?.state === 'REVIEW_REQUIRED'
                ? 'bg-amber-600 text-white shadow-xs'
                : 'text-amber-800 bg-amber-50 hover:bg-amber-100'
            }`}
          >
            4. Review Required
          </button>
          <button
            onClick={() => handleVerify('CC-UNKNOWN-RECORD')}
            className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition-all ${
              result?.state === 'NOT_FOUND'
                ? 'bg-slate-700 text-white shadow-xs'
                : 'text-slate-700 bg-slate-100 hover:bg-slate-200'
            }`}
          >
            5. Not Found
          </button>
          <button
            onClick={() => handleVerify('CC-2024-99211-LAW')}
            className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition-all ${
              result?.state === 'REVOKED'
                ? 'bg-rose-700 text-white shadow-xs'
                : 'text-rose-700 bg-rose-50 hover:bg-rose-100'
            }`}
          >
            6. Revoked
          </button>
        </div>
      </div>

      {/* Header & Authority Context Bar */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="font-label-sm text-xs uppercase tracking-wider text-on-surface-variant">
              Verification Portal
            </span>
            <span className="text-outline-variant font-label-sm">•</span>
            <span className="font-label-sm text-xs font-semibold text-primary">
              Westminster Academic Records #402
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold text-primary tracking-tight">
            Verification
          </h1>
          <p className="text-xs sm:text-sm text-on-surface-variant mt-0.5">
            Verify academic credentials and review verification activity across institutional registries.
          </p>
        </div>

        {/* Institutional Status Pill */}
        <div className="flex items-center gap-3 bg-white p-2.5 pr-4 rounded-2xl shadow-xs border border-slate-200 self-start lg:self-center">
          <div className="w-8 h-8 rounded-xl bg-emerald-100 flex items-center justify-center text-emerald-800">
            <span className="material-symbols-outlined text-[18px]">security</span>
          </div>
          <div className="flex flex-col">
            <div className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
              <span className="text-xs font-semibold text-primary leading-tight">
                Institutional Verification Engine
              </span>
            </div>
            <span className="text-[11px] text-emerald-700 font-medium">
              Active & Synchronized • Registrar Node v4.2
            </span>
          </div>
        </div>
      </div>

      {/* Main 12-Column Workspace */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left Input Card (5 Columns) */}
        <div className="lg:col-span-5 flex flex-col gap-6">
          <div className="bg-white rounded-2xl p-6 shadow-sm border border-slate-200/80 flex flex-col">
            <div className="flex items-start justify-between mb-4">
              <div>
                <h2 className="text-lg font-bold text-primary">Verify a Credential</h2>
                <p className="text-xs text-on-surface-variant mt-0.5">
                  Enter a Certificate ID or upload a certificate document to verify its registered record.
                </p>
              </div>
              <div className="w-9 h-9 rounded-xl bg-surface-container flex items-center justify-center text-primary">
                <span className="material-symbols-outlined text-[20px]">search_check</span>
              </div>
            </div>

            {/* METHOD 1: ID Look-up */}
            <div className="flex flex-col pt-2">
              <div className="flex items-center justify-between mb-2">
                <span className="font-label-sm text-xs uppercase tracking-wider font-semibold text-primary">
                  Method 1 — Certificate ID
                </span>
                <span className="font-label-sm text-[11px] text-on-surface-variant">
                  Official Archive Index
                </span>
              </div>

              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  handleVerify();
                }}
                className="flex flex-col gap-2.5"
              >
                <div className="relative flex items-center">
                  <span className="material-symbols-outlined absolute left-3.5 text-slate-400 text-[20px] pointer-events-none">
                    tag
                  </span>
                  <input
                    id="cert-input-field"
                    type="text"
                    value={certId}
                    onChange={(e) => setCertId(e.target.value)}
                    placeholder="Enter Certificate ID (e.g. CC-2024-89042-ENG)"
                    className="w-full h-11 pl-11 pr-4 bg-surface-container-low rounded-xl text-xs font-mono font-medium text-on-surface placeholder:text-slate-400 focus:outline-none focus:bg-white border border-slate-200 transition-all"
                  />
                </div>
                <button
                  type="submit"
                  id="verify-submit-btn"
                  disabled={isVerifying}
                  className="w-full h-11 bg-primary hover:bg-primary-container text-white rounded-xl text-xs font-semibold transition-all flex items-center justify-center gap-2 shadow-xs active:scale-[0.99] disabled:opacity-70"
                >
                  <span className="material-symbols-outlined text-[18px]">fingerprint</span>
                  <span>{isVerifying ? 'Querying Institutional Registry...' : 'Verify Credential'}</span>
                </button>
              </form>

              {/* Quick Shortcuts */}
              <div className="flex flex-col gap-2 mt-4 pt-3 bg-surface-container-low/60 p-3 rounded-xl border border-slate-200/50">
                <span className="font-label-sm text-[11px] text-on-surface-variant font-medium">
                  Quick Test Credentials:
                </span>
                <div className="flex flex-wrap gap-1.5">
                  <button
                    onClick={() => {
                      setCertId('CC-2024-89042-ENG');
                      handleVerify('CC-2024-89042-ENG');
                    }}
                    className="px-2.5 py-1 rounded-lg bg-white hover:bg-emerald-50 text-secondary text-[11px] font-semibold border border-slate-200 flex items-center gap-1"
                  >
                    <span className="w-1.5 h-1.5 rounded-full bg-secondary"></span>
                    CC-2024-89042-ENG (Genuine)
                  </button>
                  <button
                    onClick={() => {
                      setCertId('CC-2024-99211-LAW');
                      handleVerify('CC-2024-99211-LAW');
                    }}
                    className="px-2.5 py-1 rounded-lg bg-white hover:bg-rose-50 text-rose-700 text-[11px] font-semibold border border-slate-200 flex items-center gap-1"
                  >
                    <span className="w-1.5 h-1.5 rounded-full bg-rose-600"></span>
                    CC-2024-99211-LAW (Revoked)
                  </button>
                  <button
                    onClick={() => {
                      setCertId('CC-2024-55120-MED');
                      handleVerify('CC-2024-55120-MED');
                    }}
                    className="px-2.5 py-1 rounded-lg bg-white hover:bg-amber-50 text-amber-800 text-[11px] font-semibold border border-slate-200 flex items-center gap-1"
                  >
                    <span className="w-1.5 h-1.5 rounded-full bg-amber-600"></span>
                    CC-2024-55120-MED (Review)
                  </button>
                </div>
              </div>
            </div>

            {/* Divider */}
            <div className="relative my-6 flex items-center justify-center">
              <div className="w-full h-px bg-slate-200"></div>
              <span className="absolute bg-white px-3 text-[11px] text-on-surface-variant uppercase tracking-widest font-semibold">
                OR
              </span>
            </div>

            {/* METHOD 2: Document Upload */}
            <div className="flex flex-col">
              <div className="flex items-center justify-between mb-2">
                <span className="font-label-sm text-xs uppercase tracking-wider font-semibold text-primary">
                  Method 2 — Upload Document
                </span>
                <span className="font-label-sm text-[11px] text-on-surface-variant">
                  OCR & Hash Analysis
                </span>
              </div>
              <p className="text-xs text-on-surface-variant mb-3">
                Upload a certificate PDF or image for automated seal and registry matching.
              </p>

              <label className="group cursor-pointer p-6 rounded-2xl bg-surface-container-low hover:bg-surface-container border-2 border-dashed border-slate-300 hover:border-primary transition-all flex flex-col items-center justify-center text-center">
                <input
                  type="file"
                  accept=".pdf,.png,.jpg,.jpeg"
                  onChange={handleFileUpload}
                  className="hidden"
                />
                <div className="w-12 h-12 rounded-xl bg-white group-hover:scale-105 transition-transform flex items-center justify-center text-primary shadow-xs mb-2 border border-slate-200">
                  <span className="material-symbols-outlined text-[26px]">upload_file</span>
                </div>
                <span className="text-xs font-semibold text-primary">
                  Drag & drop certificate document
                </span>
                <span className="text-[11px] text-slate-500 mt-0.5">
                  or <span className="text-secondary font-bold underline">choose file</span> from local system
                </span>
                <div className="mt-3 inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-white text-[11px] text-on-surface-variant shadow-2xs border border-slate-200">
                  <span className="material-symbols-outlined text-[13px] text-secondary">verified_user</span>
                  <span>SHA-256 integrity auto-checked</span>
                </div>
              </label>

              <div className="mt-3.5 p-3 rounded-xl bg-surface-container-low flex items-start gap-2.5 border border-slate-200/50">
                <span className="material-symbols-outlined text-primary text-[18px] shrink-0 mt-0.5">info</span>
                <span className="text-xs text-on-surface-variant leading-relaxed">
                  The institutional backend securely parses document text and matches registered cryptographic records.
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Right Result Card (7 Columns) */}
        <div className="lg:col-span-7 flex flex-col">
          {/* Loading View */}
          {isVerifying && (
            <div className="bg-white rounded-2xl p-12 border border-slate-200/80 shadow-sm flex flex-col items-center justify-center text-center min-h-[480px]">
              <span className="w-10 h-10 border-3 border-primary border-t-transparent rounded-full animate-spin mb-4"></span>
              <h3 className="text-lg font-bold text-primary">Verifying Credential...</h3>
              <p className="text-xs text-on-surface-variant max-w-sm mt-1">
                Consulting Westminster State University Registrar archive and checking SHA-256 cryptographic proof digests.
              </p>
            </div>
          )}

          {/* Idle View */}
          {!isVerifying && !result && (
            <div className="bg-white rounded-2xl p-12 border border-slate-200/80 shadow-sm flex flex-col items-center justify-center text-center min-h-[480px]">
              <div className="w-16 h-16 rounded-2xl bg-surface-container-low flex items-center justify-center text-on-surface-variant mb-4 border border-slate-200">
                <span className="material-symbols-outlined text-[32px]">manage_search</span>
              </div>
              <h3 className="text-lg font-bold text-primary">Awaiting Credential Input</h3>
              <p className="text-xs text-on-surface-variant max-w-md mt-1">
                Provide a certificate identifier or upload an academic document using the panel on the left to initialize verification checks.
              </p>
            </div>
          )}

          {/* Result Card Views */}
          {!isVerifying && result && (
            <div className="bg-white rounded-2xl p-6 sm:p-8 border border-slate-200/80 shadow-sm space-y-6">
              {/* Header Status Strip */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-100 gap-3">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-xs font-bold text-slate-500">
                      Query ID: {result.certificateId}
                    </span>
                    <VerificationBadge state={result.state} size="sm" />
                  </div>
                  <h3 className="text-xl font-bold text-primary">
                    {result.state === 'GENUINE' && 'Credential Authenticated'}
                    {result.state === 'TAMPERED' && 'Cryptographic Mismatch Detected'}
                    {result.state === 'REVIEW_REQUIRED' && 'Manual Review Required'}
                    {result.state === 'NOT_FOUND' && 'Record Not Found in Registry'}
                    {result.state === 'REVOKED' && 'Credential Has Been Revoked'}
                  </h3>
                </div>
                <div className="text-xs text-slate-500 font-mono self-start sm:self-auto">
                  {new Date(result.timestamp).toLocaleTimeString()}
                </div>
              </div>

              {/* Message Banner */}
              <div className={`p-4 rounded-xl border text-xs leading-relaxed ${
                result.state === 'GENUINE'
                  ? 'bg-emerald-50/80 border-emerald-200 text-emerald-900'
                  : result.state === 'TAMPERED'
                  ? 'bg-rose-50/80 border-rose-200 text-rose-900'
                  : result.state === 'REVIEW_REQUIRED'
                  ? 'bg-amber-50/80 border-amber-200 text-amber-900'
                  : result.state === 'REVOKED'
                  ? 'bg-rose-50/80 border-rose-200 text-rose-900'
                  : 'bg-slate-50 border-slate-200 text-slate-800'
              }`}>
                <div className="font-bold mb-1">{result.summaryMessage}</div>
                <div>{result.detailedMessage}</div>
              </div>

              {/* Credential Details if present */}
              {result.credential && (
                <div className="p-4 rounded-xl bg-surface-container-low border border-slate-200 space-y-3">
                  <div className="flex items-center justify-between">
                    <div>
                      <span className="text-[11px] text-slate-500 uppercase tracking-wider block">Student</span>
                      <span className="text-base font-bold text-primary">{result.credential.studentName}</span>
                    </div>
                    <div className="text-right">
                      <span className="text-[11px] text-slate-500 uppercase tracking-wider block">Roll No.</span>
                      <span className="text-xs font-mono font-bold text-slate-800">{result.credential.studentRoll}</span>
                    </div>
                  </div>

                  <div className="pt-2 border-t border-slate-200/60">
                    <span className="text-[11px] text-slate-500 uppercase tracking-wider block">Qualification</span>
                    <span className="text-xs font-semibold text-slate-900">{result.credential.course}</span>
                    <div className="text-[11px] text-slate-600 mt-0.5">
                      {result.credential.institution} • {result.credential.batch} ({result.credential.grade})
                    </div>
                  </div>
                </div>
              )}

              {/* Verification Checks Checklist */}
              <div className="space-y-3">
                <span className="font-label-sm text-xs uppercase tracking-wider font-semibold text-primary block">
                  Authoritative Verification Checklist
                </span>
                <div className="space-y-2">
                  {result.checks.map((check, idx) => (
                    <div
                      key={idx}
                      className="p-3 rounded-xl bg-slate-50 border border-slate-200 flex items-start gap-3 text-xs"
                    >
                      <span className={`material-symbols-outlined text-[18px] shrink-0 mt-0.5 ${
                        check.passed ? 'text-emerald-600' : 'text-rose-600'
                      }`}>
                        {check.passed ? 'check_circle' : 'cancel'}
                      </span>
                      <div className="flex-1">
                        <span className="font-semibold text-slate-900 block">{check.name}</span>
                        <span className="text-slate-600 text-[11px]">{check.message}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Issuer Proof Metadata */}
              {result.issuerVerification && (
                <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 font-mono text-xs space-y-1.5 text-slate-600">
                  <div className="flex justify-between">
                    <span className="font-sans font-medium text-slate-500">Accreditation:</span>
                    <span className="text-primary font-semibold font-sans">{result.issuerVerification.accreditationStatus}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="font-sans font-medium text-slate-500">Registry ID:</span>
                    <span>{result.issuerVerification.registryId}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="font-sans font-medium text-slate-500">PKI Fingerprint:</span>
                    <span>{result.issuerVerification.pkiKeyFingerprint}</span>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* SECTION: RECENT VERIFICATION ACTIVITY TABLE (as required by prompt) */}
      <div className="bg-white rounded-2xl p-6 shadow-sm border border-slate-200/80">
        <div className="flex items-center justify-between pb-4 border-b border-slate-100 mb-4">
          <div>
            <h2 className="text-lg font-bold text-primary tracking-tight">Recent Verification Queries</h2>
            <p className="text-xs text-on-surface-variant mt-0.5">
              Live audit stream of inquiries made against this institutional registrar partition
            </p>
          </div>
          <span className="px-2.5 py-1 rounded-full bg-surface-container text-xs font-semibold text-primary">
            {history.length} Recent Logs
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-surface-container-low text-on-surface-variant uppercase text-[11px] font-semibold">
              <tr>
                <th className="py-3 px-4">Query ID</th>
                <th className="py-3 px-4">Requester / Organization</th>
                <th className="py-3 px-4">Channel</th>
                <th className="py-3 px-4">Authoritative Result</th>
                <th className="py-3 px-4">Timestamp</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {history.map((item) => (
                <tr key={item.id} className="hover:bg-slate-50">
                  <td className="py-3 px-4 font-mono font-bold text-primary">
                    <button
                      onClick={() => {
                        setCertId(item.queryId);
                        handleVerify(item.queryId);
                      }}
                      className="hover:underline text-left"
                    >
                      {item.queryId}
                    </button>
                  </td>
                  <td className="py-3 px-4 font-semibold text-slate-800">{item.requester}</td>
                  <td className="py-3 px-4 text-slate-600">{item.channel}</td>
                  <td className="py-3 px-4">
                    <VerificationBadge state={item.result} size="sm" />
                  </td>
                  <td className="py-3 px-4 text-slate-500 whitespace-nowrap">{item.verifiedAt}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
