import React, { useState } from 'react';
import { Menu } from 'lucide-react';

export default function SidebarWithToggle() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);

  return (
    <div className="relative h-screen bg-gray-100">
      {/* Sidebar */}
      <div
        className={`fixed top-0 left-0 h-full bg-white shadow-lg z-40 transition-transform duration-300 ease-in-out ${
          isSidebarOpen ? 'translate-x-0 w-64' : '-translate-x-full w-64'
        }`}
      >
        <div className="p-4 flex justify-between items-center border-b">
          <h2 className="text-lg font-semibold">Run Parameters</h2>
          <button
            onClick={() => setIsSidebarOpen(false)}
            className="text-gray-600 hover:text-black"
            aria-label="Close Sidebar"
          >
            ✕
          </button>
        </div>
        <div className="p-4">
          {/* Sidebar content goes here */}
          <p>Sidebar content here...</p>
        </div>
      </div>

      {/* Icon Button when sidebar is closed */}
      {!isSidebarOpen && (
        <button
          onClick={() => setIsSidebarOpen(true)}
          className="fixed top-4 left-4 z-50 p-2 bg-gray-200 rounded hover:bg-gray-300 shadow"
          aria-label="Open Sidebar"
        >
          <Menu size={20} />
        </button>
      )}

      {/* Main content */}
      <div
        className={`transition-all duration-300 ml-0 ${
          isSidebarOpen ? 'ml-64' : 'ml-0'
        } p-4`}
      >
        <h1 className="text-xl font-bold mb-4">Main Content Area</h1>
        <p>Your page content goes here...</p>
      </div>
    </div>
  );
}
