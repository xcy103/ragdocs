import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import { api } from "../../api/client";

export const fetchDocuments = createAsyncThunk("documents/fetch", () =>
  api.listDocuments(),
);

export const addDocument = createAsyncThunk("documents/add", (doc) =>
  api.createDocument(doc),
);

export const removeDocument = createAsyncThunk(
  "documents/remove",
  async (id) => {
    await api.deleteDocument(id);
    return id;
  },
);

const documentsSlice = createSlice({
  name: "documents",
  initialState: { items: [], status: "idle", error: null },
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchDocuments.pending, (state) => {
        state.status = "loading";
      })
      .addCase(fetchDocuments.fulfilled, (state, action) => {
        state.status = "idle";
        state.items = action.payload;
      })
      .addCase(fetchDocuments.rejected, (state, action) => {
        state.status = "error";
        state.error = action.error.message;
      })
      .addCase(addDocument.fulfilled, (state, action) => {
        state.items.push(action.payload);
      })
      .addCase(removeDocument.fulfilled, (state, action) => {
        state.items = state.items.filter((d) => d.id !== action.payload);
      });
  },
});

export default documentsSlice.reducer;
