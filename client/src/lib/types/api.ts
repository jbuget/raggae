// Auth
export interface RegisterRequest {
  email: string;
  password: string;
  full_name: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface UserResponse {
  id: string;
  email: string;
  full_name: string;
  is_active: boolean;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

// Projects
export type ChunkingStrategy =
  | "auto"
  | "fixed_window"
  | "paragraph"
  | "heading_section"
  | "semantic";

export interface CreateProjectRequest {
  name: string;
  description?: string;
  system_prompt?: string;
  chunking_strategy?: ChunkingStrategy;
  parent_child_chunking?: boolean;
}

export interface UpdateProjectRequest {
  name: string;
  description?: string;
  system_prompt?: string;
  chunking_strategy?: ChunkingStrategy;
  parent_child_chunking?: boolean;
}

export interface ProjectResponse {
  id: string;
  user_id: string;
  name: string;
  description: string;
  system_prompt: string;
  is_published: boolean;
  created_at: string;
  chunking_strategy: ChunkingStrategy;
  parent_child_chunking: boolean;
  reindex_status: string;
  reindex_progress: number;
  reindex_total: number;
}

export interface ReindexProjectResponse {
  project_id: string;
  total_documents: number;
  indexed_documents: number;
  failed_documents: number;
}

// Documents
export interface DocumentResponse {
  id: string;
  project_id: string;
  file_name: string;
  content_type: string;
  file_size: number;
  created_at: string;
  last_indexed_at?: string | null;
  processing_strategy: string | null;
  status: "uploaded" | "processing" | "indexed" | "error";
  error_message?: string | null;
}

export interface DocumentChunkResponse {
  id: string;
  document_id: string;
  chunk_index: number;
  content: string;
  created_at: string;
  metadata_json?: Record<string, unknown> | null;
}

export interface DocumentChunksResponse {
  document_id: string;
  processing_strategy: string | null;
  chunks: DocumentChunkResponse[];
}

export interface UploadDocumentsCreatedResponse {
  original_filename: string;
  stored_filename: string;
  document_id: string;
}

export interface UploadDocumentsErrorResponse {
  filename: string;
  code: string;
  message: string;
}

export interface UploadDocumentsResponse {
  total: number;
  succeeded: number;
  failed: number;
  created: UploadDocumentsCreatedResponse[];
  errors: UploadDocumentsErrorResponse[];
}

// Chat
export interface SendMessageRequest {
  message: string;
  limit?: number;
  conversation_id?: string | null;
  start_new_conversation?: boolean;
}

export interface RetrievedChunkResponse {
  chunk_id: string;
  document_id: string;
  document_file_name?: string | null;
  content: string;
  score: number;
}

export interface SendMessageResponse {
  project_id: string;
  conversation_id: string;
  message: string;
  answer: string;
  chunks: RetrievedChunkResponse[];
}

export interface MessageResponse {
  id: string;
  conversation_id: string;
  role: string;
  content: string;
  source_documents?: Array<{
    document_id: string;
    document_file_name?: string;
    chunk_ids?: string[];
  }> | null;
  reliability_percent?: number | null;
  created_at: string;
}

export interface ConversationResponse {
  id: string;
  project_id: string;
  user_id: string;
  created_at: string;
  title: string | null;
}

export interface ConversationDetailResponse extends ConversationResponse {
  message_count: number;
  last_message: MessageResponse | null;
}

// Streaming SSE events
export interface StreamTokenEvent {
  token: string;
}

export interface StreamDoneEvent {
  done: true;
  conversation_id: string;
  chunks: RetrievedChunkResponse[];
}

export type StreamEvent = StreamTokenEvent | StreamDoneEvent;

// User model provider credentials
export type ModelProvider = "openai" | "gemini" | "anthropic";

export interface SaveModelCredentialRequest {
  provider: ModelProvider;
  api_key: string;
}

export interface ModelCredentialResponse {
  id: string;
  provider: ModelProvider;
  masked_key: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}
