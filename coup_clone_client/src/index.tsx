import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import {
  BrowserRouter,
  Route,
  Routes,
} from "react-router-dom";
import Home from './Home';
import GameContainer from './GameContainer';


const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);

root.render(
  <React.StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/game/:gameID" element={<GameContainer />} />
      </Routes>
    </BrowserRouter>
  </React.StrictMode>
);
