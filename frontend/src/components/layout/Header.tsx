import React from 'react';
import { Link } from 'react-router-dom';

const Header: React.FC = () => {
  return (
    <header className="fixed top-0 left-0 right-0 h-[var(--header-height)] bg-surface border-b border-gray-200 z-50">
      <div className="container-fluid h-full flex items-center justify-between">
        <div className="flex items-center gap-8">
          <Link to="/" className="text-xl font-bold text-primary">
            Restaurant App
          </Link>
          <nav className="hidden md:flex items-center gap-4">
            <Link to="/menu" className="hover:text-primary transition-colors">
              Menu
            </Link>
            <Link to="/orders" className="hover:text-primary transition-colors">
              Orders
            </Link>
            <Link to="/inventory" className="hover:text-primary transition-colors">
              Inventory
            </Link>
          </nav>
        </div>
        
        <div className="flex items-center gap-4">
          <button className="btn btn-outline">
            Sign In
          </button>
        </div>
      </div>
    </header>
  );
};

export default Header; 