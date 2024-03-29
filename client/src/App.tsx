import React from "react";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import GameManager from "./managers/GameManager";
import GameContainer from "./containers/GameContainer";
import Home from "./components/Home";
import { Outlet } from "react-router-dom";

import SessionManager from "./managers/SessionManager";
import Initializing from "./components/Initializing";
import MessageManager from "./managers/MessageManager";

function App() {
  return (
    <React.StrictMode>
      <BrowserRouter>
        <Routes>
          <Route
            path="/"
            element={
              <MessageManager>
                <SessionManager initializing={<Initializing />}>
                  {(session) => <Outlet context={session} />}
                </SessionManager>
              </MessageManager>
            }
          >
            <Route index element={<Home />} />
            <Route
              path="/game/:game"
              element={
                <GameManager initializing={<Initializing />}>
                  {(state) => <GameContainer {...state} />}
                </GameManager>
              }
            />
          </Route>
        </Routes>
      </BrowserRouter>
    </React.StrictMode>
  );
}

export default App;
