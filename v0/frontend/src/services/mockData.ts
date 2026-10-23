import { Credential, AuditEvent, VerificationHistoryItem, User } from '../types';

export const MOCK_INSTITUTION_USER: User = {
  id: 'usr_inst_001',
  name: 'Dr. Arthur Pendelton',
  email: 'registrar@westminster.edu',
  role: 'institution',
  institutionId: 'inst_wsu_01',
  institutionName: 'Westminster State University',
  avatarUrl: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&q=80&w=256'
};

export const MOCK_STUDENT_USER: User = {
  id: 'usr_stu_001',
  name: 'Ananya Patil',
  email: 'ananya.patil@alumni.westminster.edu',
  role: 'student',
  studentId: 'STU-2024-89042',
  institutionName: 'Westminster State University',
  avatarUrl: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&q=80&w=256'
};

export const INITIAL_CREDENTIALS: Credential[] = [
  {
    id: 'CC-2024-89042-ENG',
    studentName: 'Ananya Patil',
    studentRoll: 'WSU-2020-CS-042',
    studentEmail: 'ananya.patil@alumni.westminster.edu',
    course: 'Bachelor of Technology in Artificial Intelligence',
    degreeType: 'Undergraduate Degree',
    institution: 'Westminster State University',
    institutionId: 'inst_wsu_01',
    issueDate: '2024-05-24',
    conferralDate: '2024-06-15',
    batch: 'Class of 2024',
    grade: 'First Class with Distinction',
    cgpa: '3.92 / 4.00',
    status: 'ACTIVE',
    sha256Hash: 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
    merkleRoot: '7d159a68bc2a342a78d067c26279f57ebbf7940e4f5cdbbfaad5b412bf2be822',
    merkleLeafIndex: 42,
    qrCodeUrl: 'https://api.qrserver.com/v1/create-qr-code/?size=180x180&data=https://chaincert.org/verify?id=CC-2024-89042-ENG',
    metadata: {
      facultyDean: 'Prof. Jonathan Vance, Ph.D.',
      registrarSignature: 'Dr. Arthur Pendelton',
      accreditationBody: 'Higher Learning Commission (HLC)',
      creditsCompleted: 148
    }
  },
  {
    id: 'CC-2024-89043-ENG',
    studentName: 'Ananya Patil',
    studentRoll: 'WSU-2020-CS-042',
    studentEmail: 'ananya.patil@alumni.westminster.edu',
    course: 'Honors Specialization in Distributed Machine Learning',
    degreeType: 'Academic Certificate of Specialization',
    institution: 'Westminster State University',
    institutionId: 'inst_wsu_01',
    issueDate: '2024-05-20',
    conferralDate: '2024-05-24',
    batch: 'Class of 2024',
    grade: 'A+ (Distinction)',
    cgpa: '4.00 / 4.00',
    status: 'ACTIVE',
    sha256Hash: '8f434346648f6b96df89dda901c5176b10a6d83961dd3c1ac88b59b2dc327aa4',
    merkleRoot: '7d159a68bc2a342a78d067c26279f57ebbf7940e4f5cdbbfaad5b412bf2be822',
    merkleLeafIndex: 43,
    qrCodeUrl: 'https://api.qrserver.com/v1/create-qr-code/?size=180x180&data=https://chaincert.org/verify?id=CC-2024-89043-ENG',
    metadata: {
      facultyDean: 'Prof. Jonathan Vance, Ph.D.',
      registrarSignature: 'Dr. Arthur Pendelton',
      accreditationBody: 'Higher Learning Commission (HLC)',
      creditsCompleted: 24
    }
  },
  {
    id: 'CC-2024-78103-CS',
    studentName: 'Marcus Vance',
    studentRoll: 'WSU-2022-MS-103',
    studentEmail: 'marcus.vance@westminster.edu',
    course: 'Master of Science in Computer Science',
    degreeType: 'Graduate Degree',
    institution: 'Westminster State University',
    institutionId: 'inst_wsu_01',
    issueDate: '2024-06-10',
    conferralDate: '2024-06-15',
    batch: 'Class of 2024',
    grade: 'High Honors',
    cgpa: '3.96 / 4.00',
    status: 'ACTIVE',
    sha256Hash: 'b5a2c94f298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852c91',
    merkleRoot: '7d159a68bc2a342a78d067c26279f57ebbf7940e4f5cdbbfaad5b412bf2be822',
    merkleLeafIndex: 12,
    qrCodeUrl: 'https://api.qrserver.com/v1/create-qr-code/?size=180x180&data=https://chaincert.org/verify?id=CC-2024-78103-CS'
  },
  {
    id: 'CC-2023-44102-BIO',
    studentName: 'Elena Rostova',
    studentRoll: 'WSU-2019-BIO-088',
    course: 'Bachelor of Science in Molecular Biochemistry',
    degreeType: 'Undergraduate Degree',
    institution: 'Westminster State University',
    institutionId: 'inst_wsu_01',
    issueDate: '2023-05-18',
    conferralDate: '2023-06-01',
    batch: 'Class of 2023',
    grade: 'Magna Cum Laude',
    cgpa: '3.88 / 4.00',
    status: 'ACTIVE',
    sha256Hash: '4a6b291c98fc1c149afbf4c8996fb92427ae41e4649b934ca495991b785211ee',
    merkleRoot: '9c218a55bc2a342a78d067c26279f57ebbf7940e4f5cdbbfaad5b412bf2bf333',
    merkleLeafIndex: 88,
    qrCodeUrl: 'https://api.qrserver.com/v1/create-qr-code/?size=180x180&data=https://chaincert.org/verify?id=CC-2023-44102-BIO'
  },
  {
    id: 'CC-2024-99211-LAW',
    studentName: 'Dev Patel',
    studentRoll: 'WSU-2021-JD-019',
    course: 'Juris Doctor in Comparative Corporate Law',
    degreeType: 'Professional Doctorate',
    institution: 'Westminster State University',
    institutionId: 'inst_wsu_01',
    issueDate: '2024-05-12',
    conferralDate: '2024-05-12',
    batch: 'Class of 2024',
    grade: 'Conferred',
    cgpa: '3.40 / 4.00',
    status: 'REVOKED',
    revocationReason: 'Conferral revoked pursuant to Academic Ethics & Integrity Board Resolution #2024-R49 (Transcript Irregularity).',
    revokedAt: '2024-07-02T14:30:00Z',
    revokedBy: 'Academic Ethics & Integrity Board, Registrar Dr. Pendelton',
    sha256Hash: '7f99120a298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b785299ff',
    merkleRoot: '7d159a68bc2a342a78d067c26279f57ebbf7940e4f5cdbbfaad5b412bf2be822',
    merkleLeafIndex: 19,
    qrCodeUrl: 'https://api.qrserver.com/v1/create-qr-code/?size=180x180&data=https://chaincert.org/verify?id=CC-2024-99211-LAW'
  },
  {
    id: 'CC-2024-55120-MED',
    studentName: 'Priya Sharma',
    studentRoll: 'WSU-2020-MD-007',
    course: 'Doctor of Medicine (Clinical Cardiology)',
    degreeType: 'Professional Doctorate',
    institution: 'Westminster State University',
    institutionId: 'inst_wsu_01',
    issueDate: '2024-05-30',
    batch: 'Class of 2024',
    grade: 'Under Review',
    cgpa: '3.85 / 4.00',
    status: 'REVIEW_REQUIRED',
    sha256Hash: '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8',
    merkleRoot: '7d159a68bc2a342a78d067c26279f57ebbf7940e4f5cdbbfaad5b412bf2be822',
    merkleLeafIndex: 7,
    qrCodeUrl: 'https://api.qrserver.com/v1/create-qr-code/?size=180x180&data=https://chaincert.org/verify?id=CC-2024-55120-MED'
  }
];

