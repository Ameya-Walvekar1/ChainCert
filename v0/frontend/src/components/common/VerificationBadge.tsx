import React from 'react';
import { VerificationState } from '../../types';

interface VerificationBadgeProps {
  state: VerificationState;
  size?: 'sm' | 'md' | 'lg';
  showIcon?: boolean;
}

export const VerificationBadge: React.FC<VerificationBadgeProps> = ({ state, size = 'md', showIcon = true }) => {
  switch (state) {
    case 'GENUINE':
      return (
        <span className={`inline-flex items-center gap-1.5 font-semibold rounded-full bg-[#ECFDF5] text-[#065F46] border border-[#A7F3D0] ${
          size === 'sm' ? 'px-2.5 py-0.5 text-xs' : size === 'lg' ? 'px-4 py-1.5 text-base' : 'px-3 py-1 text-sm'
        }`}>
          {showIcon && <span className="material-symbols-outlined text-[16px] text-[#059669]">check_circle</span>}
          GENUINE
        </span>
      );
    case 'TAMPERED':
      return (
        <span className={`inline-flex items-center gap-1.5 font-semibold rounded-full bg-[#FEF2F2] text-[#991B1B] border border-[#FECACA] ${
          size === 'sm' ? 'px-2.5 py-0.5 text-xs' : size === 'lg' ? 'px-4 py-1.5 text-base' : 'px-3 py-1 text-sm'
        }`}>
          {showIcon && <span className="material-symbols-outlined text-[16px] text-[#DC2626]">dangerous</span>}
          TAMPERED
        </span>
      );
    case 'REVIEW_REQUIRED':
      return (
        <span className={`inline-flex items-center gap-1.5 font-semibold rounded-full bg-[#FEF3C7] text-[#92400E] border border-[#FDE68A] ${
          size === 'sm' ? 'px-2.5 py-0.5 text-xs' : size === 'lg' ? 'px-4 py-1.5 text-base' : 'px-3 py-1 text-sm'
        }`}>
          {showIcon && <span className="material-symbols-outlined text-[16px] text-[#D97706]">help</span>}
          REVIEW REQUIRED
        </span>
      );
    case 'REVOKED':
      return (
        <span className={`inline-flex items-center gap-1.5 font-semibold rounded-full bg-[#FEF2F2] text-[#991B1B] border border-[#FECACA] ${
          size === 'sm' ? 'px-2.5 py-0.5 text-xs' : size === 'lg' ? 'px-4 py-1.5 text-base' : 'px-3 py-1 text-sm'
        }`}>
          {showIcon && <span className="material-symbols-outlined text-[16px] text-[#DC2626]">block</span>}
          REVOKED
        </span>
      );
    case 'NOT_FOUND':
    default:
      return (
        <span className={`inline-flex items-center gap-1.5 font-semibold rounded-full bg-[#F1F5F9] text-[#475569] border border-[#CBD5E1] ${
          size === 'sm' ? 'px-2.5 py-0.5 text-xs' : size === 'lg' ? 'px-4 py-1.5 text-base' : 'px-3 py-1 text-sm'
        }`}>
          {showIcon && <span className="material-symbols-outlined text-[16px] text-[#64748B]">search_off</span>}
          NOT FOUND
        </span>
      );
  }
};
