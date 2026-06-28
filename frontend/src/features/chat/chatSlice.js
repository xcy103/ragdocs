import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import { api } from "../../api/client";

export const sendMessage = createAsyncThunk(
  "chat/send",
  (message, { getState }) => {
    const { conversationId } = getState().chat;
    return api.sendChat(message, conversationId);
  },
);

const chatSlice = createSlice({
  name: "chat",
  initialState: { conversationId: null, turns: [], status: "idle", error: null },
  reducers: {
    addUserTurn: (state, action) => {
      state.turns.push({ role: "user", text: action.payload });
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(sendMessage.pending, (state) => {
        state.status = "loading";
        state.error = null;
      })
      .addCase(sendMessage.fulfilled, (state, action) => {
        state.status = "idle";
        state.conversationId = action.payload.conversation_id;
        state.turns.push({
          role: "assistant",
          text: action.payload.answer,
          sources: action.payload.sources,
        });
      })
      .addCase(sendMessage.rejected, (state, action) => {
        state.status = "error";
        state.error = action.error.message;
      });
  },
});

export const { addUserTurn } = chatSlice.actions;
export default chatSlice.reducer;
