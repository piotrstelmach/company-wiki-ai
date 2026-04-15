"use client";

import React, { use } from "react";
import ChatArea from "@/components/chat/ChatArea";

export default function Chat({ params }: { params: Promise<{ chat_id: string }> }) {
  const { chat_id } = use(params);

  return <ChatArea chatId={chat_id} />;
}