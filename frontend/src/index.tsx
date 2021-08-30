import "./index.css";
import "reflect-metadata";

import React from "react";
import ReactDOM from "react-dom";
import { Router } from "react-router-dom";

import App from "./App";
import { routerHistory } from "./common/router";
import reportWebVitals from "./reportWebVitals";

ReactDOM.render(
  // <React.StrictMode>
    <Router history={routerHistory}>
      <App />
    </Router>,
  // </React.StrictMode>,
  document.getElementById("root")
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
