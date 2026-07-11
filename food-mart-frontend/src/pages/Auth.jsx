import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { CheckCircle2, AlertCircle, Store } from 'lucide-react';
import apiClient from '../api/client';

export default function Auth({ setUser }) {
  const navigate = useNavigate();
  const [isLogin, setIsLogin] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [status, setStatus] = useState({ type: '', message: '' });
  
  const [formData, setFormData] = useState({
    email: '', password: '', first_name: '', last_name: '', whatsapp_number: '', phone_number: '', address: ''
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setStatus({ type: '', message: '' });
    setIsSubmitting(true);

    try {
      if (isLogin) {
        const response = await apiClient.post('/login', {
          email: formData.email,
          password: formData.password
        });
        
        const actualUser = response.data.user || response.data;
        setUser(actualUser);
        localStorage.setItem('foodMartUser', JSON.stringify(actualUser));
        
        setStatus({ type: 'success', message: 'Logged in successfully!' });
        setTimeout(() => navigate('/'), 1000);
      } else {
        const registerPayload = {
          first_name: formData.first_name,
          last_name: formData.last_name,
          email: formData.email,
          password: formData.password,
          whatsapp_number: formData.whatsapp_number
        };

        if (formData.phone_number) registerPayload.phone_number = formData.phone_number;
        if (formData.address) registerPayload.address = formData.address;

        await apiClient.post('/users', registerPayload);
        
        setStatus({ type: 'success', message: 'Registration complete! You can now log in.' });
        setIsLogin(true); 
        setFormData(prev => ({ ...prev, password: '' })); 
      }
    } catch (error) {
      const errorMsg = error.response?.data?.error || error.response?.data?.message || 'Authentication failed. Please check credentials.';
      setStatus({ type: 'error', message: errorMsg });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#f1f1f2] flex flex-col items-center pt-12 px-4 sm:px-6 lg:px-8 pb-12">
      
      {/* ✅ BRAND LOGO ON AUTH PAGE */}
      <Link to="/" className="mb-8 text-center flex flex-col items-center gap-3 hover:opacity-80 transition-opacity">
        <img src="/logo-vertical.png" alt="C_Express Mini-Mart" className="h-28 w-28 rounded-full shadow-md object-contain bg-white border-2 border-white" />
        <span className="text-gray-500 text-sm font-medium flex items-center gap-1"><Store className="h-4 w-4"/> Return to Storefront</span>
      </Link>

      <div className="max-w-md w-full bg-white rounded-2xl shadow-xl border border-gray-100 overflow-hidden mb-6">
        <div className="flex border-b border-gray-100">
          <button 
            type="button"
            className={`flex-1 py-4 text-center font-bold text-xs tracking-wider uppercase transition-colors ${isLogin ? 'bg-[#f68b1e] text-white' : 'bg-gray-50 text-gray-500 hover:bg-gray-100'}`}
            onClick={() => { setIsLogin(true); setStatus({ type: '', message: '' }); }}
          >
            Log In
          </button>
          <button 
            type="button"
            className={`flex-1 py-4 text-center font-bold text-xs tracking-wider uppercase transition-colors ${!isLogin ? 'bg-[#f68b1e] text-white' : 'bg-gray-50 text-gray-500 hover:bg-gray-100'}`}
            onClick={() => { setIsLogin(false); setStatus({ type: '', message: '' }); }}
          >
            Register Account
          </button>
        </div>

        <div className="p-8">
          <div className="text-center mb-6">
            <h2 className="text-2xl font-extrabold text-gray-950">{isLogin ? 'Welcome Back!' : 'Create New Account'}</h2>
            <p className="text-xs text-gray-400 mt-1">
              {isLogin ? 'Sign in to access your cart and orders' : 'Register to start shopping for fresh groceries'}
            </p>
          </div>

          {status.message && (
            <div className={`p-4 rounded-lg flex items-start gap-3 text-sm mb-6 ${status.type === 'success' ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'}`}>
              {status.type === 'success' ? <CheckCircle2 className="h-5 w-5 flex-shrink-0 mt-0.5" /> : <AlertCircle className="h-5 w-5 flex-shrink-0 mt-0.5" />}
              <span>{status.message}</span>
            </div>
          )}
          
          <form onSubmit={handleSubmit} className="space-y-4">
            {!isLogin && (
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-bold text-gray-500 uppercase mb-1">First Name *</label>
                  <input required type="text" className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#f68b1e] text-sm" value={formData.first_name} onChange={e => setFormData({...formData, first_name: e.target.value})} />
                </div>
                <div>
                  <label className="block text-xs font-bold text-gray-500 uppercase mb-1">Last Name *</label>
                  <input required type="text" className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#f68b1e] text-sm" value={formData.last_name} onChange={e => setFormData({...formData, last_name: e.target.value})} />
                </div>
              </div>
            )}
            
            <div>
              <label className="block text-xs font-bold text-gray-500 uppercase mb-1">Email Address *</label>
              <input required type="email" placeholder="example@mail.com" className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#f68b1e] text-sm" value={formData.email} onChange={e => setFormData({...formData, email: e.target.value})} />
            </div>

            {!isLogin && (
               <div>
                 <label className="block text-xs font-bold text-gray-500 uppercase mb-1">WhatsApp Number *</label>
                 <input required type="tel" placeholder="e.g. +234800000000" className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#f68b1e] text-sm" value={formData.whatsapp_number} onChange={e => setFormData({...formData, whatsapp_number: e.target.value})} />
               </div>
            )}

            <div>
              <label className="block text-xs font-bold text-gray-500 uppercase mb-1">Password *</label>
              <input required type="password" placeholder="••••••••" className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#f68b1e] text-sm" value={formData.password} onChange={e => setFormData({...formData, password: e.target.value})} />
            </div>

            <button type="submit" disabled={isSubmitting} className="w-full bg-[#f68b1e] text-white py-3 rounded-lg font-bold hover:bg-orange-600 shadow-md transition-all mt-6 flex justify-center items-center">
              {isSubmitting ? 'PROCESSING...' : isLogin ? 'LOG IN' : 'CREATE ACCOUNT'}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}