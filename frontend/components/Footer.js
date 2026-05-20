import React from "react";
import { useUI } from "../lib/ui-context";

export default function Footer({
  version = "v1.0.0",
  lastUpdated = "May 2026",
  copyrightOwner = "MediVision",
}) {
  const currentYear = 2026;
  const { t } = useUI();

  return (
    <footer className="siteFooter">
      

      <div className="footerCard">
        <div className="footerContent">
          <section aria-labelledby="footer-about-title" className="footerSection">
            <h3 id="footer-about-title">{t("footer_about", "About MediVision")}</h3>
            <p>
              AI-assisted tuberculosis screening and clinical decision support
              system.
            </p>
            <p>
              Supporting early detection in resource-constrained settings.
            </p>
          </section>

          <nav aria-label="Legal and policy links" className="footerSection">
            <h3>{t("footer_legal", "Legal & Policy")}</h3>
            <ul className="footerLinks">
              <li>
                <a href="/privacy-policy" className="footerLink">{t("privacy_policy", "Privacy Policy")}</a>
              </li>
              <li>
                <a href="/terms-of-use" className="footerLink">{t("terms_of_use", "Terms of Use")}</a>
              </li>
              <li>
                <a href="/data-protection-notice" className="footerLink">{t("data_protection_notice", "Data Protection Notice")}</a>
              </li>
              <li>
                <a href="/about-us" className="footerLink">{t("about_us", "About Us")}</a>
              </li>
            </ul>
          </nav>
        </div>

        <div className="footerBottom">
          <p>
            © {currentYear} {copyrightOwner}
          </p>
          <p>
            {version} • {lastUpdated}
          </p>
        </div>
      </div>
    </footer>
  );
}
