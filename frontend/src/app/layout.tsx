import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'A2A Supply Chain - Live Demo',
  description: 'Agent-to-Agent決済システム リアルタイムダッシュボード',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ja">
      <body>{children}</body>
    </html>
  );
}
