import { useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { sendMessage, addUserTurn } from "../features/chat/chatSlice";

export default function ChatPage() {
  const dispatch = useDispatch();
  const { turns, status, error } = useSelector((s) => s.chat);
  const [input, setInput] = useState("");

  const send = (e) => {
    e.preventDefault();
    const msg = input.trim();
    if (!msg || status === "loading") return;
    dispatch(addUserTurn(msg));
    dispatch(sendMessage(msg));
    setInput("");
  };

  return (
    <div className="chat">
      <div className="messages">
        {turns.map((t, i) => (
          <div key={i} className={`turn ${t.role}`}>
            <div className="bubble">{t.text}</div>
            {t.sources && t.sources.length > 0 && (
              <ul className="sources">
                {t.sources.map((s, j) => (
                  <li key={j}>
                    [{j + 1}] {s.title}{" "}
                    <small className="muted">({s.score.toFixed(2)})</small>
                  </li>
                ))}
              </ul>
            )}
          </div>
        ))}
        {status === "loading" && (
          <div className="turn assistant">
            <div className="bubble muted">…thinking</div>
          </div>
        )}
        {error && <p className="error">{error}</p>}
        {turns.length === 0 && status !== "loading" && (
          <p className="muted center">Ask a question about your documents.</p>
        )}
      </div>

      <form onSubmit={send} className="composer">
        <input
          placeholder="Ask something…"
          value={input}
          onChange={(e) => setInput(e.target.value)}
        />
        <button type="submit" disabled={status === "loading"}>
          Send
        </button>
      </form>
    </div>
  );
}
