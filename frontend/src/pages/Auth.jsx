import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams, Link } from 'react-router-dom';
import { CheckCircle2, AlertCircle, Store, Eye, EyeOff } from 'lucide-react';
import apiClient, { getApiErrorMessage } from '../api/client';
import { setAuthState } from '../store/authStore';

export default function Auth({ setUser }) {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  const [mode, setMode] = useState('login');
  const isLogin = mode === 'login';

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [status, setStatus] = useState({ type: '', message: '' });

  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [showConfirmNewPassword, setShowConfirmNewPassword] = useState(false);

  const [formData, setFormData] = useState({
    email: '', password: '', confirm_password: '', first_name: '', last_name: '', whatsapp_number: '', phone_number: '', address: ''
  });

  const [resetEmail, setResetEmail] = useState('');
  const [resetToken, setResetToken] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmNewPassword, setConfirmNewPassword] = useState('');

  // If the user lands here via the emailed reset link (e.g. /auth?token=...),
  // pick up the token from the URL and jump straight to the reset form.
  useEffect(() => {
    const tokenFromUrl = searchParams.get('token');
    if (tokenFromUrl) {
      setResetToken(tokenFromUrl);
      setMode('reset');
    }
  }, [searchParams]);

  const switchMode = (nextMode) => {
    setMode(nextMode);
    setStatus({ type: '', message: '' });
  };

  const handleLogin = async () => {
    try {
      const response = await apiClient.post('/login', {
        email: formData.email,
        password: formData.password
      });

      const actualUser = response.data.user || response.data;
      setUser(actualUser);
      setAuthState({ accessToken: response.data.access_token });

      setStatus({ type: 'success', message: 'Logged in successfully!' });
      setTimeout(() => navigate('/'), 1000);
    } catch (error) {
      const errorMsg = error.response?.data?.error || 'Authentication failed. Please check your details and try again.';
      setStatus({ type: 'error', message: errorMsg });
    }
  };

  const handleRegister = async () => {
    const registerPayload = {
      first_name: formData.first_name,
      last_name: formData.last_name,
      email: formData.email,
      password: formData.password,
      whatsapp_number: formData.whatsapp_number
    };

    if (formData.phone_number) registerPayload.phone_number = formData.phone_number;
    if (formData.address) registerPayload.address = formData.address;

    try {
      await apiClient.post('/users', registerPayload);

      setStatus({ type: 'success', message: 'Registration complete! You can now log in.' });
      switchMode('login');
      setFormData(prev => ({ ...prev, password: '', confirm_password: '' }));
    } catch (error) {
      const errorMsg = error.response?.data?.error || 'Registration failed. Please check your details and try again.';
      setStatus({ type: 'error', message: errorMsg });
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setStatus({ type: '', message: '' });

    if (!isLogin && formData.password !== formData.confirm_password) {
      setStatus({ type: 'error', message: 'Passwords do not match.' });
      return;
    }

    setIsSubmitting(true);
    try {
      await (isLogin ? handleLogin() : handleRegister());
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleForgotSubmit = async (e) => {
    e.preventDefault();
    setStatus({ type: '', message: '' });
    setIsSubmitting(true);

    try {
      await apiClient.post('/forgot-password', { email: resetEmail });

      setStatus({ type: 'success', message: 'Kindly check your email for your reset link. Click it to set a new password.' });
    } catch (error) {
      const errorMsg = getApiErrorMessage(error, 'Could not send reset link. Please try again.');
      setStatus({ type: 'error', message: errorMsg });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleResetSubmit = async (e) => {
    e.preventDefault();
    setStatus({ type: '', message: '' });

    if (!resetToken) {
      setStatus({ type: 'error', message: 'This reset link is invalid or has expired. Please request a new one.' });
      return;
    }

    if (newPassword !== confirmNewPassword) {
      setStatus({ type: 'error', message: 'Passwords do not match.' });
      return;
    }

    setIsSubmitting(true);

    try {
      // Backend verifies the token itself, so email is not required here.
      await apiClient.post('/reset-password', {
        token: resetToken,
        password: newPassword
      });

      setStatus({ type: 'success', message: 'Password reset successfully! You can now log in.' });
      setResetToken('');
      setNewPassword('');
      setConfirmNewPassword('');
      setTimeout(() => switchMode('login'), 1200);
    } catch (error) {
      const errorMsg = getApiErrorMessage(error, 'Could not reset password. This link may be invalid or expired.');
      setStatus({ type: 'error', message: errorMsg });
    } finally {
      setIsSubmitting(false);
    }
  };

  const StatusBanner = () => (
    status.message ? (
      <div className={`p-4 rounded-lg flex items-start gap-3 text-sm mb-6 ${status.type === 'success' ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'}`}>
        {status.type === 'success' ? <CheckCircle2 className="h-5 w-5 flex-shrink-0 mt-0.5" /> : <AlertCircle className="h-5 w-5 flex-shrink-0 mt-0.5" />}
        <span>{status.message}</span>
      </div>
    ) : null
  );

  return (
    <div className="min-h-screen bg-[#f1f1f2] flex flex-col items-center pt-12 px-4 sm:px-6 lg:px-8 pb-12">

      {/* ✅ BRAND LOGO ON AUTH PAGE */}
      <Link to="/" className="mb-8 text-center flex flex-col items-center gap-3 hover:opacity-80 transition-opacity">
        <img src="/logo-vertical.png" alt="CEXPRESS MINIMART" className="h-28 w-28 rounded-full shadow-md object-contain bg-white border-2 border-white" />
        <span className="text-gray-500 text-sm font-medium flex items-center gap-1"><Store className="h-4 w-4"/> Return to Storefront</span>
      </Link>

      <div className="max-w-md w-full bg-white rounded-2xl shadow-xl border border-gray-100 overflow-hidden mb-6">

        {(mode === 'login' || mode === 'register') && (
          <div className="flex flex-nowrap overflow-x-auto border-b border-gray-100">
            <button
              type="button"
              className={`min-w-[8rem] flex-1 whitespace-nowrap py-4 text-center font-bold text-xs tracking-wider uppercase transition-colors ${mode === 'login' ? 'bg-[#f68b1e] text-white' : 'bg-gray-50 text-gray-500 hover:bg-gray-100'}`}
              onClick={() => switchMode('login')}
            >
              Log In
            </button>
            <button
              type="button"
              className={`min-w-[8rem] flex-1 whitespace-nowrap py-4 text-center font-bold text-xs tracking-wider uppercase transition-colors ${mode === 'register' ? 'bg-[#f68b1e] text-white' : 'bg-gray-50 text-gray-500 hover:bg-gray-100'}`}
              onClick={() => switchMode('register')}
            >
              Register Account
            </button>
          </div>
        )}

        <div className="p-4 sm:p-8">

          {/* ---------- LOGIN / REGISTER ---------- */}
          {(mode === 'login' || mode === 'register') && (
            <>
              <div className="text-center mb-6">
                <h2 className="text-2xl font-extrabold text-gray-950">{isLogin ? 'Welcome Back!' : 'Create New Account'}</h2>
                <p className="text-xs text-gray-400 mt-1">
                  {isLogin ? 'Sign in to access your cart and orders' : 'Register to start shopping for fresh groceries'}
                </p>
              </div>

              <StatusBanner />

              <form onSubmit={handleSubmit} className="space-y-4">
                {!isLogin && (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
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
                  <div className="relative">
                    <input
                      required
                      type={showPassword ? 'text' : 'password'}
                      placeholder="••••••••"
                      className="w-full px-4 py-2 pr-10 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#f68b1e] text-sm"
                      value={formData.password}
                      onChange={e => setFormData({...formData, password: e.target.value})}
                    />
                    <button
                      type="button"
                      tabIndex={-1}
                      onClick={() => setShowPassword(s => !s)}
                      className="absolute inset-y-0 right-0 flex items-center px-3 text-gray-400 hover:text-gray-600"
                      aria-label={showPassword ? 'Hide password' : 'Show password'}
                    >
                      {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    </button>
                  </div>
                </div>

                {!isLogin && (
                  <div>
                    <label className="block text-xs font-bold text-gray-500 uppercase mb-1">Confirm Password *</label>
                    <div className="relative">
                      <input
                        required
                        type={showConfirmPassword ? 'text' : 'password'}
                        placeholder="••••••••"
                        className="w-full px-4 py-2 pr-10 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#f68b1e] text-sm"
                        value={formData.confirm_password}
                        onChange={e => setFormData({...formData, confirm_password: e.target.value})}
                      />
                      <button
                        type="button"
                        tabIndex={-1}
                        onClick={() => setShowConfirmPassword(s => !s)}
                        className="absolute inset-y-0 right-0 flex items-center px-3 text-gray-400 hover:text-gray-600"
                        aria-label={showConfirmPassword ? 'Hide password' : 'Show password'}
                      >
                        {showConfirmPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                      </button>
                    </div>
                    {formData.confirm_password && formData.password !== formData.confirm_password && (
                      <p className="text-xs text-red-500 mt-1">Passwords do not match.</p>
                    )}
                  </div>
                )}

                {isLogin && (
                  <div className="text-right -mt-1">
                    <button
                      type="button"
                      onClick={() => { setResetEmail(formData.email); setMode('forgot'); }}
                      className="text-xs font-semibold text-[#f68b1e] hover:underline"
                    >
                      Forgot password?
                    </button>
                  </div>
                )}

                <button type="submit" disabled={isSubmitting} className="w-full bg-[#f68b1e] text-white py-3 rounded-lg font-bold hover:bg-orange-600 shadow-md transition-all mt-6 flex justify-center items-center">
                  {isSubmitting ? 'PROCESSING...' : isLogin ? 'LOG IN' : 'CREATE ACCOUNT'}
                </button>
              </form>
            </>
          )}

          {/* ---------- FORGOT PASSWORD (request code) ---------- */}
          {mode === 'forgot' && (
            <>
              <div className="text-center mb-6">
                <h2 className="text-2xl font-extrabold text-gray-950">Reset Your Password</h2>
                <p className="text-xs text-gray-400 mt-1">
                  Enter your email and we'll send you a reset link
                </p>
              </div>

              <StatusBanner />

              <form onSubmit={handleForgotSubmit} className="space-y-4">
                <div>
                  <label className="block text-xs font-bold text-gray-500 uppercase mb-1">Email Address *</label>
                  <input
                    required
                    type="email"
                    placeholder="example@mail.com"
                    className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#f68b1e] text-sm"
                    value={resetEmail}
                    onChange={e => setResetEmail(e.target.value)}
                  />
                </div>

                <button type="submit" disabled={isSubmitting} className="w-full bg-[#f68b1e] text-white py-3 rounded-lg font-bold hover:bg-orange-600 shadow-md transition-all mt-6 flex justify-center items-center">
                  {isSubmitting ? 'SENDING...' : 'SEND RESET LINK'}
                </button>

                <div className="text-center mt-2">
                  <button
                    type="button"
                    onClick={() => switchMode('login')}
                    className="text-xs font-semibold text-gray-500 hover:text-[#f68b1e] hover:underline"
                  >
                    Back to Log In
                  </button>
                </div>
              </form>
            </>
          )}

          {/* ---------- RESET PASSWORD (enter token + new password) ---------- */}
          {mode === 'reset' && (
            <>
              <div className="text-center mb-6">
                <h2 className="text-2xl font-extrabold text-gray-950">Create New Password</h2>
                <p className="text-xs text-gray-400 mt-1">
                  Choose a new password for your account
                </p>
              </div>

              <StatusBanner />

              {!resetToken && status.type !== "success" && (
                <div className="p-4 rounded-lg bg-amber-50 text-amber-700 text-sm mb-6">
                  This link looks invalid or incomplete. Please request a new reset link.
                </div>
              )}

              <form onSubmit={handleResetSubmit} className="space-y-4">
                <div>
                  <label className="block text-xs font-bold text-gray-500 uppercase mb-1">New Password *</label>
                  <div className="relative">
                    <input
                      required
                      type={showNewPassword ? 'text' : 'password'}
                      placeholder="••••••••"
                      className="w-full px-4 py-2 pr-10 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#f68b1e] text-sm"
                      value={newPassword}
                      onChange={e => setNewPassword(e.target.value)}
                    />
                    <button
                      type="button"
                      tabIndex={-1}
                      onClick={() => setShowNewPassword(s => !s)}
                      className="absolute inset-y-0 right-0 flex items-center px-3 text-gray-400 hover:text-gray-600"
                      aria-label={showNewPassword ? 'Hide password' : 'Show password'}
                    >
                      {showNewPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    </button>
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-bold text-gray-500 uppercase mb-1">Confirm New Password *</label>
                  <div className="relative">
                    <input
                      required
                      type={showConfirmNewPassword ? 'text' : 'password'}
                      placeholder="••••••••"
                      className="w-full px-4 py-2 pr-10 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#f68b1e] text-sm"
                      value={confirmNewPassword}
                      onChange={e => setConfirmNewPassword(e.target.value)}
                    />
                    <button
                      type="button"
                      tabIndex={-1}
                      onClick={() => setShowConfirmNewPassword(s => !s)}
                      className="absolute inset-y-0 right-0 flex items-center px-3 text-gray-400 hover:text-gray-600"
                      aria-label={showConfirmNewPassword ? 'Hide password' : 'Show password'}
                    >
                      {showConfirmNewPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    </button>
                  </div>
                  {confirmNewPassword && newPassword !== confirmNewPassword && (
                    <p className="text-xs text-red-500 mt-1">Passwords do not match.</p>
                  )}
                </div>

                <button type="submit" disabled={isSubmitting || !resetToken} className="w-full bg-[#f68b1e] text-white py-3 rounded-lg font-bold hover:bg-orange-600 shadow-md transition-all mt-6 flex justify-center items-center disabled:opacity-50 disabled:cursor-not-allowed">
                  {isSubmitting ? 'RESETTING...' : 'RESET PASSWORD'}
                </button>

                <div className="text-center mt-2 flex flex-col md:flex-row justify-center gap-4">
                  <button
                    type="button"
                    onClick={() => switchMode('forgot')}
                    className="text-xs font-semibold text-gray-500 hover:text-[#f68b1e] hover:underline"
                  >
                    Request a new link
                  </button>
                  <button
                    type="button"
                    onClick={() => switchMode('login')}
                    className="text-xs font-semibold text-gray-500 hover:text-[#f68b1e] hover:underline"
                  >
                    Back to Log In
                  </button>
                </div>
              </form>
            </>
          )}

        </div>
      </div>
    </div>
  );
}
