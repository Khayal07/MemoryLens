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

export interface SimilarItem {
  item_id: number;
  title: string;
  description: string;
  image_url: string | null;
  source_url: string | null;
  metadata: Record<string, unknown>;
}

export interface SearchResponse {
  query: string;
  category: string;
  search_id: number;
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

export interface SavedItem {
  item_id: number;
  title: string;
  description: string;
  image_url: string | null;
  source_url: string | null;
  category: string;
  metadata: Record<string, unknown>;
}

export interface Collection {
  id: number;
  name: string;
  created_at: string;
  items: SavedItem[];
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

export interface LabelCount {
  label: string;
  count: number;
}

export interface AnalyticsOverview {
  total_searches: number;
  searches_last_7d: number;
  avg_confidence: number;
  grounded_searches: number;
  freeform_only_searches: number;
  upvotes: number;
  downvotes: number;
  by_category: LabelCount[];
  top_queries: LabelCount[];
}
