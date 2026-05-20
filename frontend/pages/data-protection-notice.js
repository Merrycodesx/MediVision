export default function DataProtectionNoticePage() {
  return (
    <main className="container">
      <section className="panel legalPagePanel">
        <h1>Data Protection Notice</h1>
        <p className="muted">Last Updated: May 2026</p>

        <p>
          MediVision recognizes the importance of protecting sensitive healthcare and
          patient-related data.
        </p>

        <h2 className="legalSectionTitle">Protection Measures</h2>
        <p>The platform is designed with security-focused features including:</p>
        <ul className="legalList">
          <li>Role-based access control</li>
          <li>Secure authentication</li>
          <li>Audit logging</li>
          <li>Controlled data access</li>
          <li>Encrypted communication where applicable</li>
        </ul>

        <h2 className="legalSectionTitle">Data Handling</h2>
        <p>
          All uploaded medical images, laboratory records, and clinical information should be
          handled in accordance with applicable healthcare privacy and ethical standards.
        </p>

        <h2 className="legalSectionTitle">Restricted Access</h2>
        <p>
          Access to sensitive data is limited to authorized users such as clinicians,
          administrators, and approved personnel.
        </p>

        <h2 className="legalSectionTitle">Research and Development Context</h2>
        <p>
          As MediVision is currently in a prototype and academic development phase, certain
          advanced compliance and regulatory protections may be expanded in future releases.
        </p>

        <h2 className="legalSectionTitle">Future Compliance Updates</h2>
        <p>
          Additional security policies, regulatory safeguards, and formal compliance procedures
          may be introduced as the platform progresses toward larger-scale deployment and
          evaluation.
        </p>
      </section>
    </main>
  );
}
