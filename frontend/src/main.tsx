import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { App } from "./App";
import { API_BASE_URL } from "./config";
import { OpenChatApiProvider } from "./hooks";
import "./styles.css";

const root = document.getElementById("root");
if (!root) {
  throw new Error("Root element #root not found");
}

createRoot(root).render(
  <StrictMode>
    <OpenChatApiProvider baseUrl={API_BASE_URL}>
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </OpenChatApiProvider>
  </StrictMode>,
);
