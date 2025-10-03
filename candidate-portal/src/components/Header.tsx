import React from 'react';

const Header: React.FC = () => {
  return (
    <header className="bg-white shadow-sm border-b">
      <div className="container mx-auto px-4 py-4">
        <div className="flex justify-between items-center">
          <div className="flex items-center space-x-4">
            <h1 className="text-2xl font-bold text-gray-900">Career Portal</h1>
            <p className="text-gray-600">Find your dream job</p>
          </div>
          <nav className="flex space-x-6">
            <a href="/" className="text-gray-700 hover:text-blue-600 transition-colors">
              Jobs
            </a>
            <a href="/test-setup" className="text-gray-700 hover:text-blue-600 transition-colors">
              Test Setup
            </a>
            <a href="/about" className="text-gray-700 hover:text-blue-600 transition-colors">
              About
            </a>
            <a href="/contact" className="text-gray-700 hover:text-blue-600 transition-colors">
              Contact
            </a>
          </nav>
        </div>
      </div>
    </header>
  );
};

export default Header;
