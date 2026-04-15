import React from "react";
import {Message} from "@/types/schemas";

const ChatMessages = ({ messages }: { messages: Message[] }) => {
    return (
        <>
            {messages.map((message, index: number) => (
                <div
                    key={index}
                    className={`flex ${
                        message.role === "user" ? "justify-end" : "justify-start"
                    } animate-in fade-in slide-in-from-bottom-2 duration-300`}>
                    <div
                        className={`max-w-[85%] px-4 py-3 rounded-2xl shadow-sm ${
                            message.role === "user"
                                ? "bg-blue-600 text-white rounded-tr-none"
                                : "bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 text-zinc-800 dark:text-zinc-200 rounded-tl-none"
                        }`}>
                        <p className="text-sm md:text-base leading-relaxed whitespace-pre-wrap">
                            {message.content}
                        </p>
                    </div>
                </div>
            ))}
        </>
    );
}

export default ChatMessages;