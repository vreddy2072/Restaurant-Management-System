import React from 'react';

const Footer: React.FC = () => {
  return (
    <footer className="fixed bottom-0 left-0 right-0 h-[var(--footer-height)] bg-surface border-t border-gray-200">
      <div className="container-fluid h-full flex items-center justify-between text-sm text-text-light">
        <div>© 2025 Restaurant App. All rights reserved.</div>
        <div className="flex items-center gap-4">
          <a href="#" className="hover:text-primary transition-colors">
            Privacy Policy
          </a>
          <a href="#" className="hover:text-primary transition-colors">
            Terms of Service
          </a>
        </div>
      </div>
    </footer>
  );
};

export default Footer; 