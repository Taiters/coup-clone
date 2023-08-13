import React from "react";
import ReactDOM from "react-dom/client";
import "./index.css";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import GameManager from "./managers/GameManager";
import AppContainer from "./containers/AppContainer";
import GameContainer from "./containers/GameContainer";
import Home from "./components/Home";

const root = ReactDOM.createRoot(
  document.getElementById("root") as HTMLElement,
);

root.render(
  <React.StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<AppContainer />}>
          <Route index element={<Home />} />
          <Route
            path="/game/:gameID"
            element={
              <GameManager render={(state) => <GameContainer {...state} />} />
            }
          />
        </Route>
      </Routes>
    </BrowserRouter>
  </React.StrictMode>,
);