export const INITIAL_AUDIT_EVENTS: AuditEvent[] = [
  {
    id: 'AUD-8921',
    eventType: 'CREDENTIAL_ISSUED',
    actor: 'Dr. Arthur Pendelton',
    actorRole: 'Chief Registrar',
    targetCertificateId: 'CC-2024-89042-ENG',
    hash: 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
    timestamp: '2024-05-24 16:22:10 UTC',
    status: 'VERIFIED',
    details: 'B.Tech in Artificial Intelligence conferred to Ananya Patil'
  },
  {
    id: 'AUD-8920',
    eventType: 'BATCH_ISSUANCE',
    actor: 'Sarah Jenkins',
    actorRole: 'Associate Registrar',
    targetCertificateId: 'BATCH-2024-ENG-04',
    hash: '7d159a68bc2a342a78d067c26279f57ebbf7940e4f5cdbbfaad5b412bf2be822',
    timestamp: '2024-05-24 14:10:05 UTC',
    status: 'VERIFIED',
    details: 'Batch issuance of 142 School of Engineering degree certificates'
  },
  {
    id: 'AUD-8899',
    eventType: 'RECORD_CORRECTED',
    actor: 'Dr. Arthur Pendelton',
    actorRole: 'Chief Registrar',
    targetCertificateId: 'CC-2024-78103-CS',
    hash: 'b5a2c94f298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852c91',
    timestamp: '2024-06-11 09:14:22 UTC',
    status: 'RECORDED',
    details: 'Typographical correction in student middle name'
  },
  {
    id: 'AUD-8742',
    eventType: 'CREDENTIAL_REVOKED',
    actor: 'Academic Ethics Board',
    actorRole: 'Executive Committee',
    targetCertificateId: 'CC-2024-99211-LAW',
    hash: '7f99120a298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b785299ff',
    timestamp: '2024-07-02 14:30:00 UTC',
    status: 'FLAGGED',
    details: 'Revocation published pursuant to resolution #2024-R49'
  },
  {
    id: 'AUD-8610',
    eventType: 'INTEGRITY_CHECK_PASSED',
    actor: 'ChainCert Daemon',
    actorRole: 'Automated Cryptographic Validator',
    targetCertificateId: 'REGISTRY-WSU-ROOT',
    hash: 'e89c0245a4401bb26a79899f12d8a1e2f9801ac0e5d89f76a5200388124efb44',
    timestamp: '2024-10-20 04:00:00 UTC',
    status: 'VERIFIED',
    details: 'Daily Merkle tree cryptographic integrity check: 100% of 1,280 certificates verified intact'
  }
];

