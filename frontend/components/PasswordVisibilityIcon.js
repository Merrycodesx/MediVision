/**
 * @param {{ visible: boolean }} props - `visible` true when password text is shown
 */
export default function PasswordVisibilityIcon({ visible }) {
  if (visible) {
    return (
      <svg className="eyeIconSvg" viewBox="0 0 24 24" aria-hidden="true">
        <path d="M1.5 12s3.8-6 10.5-6 10.5 6 10.5 6-3.8 6-10.5 6S1.5 12 1.5 12Z" />
        <circle cx="12" cy="12" r="3.2" />
      </svg>
    );
  }

  return (
    <svg className="eyeIconSvg eyeIconSvg--off" viewBox="0 0 24 24" aria-hidden="true">
      <path d="M1.5 12s3.8-6 10.5-6 10.5 6 10.5 6-3.8 6-10.5 6S1.5 12 1.5 12Z" />
      <circle cx="12" cy="12" r="3.2" />
      <path d="M3 3l18 18" strokeLinecap="round" />
    </svg>
  );
}
