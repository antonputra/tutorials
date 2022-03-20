import './App.css';
import { Link } from "react-router-dom";

function App() {
  return (
    <div>
      <h1>Bookkeeper v2!</h1>
      <nav
        style={{
          borderBottom: "solid 1px",
          paddingBottom: "1rem",
        }}
      >
        <Link to="/invoices">Invoices</Link> |{" "}
        <Link to="/expenses">Expenses</Link>
      </nav>
    </div>
  );
}

export default App;
