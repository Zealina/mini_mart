import React from 'react';
import { ShieldAlert } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function AdminRoute({ user, children }) {
  // ✅ SMART NESTING CHECK: Handle both nested and unnested session objects safely
  const actualUser = user?.user || user;
  const isAdmin = actualUser && (actualUser.is_admin === true || actualUser.is_admin === 1);

  if (!isAdmin) {
    return (
      <div className="min-h-screen bg-gray-50 flex flex-col items-center pt-20">
        <div className="max-w-md w-full mx-auto p-8 bg-white border border-red-100 rounded-2xl shadow-xl text-center">
          <ShieldAlert className="h-16 w-16 text-red-500 mx-auto mb-4 animate-bounce" />
          <h2 className="text-xl font-black text-gray-950 uppercase tracking-tight">Access Prohibited</h2>
          <p className="text-sm text-gray-500 mt-2 leading-relaxed">
            This system console is strictly reserved for authenticated administrators. Your session metadata does not contain the required clearance keys.
          </p>
          <Link 
            to="/" 
            className="mt-6 w-full inline-block bg-gray-950 text-white py-2.5 rounded-lg font-bold text-sm hover:bg-gray-800 transition-colors"
          >
            Return to Marketplace
          </Link>
        </div>
      </div>
    );
  }

  // If validated, render the AdminDashboard
  return children;
}
