export default function UserManagement({ setCurrentFeature }) {
  return (
    <section>
      <h2>User Management</h2>
      <p>Use the server API for user management.</p>
      <button onClick={() => setCurrentFeature('patients')}>Back</button>
    </section>
  );
}