import { VerificationResult, VerificationState } from '../types';
import { API_BASE_URL } from './apiConfig';

// ---------------------------------------------------------------------------
// Backend response shape from /api/v1/verify and /api/v1/verification/verify-upload
// ---------------------------------------------------------------------------
interface BackendVerifyResponse {
  success: boolean;
  status: string;          // GENUINE | TAMPERED | NOT_FOUND | REVOKED | REVIEW_REQUIRED
  explanation?: string;
  certificate_id?: string;
  certificate?: {
    certificate_id: string;
    student_name?: string;
    roll_number?: string;
    course?: string;
    cgpa?: string;
    issue_date?: string;
    institution_id?: string;
  };
  checks?: { name: string; passed: boolean; detail?: string }[];
  sha256?: string;
  merkle_root?: string;
  mismatched_fields?: string[];
  extraction?: Record<string, unknown>;
}

function mapState(status: string): VerificationState {
  switch (status.toUpperCase()) {
    case 'GENUINE': return 'GENUINE';
    case 'TAMPERED': return 'TAMPERED';
    case 'REVOKED': return 'REVOKED';
    case 'REVIEW_REQUIRED': return 'REVIEW_REQUIRED';
    default: return 'NOT_FOUND';
  }
}

function buildResult(data: BackendVerifyResponse, channel: VerificationResult['channel']): VerificationResult {
  const state = mapState(data.status);
  const certId = data.certificate_id || data.certificate?.certificate_id || 'UNKNOWN';

  const summaryMap: Record<VerificationState, string> = {
    GENUINE: 'This credential is registered with the issuing institution and details match the trusted record.',
    TAMPERED: 'The submitted credential does not match the trusted record. Field mismatch detected.',
    REVOKED: 'This credential was previously registered but has been revoked by the issuing institution.',
    REVIEW_REQUIRED: 'The credential could not be conclusively verified automatically and requires further review.',
    NOT_FOUND: 'No matching credential record was found.',
  };

  const checks = data.checks
    ? data.checks.map(c => ({ name: c.name, passed: c.passed, message: c.detail ?? '' }))
    : buildDefaultChecks(state, data.mismatched_fields ?? []);

  const result: VerificationResult = {
    state,
    certificateId: certId,
    timestamp: new Date().toISOString(),
    summaryMessage: summaryMap[state],
    detailedMessage: data.explanation ?? summaryMap[state],
    checks,
    channel,
  };

  if (data.certificate && (state === 'GENUINE' || state === 'REVOKED')) {
    const c = data.certificate;
    result.credential = {
      id: c.certificate_id,
      studentName: c.student_name ?? '',
      studentRoll: c.roll_number ?? '',
      course: c.course ?? '',
      degreeType: 'Academic Degree',
      institution: c.institution_id ?? '',
      institutionId: c.institution_id ?? '',
      issueDate: c.issue_date ?? '',
      batch: '',
      grade: '',
      cgpa: c.cgpa,
      status: state === 'REVOKED' ? 'REVOKED' : 'ACTIVE',
      sha256Hash: data.sha256 ?? '',
      merkleRoot: data.merkle_root ?? '',
    };
  }

  if (data.sha256 || data.merkle_root) {
    result.integrityProof = {
      sha256: data.sha256 ?? '',
      merkleRoot: data.merkle_root ?? '',
      batchId: '',
      leafIndex: 0,
    };
  }

  return result;
}

function buildDefaultChecks(state: VerificationState, mismatchedFields: string[]) {
  const checks = [];
  if (state === 'GENUINE') {
    checks.push(
      { name: 'Registry Lookup', passed: true, message: 'Record found in institutional registry' },
      { name: 'Hash Verification', passed: true, message: 'SHA-256 canonical hash matches trusted archive' },
      { name: 'Active Status', passed: true, message: 'Credential is active and unrevoked' },
    );
  } else if (state === 'TAMPERED') {
    checks.push(
      { name: 'Registry Lookup', passed: true, message: 'Record found in institutional registry' },
      { name: 'Field Comparison', passed: false, message: `Mismatched fields: ${mismatchedFields.join(', ') || 'unknown'}` },
    );
  } else if (state === 'REVOKED') {
    checks.push(
      { name: 'Registry Lookup', passed: true, message: 'Record found' },
      { name: 'Revocation Check', passed: false, message: 'Credential has been revoked' },
    );
  } else if (state === 'NOT_FOUND') {
    checks.push(
      { name: 'Registry Lookup', passed: false, message: 'No record found for this identifier' },
    );
  } else {
    checks.push(
      { name: 'Extraction Review', passed: false, message: 'Extraction incomplete or uncertain; manual review required' },
    );
  }
  return checks;
}

export const verificationService = {
  async verifyById(rawId: string, channel: VerificationResult['channel'] = 'ID_LOOKUP'): Promise<VerificationResult> {
    try {
      const res = await fetch(`${API_BASE_URL}/verify`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ certificate_id: rawId.trim() }),
      });
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }
      const data: BackendVerifyResponse = await res.json();
      return buildResult(data, channel);
    } catch (err) {
      // Network error or backend down — fall back gracefully
      console.error('verifyById error:', err);
      return {
        state: 'NOT_FOUND',
        certificateId: rawId,
        timestamp: new Date().toISOString(),
        summaryMessage: 'Verification service unavailable. Please ensure the backend is running.',
        detailedMessage: String(err),
        checks: [{ name: 'Backend Connection', passed: false, message: 'Could not reach the verification service' }],
        channel,
      };
    }
  },

  async verifyUploadedFile(file: File): Promise<VerificationResult> {
    try {
      const formData = new FormData();
      formData.append('document', file);

      const res = await fetch(`${API_BASE_URL}/verification/verify-upload`, {
        method: 'POST',
        body: formData,
      });
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }
      const data: BackendVerifyResponse = await res.json();
      return buildResult(data, 'DOCUMENT_UPLOAD');
    } catch (err) {
      console.error('verifyUploadedFile error:', err);
      return {
        state: 'NOT_FOUND',
        certificateId: 'UPLOAD_ERROR',
        timestamp: new Date().toISOString(),
        summaryMessage: 'Document verification failed. Please ensure the backend is running.',
        detailedMessage: String(err),
        checks: [{ name: 'Backend Connection', passed: false, message: 'Could not reach the verification service' }],
        channel: 'DOCUMENT_UPLOAD',
      };
    }
  },
};
