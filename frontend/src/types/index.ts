// Type definitions for FlintBloom API

export interface ThreadInfo {
  thread_id: string;
  checkpoint_count: number;
  latest_checkpoint_id: string | null;
  created_at?: string;
  updated_at?: string;
}

export interface ThreadListResponse {
  threads: ThreadInfo[];
  total: number;
  limit: number;
  offset: number;
}

export interface Checkpoint {
  thread_id: string;
  checkpoint_ns: string;
  checkpoint_id: string;
  parent_checkpoint_id: string | null;
  type: string | null;
  checkpoint: Record<string, any>;
  metadata: Record<string, any>;
  checkpoint_ns_hash: string;
}

export interface CheckpointListResponse {
  checkpoints: Checkpoint[];
  total: number;
  limit: number;
  offset: number;
}

export interface TraceNode {
  id: string;
  type: string;
  name: string;
  status: 'running' | 'success' | 'error';
  start_time?: string;
  end_time?: string;
  duration_ms?: number;
  input_data?: any;
  output_data?: any;
  error?: string;
  metadata: Record<string, any>;
  parent_id?: string;
  children: string[];
}

export interface TraceEdge {
  source: string;
  target: string;
  label?: string;
}

export interface TraceGraph {
  thread_id: string;
  checkpoint_id: string;
  nodes: TraceNode[];
  edges: TraceEdge[];
  metadata: Record<string, any>;
}

export interface TokenUsage {
  prompt_tokens: number;
  completion_tokens: number;
  total_tokens: number;
}

export interface CostMetrics {
  total_cost: number;
  prompt_cost: number;
  completion_cost: number;
  currency: string;
}

export interface PerformanceMetrics {
  total_duration_ms: number;
  llm_duration_ms: number;
  tool_duration_ms: number;
  avg_llm_latency_ms?: number;
  avg_tool_latency_ms?: number;
}

export interface ExecutionSummary {
  thread_id: string;
  checkpoint_id: string;
  total_nodes: number;
  success_count: number;
  error_count: number;
  token_usage: TokenUsage;
  cost_metrics: CostMetrics;
  performance_metrics: PerformanceMetrics;
  created_at: string;
}

export interface TraceDetailResponse {
  trace: TraceGraph;
  summary: ExecutionSummary;
  checkpoints: Checkpoint[];
}

export interface ThreadAnalysis {
  thread_id: string;
  checkpoint_count: number;
  total_tokens: number;
  total_cost: number;
  total_duration_ms: number;
  avg_tokens_per_checkpoint: number;
  avg_cost_per_checkpoint: number;
  checkpoints: ExecutionSummary[];
}

export interface RealtimeEvent {
  event_type: string;
  run_id: string;
  parent_run_id?: string;
  thread_id: string;
  timestamp: string;
  duration_ms?: number;
  data: Record<string, any>;
}

export interface RealtimeThreadSummary {
  thread_id: string;
  event_count: number;
  event_types: Record<string, number>;
  duration_ms?: number;
  total_tokens: number;
  start_time?: string;
  end_time?: string;
}

export interface DatabaseInfo {
  type: string;
  version: string;
  features: Record<string, boolean>;
  [key: string]: any;
}
