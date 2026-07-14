import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ShoppingCart, Minus, Plus, Trash2, CheckCircle2, AlertCircle, ShoppingBag, ArrowLeft, MapPin, CreditCard, Phone } from 'lucide-react';
import apiClient from '../api/client';

export default function Cart({ cart, clearCart, updateQuantity, removeFromCart, user }) {
  const navigate = useNavigate();
  const total = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
  const [isOrdering, setIsOrdering] = useState(false);
  const [orderStatus, setOrderStatus] = useState({ type: '', message: '' });
  
  const [deliveryAddress, setDeliveryAddress] = useState(user?.address || '');
  const [contactPhone, setContactPhone] = useState(user?.whatsapp_number || user?.phone_number || '');

  const handleCheckout = async () => {
    if (!user) {
      setOrderStatus({ type: 'error', message: 'You must be logged in to complete a checkout order.' });
      return;
    }
    
    if (!deliveryAddress.trim() || !contactPhone.trim()) {
      setOrderStatus({ type: 'error', message: 'Please provide both a delivery address and contact phone number.' });
      return;
    }

    // Safely extract the user ID
    const userId = user.id || user.user_id || user.uuid || (user.user && user.user.id);
    if (!userId) {
      setOrderStatus({ type: 'error', message: 'User session invalid. Please log in again.' });
      return;
    }

    setIsOrdering(true);
    setOrderStatus({ type: '', message: '' });

    const orderItems = {};
    cart.forEach(item => { orderItems[item.id] = item.quantity; });

    try {
      // 🚨 SPRINT FIX: Sending user_id, items, address, and phone explicitly!
      await apiClient.post('/orders', {
        user_id: userId,
        items: orderItems,
        address: deliveryAddress,
        phone: contactPhone
      });
      
      setOrderStatus({ type: 'success', message: 'Order submitted successfully! Generating your invoice...' });
      
      setTimeout(() => {
        clearCart();
        navigate('/orders');
      }, 2000);
    } catch (error) {
      setOrderStatus({ type: 'error', message: error.response?.data?.error || 'Failed to complete order.' });
    } finally {
      setIsOrdering(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#f1f1f2] font-sans text-[#282828] flex flex-col">
      <nav className="bg-white shadow-sm p-4 sticky top-0 z-50">
        <div className="max-w-5xl mx-auto flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2 text-gray-500 hover:text-[#f68b1e] font-medium transition-colors">
            <ArrowLeft className="h-5 w-5" /> Back to Shopping
          </Link>
          <span className="font-black text-[#f68b1e] text-2xl tracking-tight">FOOD MART</span>
        </div>
      </nav>

      <main className="flex-grow max-w-5xl mx-auto px-4 py-8 w-full">
        <h2 className="text-2xl font-bold text-gray-800 mb-6 flex items-center gap-2">
          <ShoppingCart className="h-6 w-6 text-[#f68b1e]" /> Your Shopping Cart
        </h2>

        {orderStatus.message && (
          <div className={`p-4 rounded-xl flex items-start gap-3 text-sm mb-6 ${orderStatus.type === 'success' ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'}`}>
            {orderStatus.type === 'success' ? <CheckCircle2 className="h-5 w-5 mt-0.5 flex-shrink-0" /> : <AlertCircle className="h-5 w-5 mt-0.5 flex-shrink-0" />}
            <span>{orderStatus.message}</span>
          </div>
        )}

        {cart.length === 0 ? (
          <div className="bg-white rounded-xl border border-gray-100 p-12 text-center shadow-sm">
            <ShoppingCart className="h-16 w-16 text-gray-200 mx-auto mb-4 stroke-1" />
            <h3 className="text-xl font-bold text-gray-700 mb-1">Your cart is empty!</h3>
            <Link to="/" className="inline-block bg-[#f68b1e] text-white px-8 py-3 rounded-lg font-bold hover:bg-orange-600 transition-colors shadow-sm mt-4">
              START SHOPPING
            </Link>
          </div>
        ) : (
          <div className="flex flex-col lg:flex-row gap-8">
            <div className="flex-grow space-y-4">
              {cart.map(item => (
                <div key={item.id} className="bg-white rounded-xl border border-gray-100 p-4 flex items-center gap-4 shadow-sm">
                  <div className="w-20 h-20 bg-gray-50 rounded-lg flex items-center justify-center border border-gray-100 flex-shrink-0 overflow-hidden">
                    {item.image_url ? (
                      <img src={item.image_url} alt={item.name} className="w-full h-full object-cover" />
                    ) : (
                      <ShoppingBag className="h-8 w-8 text-gray-300 stroke-1" />
                    )}
                  </div>
                  <div className="flex-grow">
                    <h4 className="font-semibold text-gray-800 text-sm leading-snug line-clamp-1">{item.name}</h4>
                    <p className="text-xs text-gray-400 mt-0.5">{item.brand || 'Generic'}</p>
                    <p className="text-gray-900 font-bold mt-1 text-sm">₦{parseFloat(item.price).toLocaleString()}</p>
                  </div>
                  
                  <div className="flex flex-col sm:flex-row items-center gap-3">
                    <div className="flex items-center gap-2 border border-gray-200 rounded-lg bg-gray-50 p-1">
                      <button onClick={() => updateQuantity(item.id, item.quantity - 1)} className="p-1.5 hover:text-[#f68b1e] transition-colors"><Minus className="h-3.5 w-3.5" /></button>
                      <span className="w-6 text-center text-xs font-semibold">{item.quantity}</span>
                      <button onClick={() => updateQuantity(item.id, item.quantity + 1)} className="p-1.5 hover:text-[#f68b1e] transition-colors"><Plus className="h-3.5 w-3.5" /></button>
                    </div>
                    <button onClick={() => removeFromCart(item.id)} className="p-2 text-gray-400 hover:text-red-500 transition-colors bg-white rounded-lg border border-transparent hover:border-red-100 hover:bg-red-50"><Trash2 className="h-5 w-5" /></button>
                  </div>
                </div>
              ))}
            </div>

            <div className="w-full lg:w-[22rem] h-fit sticky top-24 space-y-4">
              <div className="bg-white rounded-xl border border-gray-100 p-6 shadow-sm">
                <h3 className="text-md font-bold text-gray-800 border-b border-gray-50 pb-3 mb-5 uppercase tracking-wider">Delivery Details</h3>
                
                <div className="space-y-4">
                  <div>
                    <label className="block text-xs font-bold text-gray-500 uppercase mb-2 flex items-center gap-1">
                      <Phone className="h-3 w-3" /> Contact Phone *
                    </label>
                    <input 
                      type="tel" required value={contactPhone} onChange={(e) => setContactPhone(e.target.value)} placeholder="e.g. +2348000000"
                      className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-[#f68b1e] outline-none transition-all"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-bold text-gray-500 uppercase mb-2 flex items-center gap-1">
                      <MapPin className="h-3 w-3" /> Street Address *
                    </label>
                    <textarea 
                      required value={deliveryAddress} onChange={(e) => setDeliveryAddress(e.target.value)} placeholder="Enter house number, street, city..."
                      className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-[#f68b1e] outline-none transition-all resize-none h-24"
                    />
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-xl border border-gray-100 p-6 shadow-sm">
                <div className="flex justify-between text-gray-500 text-sm mb-2.5">
                  <span>Items Subtotal</span><span className="font-medium text-gray-800">₦{total.toLocaleString()}</span>
                </div>
                <div className="flex justify-between text-gray-500 text-sm mb-4">
                  <span>Standard Delivery</span><span className="text-green-600 text-xs font-semibold bg-green-50 px-2 py-0.5 rounded-full">FREE</span>
                </div>
                <div className="flex justify-between items-center text-sm mb-6 p-3 bg-gray-50 rounded-lg border border-gray-100">
                  <span className="text-gray-600 flex items-center gap-2 font-bold"><CreditCard className="h-4 w-4" /> Payment</span>
                  <span className="text-green-600 font-bold text-xs bg-green-50 px-2 py-1 rounded">CASH ON DELIVERY</span>
                </div>
                <div className="flex justify-between text-gray-900 font-extrabold text-lg border-t border-gray-100 pt-4 mb-6">
                  <span>Total Price</span><span className="text-[#f68b1e]">₦{total.toLocaleString()}</span>
                </div>
                
                {user ? (
                  <button onClick={handleCheckout} disabled={isOrdering} className="w-full bg-[#f68b1e] text-white py-3.5 rounded-lg font-black hover:bg-orange-600 transition-all shadow-md transform hover:scale-[1.01] flex items-center justify-center text-lg">
                    {isOrdering ? 'PLACING ORDER...' : 'PLACE ORDER NOW'}
                  </button>
                ) : (
                  <Link to="/auth" className="w-full bg-gray-100 text-gray-700 py-3 rounded-lg font-bold hover:bg-gray-200 transition-colors text-sm text-center block">LOG IN TO CHECKOUT</Link>
                )}
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

