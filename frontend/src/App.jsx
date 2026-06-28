import { useState } from "react";
import DocumentsPage from "./pages/DocumentsPage";
import ChatPage from "./pages/ChatPage";

export default function App() {
  const [tab, setTab] = useState("chat");

  return (
    <div className="app">
      <header className="topbar">
        <h1>RAGDocs</h1>
        <nav>
          <button
            className={tab === "chat" ? "active" : ""}
            onClick={() => setTab("chat")}
          >
            Chat
          </button>
          <button
            className={tab === "documents" ? "active" : ""}
            onClick={() => setTab("documents")}
          >
            Documents
          </button>
        </nav>
      </header>
      <main>{tab === "chat" ? <ChatPage /> : <DocumentsPage />}</main>
    </div>
  );
}
