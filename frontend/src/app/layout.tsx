import type { Metadata } from 'next';
import './globals.css';
import Header from '@/components/Header';

export const metadata: Metadata = {
  title: 'KCET 2026 Portal',
  description: 'College Predictor & Option Entry Optimizer',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-gray-100">
        <Header />
        <main className="min-h-screen">
          {children}
        </main>
        <footer className="bg-gray-800 text-white py-6 mt-12">
          <div className="max-w-7xl mx-auto px-4 text-center text-sm">
            <p>&copy; 2026 KCET College Predictor. All rights reserved.</p>
          </div>
        </footer>
      </body>
    </html>
  );
}
