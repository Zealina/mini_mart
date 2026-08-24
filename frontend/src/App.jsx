import React, { useState, useEffect, useSyncExternalStore } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import apiClient, { refreshAccessToken } from './api/client';
import { getAuthState, setAuthState, clearAuth, subscribeAuth } from './store/authStore';

import AdminRoute from './components/AdminRoute';
import AdminDashboard from './pages/AdminDashboard';
import Storefront from './pages/Storefront';
import Auth from './pages/Auth'; 
import Cart from './pages/Cart'; 
import Orders from './pages/Orders';
import Settings from './pages/Settings';

export default function App() {
  // `user` lives in the shared in-memory auth store (see store/authStore.js),
  // not localStorage — this keeps App and the axios client (client.js) in
  // sync on the same source of truth. setUser is a thin wrapper so every
  // page that already calls the setUser prop keeps working unchanged.
  const user = useSyncExternalStore(subscribeAuth, () => getAuthState().user);
  const setUser = (nextUser) => setAuthState({ user: nextUser });

  // Since the access token/user no longer persist across reloads, silently
  // re-establish the session on mount using the httpOnly refresh-token
  // cookie. `refresh` only returns an access token, so we follow it with a
  // "who am I" call to repopulate the user.
  // ASSUMPTION: adjust the '/me' path below if your backend exposes it
  // under a different route.
  const [authChecked, setAuthChecked] = useState(false);

  useEffect(() => {
    let cancelled = false;

    (async () => {
      try {
        await refreshAccessToken();
        const meResponse = await apiClient.get('/me');
        if (!cancelled) {
          setUser(meResponse.data.user || meResponse.data);
        }
      } catch (err) {
        // No valid refresh-token cookie, or /me failed — nothing to restore.
        if (!cancelled) clearAuth();
      } finally {
        if (!cancelled) setAuthChecked(true);
      }
    })();

    return () => { cancelled = true; };
  }, []);
  
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [reloadTrigger, setReloadTrigger] = useState(0);
  const [cart, setCart] = useState([]);

  const triggerReload = () => setReloadTrigger(prev => prev + 1);

  const getCartKey = (currentUser) => {
    if (!currentUser) return 'foodMartCart_guest';
    const uniqueId = currentUser.id || currentUser.email || (currentUser.user && (currentUser.user.id || currentUser.user.email)) || 'guest';
    return `foodMartCart_${uniqueId}`;
  };

  useEffect(() => {
    const safeParse = (key, fallback) => {
      try {
        const raw = localStorage.getItem(key);
        return raw ? JSON.parse(raw) : fallback;
      } catch (e) {
        console.warn('Failed to parse localStorage key', key, e);
        return fallback;
      }
    };

    const guestCart = safeParse('foodMartCart_guest', []);
    
    if (user) {
      const userKey = getCartKey(user);
      let userCart = safeParse(userKey, []);

      if (Array.isArray(guestCart) && guestCart.length > 0) {
        guestCart.forEach(gItem => {
          const existing = userCart.find(uItem => uItem.id === gItem.id);
          if (existing) existing.quantity = (existing.quantity || 0) + (gItem.quantity || 0);
          else userCart.push({ ...gItem, quantity: gItem.quantity || 0 });
        });

        localStorage.removeItem('foodMartCart_guest'); 
        localStorage.setItem(userKey, JSON.stringify(userCart)); 
      }
      setCart(userCart); 
    } else {
      setCart(Array.isArray(guestCart) ? guestCart : []);
    }
  }, [user]);

  useEffect(() => {
    async function fetchCatalog() {
      try {
        const [prodRes, catRes] = await Promise.all([
          apiClient.get('products'),
          apiClient.get('categories')
        ]);
        setProducts(prodRes.data);
        setCategories(catRes.data);
      } catch (err) {
        console.error("Backend connection sync failure:", err);
      }
    }
    fetchCatalog();
  }, [reloadTrigger]);

  const handleLogout = async () => {
    try {
      await apiClient.post('logout').catch(() => {});
    } finally {
      clearAuth();
      setCart([]);
    }
  };

  const addToCart = (product) => {
    setCart(prev => {
      const existing = prev.find(item => item.id === product.id);
      const newCart = existing 
        ? prev.map(item => item.id === product.id ? { ...item, quantity: item.quantity + 1 } : item)
        : [...prev, { ...product, quantity: 1 }];
      
      try { localStorage.setItem(getCartKey(user), JSON.stringify(newCart)); } catch (e) {}
      return newCart;
    });
  };

  const updateQuantity = (id, newQuantity) => {
     if (newQuantity < 1) return removeFromCart(id);
    setCart(prev => {
       const newCart = prev.map(item => item.id === id ? { ...item, quantity: newQuantity } : item);
       try { localStorage.setItem(getCartKey(user), JSON.stringify(newCart)); } catch (e) {}
       return newCart;
    });
  };

  const removeFromCart = (id) => {
    setCart(prev => {
       const newCart = prev.filter(item => item.id !== id);
       try { localStorage.setItem(getCartKey(user), JSON.stringify(newCart)); } catch (e) {}
       return newCart;
    });
  };

  const clearCart = () => {
    setCart([]);
    localStorage.removeItem(getCartKey(user));
  };

  const cartCount = cart.reduce((sum, item) => sum + item.quantity, 0);

  if (!authChecked) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#f1f1f2]">
        <span className="text-sm font-medium text-gray-400">Loading...</span>
      </div>
    );
  }

  return (
    <Router>
      <Routes>
        <Route path="/" element={<Storefront user={user} handleLogout={handleLogout} products={products} categories={categories} addToCart={addToCart} cartCount={cartCount} />} />
        
        {/* ✅ Passed triggerReload down to the cart */}
        <Route path="/cart" element={<Cart cart={cart} clearCart={clearCart} updateQuantity={updateQuantity} removeFromCart={removeFromCart} user={user} triggerReload={triggerReload} />} />
        
        <Route path="/orders" element={<Orders user={user} products={products} />} />
        <Route path="/auth" element={<Auth setUser={setUser} />} />
        
        {/* Cleanly formatted JSX to prevent parsing errors */}
        <Route 
          path="/admin" 
          element={
            <AdminRoute user={user}>
              <AdminDashboard user={user} categories={categories} products={products} triggerReload={triggerReload} handleLogout={handleLogout} />
            </AdminRoute>
          } 
        />
       
        
        <Route path="/settings" element={<Settings user={user} setUser={setUser} />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
}
