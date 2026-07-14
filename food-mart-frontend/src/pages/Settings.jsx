import React, { useState } from 'react';
import { Link, Navigate } from 'react-router-dom';
import { ArrowLeft, User, MapPin, Phone, CheckCircle2, AlertCircle, Save, Mail, MessageCircle } from 'lucide-react';
import apiClient from '../api/client';

export default function Settings({ user, setUser }) {
  const actualUser = user?.user || user;
  
  const [formData, setFormData] = useState({
    phone_number: actualUser?.phone_number || '',
    whatsapp_number: actualUser?.whatsapp_number || '',
    address: actualUser?.address || ''
  });
  
  const [status, setStatus] = useState({ type: '', message: '' });
  const [isSaving, setIsSaving] = useState(false);

  // Protect the route
  if (!actualUser) return <Navigate to="/auth" />;

  const handleSave = async (e) => {
    e.preventDefault();
    setIsSaving(true);
    setStatus({ type: '', message: '' });

    const userId = actualUser.id || actualUser.user_id || actualUser.uuid;

    try {
      const response = await apiClient.put(`/users/${userId}`, formData);
      const updatedUser = response.data;
      
      // Update global user state & localStorage to lock in the new data
      setUser(updatedUser);
      localStorage.setItem('foodMartUser', JSON.stringify(updatedUser));
      
      setStatus({ type: 'success', message: 'Profile updated successfully! Your new details will be used for future orders.' });
    } catch (error) {
      setStatus({ type: 'error', message: error.response?.data?.error || 'Failed to update profile.' });
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#f1f1f2] font-sans text-[#282828] flex flex-col">
      <nav className="bg-white shadow-sm p-4 sticky top-0 z-50">
        <div className="max-w-3xl mx-auto flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2 text-gray-500 hover:text-[#f68b1e] font-medium transition-colors">
            <ArrowLeft className="h-5 w-5" /> Back to Storefront
          </Link>
          <span className="font-black text-[#f68b1e] text-2xl tracking-tight">FOOD MART</span>
        </div>
      </nav>

      <main className="flex-grow max-w-3xl mx-auto px-4 py-8 w-full">
        <h2 className="text-2xl font-bold text-gray-800 mb-6 flex items-center gap-2">
          <User className="h-6 w-6 text-[#f68b1e]" /> Account Settings
        </h2>

        {status.message && (
          <div className={`p-4 rounded-xl flex items-start gap-3 text-sm mb-6 ${status.type === 'success' ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'}`}>
            {status.type === 'success' ? <CheckCircle2 className="h-5 w-5 mt-0.5 flex-shrink-0" /> : <AlertCircle className="h-5 w-5 mt-0.5 flex-shrink-0" />}
            <span>{status.message}</span>
          </div>
        )}

        <div className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
          
          {/* Read-Only Profile Header */}
          <div className="bg-gray-50 p-6 border-b border-gray-100 flex items-center gap-4">
            <div className="h-16 w-16 bg-[#f68b1e] text-white rounded-full flex items-center justify-center text-2xl font-black shadow-inner">
              {actualUser.first_name?.charAt(0).toUpperCase()}
            </div>
            <div>
              <h3 className="text-xl font-black text-gray-900">{actualUser.first_name} {actualUser.last_name}</h3>
              <p className="text-sm text-gray-500 flex items-center gap-1.5 mt-1">
                <Mail className="h-3.5 w-3.5" /> {actualUser.email}
              </p>
            </div>
          </div>

          {/* Editable Form */}
          <form onSubmit={handleSave} className="p-6 md:p-8 space-y-6">
            <div>
              <h4 className="text-xs font-bold text-[#f68b1e] uppercase tracking-wider mb-4 border-b border-orange-100 pb-2">Delivery & Contact Preferences</h4>
              
              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-bold text-gray-500 uppercase mb-2 flex items-center gap-1">
                      <MessageCircle className="h-3 w-3" /> WhatsApp Number
                    </label>
                    <input 
                      type="tel" 
                      value={formData.whatsapp_number} 
                      onChange={(e) => setFormData({...formData, whatsapp_number: e.target.value})}
                      placeholder="e.g. +2348000000"
                      className="w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-lg text-sm focus:bg-white focus:ring-2 focus:ring-[#f68b1e] outline-none transition-all"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-bold text-gray-500 uppercase mb-2 flex items-center gap-1">
                      <Phone className="h-3 w-3" /> Alt Phone Number
                    </label>
                    <input 
                      type="tel" 
                      value={formData.phone_number} 
                      onChange={(e) => setFormData({...formData, phone_number: e.target.value})}
                      placeholder="Optional alternate number"
                      className="w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-lg text-sm focus:bg-white focus:ring-2 focus:ring-[#f68b1e] outline-none transition-all"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-bold text-gray-500 uppercase mb-2 flex items-center gap-1">
                    <MapPin className="h-3 w-3" /> Default Delivery Address
                  </label>
                  <textarea 
                    value={formData.address} 
                    onChange={(e) => setFormData({...formData, address: e.target.value})}
                    placeholder="Enter your full house address for faster checkouts..."
                    className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-lg text-sm focus:bg-white focus:ring-2 focus:ring-[#f68b1e] outline-none transition-all resize-none h-24"
                  />
                  <p className="text-xs text-gray-400 mt-2">This address will automatically pre-fill your shopping cart during checkout.</p>
                </div>
              </div>
            </div>

            <div className="pt-4 flex justify-end">
              <button 
                type="submit" 
                disabled={isSaving}
                className="bg-[#f68b1e] text-white px-8 py-3 rounded-xl font-bold hover:bg-orange-600 transition-all shadow-md transform hover:-translate-y-0.5 flex items-center gap-2"
              >
                <Save className="h-4 w-4" />
                {isSaving ? 'SAVING CHANGES...' : 'SAVE SETTINGS'}
              </button>
            </div>
          </form>

        </div>
      </main>
    </div>
  );
}