'use client';

import { useState, useEffect, useRef } from 'react';
import type { LogEntry, AgentStatus, Transaction, AgentInfo } from '@/types';

export default function DashboardPage() {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [agentStatus, setAgentStatus] = useState<Record<string, AgentStatus>>({
    demand_forecast: { status: 'idle', progress: 0 },
    inventory_optimizer: { status: 'idle', progress: 0 },
    report_generator: { status: 'idle', progress: 0 },
  });
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [agents, setAgents] = useState<AgentInfo[]>([]);
  const [isRunning, setIsRunning] = useState(false);
  const logsEndRef = useRef<HTMLDivElement>(null);

  // 自動スクロール
  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  // SSEでログをストリーミング
  useEffect(() => {
    if (!isRunning) return;

    const eventSource = new EventSource('http://localhost:8000/api/logs/stream');

    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.type === 'status') {
        setAgentStatus(data.data);
      } else if (data.type === 'task_complete') {
        // タスク完了通知を受信
        console.log('Task completed, enabling button');
        setIsRunning(false);
      } else {
        setLogs((prev) => [...prev, data]);
      }
    };

    eventSource.onerror = () => {
      console.error('SSE connection error');
      eventSource.close();
      setIsRunning(false); // エラー時もボタンを再度有効化
    };

    return () => {
      eventSource.close();
    };
  }, [isRunning]);

  // トランザクション履歴を定期的に取得
  useEffect(() => {
    if (!isRunning) return;

    const interval = setInterval(async () => {
      try {
        const response = await fetch('http://localhost:8000/api/transactions');
        const data = await response.json();
        setTransactions(data.transactions);
      } catch (error) {
        console.error('Failed to fetch transactions:', error);
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [isRunning]);

  // エージェント情報とウォレット残高を取得
  useEffect(() => {
    const fetchAgents = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/agents');
        const data = await response.json();
        setAgents(data.agents);
      } catch (error) {
        console.error('Failed to fetch agents:', error);
      }
    };

    // 初回取得
    fetchAgents();

    // 5秒ごとに更新（残高が変わる可能性があるため）
    const interval = setInterval(fetchAgents, 5000);

    return () => clearInterval(interval);
  }, []);

  // 最適化タスクを開始
  const startOptimization = async () => {
    setLogs([]);
    setTransactions([]);
    setIsRunning(true);

    try {
      await fetch('http://localhost:8000/api/optimize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          product_sku: 'TOMATO-001',
          store_id: 'SHIBUYA-01',
          weather: '晴れ',
          day_type: '週末',
          unit_price: 200.0,
        }),
      });
    } catch (error) {
      console.error('Failed to start optimization:', error);
      setIsRunning(false);
    }
  };

  // ログレベルのスタイル
  const getLogStyle = (level: string) => {
    switch (level) {
      case 'success':
        return 'text-green-400';
      case 'error':
        return 'text-red-400';
      case 'warning':
        return 'text-yellow-400';
      case 'payment':
        return 'text-purple-400';
      case 'transaction':
        return 'text-blue-400';
      default:
        return 'text-gray-300';
    }
  };

  // エージェントステータスの表示
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'running':
        return '🔵';
      case 'completed':
        return '🟢';
      case 'error':
        return '🔴';
      default:
        return '⚪';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'running':
        return 'Running...';
      case 'completed':
        return 'Completed';
      case 'error':
        return 'Error';
      default:
        return 'Waiting...';
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 p-6">
      {/* ヘッダー */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-white mb-2">
          A2A Supply Chain - Live Demo Dashboard
        </h1>
        <p className="text-gray-400">
          エージェント協調制御 + ブロックチェーン決済のリアルタイムモニタリング
        </p>
      </div>

      {/* 開始ボタン */}
      <div className="mb-6">
        <button
          onClick={startOptimization}
          disabled={isRunning}
          className={`px-6 py-3 rounded-lg font-semibold ${
            isRunning
              ? 'bg-gray-600 cursor-not-allowed'
              : 'bg-blue-600 hover:bg-blue-700'
          } text-white transition`}
        >
          {isRunning ? '実行中...' : '🚀 最適化タスクを開始'}
        </button>
      </div>

      {/* メインコンテンツ */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 左側: エージェントステータス */}
        <div className="lg:col-span-1 space-y-4">
          <h2 className="text-xl font-semibold text-white mb-4">Agent Status</h2>

          {/* 需要予測エージェント */}
          <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center space-x-2">
                <span className="text-2xl">
                  {getStatusIcon(agentStatus.demand_forecast.status)}
                </span>
                <span className="font-semibold">需要予測</span>
              </div>
              <span className="text-sm text-gray-400">
                {getStatusText(agentStatus.demand_forecast.status)}
              </span>
            </div>
            <div className="w-full bg-gray-700 rounded-full h-2">
              <div
                className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                style={{ width: `${agentStatus.demand_forecast.progress}%` }}
              />
            </div>
            <div className="mt-2 text-xs text-gray-400">
              Progress: {agentStatus.demand_forecast.progress}%
            </div>
            {agents.find(a => a.id === 'demand_forecast') && (
              <div className="mt-2 pt-2 border-t border-gray-700">
                <div className="text-xs text-gray-500 mb-1">Wallet Balance:</div>
                <div className="font-mono text-sm text-purple-400">
                  {agents.find(a => a.id === 'demand_forecast')?.jpyc_balance.toLocaleString()} JPYC
                </div>
                <div className="text-xs text-gray-500 mt-1 truncate">
                  {agents.find(a => a.id === 'demand_forecast')?.address}
                </div>
              </div>
            )}
          </div>

          {/* 在庫最適化エージェント */}
          <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center space-x-2">
                <span className="text-2xl">
                  {getStatusIcon(agentStatus.inventory_optimizer.status)}
                </span>
                <span className="font-semibold">在庫最適化</span>
              </div>
              <span className="text-sm text-gray-400">
                {getStatusText(agentStatus.inventory_optimizer.status)}
              </span>
            </div>
            <div className="w-full bg-gray-700 rounded-full h-2">
              <div
                className="bg-green-500 h-2 rounded-full transition-all duration-300"
                style={{ width: `${agentStatus.inventory_optimizer.progress}%` }}
              />
            </div>
            <div className="mt-2 text-xs text-gray-400">
              Progress: {agentStatus.inventory_optimizer.progress}%
            </div>
            {agents.find(a => a.id === 'inventory_optimizer') && (
              <div className="mt-2 pt-2 border-t border-gray-700">
                <div className="text-xs text-gray-500 mb-1">Wallet Balance:</div>
                <div className="font-mono text-sm text-purple-400">
                  {agents.find(a => a.id === 'inventory_optimizer')?.jpyc_balance.toLocaleString()} JPYC
                </div>
                <div className="text-xs text-gray-500 mt-1 truncate">
                  {agents.find(a => a.id === 'inventory_optimizer')?.address}
                </div>
              </div>
            )}
          </div>

          {/* レポート生成エージェント */}
          <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center space-x-2">
                <span className="text-2xl">
                  {getStatusIcon(agentStatus.report_generator.status)}
                </span>
                <span className="font-semibold">レポート生成</span>
              </div>
              <span className="text-sm text-gray-400">
                {getStatusText(agentStatus.report_generator.status)}
              </span>
            </div>
            <div className="w-full bg-gray-700 rounded-full h-2">
              <div
                className="bg-purple-500 h-2 rounded-full transition-all duration-300"
                style={{ width: `${agentStatus.report_generator.progress}%` }}
              />
            </div>
            <div className="mt-2 text-xs text-gray-400">
              Progress: {agentStatus.report_generator.progress}%
            </div>
            {agents.find(a => a.id === 'report_generator') && (
              <div className="mt-2 pt-2 border-t border-gray-700">
                <div className="text-xs text-gray-500 mb-1">Wallet Balance:</div>
                <div className="font-mono text-sm text-purple-400">
                  {agents.find(a => a.id === 'report_generator')?.jpyc_balance.toLocaleString()} JPYC
                </div>
                <div className="text-xs text-gray-500 mt-1 truncate">
                  {agents.find(a => a.id === 'report_generator')?.address}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* 右側: リアルタイムログ（ターミナル風） */}
        <div className="lg:col-span-2">
          <h2 className="text-xl font-semibold text-white mb-4">
            Real-time Logs (Terminal Style)
          </h2>
          <div className="bg-gray-950 rounded-lg border border-gray-700 h-[600px] overflow-y-auto custom-scrollbar p-4 font-mono text-sm">
            {logs.length === 0 ? (
              <div className="text-gray-500 italic">
                <span className="cursor-blink">▊</span> Waiting for logs...
              </div>
            ) : (
              logs.map((log, index) => (
                <div key={index} className="mb-1">
                  <span className="text-gray-500">[{log.timestamp}]</span>{' '}
                  <span className={getLogStyle(log.level)}>{log.message}</span>
                  {log.details && Object.keys(log.details).length > 0 && (
                    <div className="ml-12 text-gray-400 text-xs mt-1">
                      {JSON.stringify(log.details, null, 2)}
                    </div>
                  )}
                </div>
              ))
            )}
            <div ref={logsEndRef} />
          </div>
        </div>
      </div>

      {/* 下部: トランザクション履歴 */}
      <div className="mt-6">
        <h2 className="text-xl font-semibold text-white mb-4">Transaction History</h2>
        <div className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
          <table className="w-full">
            <thead className="bg-gray-900">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-400 uppercase">
                  Timestamp
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-400 uppercase">
                  Agent
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-400 uppercase">
                  Amount
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-400 uppercase">
                  Address
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-400 uppercase">
                  TX Hash
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-400 uppercase">
                  Status
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-700">
              {transactions.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-4 py-8 text-center text-gray-500">
                    トランザクション履歴がありません
                  </td>
                </tr>
              ) : (
                transactions.map((tx, index) => (
                  <tr key={index} className="hover:bg-gray-750">
                    <td className="px-4 py-3 text-sm text-gray-300">
                      {new Date(tx.timestamp).toLocaleTimeString()}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-300">{tx.agent}</td>
                    <td className="px-4 py-3 text-sm text-purple-400 font-semibold">
                      {tx.amount} JPYC
                    </td>
                    <td className="px-4 py-3 text-sm font-mono text-gray-400">
                      {tx.address.slice(0, 6)}...{tx.address.slice(-4)}
                    </td>
                    <td className="px-4 py-3 text-sm">
                      <a
                        href={`https://amoy.polygonscan.com/tx/${tx.tx_hash}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-400 hover:text-blue-300 font-mono"
                      >
                        {tx.tx_hash.slice(0, 10)}...
                      </a>
                    </td>
                    <td className="px-4 py-3 text-sm">
                      <span
                        className={`px-2 py-1 rounded text-xs font-semibold ${
                          tx.status === 'completed'
                            ? 'bg-green-900 text-green-300'
                            : tx.status === 'pending'
                            ? 'bg-yellow-900 text-yellow-300'
                            : 'bg-red-900 text-red-300'
                        }`}
                      >
                        {tx.status}
                      </span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
