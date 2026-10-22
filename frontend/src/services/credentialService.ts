import { Credential } from '../types';
import { apiRequest } from './apiConfig';

// ---------------------------------------------------------------------------
// Backend certificate record shape
// ---------------------------------------------------------------------------
interface BackendCert {
  certificate_id: string;
  student_name?: string;
  roll_number?: string;
  course?: string;
  cgpa?: string;
  issue_date?: string;
  institution_id?: string;
  certificate_hash?: string;
  merkle_root?: string;
  merkle_leaf_index?: number;
  batch_id?: string;
  status?: string;
  revocation_reason?: string;
  revoked_at?: string;
}

function mapCert(r: BackendCert): Credential {
  const status = (r.status?.toUpperCase() ?? 'ACTIVE') as Credential['status'];
  return {
    id: r.certificate_id,
    studentName: r.student_name ?? '',
    studentRoll: r.roll_number ?? '',
    course: r.course ?? '',
    degreeType: 'Academic Degree',
    institution: r.institution_id ?? '',
    institutionId: r.institution_id ?? '',
    issueDate: r.issue_date ?? '',
    batch: r.batch_id ?? '',
    grade: '',
    cgpa: r.cgpa,
    status: ['ACTIVE', 'CONFERRED', 'REVOKED', 'REVIEW_REQUIRED'].includes(status) ? status : 'ACTIVE',
    sha256Hash: r.certificate_hash ?? '',
    merkleRoot: r.merkle_root ?? '',
    merkleLeafIndex: r.merkle_leaf_index,
    revocationReason: r.revocation_reason,
    revokedAt: r.revoked_at,
    qrCodeUrl: `https://api.qrserver.com/v1/create-qr-code/?size=180x180&data=${encodeURIComponent(
      `${window.location.origin}/verify?id=${encodeURIComponent(r.certificate_id)}`
    )}`,
  };
}

export const credentialService = {
  async getAll(): Promise<Credential[]> {
    try {
      const data = await apiRequest<{ certificates: BackendCert[] }>('/certificates');
      return (data.certificates ?? []).map(mapCert);
    } catch (err) {
      console.warn('credentialService.getAll failed, using empty list:', err);
      return [];
    }
  },

  async getById(id: string): Promise<Credential | null> {
    try {
      const data = await apiRequest<{ certificate: BackendCert }>(`/certificates/${encodeURIComponent(id)}`);
      return data.certificate ? mapCert(data.certificate) : null;
    } catch {
      return null;
    }
  },

  async register(newCred: {
    id: string;
    studentName: string;
    studentRoll: string;
    course: string;
    issueDate: string;
    institution: string;
    cgpa?: string;
  }): Promise<Credential> {
    const payload = {
      certificate: {
        certificate_id: newCred.id,
        student_name: newCred.studentName,
        roll_number: newCred.studentRoll,
        course: newCred.course,
        cgpa: newCred.cgpa ?? '',
        issue_date: newCred.issueDate,
        institution_id: newCred.institution,
      },
    };
    const data = await apiRequest<{ certificate: BackendCert }>('/certificates', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
    return mapCert(data.certificate);
  },

  async revoke(id: string, reason: string): Promise<Credential> {
    await apiRequest<unknown>(`/certificates/${encodeURIComponent(id)}/revoke`, {
      method: 'POST',
      body: JSON.stringify({ reason }),
    });
    // Fetch updated record
    const updated = await this.getById(id);
    if (!updated) throw new Error('Certificate not found after revoke');
    return updated;
  },

  // The backend does not expose a PATCH endpoint; return the merged object locally.
  async update(id: string, updates: Partial<Credential>): Promise<Credential> {
    console.warn('credentialService.update: no backend endpoint; changes are display-only.', id, updates);
    const existing = await this.getById(id);
    if (!existing) throw new Error('Certificate not found');
    return { ...existing, ...updates };
  },

  // Bulk issuance is not supported by the backend API; kept as no-op placeholder.
  async processBulkIssuance(_batch: unknown): Promise<{ issuedCount: number; batchId: string }> {
    throw new Error('Bulk issuance is not implemented by the backend API.');
  },
};
