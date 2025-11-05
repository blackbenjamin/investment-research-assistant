export interface Source {
  document_name: string;
  page_number: number;
  text: string;
  score: number;
}

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: Source[];
  timestamp: Date;
}

export interface QueryRequest {
  query: string;
  top_k?: number;
  use_reranking?: boolean;
}

export interface QueryResponse {
  answer: string;
  sources: Source[];
  query: string;
}

export interface DocumentInfo {
  name: string;
  status: string;
  file_size?: number;
}
