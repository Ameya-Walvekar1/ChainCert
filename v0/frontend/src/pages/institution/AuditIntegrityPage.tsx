import React, { useState, useEffect } from 'react';
import { auditService } from '../../services/auditService';
import { AuditEvent, VerificationHistoryItem } from '../../types';
import { VerificationBadge } from '../../components/common/VerificationBadge';

export const AuditIntegrityPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'events' | 'verifications'>('events');
  const [events, setEvents] = useState<AuditEvent[]>([]);
  const [history, setHistory] = useState<VerificationHistoryItem[]>([]);
  const [search, setSearch] = useState('');
  const [isChecking, setIsChecking] = useState(false);
  const [checkProgress, setCheckProgress] = useState(100);
  const [checkedCount, setCheckedCount] = useState(1280);
  const [checkFinished, setCheckFinished] = useState(true);

  useEffect(() => {
    Promise.all([
      auditService.getAuditEvents(),
      auditService.getVerificationHistory()
    ]).then(([evts, hist]) => {
      setEvents(evts);
      setHistory(hist);
    });
  }, []);

  const handleRunIntegrityCheck = async () => {
    setIsChecking(true);
    setCheckFinished(false);
    setCheckProgress(0);
    setCheckedCount(0);

    const interval = setInterval(() => {
      setCheckProgress((prev) => {
        if (prev >= 95) {
          clearInterval(interval);
          return 95;
        }
        return prev + 15;
      });
      setCheckedCount((prev) => Math.min(events.length || 1, prev + 1));
    }, 150);

    await auditService.runIntegrityCheck();

    clearInterval(interval);
    setCheckProgress(100);
    setCheckedCount(events.length || 0);
    setIsChecking(false);
    setCheckFinished(true);
  };

  const filteredEvents = events.filter((e) => {
    const q = search.toLowerCase();
    return (
      e.id.toLowerCase().includes(q) ||
      e.actor.toLowerCase().includes(q) ||
      e.targetCertificateId.toLowerCase().includes(q) ||
      e.details.toLowerCase().includes(q)
    );
  });

  const filteredHistory = history.filter((h) => {
    const q = search.toLowerCase();
    return (
      h.queryId.toLowerCase().includes(q) ||
      h.requester.toLowerCase().includes(q) ||
      h.channel.toLowerCase().includes(q)
    );
  });

  const handleExportCsv = () => {
    const csvContent =
      'data:text/csv;charset=utf-8,' +
      (activeTab === 'events'
        ? 'ID,Event Type,Actor,Target,Hash,Timestamp,Status\n' +
          events.map((e) => `${e.id},${e.eventType},${e.actor},${e.targetCertificateId},${e.hash},${e.timestamp},${e.status}`).join('\n')
        : 'ID,Requester,Query ID,Result,Timestamp,Channel\n' +
          history.map((h) => `${h.id},${h.requester},${h.queryId},${h.result},${h.verifiedAt},${h.channel}`).join('\n'));

    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `chaincert_audit_${activeTab}_export.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="flex flex-col w-full space-y-6">
      {/* Header & Export Action */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="font-label-sm text-xs uppercase tracking-wider text-on-surface-variant">
              System Auditability
            </span>
            <span className="text-outline-variant font-label-sm">•</span>
            <span className="font-label-sm text-xs font-semibold text-primary">
              Westminster Academic Records #402
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold text-primary tracking-tight">
            Audit & Integrity
          </h1>
          <p className="text-xs sm:text-sm text-on-surface-variant mt-0.5">
            Cryptographic ledger validation, tamper-evident issuance logs, and verification telemetry.
          </p>
        </div>

        <button
          onClick={handleExportCsv}
          id="exportCsvBtn"
          className="inline-flex items-center gap-2 h-11 px-5 rounded-xl bg-white hover:bg-slate-50 text-primary border border-slate-200 text-xs font-semibold shadow-xs transition-colors shrink-0"
        >
          <span className="material-symbols-outlined text-[18px]">download</span>
          <span>Export Audit Log (CSV)</span>
        </button>
      </div>

      {/* Cryptographic Architecture & Run Check Card */}
      <div className="bg-primary-container text-white rounded-2xl p-6 sm:p-8 shadow-md border border-slate-700 space-y-6 relative overflow-hidden" id="simulationBox">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-center">
          <div className="lg:col-span-8 space-y-3">
            <div className="flex items-center gap-2">
              <span className={`w-2.5 h-2.5 rounded-full ${checkFinished ? 'bg-emerald-400' : 'bg-amber-400 animate-ping'}`} id="simDot"></span>
              <span className="text-xs uppercase tracking-widest font-bold text-emerald-300 font-mono" id="simStatus">
                {isChecking ? 'Running Merkle Tree Integrity Check...' : 'Cryptographic Integrity Architecture: Synchronized'}
              </span>
            </div>

            <h2 className="text-xl sm:text-2xl font-bold">
              Merkle Tree Root & Canonical Ledger Hashes
            </h2>
            <p className="text-xs text-[#7991af] max-w-2xl leading-relaxed" id="simMessage">
              Every conferred degree produces a deterministic SHA-256 digest linked in a cryptographic Merkle tree. Any post-issuance database tampering causes an immediate root hash discrepancy.
            </p>

            <div className="p-3.5 rounded-xl bg-white/5 border border-white/10 space-y-2 text-xs font-mono text-[#b0c9e8]">
              <div className="flex flex-col sm:flex-row sm:justify-between gap-1">
                <span className="text-white/60 font-sans">Active Merkle Root:</span>
                <span className="font-bold text-emerald-300 break-all">
                  7d159a68bc2a342a78d067c26279f57ebbf7940e4f5cdbbfaad5b412bf2be822
                </span>
              </div>
              <div className="flex flex-col sm:flex-row sm:justify-between gap-1 pt-1 border-t border-white/10">
                <span className="text-white/60 font-sans">Anchored Certificates:</span>
                <span id="simCount">{checkedCount.toLocaleString()} Verified Records (100% In Custody)</span>
              </div>
            </div>
          </div>

          <div className="lg:col-span-4 flex flex-col items-start lg:items-end justify-center gap-3">
            <button
              onClick={handleRunIntegrityCheck}
              disabled={isChecking}
              id="runCheckBtn"
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2 h-12 px-6 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs shadow-md transition-all active:scale-95 disabled:opacity-60"
            >
              <span className={`material-symbols-outlined text-[20px] ${isChecking ? 'animate-spin' : ''}`} id="btnIcon">
                {isChecking ? 'refresh' : 'verified_user'}
              </span>
              <span id="btnText">{isChecking ? 'Validating Tree Nodes...' : 'Run Integrity Check'}</span>
            </button>

            {isChecking && (
              <div className="w-full space-y-1">
                <div className="flex justify-between text-[11px] text-[#7991af] font-mono">
                  <span>Traversing Merkle leaves...</span>
                  <span>{checkProgress}%</span>
                </div>
                <div className="w-full bg-white/20 rounded-full h-2 overflow-hidden">
                  <div
                    className="bg-emerald-400 h-2 rounded-full transition-all duration-200"
                    id="simProgress"
                    style={{ width: `${checkProgress}%` }}
                  ></div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Tabs & Search Controls */}
      <div className="bg-white rounded-2xl p-4 sm:p-5 border border-slate-200/80 shadow-sm space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          {/* Tabs */}
          <div className="inline-flex p-1 bg-surface-container-low rounded-xl border border-slate-200/60">
            <button
              onClick={() => setActiveTab('events')}
              id="tabBtnEvents"
              className={`px-4 py-2 rounded-lg text-xs font-semibold transition-all ${
                activeTab === 'events'
                  ? 'bg-white text-primary shadow-xs'
                  : 'text-on-surface-variant hover:text-primary'
              }`}
            >
              Audit Events ({events.length})
            </button>
            <button
              onClick={() => setActiveTab('verifications')}
              id="tabBtnVerifications"
              className={`px-4 py-2 rounded-lg text-xs font-semibold transition-all ${
                activeTab === 'verifications'
                  ? 'bg-white text-primary shadow-xs'
                  : 'text-on-surface-variant hover:text-primary'
              }`}
            >
              Verification Inquiries ({history.length})
            </button>
          </div>

          {/* Search Box */}
          <div className="relative w-full sm:w-72">
            <span className="material-symbols-outlined absolute left-3 top-2.5 text-slate-400 text-[18px]">
              search
            </span>
            <input
              type="text"
              id="tableSearch"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Filter audit log records..."
              className="w-full h-9 pl-9 pr-3 rounded-xl bg-surface-container-low border border-slate-200 text-xs focus:bg-white focus:outline-none"
            />
          </div>
        </div>

        {/* Tab 1: Audit Events Table */}
        {activeTab === 'events' && (
          <div className="overflow-x-auto" id="panelEvents">
            <table className="w-full text-left text-xs" id="auditEventsTable">
              <thead className="bg-surface-container-low text-on-surface-variant uppercase text-[11px] font-semibold">
                <tr>
                  <th className="py-3 px-3">Audit Event</th>
                  <th className="py-3 px-3">Actor / Signer</th>
                  <th className="py-3 px-3">Target Reference</th>
                  <th className="py-3 px-3">Cryptographic Digest</th>
                  <th className="py-3 px-3">Timestamp</th>
                  <th className="py-3 px-3">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-medium">
                {filteredEvents.map((evt) => (
                  <tr key={evt.id} className="hover:bg-slate-50">
                    <td className="py-3.5 px-3">
                      <span className="font-bold text-primary block">{evt.id}</span>
                      <span className="text-[11px] text-slate-500">{evt.eventType}</span>
                    </td>
                    <td className="py-3.5 px-3">
                      <span className="font-semibold text-slate-900 block">{evt.actor}</span>
                      <span className="text-[11px] text-slate-500">{evt.actorRole}</span>
                    </td>
                    <td className="py-3.5 px-3 font-mono font-semibold text-primary">
                      {evt.targetCertificateId}
                    </td>
                    <td className="py-3.5 px-3 font-mono text-[11px] text-slate-600 truncate max-w-[180px]">
                      {evt.hash}
                    </td>
                    <td className="py-3.5 px-3 text-slate-500 whitespace-nowrap">
                      {evt.timestamp}
                    </td>
                    <td className="py-3.5 px-3">
                      <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-semibold ${
                        evt.status === 'VERIFIED'
                          ? 'bg-emerald-50 text-emerald-800 border border-emerald-200'
                          : evt.status === 'FLAGGED'
                          ? 'bg-rose-50 text-rose-800 border border-rose-200'
                          : 'bg-blue-50 text-blue-800 border border-blue-200'
                      }`}>
                        <span className="w-1.5 h-1.5 rounded-full bg-current"></span>
                        {evt.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Tab 2: Verification History Table */}
        {activeTab === 'verifications' && (
          <div className="overflow-x-auto" id="panelVerifications">
            <table className="w-full text-left text-xs" id="verificationHistoryTable">
              <thead className="bg-surface-container-low text-on-surface-variant uppercase text-[11px] font-semibold">
                <tr>
                  <th className="py-3 px-3">Log ID</th>
                  <th className="py-3 px-3">Requester Organization</th>
                  <th className="py-3 px-3">Query Certificate ID</th>
                  <th className="py-3 px-3">Result</th>
                  <th className="py-3 px-3">Channel</th>
                  <th className="py-3 px-3">Verification Time</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-medium">
                {filteredHistory.map((h) => (
                  <tr key={h.id} className="hover:bg-slate-50">
                    <td className="py-3.5 px-3 font-mono font-bold text-slate-700">{h.id}</td>
                    <td className="py-3.5 px-3 font-semibold text-slate-900">{h.requester}</td>
                    <td className="py-3.5 px-3 font-mono font-bold text-primary">{h.queryId}</td>
                    <td className="py-3.5 px-3">
                      <VerificationBadge state={h.result} size="sm" />
                    </td>
                    <td className="py-3.5 px-3 text-slate-600">
                      <span className="px-2 py-0.5 rounded bg-surface-container text-[11px]">
                        {h.channel}
                      </span>
                    </td>
                    <td className="py-3.5 px-3 text-slate-500 whitespace-nowrap">{h.verifiedAt}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
