import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import apiClient from './api/client';

import AdminRoute from './components/AdminRoute';
import AdminDashboard from './pages/AdminDashboard';
import Storefront from './pages/Storefront';
import Auth from './pages/Auth'; 
import Cart from './pages/Cart'; 
import Orders from './pages/Orders';
import Settings from './pages/Settings';

export default function App() {
  const [user, setUser] = useState(() => {
    const savedUser = localStorage.getItem('foodMartUser');
    return savedUser ? JSON.parse(savedUser) : null;
  }); 
  
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
          apiClient.get('/products'),
          apiClient.get('/categories')
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
      await apiClient.post('/logout').catch(() => {});
    } finally {
      setUser(null);
      setCart([]);
      localStorage.removeItem('foodMartUser');
    }
  };

  useEffect(() => {
    try {
      if (user) localStorage.setItem('foodMartUser', JSON.stringify(user));
      else localStorage.removeItem('foodMartUser');
    } catch (e) {
      console.warn('Failed to persist user', e);
    }
  }, [user]);

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
              <AdminDashboard categories={categories} products={products} triggerReload={triggerReload} />
            </AdminRoute>
          } 
        />
        
        <Route path="/settings" element={<Settings user={user} setUser={setUser} />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
}