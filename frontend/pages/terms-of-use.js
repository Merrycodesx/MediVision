export default function TermsOfUsePage() {
  return (
    <main className="container">
      <section className="panel legalPagePanel">
        <h1>Terms of Use</h1>
        <p className="muted">Last Updated: May 2026</p>

        <p>
          By accessing or using MediVision, users agree to the following terms and conditions.
        </p>

        <h2 className="legalSectionTitle">Intended Use</h2>
        <p>
          MediVision is an AI-assisted tuberculosis screening and clinical decision support system
          intended to support healthcare professionals during screening and triage processes.
        </p>

        <h2 className="legalSectionTitle">No Replacement for Medical Judgment</h2>
        <p>
          MediVision does not replace professional medical diagnosis, clinical expertise, or
          physician decision-making. Final clinical decisions remain the responsibility of
          qualified healthcare providers.
        </p>

        <h2 className="legalSectionTitle">Authorized Usage</h2>
        <p>
          Users must use the platform responsibly and only for authorized healthcare, research, or
          educational purposes.
        </p>

        <h2 className="legalSectionTitle">System Availability</h2>
        <p>
          While efforts are made to ensure reliability, MediVision does not guarantee uninterrupted
          service, complete accuracy, or continuous availability.
        </p>

        <h2 className="legalSectionTitle">User Responsibilities</h2>
        <p>Users are responsible for:</p>
        <ul className="legalList">
          <li>Maintaining account confidentiality</li>
          <li>Protecting patient information</li>
          <li>Using accurate clinical data</li>
          <li>Following institutional and ethical guidelines</li>
        </ul>

        <h2 className="legalSectionTitle">Prototype Disclaimer</h2>
        <p>
          This platform is currently developed as part of a research and academic project.
          Features, workflows, and policies may evolve in future versions.
        </p>

        <h2 className="legalSectionTitle">Future Modifications</h2>
        <p>
          MediVision reserves the right to update system functionality, policies, and terms as the
          platform continues to develop.
        </p>
      </section>
    </main>
  );
}
