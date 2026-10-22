import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { GetStartedModal } from './GetStartedModal';
import { authService } from '../../services/authService';

export const Navbar: React.FC = () => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const currentUser = authService.getCurrentUser();

  const isCurrent = (path: string) => location.pathname === path;

  return (
    <>
      <header className="fixed top-0 w-full z-50 bg-white/95 backdrop-blur-xl border-b border-slate-100 shadow-[0_1px_8px_rgba(15,41,66,0.04)]">
        <div className="h-16 max-w-7xl mx-auto px-4 lg:px-12 flex items-center justify-between gap-6">
          {/* Logo */}
          <div className="flex items-center gap-3">
            <Link to="/" className="flex items-center gap-2">
              <img
                src="https://lh3.googleusercontent.com/aida/AEtjO1WLQwpM3SrvresAERoW5-xMtIBKgFfc3xMjiQ72Yok767X0KuoUaADsLJvPmMC1oJt0QHkk3FVD70DDGNCt-Vtb18NbQSBAWM1zeHe_KpdUMPWZqkxpiju-hLvKJ46rSdDWZrPJQrSwDXXgH4KpTqIxMc824a5_Xvdxeus_mvwkbi-25RdS6NCiYdshW0RBOFAqJ3NzKuQiIXVEIOIrD7Kt5bsbGImHoFgxZIr9N-j8nDd_d6tnxHzYZhV_"
                alt="ChainCert Institutional Logo"
                className="h-8 w-auto object-contain"
              />
              <span className="flex items-center text-xl font-bold tracking-tight">
                <span className="text-primary font-bold">Chain</span>
                <span className="text-secondary font-bold">Cert</span>
              </span>
            </Link>
          </div>

          {/* Nav Links */}
          <nav className="hidden md:flex items-center gap-8">
            <Link
              to="/"
              className={`text-sm font-medium transition-colors ${
                isCurrent('/') ? 'text-primary font-semibold' : 'text-on-surface-variant hover:text-primary'
              }`}
            >
              Home
            </Link>
            <a
              href="/#how-it-works"
              className="text-sm font-medium text-on-surface-variant hover:text-primary transition-colors"
            >
              How It Works
            </a>
            <Link
              to="/verify"
              className={`text-sm font-medium transition-colors ${
                isCurrent('/verify') ? 'text-primary font-semibold' : 'text-on-surface-variant hover:text-primary'
              }`}
            >
              Verify Credential
            </Link>
            <a
              href="/#registry"
              className="text-sm font-medium text-on-surface-variant hover:text-primary transition-colors"
            >
              Institutional Registry
            </a>
          </nav>

          {/* Right Action Buttons */}
          <div className="flex items-center gap-3">
            {currentUser ? (
              <div className="flex items-center gap-2">
                <Link
                  to={currentUser.role === 'institution' ? '/institution/dashboard' : '/student/credentials'}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-surface-container hover:bg-surface-container-high text-primary font-medium text-xs transition-colors"
                >
                  <span className="material-symbols-outlined text-[16px]">
                    {currentUser.role === 'institution' ? 'account_balance' : 'school'}
                  </span>
                  <span>{currentUser.role === 'institution' ? 'Portal' : 'My Credentials'}</span>
                </Link>
                <button
                  onClick={() => {
                    authService.logout();
                    navigate('/');
                  }}
                  title="Sign Out"
                  className="w-8 h-8 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-600 flex items-center justify-center transition-colors"
                >
                  <span className="material-symbols-outlined text-[16px]">logout</span>
                </button>
              </div>
            ) : (
              <>
                <button
                  onClick={() => setIsModalOpen(true)}
                  className="hidden sm:inline-block font-body-md text-sm text-on-surface-variant hover:text-on-surface font-medium transition-colors px-2 py-1"
                >
                  Sign In
                </button>
                <button
                  onClick={() => setIsModalOpen(true)}
                  className="inline-flex items-center justify-center h-10 px-5 rounded-lg bg-primary-container hover:bg-primary text-on-primary font-title-md text-sm font-medium transition-all shadow-sm"
                >
                  Get Started
                </button>
                <button
                  onClick={() => setIsModalOpen(true)}
                  className="w-8 h-8 rounded-full bg-primary flex items-center justify-center shrink-0 text-white"
                  aria-label="Account Access"
                >
                  <span className="material-symbols-outlined text-white text-[18px]">person</span>
                </button>
              </>
            )}
          </div>
        </div>
      </header>

      <GetStartedModal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} />
    </>
  );
};
