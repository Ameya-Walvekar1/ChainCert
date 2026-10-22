import React from 'react';
import { NavLink, useNavigate, Link } from 'react-router-dom';
import { authService } from '../../services/authService';

interface InstitutionSidebarProps {
  mobileOpen?: boolean;
  onCloseMobile?: () => void;
}

export const InstitutionSidebar: React.FC<InstitutionSidebarProps> = ({ mobileOpen, onCloseMobile }) => {
  const navigate = useNavigate();
  const currentUser = authService.getCurrentUser();

  const navItems = [
    { label: 'Dashboard', path: '/institution/dashboard', icon: 'dashboard' },
    { label: 'Certificates', path: '/institution/certificates', icon: 'school' },
    { label: 'Bulk Issuance', path: '/institution/bulk-issuance', icon: 'publish' },
    { label: 'Verification', path: '/institution/verification', icon: 'fact_check' },
    { label: 'Audit & Integrity', path: '/institution/audit', icon: 'history_edu' },
  ];

  const handleLogout = () => {
    authService.logout();
    navigate('/');
  };

  return (
    <>
      {/* Mobile backdrop */}
      {mobileOpen && (
        <div 
          className="fixed inset-0 z-40 bg-black/40 lg:hidden"
          onClick={onCloseMobile}
        />
      )}

      <aside className={`fixed left-0 top-0 h-full w-72 bg-surface-container-low border-r border-slate-200/80 shadow-[0_1px_8px_rgba(15,41,66,0.04)] z-50 flex flex-col justify-between transition-transform duration-300 lg:translate-x-0 ${
        mobileOpen ? 'translate-x-0' : '-translate-x-full'
      }`}>
        <div className="flex flex-col pt-6">
          {/* Logo & Institution Header */}
          <div className="flex items-center gap-3 px-6 mb-8">
            <Link to="/" className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-primary flex items-center justify-center text-on-primary shadow-sm shrink-0">
                <span className="material-symbols-outlined text-[24px]">verified</span>
              </div>
              <div className="flex flex-col">
                <span className="font-headline-sm text-lg text-on-surface font-bold tracking-tight leading-none">
                  ChainCert
                </span>
                <span className="font-label-sm text-[11px] text-on-surface-variant uppercase tracking-wider leading-none mt-1 font-semibold">
                  Registrar Portal
                </span>
              </div>
            </Link>
          </div>

          {/* Navigation Links */}
          <nav className="flex flex-col gap-1 px-4">
            {navItems.map((item) => (
              <NavLink
                key={item.path}
                to={item.path}
                onClick={onCloseMobile}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-4 py-2.5 rounded-lg transition-all ${
                    isActive
                      ? 'bg-primary-container text-on-primary font-title-md font-semibold shadow-sm'
                      : 'text-on-surface-variant hover:bg-surface-container hover:text-on-surface font-body-md text-sm'
                  }`
                }
              >
                <span className="material-symbols-outlined text-[20px]">{item.icon}</span>
                <span>{item.label}</span>
              </NavLink>
            ))}
          </nav>
        </div>

        {/* Institution & Registrar Profile Footer */}
        <div className="p-4 border-t border-slate-200/80 bg-surface-container/40">
          <div className="flex items-center justify-between mb-3 px-2">
            <div className="flex items-center gap-2.5 overflow-hidden">
              <div className="w-9 h-9 rounded-full bg-primary-container text-white flex items-center justify-center font-bold text-sm shrink-0">
                AP
              </div>
              <div className="flex flex-col overflow-hidden">
                <span className="text-xs font-semibold text-primary truncate">
                  {currentUser?.name || 'Dr. Arthur Pendelton'}
                </span>
                <span className="text-[11px] text-on-surface-variant truncate">
                  {currentUser?.institutionName || 'Westminster State Univ.'}
                </span>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <Link
              to="/"
              className="flex-1 inline-flex items-center justify-center gap-1.5 h-8 px-2 rounded-lg bg-surface-container-high hover:bg-surface-container-highest text-primary font-medium text-xs transition-colors"
            >
              <span className="material-symbols-outlined text-[16px]">home</span>
              <span>Home</span>
            </Link>
            <button
              onClick={handleLogout}
              className="inline-flex items-center justify-center h-8 px-3 rounded-lg bg-rose-50 hover:bg-rose-100 text-rose-700 font-medium text-xs transition-colors"
              title="Sign Out"
            >
              <span className="material-symbols-outlined text-[16px]">logout</span>
            </button>
          </div>
        </div>
      </aside>
    </>
  );
};
