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
  /** Per-signal contribution (pp) behind confidence; absent on legacy responses. */
  breakdown?: Record<string, number> | null;
  /** Free-form only: the model's own sentence on why it is this confident. */
  confidence_note?: string | null;
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
  // Akinator mode: one follow-up question when the grounded match was weak.
  clarifying_question?: string | null;
}

export interface SearchSummary {
  id: number;
  category: string;
  query: string;
  created_at: string;
  result_count: number;
  /** Best match from the snapshot; null on searches predating it. */
  top_title?: string | null;
  top_image?: string | null;
  top_confidence?: number | null;
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

export interface ConstellationNode {
  id: number;
  title: string;
  category: string;
  image_url: string | null;
  source_url: string | null;
  seen_count: number;
}

export interface ConstellationEdge {
  a: number;
  b: number;
  weight: number;
}

export interface ConstellationResponse {
  nodes: ConstellationNode[];
  edges: ConstellationEdge[];
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
