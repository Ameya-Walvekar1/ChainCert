import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';

// Layouts
import { PublicLayout } from '../layouts/PublicLayout';
import { InstitutionLayout } from '../layouts/InstitutionLayout';
import { StudentLayout } from '../layouts/StudentLayout';

// Public Pages
import { LandingPage } from '../pages/public/LandingPage';
import { PublicVerificationPage } from '../pages/public/PublicVerificationPage';
import { VerificationResultPage } from '../pages/public/VerificationResultPage';

// Auth Pages
import { InstitutionLoginPage } from '../pages/auth/InstitutionLoginPage';
import { StudentLoginPage } from '../pages/auth/StudentLoginPage';

// Institution Pages
import { InstitutionDashboardPage } from '../pages/institution/InstitutionDashboardPage';
import { CertificatesPage } from '../pages/institution/CertificatesPage';
import { BulkIssuancePage } from '../pages/institution/BulkIssuancePage';
import { InstitutionVerificationPage } from '../pages/institution/InstitutionVerificationPage';
import { AuditIntegrityPage } from '../pages/institution/AuditIntegrityPage';

// Student Pages
import { StudentCredentialsPage } from '../pages/student/StudentCredentialsPage';
import { StudentCredentialDetailsPage } from '../pages/student/StudentCredentialDetailsPage';

export const AppRoutes: React.FC = () => {
  return (
    <Routes>
      {/* Public Pages */}
      <Route element={<PublicLayout />}>
        <Route path="/" element={<LandingPage />} />
        <Route path="/verify" element={<PublicVerificationPage />} />
        <Route path="/verify/result" element={<VerificationResultPage />} />
      </Route>

      {/* Authentication */}
      <Route path="/institution/login" element={<InstitutionLoginPage />} />
      <Route path="/student/login" element={<StudentLoginPage />} />

      {/* Institution Portal */}
      <Route path="/institution" element={<InstitutionLayout />}>
        <Route index element={<Navigate to="/institution/dashboard" replace />} />
        <Route path="dashboard" element={<InstitutionDashboardPage />} />
        <Route path="certificates" element={<CertificatesPage />} />
        <Route path="bulk-issuance" element={<BulkIssuancePage />} />
        <Route path="verification" element={<InstitutionVerificationPage />} />
        <Route path="audit" element={<AuditIntegrityPage />} />
      </Route>

      {/* Student Portal */}
      <Route path="/student" element={<StudentLayout />}>
        <Route index element={<Navigate to="/student/credentials" replace />} />
        <Route path="credentials" element={<StudentCredentialsPage />} />
        <Route path="credentials/:id" element={<StudentCredentialDetailsPage />} />
      </Route>

      {/* Fallback */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
};
