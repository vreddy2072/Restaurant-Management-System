import React from 'react';
import { Link, useLocation } from 'react-router-dom';

const menuItems = [
  {
    title: 'Dashboard',
    path: '/',
    icon: '📊'
  },
  {
    title: 'Menu Management',
    path: '/menu',
    icon: '🍽️'
  },
  {
    title: 'Orders',
    path: '/orders',
    icon: '📝'
  },
  {
    title: 'Inventory',
    path: '/inventory',
    icon: '📦'
  },
  {
    title: 'Settings',
    path: '/settings',
    icon: '⚙️'
  }
];

const Sidebar: React.FC = () => {
  const location = useLocation();

  return (
    <aside className="fixed left-0 top-[var(--header-height)] h-[calc(100vh-var(--header-height))] w-[var(--sidebar-width)] bg-surface border-r border-gray-200">
      <nav className="p-4">
        <ul className="space-y-2">
          {menuItems.map((item) => (
            <li key={item.path}>
              <Link
                to={item.path}
                className={`flex items-center gap-3 px-4 py-2 rounded-md transition-colors ${
                  location.pathname === item.path
                    ? 'bg-primary text-white'
                    : 'hover:bg-gray-100'
                }`}
              >
                <span>{item.icon}</span>
                <span>{item.title}</span>
              </Link>
            </li>
          ))}
        </ul>
      </nav>
    </aside>
  );
};

export default Sidebar; 