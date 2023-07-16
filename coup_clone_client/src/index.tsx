import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import {
  createBrowserRouter,
  redirect,
  RouterProvider,
} from "react-router-dom";
import Home from './Home';
import Game from './Game';

const router = createBrowserRouter([
  {
    path: "/",
    element: <Home />,
    action: async () => {
      const response = await fetch("/games", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        }
      });
      const data = await response.json();
      return redirect(`/game/${data.game_id}`);
    }
  },
  {
    path: "/game/:gameID",
    element: <Game />
  },
]);

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);

root.render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>
);
