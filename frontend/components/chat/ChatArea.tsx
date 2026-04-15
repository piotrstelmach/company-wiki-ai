"use client";

import React, { useState, useRef, useEffect } from "react";
import ChatMessages from "@/components/chat/ChatMessages";
import {useMutation, useQueryClient, useQuery} from "@tanstack/react-query";
import {Chat, Message} from "@/types/schemas";
import {useRouter, useSearchParams} from "next/navigation";
import { apiFetch } from "@/lib/api";

interface ChatAreaProps {
  chatId?: string | undefined;
  initialMessages?: Message[];
}

const ChatArea: React.FC<ChatAreaProps> = ({ chatId, initialMessages }: ChatAreaProps) => {
  const queryClient = useQueryClient();
  const router = useRouter();
  const searchParams = useSearchParams();
  const initialMessageSent = useRef(false);

  const { data } = useQuery<Message[]>(
      {
        queryKey: ['chatMessages', chatId],
        queryFn: async () => {
          const res = await apiFetch(`/chats/${chatId}/messages`);
          if (!res.ok) {
            throw new Error('Failed to fetch chat messages');
          }
          return await res.json() as Message[];
        },
        enabled: !!chatId,
        staleTime: 1000 * 60 * 5,
        initialData: initialMessages,
      }
  )

  const [streamingMessage, setStreamingMessage] = useState<string | null>(null);
  const [optimisticMessages, setOptimisticMessages] = useState<Message[]>([]);

  const mutation = useMutation({
    mutationFn: async ({ content, chatId }: { content: string, chatId?: string }) => {
      const res = await apiFetch(`/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            "message": content,
            "chat_id": chatId
        }),
      });

      if (!res.ok) {
        throw new Error('Failed to send message');
      }

      const returnedChatId = res.headers.get("X-Chat-Id");

      if (!res.body) throw new Error("No body in response");

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let done = false;
      let fullText = "";

      setStreamingMessage("");

      try {
        while (!done) {
          const { value, done: readerDone } = await reader.read();
          done = readerDone;
          if (value) {
            const chunk = decoder.decode(value, { stream: true });
            fullText += chunk;
            setStreamingMessage((prev) => (prev !== null ? prev + chunk : chunk));
          }
        }
      } catch (err) {
        console.error("Error reading stream:", err);
      } finally {
        setStreamingMessage(null);
      }

      return { 
        role: 'ai', 
        content: fullText, 
        chat_id: (returnedChatId || chatId) as any
      } as Message;
    },
    onSuccess: async (aiMessage, variables) => {
        setOptimisticMessages([]);
        await queryClient.invalidateQueries({ queryKey: ['chatMessages', chatId] });
        await queryClient.invalidateQueries({ queryKey: ['chatHistory'] });
    },
    onError: () => {
        setOptimisticMessages([]);
    }
  });

  const [input, setInput] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [data, streamingMessage, optimisticMessages]);

  useEffect(() => {
    // If we're on a new chat (chatId is set) and there's a 'message' in the URL,
    // and we haven't sent it yet, let's send it.
    const firstMessage = searchParams.get('message');
    if (firstMessage && chatId && !initialMessageSent.current && (!data || data.length === 0) && !mutation.isPending) {
        initialMessageSent.current = true;
        setOptimisticMessages([{ role: 'user', content: firstMessage, chat_id: chatId as any }]);
        mutation.mutate({ content: firstMessage, chatId });
        
        // Clean up URL
        const newUrl = window.location.pathname;
        window.history.replaceState({}, '', newUrl);
    }
  }, [chatId, searchParams, data, mutation]);

  const handleSend = async () => {
    if (!input.trim() || mutation.isPending) return;
    
    const messageContent = input.trim();
    setInput("");
    
    if (!chatId) {
        try {
            const res = await apiFetch(`/chats`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ title: messageContent })
            });
            if (!res.ok) throw new Error('Failed to create chat');
            const newChat = await res.json() as Chat;
            router.push(`/chat/${newChat.id}?message=${encodeURIComponent(messageContent)}`);
            return;
        } catch (error) {
            console.error("Failed to create chat:", error);
            setInput(messageContent);
            return;
        }
    }

    setOptimisticMessages([{ role: 'user', content: messageContent, chat_id: chatId as any }]);
    try {
      await mutation.mutateAsync({ content: messageContent, chatId });
    } catch (error) {
      console.error("Failed to send message:", error);
      setInput(messageContent);
    }
  };

  const allMessages = [...(data || []), ...optimisticMessages];

  return (
    <div className="flex flex-col h-full relative">
      <div className="flex-1 overflow-y-auto p-4 md:p-8 space-y-6">
        <div className="max-w-3xl mx-auto space-y-6">
          <ChatMessages messages={allMessages} />
          {streamingMessage !== null && (
            <div className="flex justify-start animate-in fade-in slide-in-from-bottom-2 duration-300">
              <div className="max-w-[85%] px-4 py-3 rounded-2xl shadow-sm bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 text-zinc-800 dark:text-zinc-200 rounded-tl-none">
                <p className="text-sm md:text-base leading-relaxed whitespace-pre-wrap">
                  {streamingMessage}
                  <span className="inline-block w-1.5 h-4 ml-1 bg-blue-600 animate-pulse align-middle" />
                </p>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>

      <div className="p-4 md:p-8 bg-linear-to-t from-white dark:from-zinc-950 via-white dark:via-zinc-950 to-transparent pt-10">
        <div className="max-w-3xl mx-auto relative group">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={async (e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                await handleSend();
              }
            }}
            placeholder="Ask anything..."
            className="w-full bg-zinc-50 dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-2xl px-4 py-4 pr-12 text-zinc-800 dark:text-zinc-200 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500 transition-all shadow-sm resize-none min-h-[56px] max-h-40"
            rows={1}
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || mutation.isPending}
            className="absolute right-3 bottom-3 p-2 bg-blue-600 hover:bg-blue-700 disabled:bg-zinc-300 dark:disabled:bg-zinc-800 disabled:cursor-not-allowed text-white rounded-xl transition-all shadow-md active:scale-95"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="m5 12 7-7 7 7" />
              <path d="M12 19V5" />
            </svg>
          </button>
        </div>
        <p className="text-center text-[10px] md:text-xs text-zinc-500 mt-4">
          Wiki AI can make mistakes. Check important info.
        </p>
      </div>
    </div>
  );
};

export default ChatArea;
