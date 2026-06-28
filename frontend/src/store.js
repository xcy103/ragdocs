import { configureStore } from "@reduxjs/toolkit";
import documentsReducer from "./features/documents/documentsSlice";
import chatReducer from "./features/chat/chatSlice";

export const store = configureStore({
  reducer: {
    documents: documentsReducer,
    chat: chatReducer,
  },
});
