import { useState } from 'react';
import { registerUser } from '../lib/api';
import { useUI } from '../lib/ui-context';
import PasswordVisibilityIcon from './PasswordVisibilityIcon';

function formatErrorValue(value) {
  if (Array.isArray(value)) {
    return value
      .map((item) => (typeof item === 'string' ? item : JSON.stringify(item)))
      .join('; ');
  }
  if (value && typeof value === 'object') {
    return Object.entries(value)
      .map(([key, innerValue]) => `${key}: ${formatErrorValue(innerValue)}`)
      .join('; ');
  }
  return String(value);
}

function parseApiErrorPayload(data) {
  if (data == null) return null;
  if (typeof data === 'string') return data;
  if (Array.isArray(data)) return data.map(formatErrorValue).join('; ');
  return Object.entries(data)
    .map(([key, value]) => `${key}: ${formatErrorValue(value)}`)
    .join('; ');
}

export default function Register({ setCurrentFeature }) {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [phoneNum, setPhoneNum] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [role, setRole] = useState('clinician');
  const [hospitalCode, setHospitalCode] = useState('');
  const [hospitalName, setHospitalName] = useState('');
  const [message, setMessage] = useState('');
  const [backendErrors, setBackendErrors] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);
  const { t } = useUI();

  const handleRegister = async () => {
    setMessage('');
    setBackendErrors(null);
    setIsSuccess(false);

    if (!username || !email || !password) {
      setMessage('Username, email and password are required.');
      return;
    }
    if (password !== confirmPassword) {
      setMessage('Password and confirm password must match.');
      return;
    }

    try {
      const payload = {
        username,
        email,
        password,
        first_name: firstName,
        last_name: lastName,
        phone_num: phoneNum,
        role,
        hospital_code: hospitalCode,
        hospital_name: hospitalName,
      };
      console.info('[Register] Submit', payload);
      setIsLoading(true);
      setBackendErrors(null);
      setIsSuccess(false);
      setMessage('');

      const response = await registerUser(payload);
      console.info('[Register] Response', response);

      setMessage('Registration successful. You can now login.');
      setIsSuccess(true);
      setUsername('');
      setEmail('');
      setFirstName('');
      setLastName('');
      setPhoneNum('');
      setPassword('');
      setConfirmPassword('');
      setHospitalCode('');
      setHospitalName('');
    } catch (error) {
      console.error('[Register] Registration failed', error);
      const details = error.data || null;
      setBackendErrors(details);
      setIsSuccess(false);
      setMessage(parseApiErrorPayload(details) || error.message || 'Registration failed.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <section>
      <h2>{t('register_title', 'User Registration')}</h2>
      <label>{t('username', 'Username')}</label><br />
      <input
        value={username}
        onChange={(e) => setUsername(e.target.value)}
        placeholder={t('username', 'Username')}
      /><br />
      <label>{t('email', 'Email')}</label><br />
      <input
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder={t('email', 'Email')}
      /><br />
      <label>{t('first_name', 'First Name')}</label><br />
      <input
        value={firstName}
        onChange={(e) => setFirstName(e.target.value)}
        placeholder={t('first_name', 'First Name')}
      /><br />
      <label>{t('last_name', 'Last Name')}</label><br />
      <input
        value={lastName}
        onChange={(e) => setLastName(e.target.value)}
        placeholder={t('last_name', 'Last Name')}
      /><br />
      <label>{t('phone_number', 'Phone Number')}</label><br />
      <input
        value={phoneNum}
        onChange={(e) => setPhoneNum(e.target.value)}
        placeholder={t('phone_number', 'Phone Number')}
      /><br />
      <label>{t('password', 'Password')}</label><br />
      <div className="passwordField">
        <div className="passwordFieldInput">
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
      <label>{t('confirm_password', 'Confirm Password')}</label><br />
      <div className="passwordField">
        <div className="passwordFieldInput">
          <input
            type={showConfirmPassword ? 'text' : 'password'}
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            placeholder={t('confirm_password', 'Confirm Password')}
          />
        </div>
        <button
          type="button"
          className="eyeBtn"
          onClick={() => setShowConfirmPassword((current) => !current)}
          aria-label={showConfirmPassword ? 'Hide confirm password' : 'Show confirm password'}
          title={showConfirmPassword ? 'Hide confirm password' : 'Show confirm password'}
        >
          <PasswordVisibilityIcon visible={showConfirmPassword} />
        </button>
      </div>
      <label>{t('role', 'Role')}</label><br />
      <select value={role} onChange={(e) => setRole(e.target.value)}>
        <option value="clinician">Clinician</option>
        <option value="radiologist">Radiologist</option>
        <option value="admin">Admin</option>
        <option value="auditor">Auditor</option>
      </select><br />
      <label>{t('hospital_code', 'Hospital Code')}</label><br />
      <input
        value={hospitalCode}
        onChange={(e) => setHospitalCode(e.target.value)}
        placeholder="Existing code, or new code for admin bootstrap"
      /><br />
      <label>{t('hospital_name', 'Hospital Name')}</label><br />
      <input
        value={hospitalName}
        onChange={(e) => setHospitalName(e.target.value)}
        placeholder="Hospital name"
      /><br />
      <div className="btnGroup">
        <button type="button" className="btn btn--primary" onClick={handleRegister} disabled={isLoading}>
          {isLoading ? t('registering', 'Registering...') : t('register', 'Register')}
        </button>
        <button type="button" className="btn btn--secondary" onClick={() => setCurrentFeature('auth')} disabled={isLoading}>
          {t('cancel', 'Cancel')}
        </button>
      </div>
      {message ? (
        <p className={isSuccess ? 'successMessage' : 'errorMessage'}>{message}</p>
      ) : null}
      {backendErrors ? (
        <div className="errorDetails" aria-live="polite">
          <strong>{t('validation_errors', 'Validation errors:')}</strong>
          <ul>
            {Object.entries(backendErrors).map(([key, value]) => (
              <li key={key}>{`${key}: ${formatErrorValue(value)}`}</li>
            ))}
          </ul>
        </div>
      ) : null}
    </section>
  );
}
