import React from 'react';
import { useAuth } from '../contexts/AuthContext';

const DebugRole = () => {
  const { user, isAuthenticated } = useAuth();
  
  return (
    <div className="fixed top-4 right-4 bg-white p-4 rounded-lg shadow-lg border border-gray-200 z-50">
      <h3 className="font-bold text-sm mb-2">🔍 Debug Info</h3>
      <div className="text-xs space-y-1">
        <div><strong>Authenticated:</strong> {isAuthenticated ? '✅ Yes' : '❌ No'}</div>
        {user && (
          <>
            <div><strong>User ID:</strong> {user.user_id}</div>
            <div><strong>Email:</strong> {user.email}</div>
            <div><strong>Role:</strong> {user.role || 'Not set'}</div>
          </>
        )}
        <div><strong>Current Role:</strong> {isAuthenticated && user?.role ? user.role : 'hr (fallback)'}</div>
      </div>
    </div>
  );
};

export default DebugRole;
