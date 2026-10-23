import React from 'react';

interface InstitutionHeaderProps {
  onToggleMobileSidebar: () => void;
  title?: string;
  subtitle?: string;
}

export const InstitutionHeader: React.FC<InstitutionHeaderProps> = ({
  onToggleMobileSidebar,
  title,
  subtitle
}) => {
  return (
    <header className="fixed top-0 right-0 left-0 lg:left-72 h-16 bg-white/95 backdrop-blur-md border-b border-slate-200/80 z-30 flex items-center justify-between px-4 sm:px-8 shadow-sm">
      <div className="flex items-center gap-3">
        <button
          onClick={onToggleMobileSidebar}
          className="lg:hidden p-2 rounded-lg text-on-surface-variant hover:bg-slate-100 transition-colors"
          type="button"
          aria-label="Open navigation menu"
        >
          <span className="material-symbols-outlined text-[24px]">menu</span>
        </button>

        {title ? (
          <div>
            <h1 className="text-base sm:text-lg font-bold text-primary tracking-tight leading-tight">
              {title}
            </h1>
            {subtitle && (
              <p className="text-xs text-on-surface-variant hidden sm:block">
                {subtitle}
              </p>
            )}
          </div>
        ) : (
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse"></span>
            <span className="font-label-sm text-xs font-semibold uppercase tracking-wider text-primary">
              Westminster State University Registrar Registry
            </span>
          </div>
        )}
      </div>

      <div className="flex items-center gap-3">
        {/* Node Certificate Badge */}
        <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-surface-container text-xs font-medium text-slate-700">
          <span className="material-symbols-outlined text-[16px] text-primary">security</span>
          <span className="hidden md:inline">PKI Key: 4B:A2:99...</span>
          <span className="md:hidden">Node</span>
        </div>
      </div>
    </header>
  );
};