export const INITIAL_VERIFICATION_HISTORY: VerificationHistoryItem[] = [
  {
    id: 'VRF-4902',
    requester: 'Deloitte Global Talent Acquisition',
    queryId: 'CC-2024-89042-ENG',
    result: 'GENUINE',
    verifiedAt: '2024-10-20 15:42:10 UTC',
    channel: 'Public Portal (QR Scan)'
  },
  {
    id: 'VRF-4901',
    requester: 'Amazon AWS Admissions & Background',
    queryId: 'CC-2024-78103-CS',
    result: 'GENUINE',
    verifiedAt: '2024-10-20 14:18:04 UTC',
    channel: 'ID Lookup API'
  },
  {
    id: 'VRF-4888',
    requester: 'Bar Council Legal Accreditation',
    queryId: 'CC-2024-99211-LAW',
    result: 'REVOKED',
    verifiedAt: '2024-10-19 11:05:40 UTC',
    channel: 'Direct URL Query'
  },
  {
    id: 'VRF-4872',
    requester: 'Public Employer Verification Portal',
    queryId: 'CC-2024-55120-MED',
    result: 'REVIEW_REQUIRED',
    verifiedAt: '2024-10-18 09:32:15 UTC',
    channel: 'Document Upload (PDF)'
  },
  {
    id: 'VRF-4850',
    requester: 'Anonymous Verifier',
    queryId: 'CC-9999-00000-FAKE',
    result: 'NOT_FOUND',
    verifiedAt: '2024-10-17 18:20:00 UTC',
    channel: 'ID Lookup'
  }
];
