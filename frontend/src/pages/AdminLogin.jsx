import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Shield, Lock, AlertTriangle, ArrowLeft, Mail } from 'lucide-react';
import apiClient from '../api/client';
import { setAuthState } from '../store/authStore';

export default function AdminLogin({ setUser }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      // Authenticate with the real backend to get the secure session cookie (Fixes 401 Error)
      const response = await apiClient.post('/login', { email, password });
      const userData = response.data.user || response.data;

      // Verify they actually have database admin rights
      if (userData.is_admin == 1 || userData.is_admin === true) {
        setUser(userData);
        setAuthState({ accessToken: response.data.access_token });
        navigate('/admin');
      } else {
        // If they are a normal user trying to log into the admin portal, boot them out
        await apiClient.post('/logout').catch(() => {});
        setError('Access Denied: Account lacks administrator privileges.');
      }
    } catch (err) {
      setError(err.response?.data?.error || err.response?.data?.message || 'Invalid clearance credentials.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-950 flex flex-col items-center justify-center p-4 font-sans">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-2xl overflow-hidden">
        <div className="bg-gray-900 p-8 text-center border-b border-gray-800">
          <Shield className="h-12 w-12 text-[#f68b1e] mx-auto mb-4" />
          <h2 className="text-2xl font-black text-white tracking-widest uppercase">System Console</h2>
          <p className="text-gray-400 text-xs mt-2 font-mono">AUTHORIZED PERSONNEL ONLY</p>
        </div>
        
        <div className="p-8">
          {error && (
            <div className="bg-red-50 text-red-600 p-3 rounded-lg flex items-start gap-2 mb-6 text-sm font-bold border border-red-100">
              <AlertTriangle className="h-5 w-5 flex-shrink-0 mt-0.5" /> <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleLogin} className="space-y-5">
            <div>
              <label className="block text-xs font-bold text-gray-500 uppercase mb-2 flex items-center gap-2">
                <Mail className="h-3 w-3" /> Admin Email
              </label>
              <input 
                type="email" 
                required
                autoFocus
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="admin@cexpressminimart.com"
                className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#f68b1e] text-sm font-medium"
              />
            </div>

            <div>
              <label className="block text-xs font-bold text-gray-500 uppercase mb-2 flex items-center gap-2">
                <Lock className="h-3 w-3" /> Clearance Password
              </label>
              <input 
                type="password" 
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#f68b1e] text-sm tracking-widest"
              />
            </div>

            <button type="submit" disabled={isLoading} className="w-full bg-[#f68b1e] text-white py-3.5 rounded-xl font-black uppercase tracking-wider hover:bg-orange-600 transition-colors shadow-lg shadow-orange-500/30">
              {isLoading ? 'AUTHENTICATING...' : 'AUTHENTICATE'}
            </button>
          </form>

          <button onClick={() => navigate('/')} className="mt-6 w-full text-center text-xs text-gray-400 font-bold hover:text-gray-600 flex items-center justify-center gap-1">
            <ArrowLeft className="h-3 w-3" /> Return to Storefront
          </button>
        </div>
      </div>
    </div>
  );
}
