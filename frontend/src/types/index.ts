/**
 * 型定義
 */

export interface LogEntry {
  timestamp: string;
  level: 'info' | 'success' | 'warning' | 'error' | 'payment' | 'transaction';
  agent: string | null;
  message: string;
  details?: Record<string, any>;
}

export interface AgentStatus {
  status: 'idle' | 'running' | 'completed' | 'error';
  progress: number;
}

export interface Transaction {
  timestamp: string;
  agent: string;
  amount: number;
  address: string;
  tx_hash: string;
  status: 'pending' | 'completed' | 'failed';
}

export interface OptimizationRequest {
  product_sku: string;
  store_id: string;
  weather?: string;
  day_type?: string;
  unit_price?: number;
}

export interface AgentInfo {
  id: string;
  name: string;
  address: string;
  jpyc_balance: number;
  status: 'idle' | 'running' | 'completed' | 'error';
  progress: number;
}
