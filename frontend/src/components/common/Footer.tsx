import React from 'react';
import { Link } from 'react-router-dom';

export const Footer: React.FC = () => {
  return (
    <footer className="w-full bg-surface-container-low border-t border-slate-200/60 shadow-[0_-1px_8px_rgba(15,41,66,0.03)]">
      <div className="max-w-7xl mx-auto px-4 lg:px-12 py-10">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
          {/* Brand Info */}
          <div className="md:col-span-2 space-y-4">
            <div className="flex items-center gap-2">
              <img
                src="https://lh3.googleusercontent.com/aida/AEtjO1WLQwpM3SrvresAERoW5-xMtIBKgFfc3xMjiQ72Yok767X0KuoUaADsLJvPmMC1oJt0QHkk3FVD70DDGNCt-Vtb18NbQSBAWM1zeHe_KpdUMPWZqkxpiju-hLvKJ46rSdDWZrPJQrSwDXXgH4KpTqIxMc824a5_Xvdxeus_mvwkbi-25RdS6NCiYdshW0RBOFAqJ3NzKuQiIXVEIOIrD7Kt5bsbGImHoFgxZIr9N-j8nDd_d6tnxHzYZhV_"
                alt="ChainCert Institutional Logo"
                className="h-7 w-auto object-contain"
              />
              <span className="font-headline-sm text-lg text-primary tracking-tight font-semibold">
                ChainCert
              </span>
            </div>
            <p className="font-body-md text-sm text-on-surface-variant max-w-md leading-relaxed">
              The trusted institutional standard for official academic credential verification, transcript validation, and registrar-grade provenance for higher education institutions globally.
            </p>
            <div className="flex flex-wrap items-center gap-2 pt-1">
              <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-surface-container-highest text-primary font-label-sm text-xs font-medium">
                <span className="material-symbols-outlined text-[14px] text-secondary">verified_user</span>
                ISO 27001 Accredited
              </span>
              <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-surface-container-highest text-primary font-label-sm text-xs font-medium">
                <span className="material-symbols-outlined text-[14px] text-secondary">shield</span>
                FERPA Compliant
              </span>
            </div>
          </div>

          {/* Platform Links */}
          <div className="space-y-3">
            <div className="font-title-md text-sm text-primary font-semibold uppercase tracking-wider">
              Platform
            </div>
            <ul className="space-y-2 font-body-md text-sm">
              <li>
                <Link to="/verify" className="text-on-surface-variant hover:text-primary transition-colors">
                  Verify Credential
                </Link>
              </li>
              <li>
                <a href="/#how-it-works" className="text-on-surface-variant hover:text-primary transition-colors">
                  How It Works
                </a>
              </li>
              <li>
                <a href="/#registry" className="text-on-surface-variant hover:text-primary transition-colors">
                  Institutional Registry
                </a>
              </li>
              <li>
                <Link to="/institution/login" className="text-on-surface-variant hover:text-primary transition-colors">
                  Registrar Portal
                </Link>
              </li>
            </ul>
          </div>

          {/* Governance Links */}
          <div className="space-y-3">
            <div className="font-title-md text-sm text-primary font-semibold uppercase tracking-wider">
              Governance
            </div>
            <ul className="space-y-2 font-body-md text-sm">
              <li>
                <span className="text-on-surface-variant hover:text-primary transition-colors cursor-pointer">
                  Accreditation Standards
                </span>
              </li>
              <li>
                <span className="text-on-surface-variant hover:text-primary transition-colors cursor-pointer">
                  Privacy & FERPA
                </span>
              </li>
              <li>
                <Link to="/institution/audit" className="text-on-surface-variant hover:text-primary transition-colors">
                  Audit & Security
                </Link>
              </li>
              <li>
                <span className="text-on-surface-variant hover:text-primary transition-colors cursor-pointer">
                  Support Desk
                </span>
              </li>
            </ul>
          </div>
        </div>

        <div className="pt-6 border-t border-slate-200/80 flex flex-col sm:flex-row items-center justify-between gap-4 font-label-md text-xs text-on-surface-variant">
          <p>© 2026 ChainCert Institutional Systems, Inc. All rights reserved. Official academic verification repository.</p>
          <div className="flex items-center gap-6">
            <span className="hover:text-on-surface transition-colors cursor-pointer">Privacy Policy</span>
            <span className="hover:text-on-surface transition-colors cursor-pointer">Terms of Service</span>
            <span className="hover:text-on-surface transition-colors cursor-pointer">Institutional Inquiries</span>
          </div>
        </div>
      </div>
    </footer>
  );
};
