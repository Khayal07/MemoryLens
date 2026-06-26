export interface Category {
  key: string;
  display_name: string;
  icon: string | null;
}

export interface ResultItem {
  item_id: number;
  title: string;
  description: string;
  image_url: string | null;
  source_url: string | null;
  metadata: Record<string, unknown>;
  confidence: number;
  reason: string | null;
}

export interface MismatchSuggestion {
  suspected_category: string;
  message: string;
}

export interface SearchResponse {
  query: string;
  category: string;
  results: ResultItem[];
  suggestion: MismatchSuggestion | null;
}

export interface SearchSummary {
  id: number;
  category: string;
  query: string;
  created_at: string;
  result_count: number;
}

export interface Tokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface User {
  id: number;
  email: string;
}
