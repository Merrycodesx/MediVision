import React from "react";
import { useUI } from "../lib/ui-context";

export default function AppHeader({ canGoBack, onBack, transparent, variant }) {
  const {
    language,
    setLanguage,
    fontFamily,
    setFontFamily,
    fontSize,
    setFontSize,
    t,
  } = useUI();

  const variantClass = variant === 'onImage' ? ' appTopBar--onImage' : '';

  return (
    <header className={`appTopBar${transparent ? ' appTopBar--transparent' : ''}${variantClass}`}>
      {canGoBack ? (
        <button type="button" className="backTopBtn" onClick={onBack}>
          {t("back", "Back")}
        </button>
      ) : (
        <span className="appTopBarSpacer" aria-hidden="true" />
      )}

      <div className="appTopControls">
        <label>{t("language", "Language")}</label>
        <select value={language} onChange={(e) => setLanguage(e.target.value)}>
          <option value="English">English</option>
          <option value="Amharic">Amharic</option>
        </select>

        <label>{t("font", "Font")}</label>
        <select value={fontFamily} onChange={(e) => setFontFamily(e.target.value)}>
          <option value="Segoe UI">Segoe UI</option>
          <option value="Nyala">Nyala</option>
          <option value="Noto Sans Ethiopic">Noto Sans Ethiopic</option>
          <option value="Arial">Arial</option>
        </select>

        <label>{t("size", "Size")}</label>
        <select value={String(fontSize)} onChange={(e) => setFontSize(Number(e.target.value))}>
          {Array.from({ length: 13 }, (_, i) => 12 + i).map((size) => (
            <option key={size} value={String(size)}>
              {size}
            </option>
          ))}
        </select>
      </div>
    </header>
  );
}
