import React from 'react';
import Header from './Header';
import Sidebar from './Sidebar';
import Footer from './Footer';

interface MainLayoutProps {
  children: React.ReactNode;
}

const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
  return (
    <div className="min-h-screen bg-background text-text">
      <Header />
      <div className="flex">
        <Sidebar />
        <main className="flex-1 p-4 ml-[var(--sidebar-width)] mt-[var(--header-height)]">
          {children}
        </main>
      </div>
      <Footer />
    </div>
  );
};

export default MainLayout; 