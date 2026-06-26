import React from 'react';
import Link from 'next/link';

export const Header: React.FC = () => {
  return (
    <header className="bg-gradient-to-r from-blue-600 to-blue-800 text-white shadow-lg">
      <div className="max-w-7xl mx-auto px-4 py-6">
        <div className="flex justify-between items-center">
          <div className="flex items-center space-x-4">
            <div>
              <h1 className="text-3xl font-bold">KCET 2026 Portal</h1>
              <p className="text-blue-100 text-sm">College Predictor & Option Entry Optimizer</p>
            </div>
          </div>
          <nav className="flex space-x-6">
            <Link href="/" className="hover:text-blue-200 transition">Home</Link>
            <Link href="/predictor" className="hover:text-blue-200 transition">Predictor</Link>
            <Link href="/choices" className="hover:text-blue-200 transition">My Choices</Link>
          </nav>
        </div>
      </div>
    </header>
  );
};

export default Header;
