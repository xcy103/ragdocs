import { useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import {
  fetchDocuments,
  addDocument,
  removeDocument,
} from "../features/documents/documentsSlice";

export default function DocumentsPage() {
  const dispatch = useDispatch();
  const { items, status, error } = useSelector((s) => s.documents);
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");

  useEffect(() => {
    dispatch(fetchDocuments());
  }, [dispatch]);

  const submit = (e) => {
    e.preventDefault();
    if (!title.trim() || !content.trim()) return;
    dispatch(addDocument({ title, content })).then(() => {
      setTitle("");
      setContent("");
    });
  };

  return (
    <div className="documents">
      <form onSubmit={submit} className="doc-form">
        <input
          placeholder="Title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
        />
        <textarea
          placeholder="Paste document text…"
          rows={5}
          value={content}
          onChange={(e) => setContent(e.target.value)}
        />
        <button type="submit">Add document</button>
      </form>

      {status === "loading" && <p className="muted">Loading…</p>}
      {error && <p className="error">{error}</p>}

      <ul className="doc-list">
        {items.map((d) => (
          <li key={d.id}>
            <span>
              {d.title} <small className="muted">({d.num_chunks} chunks)</small>
            </span>
            <button className="danger" onClick={() => dispatch(removeDocument(d.id))}>
              Delete
            </button>
          </li>
        ))}
        {items.length === 0 && status !== "loading" && (
          <li className="muted">No documents yet — add one above.</li>
        )}
      </ul>
    </div>
  );
}
