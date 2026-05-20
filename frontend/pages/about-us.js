const TEAM_MEMBERS = [
  { no: 1, name: 'Bealprasim Demere', id: 'UGR/25540/14' },
  { no: 2, name: 'Meron Bahiru', id: 'UGR/25880/14' },
  { no: 3, name: 'Mhiret Lealem', id: 'UGR/25335/14' },
  { no: 4, name: 'Abel Alemayehu', id: 'UGR/25383/14' },
  { no: 5, name: 'Kalkidan Yalew', id: 'UGR/25325/14' },
];

export default function AboutUsPage() {
  return (
    <main className="container">
      <section className="panel aboutUsPanel">
        <h1>About Us</h1>
        <p className="muted">MediVision — Adama Science and Technology University</p>

        <p className="aboutUsIntro">
          We are students of Adama Science and Technology University in the School of Electrical
          Engineering and Computing in the Department of Computer Science and Engineering. The
          information found in this project is our original work. And all sources of materials that
          will be used for the project work will be fully acknowledged.
        </p>

        <h2 className="aboutUsSubtitle">Project Team</h2>
        <div className="aboutUsTableWrap">
          <table className="aboutUsTable">
            <thead>
              <tr>
                <th scope="col">No</th>
                <th scope="col">Name</th>
                <th scope="col">ID</th>
              </tr>
            </thead>
            <tbody>
              {TEAM_MEMBERS.map((member) => (
                <tr key={member.id}>
                  <td>{member.no}</td>
                  <td>{member.name}</td>
                  <td>{member.id}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </main>
  );
}
