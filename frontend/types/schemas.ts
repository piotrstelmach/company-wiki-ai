import { z } from 'zod';

export const MessageSchema = z.object({
  id: z.number().optional(),
  role: z.enum(['user', 'ai']),
  content: z.string(),
  created_at: z.date().optional(),
  chat_id: z.uuidv4(),
});

export type Message = z.infer<typeof MessageSchema>;

export const ChatSchema = z.object({
  id: z.uuidv4(),
  title: z.string(),
  timestamp: z.date().optional(),
  messages: z.array(MessageSchema).optional(),
});

export type Chat = z.infer<typeof ChatSchema>;

export const UploadedFileSchema = z.object({
  id: z.number().optional(),
  filename: z.string(),
  file_path: z.string(),
  status: z.string(),
  chunk_count: z.number(),
  upload_date: z.date().optional(),
});

export type UploadedFile = z.infer<typeof UploadedFileSchema>;

export const ChatRequestSchema = z.object({
  message: z.string().min(1, "Message cannot be empty"),
  chat_id: z.uuidv4(),
});

export type ChatRequest = z.infer<typeof ChatRequestSchema>;

export const ProcessFileResponseSchema = z.object({
  status: z.string(),
  db_id: z.number(),
});

export type ProcessFileResponse = z.infer<typeof ProcessFileResponseSchema>;
