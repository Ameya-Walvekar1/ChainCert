import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { GetStartedModal } from '../../components/common/GetStartedModal';

export const LandingPage: React.FC = () => {
  const [lookupQuery, setLookupQuery] = useState('CC-2024-89042-ENG');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const navigate = useNavigate();

  const handleLookupSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!lookupQuery.trim()) return;
    navigate(`/verify?id=${encodeURIComponent(lookupQuery.trim())}`);
  };

  return (
    <div className="flex flex-col w-full">
      {/* Subtle Atmospheric Accent Layer */}
      <div className="relative w-full overflow-hidden bg-surface py-12 lg:py-20">
        {/* Ambient Backdrop Light Field */}
        <div className="absolute -top-32 right-0 w-[540px] h-[540px] bg-surface-container-high rounded-full blur-3xl opacity-60 pointer-events-none -z-0"></div>
        <div className="absolute top-1/2 -left-20 w-[420px] h-[420px] bg-secondary-container rounded-full blur-3xl opacity-20 pointer-events-none -z-0"></div>

        <div className="max-w-7xl mx-auto px-4 lg:px-12 relative z-10">
          {/* HERO SPLIT LAYOUT */}
          <div className="flex flex-col items-center justify-center max-w-4xl mx-auto text-center">
            <div className="flex flex-col items-center space-y-6 w-full">
              {/* Overline Badge */}
              <div className="inline-flex items-center gap-1.5 px-4 py-1.5 rounded-full bg-surface-container-high shadow-sm mx-auto border border-slate-200/50">
                <span className="material-symbols-outlined text-secondary text-[18px]">verified</span>
                <span className="font-label-sm text-xs uppercase tracking-wider text-primary font-semibold">
                  Institutional Provenance Standard
                </span>
              </div>

              {/* Hero Main Title */}
              <h1 className="font-display-lg text-3xl sm:text-4xl lg:text-5xl text-primary tracking-tight font-bold text-center leading-tight">
                Trusted Academic Credentials.<br className="hidden sm:inline" /> Verified with Confidence.
              </h1>

              {/* Hero Supporting Copy */}
              <p className="font-body-lg text-base sm:text-lg text-on-surface-variant max-w-2xl leading-relaxed mx-auto text-center">
                ChainCert helps institutions issue secure academic credentials and enables students, employers, and other authorized users to verify them quickly and confidently.
              </p>

              {/* CTAs Bar */}
              <div className="flex flex-wrap items-center justify-center gap-4 pt-2 mx-auto">
                <button
                  onClick={() => setIsModalOpen(true)}
                  className="inline-flex items-center justify-center h-12 px-7 rounded-xl bg-primary-container hover:bg-primary text-on-primary font-title-md text-base font-semibold shadow-md transition-all group"
                  id="heroGetStartedBtn"
                  type="button"
                >
                  <span>Get Started</span>
                  <span className="material-symbols-outlined ml-2 text-[20px] group-hover:translate-x-1 transition-transform">
                    arrow_forward
                  </span>
                </button>

                <button
                  onClick={() => navigate('/verify')}
                  className="inline-flex items-center justify-center h-12 px-6 rounded-xl bg-white hover:bg-slate-50 text-on-surface font-title-md text-base font-medium shadow-sm border border-slate-200 transition-all"
                  id="quickLookupToggleBtn"
                  type="button"
                >
                  <span className="material-symbols-outlined mr-2 text-secondary text-[20px]">search_check</span>
                  <span>Verify Credential</span>
                </button>
              </div>

              {/* Inline Quick Verification Input Box */}
              <div
                className="w-full max-w-2xl p-4 sm:p-6 rounded-2xl bg-white border border-slate-200/80 shadow-lg transition-all duration-300 mx-auto text-left mt-4"
                id="quickLookupPanel"
              >
                <div className="flex items-center justify-between pb-3 border-b border-slate-100">
                  <span className="font-label-md text-xs text-on-surface-variant font-semibold uppercase tracking-wider flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-secondary"></span>
                    Instant Identifier Lookup
                  </span>
                  <span className="font-label-sm text-xs text-on-surface-variant">
                    Registrar Directory Query
                  </span>
                </div>

                <form onSubmit={handleLookupSubmit} className="flex flex-col sm:flex-row gap-3 pt-4" id="heroLookupForm">
                  <div className="relative flex-1">
                    <span className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                      <span className="material-symbols-outlined text-[20px]">badge</span>
                    </span>
                    <input
                      className="w-full h-11 pl-11 pr-4 rounded-xl bg-surface-container-low text-primary font-body-md text-sm focus:bg-white focus:ring-2 focus:ring-primary-container focus:outline-none transition-all border border-slate-200"
                      id="certificateLookupInput"
                      placeholder="Enter Certificate ID (e.g. CC-2024-...)"
                      type="text"
                      value={lookupQuery}
                      onChange={(e) => setLookupQuery(e.target.value)}
                    />
                  </div>
                  <button
                    className="h-11 px-6 rounded-xl bg-primary-container hover:bg-primary text-on-primary font-title-md text-sm font-semibold transition-all shadow-sm shrink-0 flex items-center justify-center gap-2"
                    type="submit"
                  >
                    <span className="material-symbols-outlined text-[18px]">verified_user</span>
                    <span>Check Record</span>
                  </button>
                </form>

                <div className="mt-3 p-3 rounded-lg bg-surface-container-low text-on-surface-variant text-xs flex items-center gap-2 border border-slate-200/50">
                  <span className="material-symbols-outlined text-secondary text-[16px]">info</span>
                  <span>Try: <strong className="text-primary font-mono cursor-pointer hover:underline" onClick={() => setLookupQuery('CC-2024-89042-ENG')}>CC-2024-89042-ENG</strong>, <strong className="text-primary font-mono cursor-pointer hover:underline" onClick={() => setLookupQuery('CC-2024-99211-LAW')}>CC-2024-99211-LAW</strong> (Revoked), or upload a document in full verification.</span>
                </div>
              </div>

              {/* Proof Metrics Strip */}
              <div className="grid grid-cols-3 gap-6 pt-4 w-full max-w-xl mx-auto text-center">
                <div>
                  <div className="font-headline-sm text-2xl lg:text-3xl text-primary font-bold">140+</div>
                  <div className="font-label-sm text-xs text-on-surface-variant mt-1">Accredited Campuses</div>
                </div>
                <div>
                  <div className="font-headline-sm text-2xl lg:text-3xl text-primary font-bold">&lt; 1.2s</div>
                  <div className="font-label-sm text-xs text-on-surface-variant mt-1">Average Resolution</div>
                </div>
                <div>
                  <div className="font-headline-sm text-2xl lg:text-3xl text-primary font-bold">100%</div>
                  <div className="font-label-sm text-xs text-on-surface-variant mt-1">Institutional Custody</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* HOW IT WORKS SECTION */}
      <section className="w-full py-16 lg:py-24 bg-surface-container-low border-y border-slate-200/60" id="how-it-works">
        <div className="max-w-7xl mx-auto px-4 lg:px-12">
          {/* Section Header */}
          <div className="max-w-2xl mx-auto text-center space-y-2 mb-12">
            <span className="font-label-sm text-xs text-secondary uppercase tracking-widest font-bold">
              Standardized Architecture
            </span>
            <h2 className="font-headline-lg text-2xl sm:text-3xl text-primary tracking-tight font-bold">
              How It Works
            </h2>
            <p className="font-body-lg text-sm sm:text-base text-on-surface-variant">
              A dependable framework for institutional validation and instant student record verification.
            </p>
          </div>

          {/* 3 Steps Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 relative">
            {/* Step 01 */}
            <div className="flex flex-col bg-white p-6 rounded-2xl shadow-sm border border-slate-200/80 hover:shadow-md transition-shadow">
              <div className="flex items-center justify-between pb-4">
                <span className="w-12 h-12 rounded-xl bg-surface-container-high text-primary flex items-center justify-center font-headline-sm text-lg font-bold">
                  01
                </span>
                <span className="material-symbols-outlined text-secondary text-[28px]">domain_verification</span>
              </div>
              <h3 className="font-title-md text-base sm:text-lg text-primary font-bold mb-2">
                Institution Issues
              </h3>
              <p className="font-body-md text-sm text-on-surface-variant leading-relaxed">
                Institutions register and issue academic credentials through ChainCert with verified administrator sign-off.
              </p>
              <div className="mt-4 pt-3 bg-surface-container-low p-3 rounded-xl flex items-center gap-2 text-on-surface-variant text-xs font-medium">
                <span className="material-symbols-outlined text-[16px] text-primary">security</span>
                <span>Registrar PKI Authorized</span>
              </div>
            </div>

            {/* Step 02 */}
            <div className="flex flex-col bg-white p-6 rounded-2xl shadow-sm border border-slate-200/80 hover:shadow-md transition-shadow">
              <div className="flex items-center justify-between pb-4">
                <span className="w-12 h-12 rounded-xl bg-surface-container-high text-primary flex items-center justify-center font-headline-sm text-lg font-bold">
                  02
                </span>
                <span className="material-symbols-outlined text-secondary text-[28px]">lock</span>
              </div>
              <h3 className="font-title-md text-base sm:text-lg text-primary font-bold mb-2">
                Credential Is Protected
              </h3>
              <p className="font-body-md text-sm text-on-surface-variant leading-relaxed">
                Credential information is securely recorded and associated with a unique, unalterable Certificate ID.
              </p>
              <div className="mt-4 pt-3 bg-surface-container-low p-3 rounded-xl flex items-center gap-2 text-on-surface-variant text-xs font-medium">
                <span className="material-symbols-outlined text-[16px] text-primary">fingerprint</span>
                <span>Canonical Cryptographic Seal</span>
              </div>
            </div>

            {/* Step 03 */}
            <div className="flex flex-col bg-white p-6 rounded-2xl shadow-sm border border-slate-200/80 hover:shadow-md transition-shadow">
              <div className="flex items-center justify-between pb-4">
                <span className="w-12 h-12 rounded-xl bg-surface-container-high text-primary flex items-center justify-center font-headline-sm text-lg font-bold">
                  03
                </span>
                <span className="material-symbols-outlined text-secondary text-[28px]">fact_check</span>
              </div>
              <h3 className="font-title-md text-base sm:text-lg text-primary font-bold mb-2">
                Anyone Can Verify
              </h3>
              <p className="font-body-md text-sm text-on-surface-variant leading-relaxed">
                Authorized users can verify a credential using its Certificate ID or direct official verification link in seconds.
              </p>
              <div className="mt-4 pt-3 bg-surface-container-low p-3 rounded-xl flex items-center gap-2 text-on-surface-variant text-xs font-medium">
                <span className="material-symbols-outlined text-[16px] text-primary">public</span>
                <span>Real-time Global Resolution</span>
              </div>
            </div>
          </div>

          {/* Process Diagram Ribbon */}
          <div className="mt-8 p-6 rounded-2xl bg-surface-container flex flex-col md:flex-row items-center justify-between gap-4 border border-slate-200/80">
            <div className="flex items-center gap-4">
              <div className="w-10 h-10 rounded-full bg-primary text-on-primary flex items-center justify-center shrink-0">
                <span className="material-symbols-outlined text-[20px]">sync</span>
              </div>
              <div>
                <h4 className="font-title-md text-sm sm:text-base text-primary font-semibold">
                  FERPA & High-Trust Compliance Standard
                </h4>
                <p className="font-body-md text-xs sm:text-sm text-on-surface-variant">
                  Built to integrate with Student Information Systems (Banner, Peoplesoft, Workday) without disruption.
                </p>
              </div>
            </div>
            <button
              onClick={() => setIsModalOpen(true)}
              className="inline-flex items-center gap-1.5 px-6 h-10 rounded-xl bg-primary-container text-on-primary font-title-md text-sm font-medium hover:bg-primary transition-colors shrink-0 shadow-sm"
              type="button"
            >
              <span>Get Started Now</span>
              <span className="material-symbols-outlined text-[18px]">chevron_right</span>
            </button>
          </div>
        </div>
      </section>

      {/* TRUST & VALUE SECTION */}
      <section className="w-full py-16 lg:py-24 bg-surface" id="trust">
        <div className="max-w-7xl mx-auto px-4 lg:px-12">
          <div className="flex flex-col md:flex-row md:items-end justify-between mb-12 gap-4">
            <div className="max-w-2xl space-y-2">
              <span className="font-label-sm text-xs text-secondary uppercase tracking-widest font-bold">
                Institutional Security Standard
              </span>
              <h2 className="font-headline-lg text-2xl sm:text-3xl text-primary tracking-tight font-bold">
                Built for Academic Integrity
              </h2>
              <p className="font-body-lg text-sm sm:text-base text-on-surface-variant">
                Delivering infallible validation workflows across university registrars, employers, and background verification analysts.
              </p>
            </div>
            <div className="text-left md:text-right">
              <span className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-full bg-surface-container text-primary font-label-md text-xs font-semibold">
                <span className="material-symbols-outlined text-secondary text-[16px]">verified</span>
                Strict Registrar Custody
              </span>
            </div>
          </div>

          {/* 4 Clean Institutional Value Cards Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {/* Value 1 */}
            <div className="p-6 rounded-2xl bg-white border border-slate-200/80 shadow-sm hover:shadow-md transition-all flex flex-col justify-between">
              <div className="space-y-4">
                <div className="w-12 h-12 rounded-xl bg-surface-container-high flex items-center justify-center text-primary">
                  <span className="material-symbols-outlined text-[24px]">encrypted</span>
                </div>
                <h3 className="font-title-md text-base text-primary font-bold">
                  Secure Credential Records
                </h3>
                <p className="font-body-md text-xs sm:text-sm text-on-surface-variant leading-relaxed">
                  Encrypted, tamper-evident record archives managed directly under institutional governance and legal data mandates.
                </p>
              </div>
              <div className="pt-6 flex items-center text-secondary font-label-md text-xs font-semibold gap-1.5">
                <span className="material-symbols-outlined text-[16px]">check_circle</span>
                <span>Encrypted at Rest & Transit</span>
              </div>
            </div>

            {/* Value 2 */}
            <div className="p-6 rounded-2xl bg-white border border-slate-200/80 shadow-sm hover:shadow-md transition-all flex flex-col justify-between">
              <div className="space-y-4">
                <div className="w-12 h-12 rounded-xl bg-surface-container-high flex items-center justify-center text-primary">
                  <span className="material-symbols-outlined text-[24px]">speed</span>
                </div>
                <h3 className="font-title-md text-base text-primary font-bold">
                  Fast Verification
                </h3>
                <p className="font-body-md text-xs sm:text-sm text-on-surface-variant leading-relaxed">
                  Instant validation for employers and admissions councils in seconds, eliminating manual transcript phone calls and delays.
                </p>
              </div>
              <div className="pt-6 flex items-center text-secondary font-label-md text-xs font-semibold gap-1.5">
                <span className="material-symbols-outlined text-[16px]">check_circle</span>
                <span>Zero Administrative Overhead</span>
              </div>
            </div>

            {/* Value 3 */}
            <div className="p-6 rounded-2xl bg-white border border-slate-200/80 shadow-sm hover:shadow-md transition-all flex flex-col justify-between">
              <div className="space-y-4">
                <div className="w-12 h-12 rounded-xl bg-surface-container-high flex items-center justify-center text-primary">
                  <span className="material-symbols-outlined text-[24px]">admin_panel_settings</span>
                </div>
                <h3 className="font-title-md text-base text-primary font-bold">
                  Institution-Controlled Issuance
                </h3>
                <p className="font-body-md text-xs sm:text-sm text-on-surface-variant leading-relaxed">
                  Dedicated cryptographic signing keys and administrative authorization hierarchies reserved strictly for accredited registrar offices.
                </p>
              </div>
              <div className="pt-6 flex items-center text-secondary font-label-md text-xs font-semibold gap-1.5">
                <span className="material-symbols-outlined text-[16px]">check_circle</span>
                <span>Multi-Registrar Dual Sign-off</span>
              </div>
            </div>

            {/* Value 4 */}
            <div className="p-6 rounded-2xl bg-white border border-slate-200/80 shadow-sm hover:shadow-md transition-all flex flex-col justify-between">
              <div className="space-y-4">
                <div className="w-12 h-12 rounded-xl bg-surface-container-high flex items-center justify-center text-primary">
                  <span className="material-symbols-outlined text-[24px]">history_edu</span>
                </div>
                <h3 className="font-title-md text-base text-primary font-bold">
                  Transparent Verification Status
                </h3>
                <p className="font-body-md text-xs sm:text-sm text-on-surface-variant leading-relaxed">
                  Real-time active, revoked, or conferred status indicators with complete institutional audit trails and historical timestamps.
                </p>
              </div>
              <div className="pt-6 flex items-center text-secondary font-label-md text-xs font-semibold gap-1.5">
                <span className="material-symbols-outlined text-[16px]">check_circle</span>
                <span>Auditable Logging Standard</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CAMPUS & REGISTRAR VALIDATION REPOSITORY SECTION */}
      <section className="w-full py-16 bg-surface-container-low border-t border-slate-200/60" id="registry">
        <div className="max-w-7xl mx-auto px-4 lg:px-12">
          <div className="bg-white rounded-2xl p-6 lg:p-10 border border-slate-200 shadow-md">
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
              <div className="lg:col-span-8 space-y-3">
                <span className="font-label-sm text-xs text-secondary uppercase font-bold tracking-wider">
                  Institutional Registry Access
                </span>
                <h3 className="font-headline-lg text-2xl lg:text-3xl text-primary font-bold">
                  Are you an Accredited Registrar or University Officer?
                </h3>
                <p className="font-body-lg text-sm sm:text-base text-on-surface-variant max-w-2xl leading-relaxed">
                  Connect your Student Information System with ChainCert’s secure registry. Automate credential generation, eliminate verification backlogs, and preserve permanent diploma provenance.
                </p>
              </div>
              <div className="lg:col-span-4 flex flex-col sm:flex-row lg:flex-col gap-3 justify-end">
                <button
                  onClick={() => setIsModalOpen(true)}
                  className="inline-flex items-center justify-center h-11 px-6 rounded-xl bg-primary-container hover:bg-primary text-on-primary font-title-md text-sm font-semibold shadow-sm transition-all"
                  type="button"
                >
                  <span>Institution Portal Access</span>
                  <span className="material-symbols-outlined ml-2 text-[18px]">login</span>
                </button>
                <button
                  onClick={() => navigate('/verify')}
                  className="inline-flex items-center justify-center h-11 px-6 rounded-xl bg-surface-container hover:bg-surface-container-high text-on-surface font-title-md text-sm font-semibold shadow-sm transition-all border border-slate-200"
                  type="button"
                >
                  <span>Verify a Credential</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>

      <GetStartedModal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} />
    </div>
  );
};
