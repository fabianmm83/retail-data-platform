import { useState } from 'react';
import { Link, Outlet, useLocation } from 'react-router-dom';

const NAV_ITEMS = [
  { path: '/', label: 'Overview', icon: '📊' },
  { path: '/sales', label: 'Sales', icon: '💰' },
  { path: '/products', label: 'Products', icon: '👕' },
  { path: '/states', label: 'States', icon: '🗺️' },
  { path: '/channels', label: 'Channels', icon: '🛒' },
];

export default function Layout() {
  const location = useLocation();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="min-h-screen flex">
      {/* Overlay móvil */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-30 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`
          fixed lg:sticky top-0 left-0 z-40 h-screen w-64 bg-white border-r border-gray-200 flex flex-col
          transform transition-transform duration-200
          ${sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
        `}
      >
        {/* Logo */}
        <div className="p-4 sm:p-6 border-b border-gray-200 flex items-center justify-between">
          <div>
            <h1 className="text-lg sm:text-xl font-bold text-gray-900">
              Cuidado con Rikochet
            </h1>
            <p className="text-xs text-gray-500 mt-1">Retail Data Platform</p>
          </div>
          <button
            onClick={() => setSidebarOpen(false)}
            className="lg:hidden text-gray-400 hover:text-gray-600 text-2xl leading-none"
            aria-label="Cerrar menú"
          >
            ×
          </button>
        </div>

        {/* Navegación */}
        <nav className="flex-1 p-3 sm:p-4 overflow-y-auto">
          <ul className="space-y-1">
            {NAV_ITEMS.map((item) => {
              const isActive = location.pathname === item.path;
              return (
                <li key={item.path}>
                  <Link
                    to={item.path}
                    onClick={() => setSidebarOpen(false)}
                    className={`flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                      isActive
                        ? 'bg-brand-500 text-white'
                        : 'text-gray-700 hover:bg-gray-100'
                    }`}
                  >
                    <span className="text-lg">{item.icon}</span>
                    {item.label}
                  </Link>
                </li>
              );
            })}
          </ul>
        </nav>

        {/* Footer */}
        <div className="p-4 border-t border-gray-200">
          <p className="text-xs text-gray-400">v0.1.0 · Data Platform</p>
        </div>
      </aside>

      {/* Contenido principal */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top bar móvil */}
        <header className="lg:hidden sticky top-0 z-20 bg-white border-b border-gray-200 px-4 py-3 flex items-center gap-3">
          <button
            onClick={() => setSidebarOpen(true)}
            className="text-gray-600 hover:text-gray-900 text-2xl leading-none"
            aria-label="Abrir menú"
          >
            ☰
          </button>
          <h1 className="text-base font-bold text-gray-900 truncate">
            Cuidado con Rikochet
          </h1>
        </header>

        <main className="flex-1 overflow-auto">
          <div className="p-4 sm:p-6 lg:p-8">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
}