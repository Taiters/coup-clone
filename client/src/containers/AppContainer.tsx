import { Outlet } from "react-router-dom";

import SessionManager from "../managers/SessionManager";
import Initializing from "../components/Initializing";

function App() {
  return (
    <SessionManager initializing={<Initializing />}>
      <Outlet />
    </SessionManager>
  );
}

export default App;
