import React from "react";
import ReactDOM from "react-dom/client";
import theme from "./static/theme";
import App from "./App.jsx";
import { ThemeProvider } from "@mui/material/styles";
import "./static/style.css";
import Navbar from "./static/cogbar";

ReactDOM.createRoot(document.querySelector("#root")).render(
  <ThemeProvider theme={theme}>
    <Navbar />
    <App />
  </ThemeProvider>
);
