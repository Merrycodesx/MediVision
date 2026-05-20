import { useState } from 'react';
import { login, saveSession } from '../lib/api';
import { useUI } from '../lib/ui-context';
import PasswordVisibilityIcon from './PasswordVisibilityIcon';

export default function Auth({ setCurrentFeature }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [role, setRole] = useState('doctor');
  const [message, setMessage] = useState('');
  const { t } = useUI();

  const handleLogin = async () => {
    if (!email || !password || !role) {
      setMessage('Email, password, and role are required.');
      return;
    }
    setMessage('Logging in...');

    try {
      const data = await login(email, password, role);
      saveSession(data);
      setMessage(`Login successful${data.hospital_name ? ` at ${data.hospital_name}` : ''}.`);
      setCurrentFeature('patients');
    } catch (error) {
      console.error(error);
      setMessage(error.message || 'Login failed, check credentials.');
    }
  };

  return (
    <section className="authScreen">
      <article className="authCard">
        <div className="authHeader">
          <p className="authTitle">
            <img src="/icons/login-logo.png" alt="" className="authTitleLogo" />
            {t('app_title', 'MediVision Multimodal TB CAD')}
          </p>
          <p className="authSubtitle">{t('app_subtitle', 'AI-powered Tuberculosis Diagnosis System')}</p>
        </div>

        <h2 className="authSectionTitle">{t('login_title', 'Login')}</h2>

        <label className="authLabel">{t('email', 'Email')}</label>
        <div className="inputWithIcon">
          <svg viewBox="0 0 24 24" className="fieldIcon" aria-hidden="true">
            <path d="M3 6h18v12H3z" />
            <path d="m4 7 8 6 8-6" />
          </svg>
          <input
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder={t('email', 'Email')}
          />
        </div>

        <label className="authLabel">{t('password', 'Password')}</label>
        <div className="passwordField">
          <div className="passwordFieldInput inputWithIcon">
            <svg viewBox="0 0 24 24" className="fieldIcon" aria-hidden="true">
              <rect x="5" y="10" width="14" height="10" rx="2" />
              <path d="M8 10V8a4 4 0 1 1 8 0v2" />
            </svg>
            <input
              type={showPassword ? 'text' : 'password'}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder={t('password', 'Password')}
            />
          </div>
          <button
            type="button"
            className="eyeBtn"
            onClick={() => setShowPassword((current) => !current)}
            aria-label={showPassword ? 'Hide password' : 'Show password'}
            title={showPassword ? 'Hide password' : 'Show password'}
          >
            <PasswordVisibilityIcon visible={showPassword} />
          </button>
        </div>

        <label className="authLabel">{t('login_as', 'Login as')}</label>
        <select className="authSelect" value={role} onChange={(e) => setRole(e.target.value)}>
          <option value="doctor">Doctor</option>
          <option value="clinician">Clinician</option>
          <option value="radiologist">Radiologist</option>
          <option value="admin">Admin</option>
          <option value="auditor">Auditor</option>
        </select>

        <div className="authActions">
          <button type="button" className="btn btn--primary authPrimaryBtn" onClick={handleLogin}>{t('login', 'Login')}</button>
          <button type="button" className="btn btn--secondary authSecondaryBtn" onClick={() => setCurrentFeature('register')}>{t('register', 'Register')}</button>
        </div>

        {message && <p className="message authMessage">{message}</p>}
        <p className="authFooter">Secure medical system • Authorized access only</p>
      </article>
    </section>
  );
}
