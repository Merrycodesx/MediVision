export default function PrivacyPolicyPage() {
  return (
    <main className="container">
      <section className="panel legalPagePanel">
        <h1>Privacy Policy</h1>
        <p className="muted">Last Updated: May 2026</p>

        <p>
          MediVision respects the privacy and confidentiality of all users and patient-related
          information. This platform is designed to support tuberculosis (TB) screening and
          clinical decision-making through AI-assisted analysis.
        </p>

        <h2 className="legalSectionTitle">Information We Collect</h2>
        <p>MediVision may collect:</p>
        <ul className="legalList">
          <li>Chest X-ray images</li>
          <li>Clinical and laboratory information</li>
          <li>User account information</li>
          <li>System usage and audit logs</li>
        </ul>
        <p>
          All data used within the platform is intended solely for healthcare support, research,
          and system improvement purposes.
        </p>

        <h2 className="legalSectionTitle">Data Usage</h2>
        <p>Collected information is used to:</p>
        <ul className="legalList">
          <li>Generate AI-assisted screening results</li>
          <li>Improve system performance and usability</li>
          <li>Support healthcare professionals during screening workflows</li>
          <li>Maintain system security and auditability</li>
        </ul>

        <h2 className="legalSectionTitle">Data Security</h2>
        <p>
          MediVision implements reasonable technical and organizational measures to protect stored
          information from unauthorized access, misuse, or disclosure.
        </p>

        <h2 className="legalSectionTitle">Confidentiality</h2>
        <p>
          Patient-related information should only be accessed by authorized healthcare personnel
          through role-based access control mechanisms.
        </p>

        <h2 className="legalSectionTitle">Limitations</h2>
        <p>
          MediVision is currently a prototype/research-stage system and not a fully certified
          medical product. Additional privacy, compliance, and regulatory updates may be
          introduced in future versions of the platform.
        </p>

        <h2 className="legalSectionTitle">Future Updates</h2>
        <p>
          This Privacy Policy may be updated as the system evolves, including future compliance
          improvements, deployment requirements, and regulatory standards.
        </p>
      </section>
    </main>
  );
}
