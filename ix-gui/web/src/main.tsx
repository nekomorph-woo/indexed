import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { AppRoot } from "@/components/AppRoot";
import "@/app.css";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <AppRoot />
  </StrictMode>,
);
