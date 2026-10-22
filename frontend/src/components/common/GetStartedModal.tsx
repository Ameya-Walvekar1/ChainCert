import React from 'react';
import { useNavigate } from 'react-router-dom';

interface GetStartedModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const GetStartedModal: React.FC<GetStartedModalProps> = ({ isOpen, onClose }) => {
  const navigate = useNavigate();

  if (!isOpen) return null;

  return (
    <div 
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-primary/70 backdrop-blur-md transition-opacity duration-300"
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
      id="getStartedModal"
    >
      <div className="relative w-full max-w-2xl rounded-2xl bg-white p-6 sm:p-8 shadow-2xl overflow-hidden transition-all transform scale-100 border border-slate-100">
        {/* Modal Header */}
        <div className="flex items-start justify-between pb-6">
          <div>
            <span className="font-label-sm text-xs text-secondary uppercase tracking-widest font-bold">
              ChainCert Portal Access
            </span>
            <h2 className="font-headline-lg text-2xl sm:text-3xl text-primary font-bold tracking-tight mt-1">
              How would you like to continue?
            </h2>
            <p className="font-body-md text-sm text-on-surface-variant mt-1">
              Select your role to access issuance tools, institutional portals, or individual records.
            </p>
          </div>
          <button
            onClick={onClose}
            className="w-9 h-9 rounded-full bg-surface-container-high hover:bg-surface-container-highest text-on-surface-variant hover:text-primary flex items-center justify-center transition-colors"
            type="button"
            aria-label="Close dialog"
          >
            <span className="material-symbols-outlined text-[20px]">close</span>
          </button>
        </div>

        {/* Two Options Side by Side */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-1 pb-4">
          {/* Option 1: Institution / Admin */}
          <div className="flex flex-col justify-between p-5 rounded-xl bg-surface-container-low hover:bg-surface-container transition-all border border-slate-200/60 shadow-sm">
            <div className="space-y-3">
              <div className="w-12 h-12 rounded-lg bg-primary text-on-primary flex items-center justify-center shadow-sm">
                <span className="material-symbols-outlined text-[26px]">account_balance</span>
              </div>
              <h3 className="font-title-md text-lg text-primary font-bold">
                Institution / Admin
              </h3>
              <p className="font-body-md text-sm text-on-surface-variant leading-relaxed">
                Issue, manage and verify academic credentials with accredited university registrar permissions.
              </p>
            </div>
            <div className="pt-6">
              <button
                onClick={() => {
                  onClose();
                  navigate('/institution/login');
                }}
                className="inline-flex items-center justify-center w-full h-11 px-4 rounded-lg bg-primary hover:bg-primary-container text-on-primary font-title-md text-sm font-semibold transition-all shadow-sm"
                type="button"
              >
                <span>Continue as Institution</span>
                <span className="material-symbols-outlined ml-1.5 text-[18px]">arrow_forward</span>
              </button>
            </div>
          </div>

          {/* Option 2: Student */}
          <div className="flex flex-col justify-between p-5 rounded-xl bg-surface-container-low hover:bg-surface-container transition-all border border-slate-200/60 shadow-sm">
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <div className="w-12 h-12 rounded-lg bg-primary text-on-primary flex items-center justify-center shadow-sm">
                  <span className="material-symbols-outlined text-[26px]">school</span>
                </div>
                <span className="px-2 py-0.5 rounded text-[11px] font-semibold bg-secondary/10 text-secondary border border-secondary/20">
                  Student Portal
                </span>
              </div>
              <h3 className="font-title-md text-lg text-primary font-bold">
                Student
              </h3>
              <p className="font-body-md text-sm text-on-surface-variant leading-relaxed">
                View and manage your verified academic credentials, transcripts, and official shareable links.
              </p>
            </div>
            <div className="pt-6">
              <button
                onClick={() => {
                  onClose();
                  navigate('/student/login');
                }}
                className="inline-flex items-center justify-center w-full h-11 px-4 rounded-lg bg-secondary hover:bg-secondary/90 text-white font-title-md text-sm font-semibold transition-all shadow-sm"
                type="button"
              >
                <span>Continue as Student</span>
                <span className="material-symbols-outlined ml-1.5 text-[18px]">arrow_forward</span>
              </button>
            </div>
          </div>
        </div>

        {/* Modal Footer */}
        <div className="pt-3 border-t border-slate-100 flex items-center justify-between text-on-surface-variant font-label-md text-xs">
          <span className="flex items-center gap-1.5">
            <span className="material-symbols-outlined text-secondary text-[16px]">shield</span>
            Registrar-grade cryptographic validation
          </span>
          <button
            onClick={onClose}
            className="text-primary hover:underline font-medium"
            type="button"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
};
