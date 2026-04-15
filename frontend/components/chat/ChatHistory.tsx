import React from "react";
import {Chat} from "@/types/schemas";
import Link from "next/link";
import {useParams} from "next/navigation";

interface ChatHistoryProps {
    chats: Chat[] | undefined;
}

const ChatHistory = ({chats}: ChatHistoryProps) => {
    const { chat_id } = useParams();

    if (!chats) return null;
    return (
        <>
            {chats.map((chat) => (
                <Link href={`/chat/${chat.id}`} key={chat.id}>
                    <button
                        className={`w-full text-left p-3 text-sm rounded-lg transition-colors truncate ${
                            chat_id === chat.id 
                            ? "bg-zinc-200 dark:bg-zinc-800 text-zinc-900 dark:text-zinc-100 font-medium" 
                            : "text-zinc-700 dark:text-zinc-300 hover:bg-zinc-100 dark:hover:bg-zinc-900"
                        }`}
                    >
                        {chat.title}
                    </button>
                </Link>
            ))}
        </>
    )
}

export default ChatHistory;