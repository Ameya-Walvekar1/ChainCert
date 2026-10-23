import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { authService } from '../../services/authService';

export const StudentHeader: React.FC = () => {
  const navigate = useNavigate();
  const user = authService.getCurrentUser();

  const handleLogout = () => {
    authService.logout();
    navigate('/');
  };

  return (
    <header className="fixed top-0 w-full z-50 bg-white/95 backdrop-blur-xl border-b border-slate-200/80 shadow-sm">
      <div className="h-16 max-w-7xl mx-auto px-4 lg:px-12 flex items-center justify-between gap-4">
        {/* Logo & Portal Label */}
        <div className="flex items-center gap-3">
          <Link to="/" className="flex items-center gap-2">
            <img
              src="https://lh3.googleusercontent.com/aida/AEtjO1WLQwpM3SrvresAERoW5-xMtIBKgFfc3xMjiQ72Yok767X0KuoUaADsLJvPmMC1oJt0QHkk3FVD70DDGNCt-Vtb18NbQSBAWM1zeHe_KpdUMPWZqkxpiju-hLvKJ46rSdDWZrPJQrSwDXXgH4KpTqIxMc824a5_Xvdxeus_mvwkbi-25RdS6NCiYdshW0RBOFAqJ3NzKuQiIXVEIOIrD7Kt5bsbGImHoFgxZIr9N-j8nDd_d6tnxHzYZhV_"
              alt="ChainCert"
              className="h-8 w-auto object-contain"
            />
            <span className="flex items-center text-xl font-bold tracking-tight">
              <span className="text-primary font-bold">Chain</span>
              <span className="text-secondary font-bold">Cert</span>
            </span>
          </Link>
          <span className="hidden sm:inline-block h-4 w-px bg-slate-300"></span>
          <span className="hidden sm:inline-block text-xs font-semibold text-secondary uppercase tracking-wider bg-secondary/10 px-2.5 py-0.5 rounded-full border border-secondary/20">
            Student Portal
          </span>
        </div>

        {/* Student Nav & User info */}
        <div className="flex items-center gap-4">
          <Link
            to="/student/credentials"
            className="text-sm font-semibold text-primary hover:text-secondary transition-colors"
          >
            My Credentials
          </Link>
          <Link
            to="/verify"
            className="hidden md:inline-block text-sm text-on-surface-variant hover:text-primary transition-colors"
          >
            Public Verification
          </Link>

          <div className="flex items-center gap-2.5 pl-2 border-l border-slate-200">
            <div className="w-8 h-8 rounded-full bg-primary-container text-white flex items-center justify-center font-bold text-xs">
              AP
            </div>
            <div className="hidden lg:flex flex-col">
              <span className="text-xs font-bold text-primary leading-tight">
                {user?.name || 'Ananya Patil'}
              </span>
              <span className="text-[11px] text-on-surface-variant leading-none">
                {user?.studentId || 'STU-2024-89042'}
              </span>
            </div>
            <button
              onClick={handleLogout}
              className="w-8 h-8 rounded-lg text-slate-500 hover:text-rose-600 hover:bg-rose-50 flex items-center justify-center transition-colors ml-1"
              title="Sign Out"
            >
              <span className="material-symbols-outlined text-[18px]">logout</span>
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};
