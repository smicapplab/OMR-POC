# 🎯 OMR-PROD: Enterprise Optical Mark Recognition System

[![Architecture: Distributed](https://img.shields.io/badge/Architecture-Distributed_Edge--to--Cloud-blue)](https://github.com/)
[![Security: AES-256](https://img.shields.io/badge/Security-AES--256_Encrypted-green)](https://github.com/)
[![Privacy: AWS_KMS](https://img.shields.io/badge/Privacy-AWS_KMS_Field_Level-orange)](https://github.com/)

## 📌 Executive Summary
**OMR-PROD** is an enterprise-grade, multi-tenant Optical Mark Recognition system engineered for high-stakes government and college entrance examinations. Unlike traditional OMR solutions, OMR-PROD is built for **forensic accountability**. It ensures that every student's answer is captured, signed, and preserved in a manner that is mathematically provable and legally defensible, even in environments with intermittent internet connectivity.

---

## 🏗 System Architecture

The system utilizes a **Symmetric Monorepo** architecture, separating the high-performance local ingestion engine from the scalable central administration hub.

### 1. The Edge Appliance (Local School Site)
Designed to run on local hardware (macOS M4 Mini / Linux) to ensure zero-latency scanning and data capture.
*   **OMR Engine:** Built on Python 3.11 and OpenCV. Features advanced deskewing, fiducial marker alignment, and circular-masking bubble detection.
*   **Local Persistence:** Uses **SQLCipher** (AES-256 encrypted SQLite) to prevent unauthorized local access to exam data.
*   **Edge Console:** A static Next.js frontend that allows operators to manage the scan queue, verify image quality, and monitor sync status without exposing exam scores.
*   **Hardware Integrity:** Each machine is bound to a unique cryptographic identity (mTLS/Signed JWT).

### 2. The Cloud Hub (National Administration)
A serverless architecture designed for massive concurrency during peak exam seasons.
*   **Orchestration Layer:** NestJS (TypeScript) deployed via AWS Lambda.
*   **Relational Engine:** Supabase (Postgres) with **Row Level Security (RLS)** for strict multi-tenant school isolation.
*   **Asset Management:** AWS S3 with **Object Lock (WORM)** technology.
*   **Identity Provider:** Custom Auth (based on HRIS enterprise standards) with rotating `HttpOnly` refresh tokens.

---

## 🔐 Security & Forensic Integrity

The system's "Vault" security model is designed to survive technical audits and legal challenges.

### 1. Chain of Custody (Digital Signatures)
*   **At-Source Hashing:** The moment a scan is processed at the edge, a **SHA-256 hash** is generated for the raw image.
*   **Cryptographic Signing:** The hash, student LRN, and timestamp are signed using the machine's private key.
*   **Verification:** The Cloud API validates this signature upon arrival. If a single pixel in the image or a single digit in the score is modified locally, the cloud will reject the record as "Tampered."

### 2. Privacy & PII (AWS KMS)
*   **Zero-Knowledge Storage:** Personally Identifiable Information (PII), such as Student Names, is encrypted using **AWS KMS** before it leaves the school's local network.
*   **Field-Level Encryption:** The database stores names as encrypted blobs. Decryption only occurs in the memory of the NestJS Lambda during an authorized session, meaning even a database breach would not leak student identities.

### 3. Multi-Tenant School Isolation
*   **RLS Enforcement:** Security is not handled in the application code alone. Postgres **Row Level Security (RLS)** ensures that employees from "School A" are mathematically blocked from querying or seeing data from "School B."

### 4. Forensic Evidence (Object Lock)
*   **Immutability:** High-resolution masters are stored with **WORM (Write Once, Read Many)** policies. This prevents deletion or modification by any user—including administrators—for a set legal retention period (e.g., 5 years).

---

## 📡 Resilience: The Sync Engine

To handle regional connectivity issues, OMR-PROD utilizes a **Store-and-Forward** sync strategy:

*   **Dual-Asset Upload:**
    1.  **Immediate:** Syncs JSON scores and a lightweight **WebP Proxy** (~1.5MB) for instant cloud review.
    2.  **Background:** Syncs the **Full PNG Master** (~27MB) using S3 Multipart Uploads with automatic resume capability.
*   **Conflict Resolution:** Uses a "Vector Clock" approach to ensure the machine's local state and the cloud's state are always synchronized without data loss.

---

## 📂 Project Structure

```text
OMR-PROD/
├── apps/
│   ├── web-cloud/      # Next.js: National Admin & School Portals
│   ├── web-edge/       # Next.js: Local School Scanning Console
│   ├── api-cloud/      # NestJS: Central API (Auth, KMS, Reporting)
│   └── api-edge/       # Python: OMR Engine, FastAPI & Sync Agent
├── packages/
│   ├── database/       # Drizzle: Unified schemas (Postgres + SQLite)
│   ├── contracts/      # Zod: Shared Sync & API Contracts (Single Source of Truth)
│   ├── ui/             # React: Shared Shadcn/UI component library
│   └── config/         # Standardized TS, ESLint, and Prettier rules
└── supabase/           # SQL: Row Level Security (RLS) policies & migrations
```

---

## 🛠 Technology Stack Rationale

| Tech | Choice | Rationale |
| :--- | :--- | :--- |
| **Monorepo** | Turborepo | Maintains type-safety across Python, TypeScript, and Edge/Cloud apps. |
| **API** | NestJS | Proven enterprise-grade dependency injection and middleware. |
| **Logic** | Python | Industry-standard libraries for Computer Vision (OpenCV) and OMR. |
| **Database** | Postgres | Advanced relational capabilities for multi-tenant querying and RLS. |
| **ORM** | Drizzle | Headless, type-safe, and supports both PG (Cloud) and SQLite (Edge). |
| **Styling** | Shadcn/UI | Modern, accessible, and easily themeable for school-specific branding. |

---

## 📑 Compliance & Audit
OMR-PROD maintains an **Immutable Audit Log**. Every manual change to a score (e.g., after a student dispute) is recorded with:
*   Original Machine Score
*   User ID of the Reviewer
*   Timestamp & IP Address
*   Justification Code
*   Digital Signature of the Edit

---

## 🚀 Future Roadmap
- [ ] Template Versioning (Support for multiple answer sheet layouts).
- [ ] Over-the-Air (OTA) Updates for Edge Appliances.
- [ ] Student Self-Service Portal with secure result verification.
- [ ] AI-assisted smudge and double-mark detection.

---
© 2026 OMR-PROD Enterprise. Proprietary and Confidential.
