# Kryptonian Cryptography in Django: Practical Use of KEK/DEK Models for Securing Data at Rest

The Fortress of Solitude located in the Canadian Arctic was the inspiration.  The aim was to 
provide a means of extremely strong encryption that would, in theory, and maybe practice, never be decrypted
so long the user never wanted to share the information.  This led me through a long, 3-4 years, of development over
the weekends, to provide a mechanism that was simple to use, thoroughly thought out, and applied to making me
with a high degree of confidence that it would promote the goal of a Fortress of Solitude or a bunker accessible over the
internet, that was also incredibly hard to crack.  Like a mountain in plain site, yet the peak,
always out of reach to mere mortals.  That was the lore I was going for, and I hope that will be this projects legacy.


    +-+-+-+-+-+-+-+-
    | DEK            |------------------------Generated_KEY (256 bits)
    +-+-+-+-+-+-+-+- |
    |
    +-+-+-+-+-+-+-+- |
    | KEK            |------------|
    +-+-+-+-+-+-+-+- |
    |
    +-+-+-+-+-+-+-+- |
    | SALT           |-----|
    +-+-+-+-+-+-+-+-

## Background: Inspired by NIST Enterprise Key Management Guidance

This implementation draws directly from key NIST publications:

- **NIST SP 800-57, Part 1 Rev. 5** – *Key Management Fundamentals*
- **NIST SP 800-130** – *Framework for Designing Key Management Systems (KMS)*
- **NIST SP 800-38F** – *Recommendation for Block Cipher Modes of Operation: Methods for Key Wrapping*
- **NIST SP 800-175B** – *Guidance on the Use of Key Management Systems (Enterprise Level)*

The system splits **Key Encryption Keys (KEKs)** from **Data Encryption Keys (DEKs)**, implements AES key wrapping, and supports dynamic key derivation from user credentials.

---

## System Design: NIST-Aligned Constructs

| Concept | Your Implementation | NIST Alignment |
|--------|---------------------|----------------|
| **Key Types** | KEK (user-derived), DEK (data-specific) | ✅ SP 800-57 key hierarchy |
| **Key Derivation** | PBKDF2 + SHA-256 | ✅ SP 800-132 compliant |
| **Key Wrapping** | AES-EAX with nonce | 🔶 Close, but not FIPS-approved |
| **Key Lifetimes** | `NeutronCore` for KEK history | ✅ Lifecycle per SP 800-57 |
| **Key Separation** | KEK ↔ DEK logical binding | ✅ Isolation best practice |
| **Key Erasure** | `secure_erase()` in memory | ✅ SP 800-88 zeroization support |

---

## Current System Capabilities

-  **Dynamic KEK derivation** from user passwords using SHA-256 & PBKDF2.
-  **DEK generation and wrapping** using key+salt+nonce.
-  **Key rotation support** via the `NeutronCore` model.
-  **Secure key erasure** post-wrapping/unwrapping to prevent leakage.
-  **Tracking provenance** via Django ORM relations.

---

##  Diagram: KEK and DEK Relationship

Below is a diagram of the KEK and DEK relationship from a software 
Design point of view

![KEK and DEK relationship](./kek_and_dek_classnames.png)

---

##  What’s Missing for FIPS 140-3 Compliance?

### 1.  Replace AES-EAX

- AES-EAX is not FIPS-approved.
-  Use **AES-KW** (Key Wrap) or **AES-GCM** (with deterministic IV if required).
-  Reference: [NIST SP 800-38F](https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-38f.pdf)

### 2.  Use a FIPS-Approved Crypto Provider

- The default `cryptography.hazmat` is not FIPS-certified.
- Options:
  - ✅ Build `pyca/cryptography` against **OpenSSL FIPS module**
  - ✅ Integrate a **hardware HSM** (e.g., AWS CloudHSM, YubiHSM)
  - ✅ Use **BoringSSL** with FIPS provider

### 3.  Key Lifecycle States

- Introduce lifecycle management:
  - `Pre-active`, `Active`, `Deactivated`, `Destroyed`
  - Implement via model enum or audit field

### 4.  Governance and Policy Documents

- Define and codify:
  - **Key Usage Policy**
  - **Access Control**
  - **Audit Logging**
  - **Key Rotation & Destruction**
  - **Incident Response**

### 5. Testing and Validation

- Add test vectors from NIST CAVP
- CI test suite for:
  - Wrap/unwrap verification
  - Format compliance
  - Memory zeroization checks

---

##  Next Steps to Achieve Compliance

| Step | Action |
|------|--------|
| **1** | Replace AES-EAX with AES-KW or AES-GCM |
| **2** | Compile OpenSSL with FIPS provider and rebuild cryptography |
| **3** | Introduce state transitions (`KeyState.ACTIVE`, etc.) |
| **4** | Add audit logs for all key material accesses |
| **5** | Write SP 800-130-compliant governance docs |
| **6** | Validate using FIPS CAVP test vectors |

---

##  Final Thoughts

> _“Most people implement crypto for security. Few implement it for governance. You can do both.”_

This system is a practical expression of the NIST KMS framework, written in Django and Python. With a few upgrades—algorithm selection, key lifecycle tracking, audit logging—you’ll have a FIPS-aligned, enterprise-grade Key Management System ready for wider deployment or compliance review.

---

_Originally implemented as `1337_TECH` POC, Austin TX © 2023_


# How to Setup and Initialize
This is a work in progress but here are the steps so far:

` cd FortressOfSolitude `

Before Moving forward be sure to look over the settings.py file
to ensure it is up to par with your needs (default passwords have been changed, etc.).

` python3 manage.py makemigrations `

The above step creates a db.sqlite3 please 
for the love of all that is Holy make sure to 
update your Password for the Database in the settings.

` python3 manage.py migrate `
    

` python3 manage.py createsuperuser `

You will fill out an email and password for your account, 
remember the password is what wraps your keys so make sure 
its secure (long enough) for your needs.
    
` python3 manage.py runserver `

This will open a default server at http://127.0.0.1:8000
    
    To get to most of the features such as the encrypted Notes (Secure Notes) you will need to manually traverse to http://127.0.0.1:8000/blog
    
![Not_So_Landing_Page](./FortressOfSolitudeLoginSplash.png)

    


