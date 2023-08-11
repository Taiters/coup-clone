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
import App from './App';


const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);

root.render(
  <React.StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<App />} >
          <Route index element={<Home />} />
          <Route path="/game/:gameID" element={<GameContainer />} />
        </Route>
      </Routes>
    </BrowserRouter>
  </React.StrictMode>
);
