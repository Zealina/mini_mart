import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  Database, Store, PlusCircle, Tag, Package, Trash2, 
  Edit3, CheckCircle2, AlertCircle, X, Layers, Image as ImageIcon, 
  Truck, Clock, MapPin, Phone, Navigation, ExternalLink, ShoppingBag, FileText
} from 'lucide-react';
import apiClient from '../api/client';

export default function AdminDashboard({ categories, products, triggerReload }) {
  const [status, setStatus] = useState({ type: '', message: '' });
  const [activeTab, setActiveTab] = useState('orders'); // Defaulted to orders for quick dispatch
  
  // Forms & Modals
  const [catName, setCatName] = useState('');
  const [editingId, setEditingId] = useState(null);
  const [prodForm, setProdForm] = useState({
    name: '', price: '', brand: '', category_id: '', stock: 20, package_size: '', description: ''
  });
  const [prodImage, setProdImage] = useState(null);
  
  const [orders, setOrders] = useState([]);
  const [viewOrder, setViewOrder] = useState(null);

  useEffect(() => {
    const fetchAdminOrders = async () => {
      try {
        const response = await apiClient.get('/orders');
        setOrders(response.data.reverse()); // Newest first
      } catch (error) {
        console.error("Failed to fetch admin orders:", error);
      }
    };
    if (activeTab === 'orders') {
      fetchAdminOrders();
    }
  }, [activeTab]);

  const displayAlert = (type, message) => {
    setStatus({ type, message });
    setTimeout(() => setStatus({ type: '', message: '' }), 4000);
  };

  const getItemsCount = (order) => {
    const items = order.order_items || order.items;
    if (!items) return 0;
    if (Array.isArray(items)) return items.length;
    if (typeof items === 'object') return Object.keys(items).length;
    return 0;
  };

  const handleCategorySubmit = async (e) => {
    e.preventDefault();
    if (!catName.trim()) return;
    try {
      if (editingId) {
        await apiClient.put(`/categories/${editingId}`, { name: catName });
        displayAlert('success', `Category updated successfully!`);
      } else {
        await apiClient.post('/categories', { name: catName });
        displayAlert('success', `Category "${catName}" added successfully!`);
      }
      setCatName('');
      setEditingId(null);
      triggerReload();
    } catch (err) {
      displayAlert('error', err.response?.data?.error || 'Category operation failed.');
    }
  };

  const handleDeleteCategory = async (id) => {
    if (!window.confirm("Are you sure? Deleting this category might impact linked products!")) return;
    try {
      await apiClient.delete(`/categories/${id}`);
      displayAlert('success', 'Category deleted from database.');
      triggerReload();
    } catch (err) {
      displayAlert('error', err.response?.data?.error || 'Failed to delete category.');
    }
  };

  const handleProductSubmit = async (e) => {
    e.preventDefault();
    const formData = new FormData();
    formData.append('name', prodForm.name);
    formData.append('price', prodForm.price);
    formData.append('category_id', prodForm.category_id);
    formData.append('stock', prodForm.stock);
    if (prodForm.brand) formData.append('brand', prodForm.brand);
    if (prodForm.package_size) formData.append('package_size', prodForm.package_size);
    if (prodForm.description) formData.append('description', prodForm.description);
    
    if (prodImage) {
      formData.append('images', prodImage);
    }

    try {
      if (editingId) {
        await apiClient.put(`/products/${editingId}`, formData, { headers: { 'Content-Type': 'multipart/form-data' }});
        displayAlert('success', 'Product updated successfully!');
      } else {
        await apiClient.post('/products', formData, { headers: { 'Content-Type': 'multipart/form-data' }});
        displayAlert('success', `Product "${prodForm.name}" created!`);
      }
      setEditingId(null);
      setProdForm({ name: '', price: '', brand: '', category_id: '', stock: 20, package_size: '', description: '' });
      setProdImage(null); 
      triggerReload();
    } catch (err) {
      displayAlert('error', err.response?.data?.error || 'Product operation failed.');
    }
  };

  const handleEditProductClick = (product) => {
    setEditingId(product.id);
    setProdForm({
      name: product.name, price: product.price, brand: product.brand || '',
      category_id: product.category_id || '', stock: product.stock,
      package_size: product.package_size || '', description: product.description || ''
    });
    setProdImage(null); 
    setActiveTab('products');
  };

  const handleDeleteProduct = async (id) => {
    if (!window.confirm("Delete this product permanently?")) return;
    try {
      await apiClient.delete(`/products/${id}`);
      displayAlert('success', 'Product dropped from inventory.');
      triggerReload();
    } catch (err) {
      displayAlert('error', err.response?.data?.error || 'Failed to delete product.');
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 font-sans text-gray-900 pb-12">
      {/* Isolated Admin Top-Bar */}
      <nav className="bg-gray-950 text-white shadow-md p-3 flex justify-between items-center px-4 sm:px-8 sticky top-0 z-40">
        <div className="flex items-center gap-3">
          <img src="/logo-circular.jpg" alt="C_Express" className="h-10 w-10 rounded-full object-contain bg-white" />
          <div>
            <span className="block font-black tracking-widest uppercase text-sm leading-none">C_EXPRESS CONSOLE</span>
            <span className="block text-[10px] text-gray-400 font-mono mt-1">v1.0.0 (Authorized Access)</span>
          </div>
        </div>
        
        <div className="flex items-center gap-4">
          <button 
            onClick={() => {
              localStorage.removeItem('foodMartUser');
              window.location.href = '/';
            }} 
            className="flex items-center gap-2 text-xs font-bold text-red-400 hover:text-white hover:bg-red-500/20 px-3 py-2 rounded-lg transition-colors"
          >
            End Session
          </button>
          
          <Link to="/" className="flex items-center gap-2 text-xs font-bold bg-white/10 hover:bg-white/20 px-4 py-2.5 rounded-lg transition-colors border border-white/5">
            <Store className="h-4 w-4" /> Storefront
          </Link>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Navigation Tabs */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center border-b border-gray-200 pb-5 mb-8 gap-4">
          <div>
            <h1 className="text-2xl font-black text-gray-950 tracking-tight">System Administration</h1>
            <p className="text-sm text-gray-500">Manage products, categories, and fulfill incoming orders.</p>
          </div>
          
          <div className="flex bg-gray-100 p-1 rounded-xl w-full md:w-auto overflow-x-auto">
            <button onClick={() => { setActiveTab('orders'); setEditingId(null); }} className={`px-5 py-2 whitespace-nowrap rounded-lg text-sm font-bold transition-all flex items-center justify-center gap-2 ${activeTab === 'orders' ? 'bg-white text-[#f68b1e] shadow-sm' : 'text-gray-600 hover:text-gray-900'}`}>
              <Truck className="h-4 w-4" /> Incoming Orders
            </button>
            <button onClick={() => { setActiveTab('products'); setEditingId(null); }} className={`px-5 py-2 whitespace-nowrap rounded-lg text-sm font-bold transition-all flex items-center justify-center gap-2 ${activeTab === 'products' ? 'bg-white text-[#f68b1e] shadow-sm' : 'text-gray-600 hover:text-gray-900'}`}>
              <Package className="h-4 w-4" /> Products Inventory
            </button>
            <button onClick={() => { setActiveTab('categories'); setEditingId(null); }} className={`px-5 py-2 whitespace-nowrap rounded-lg text-sm font-bold transition-all flex items-center justify-center gap-2 ${activeTab === 'categories' ? 'bg-white text-[#f68b1e] shadow-sm' : 'text-gray-600 hover:text-gray-900'}`}>
              <Layers className="h-4 w-4" /> Categories
            </button>
          </div>
        </div>

        {status.message && (
          <div className={`p-4 rounded-xl flex items-start gap-3 text-sm mb-6 max-w-2xl animate-fade-in shadow-sm ${status.type === 'success' ? 'bg-green-50 text-green-700 border border-green-100' : 'bg-red-50 text-red-700 border border-red-100'}`}>
            {status.type === 'success' ? <CheckCircle2 className="h-5 w-5 mt-0.5" /> : <AlertCircle className="h-5 w-5 mt-0.5" />}
            <span className="font-medium">{status.message}</span>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* ORDERS TAB (FULL WIDTH) */}
          {activeTab === 'orders' && (
            <div className="lg:col-span-3">
              <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
                <h3 className="text-sm font-bold text-gray-400 uppercase tracking-wider mb-6 flex items-center gap-2">
                  <FileText className="h-4 w-4" /> Customer Purchase Orders
                </h3>
                
                {orders.length === 0 ? (
                  <div className="text-center py-12 text-gray-400">
                    <Truck className="h-12 w-12 mx-auto mb-3 opacity-20" />
                    <p>No incoming orders found in the database.</p>
                  </div>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="w-full text-left border-collapse text-sm">
                      <thead>
                        <tr className="border-b border-gray-200 text-gray-500 font-bold bg-gray-50/50 uppercase text-xs tracking-wider">
                          <th className="p-4 rounded-tl-lg">Order Number</th>
                          <th className="p-4">Items</th>
                          <th className="p-4">Contact Number</th>
                          <th className="p-4">GPS / Address</th>
                          <th className="p-4 text-right rounded-tr-lg">Action</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-gray-100">
                        {orders.map((order, idx) => {
                          const orderNumber = orders.length - idx;
                          return (
                            <tr key={order.id} className="hover:bg-orange-50/30 transition-colors group">
                              <td className="p-4">
                                <div className="font-black text-gray-900 text-sm">Order #{orderNumber}</div>
                                <div className="font-mono text-[10px] text-gray-400 mt-0.5">UUID: {order.id.substring(0, 8)}</div>
                              </td>
                              <td className="p-4 font-bold text-gray-800">
                                <span className="bg-gray-100 text-gray-700 px-2.5 py-1 rounded text-xs">
                                  {getItemsCount(order)} units
                                </span>
                              </td>
                              <td className="p-4 text-gray-600 font-medium">
                                {order.contact_phone || 'No phone'}
                              </td>
                              <td className="p-4">
                                {order.gps_link ? (
                                  <span className="text-blue-600 font-bold flex items-center gap-1 text-xs bg-blue-50 px-2.5 py-1 rounded w-max border border-blue-100">
                                    <Navigation className="h-3 w-3" /> GPS Location Attached
                                  </span>
                                ) : (
                                  <span className="text-gray-500 text-xs truncate max-w-[200px] inline-block font-medium">
                                    {order.delivery_address || 'Not Provided'}
                                  </span>
                                )}
                              </td>
                              <td className="p-4 text-right">
                                <button 
                                  onClick={() => setViewOrder({ ...order, orderNumber })}
                                  className="text-xs font-bold bg-gray-900 text-white px-5 py-2 rounded-lg hover:bg-[#f68b1e] shadow-sm transition-all flex items-center gap-2 ml-auto"
                                >
                                  View Dispatch <ExternalLink className="h-3.5 w-3.5" />
                                </button>
                              </td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* PRODUCTS & CATEGORIES TABS (SPLIT VIEW) */}
          {activeTab !== 'orders' && (
            <>
              {/* Left Form Column */}
              <div className="lg:col-span-1">
                <div className="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm sticky top-24">
                  {activeTab === 'categories' ? (
                    <>
                      <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
                        <PlusCircle className="h-5 w-5 text-[#f68b1e]" /> 
                        {editingId ? 'Modify Category' : 'Create Category'}
                      </h3>
                      <form onSubmit={handleCategorySubmit} className="space-y-4">
                        <div>
                          <label className="block text-xs font-bold text-gray-500 uppercase mb-1">Name</label>
                          <input type="text" required placeholder="e.g. Beverages" className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#f68b1e] text-sm" value={catName} onChange={e => setCatName(e.target.value)} />
                        </div>
                        <div className="flex gap-2">
                          <button type="submit" className="flex-1 bg-[#f68b1e] text-white py-2 rounded-lg text-sm font-bold hover:bg-orange-600 transition-colors">
                            {editingId ? 'Update Category' : 'Save Category'}
                          </button>
                          {editingId && (
                            <button type="button" onClick={() => { setEditingId(null); setCatName(''); }} className="p-2 bg-gray-100 rounded-lg text-gray-500 hover:bg-gray-200">
                              <X className="h-4 w-4" />
                            </button>
                          )}
                        </div>
                      </form>
                    </>
                  ) : (
                    <>
                      <div className="flex justify-between items-center mb-4">
                        <h3 className="text-lg font-bold text-gray-900 flex items-center gap-2">
                          <PlusCircle className="h-5 w-5 text-[#f68b1e]" /> 
                          {editingId ? 'Modify Product' : 'Add Product'}
                        </h3>
                        {editingId && (
                          <button onClick={() => { setEditingId(null); setProdForm({ name: '', price: '', brand: '', category_id: '', stock: 20, package_size: '', description: '' }); setProdImage(null); }} className="text-xs font-bold text-gray-400 hover:text-gray-600 flex items-center gap-1">
                            <X className="h-3.5 w-3.5" /> Clear Edit
                          </button>
                        )}
                      </div>
                      <form onSubmit={handleProductSubmit} className="space-y-3.5">
                        <div>
                          <label className="block text-xs font-bold text-gray-500 uppercase mb-1">Product Title *</label>
                          <input required type="text" className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#f68b1e]" value={prodForm.name} onChange={e => setProdForm({...prodForm, name: e.target.value})} />
                        </div>
                        <div className="grid grid-cols-2 gap-3">
                          <div>
                            <label className="block text-xs font-bold text-gray-500 uppercase mb-1">Price (₦) *</label>
                            <input required type="number" step="0.01" className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#f68b1e]" value={prodForm.price} onChange={e => setProdForm({...prodForm, price: e.target.value})} />
                          </div>
                          <div>
                            <label className="block text-xs font-bold text-gray-500 uppercase mb-1">Stock Vol *</label>
                            <input required type="number" className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#f68b1e]" value={prodForm.stock} onChange={e => setProdForm({...prodForm, stock: e.target.value})} />
                          </div>
                        </div>
                        <div className="grid grid-cols-2 gap-3">
                          <div>
                            <label className="block text-xs font-bold text-gray-500 uppercase mb-1">Category Link *</label>
                            <select required className="w-full px-2 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#f68b1e]" value={prodForm.category_id} onChange={e => setProdForm({...prodForm, category_id: e.target.value})}>
                              <option value="">Select...</option>
                              {categories.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
                            </select>
                          </div>
                          <div>
                            <label className="block text-xs font-bold text-gray-500 uppercase mb-1">Brand</label>
                            <input type="text" className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#f68b1e]" value={prodForm.brand} onChange={e => setProdForm({...prodForm, brand: e.target.value})} />
                          </div>
                        </div>
                        <div>
                          <label className="block text-xs font-bold text-gray-500 uppercase mb-1">Package Sizing</label>
                          <input type="text" placeholder="e.g. 50cl, 1kg" className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#f68b1e]" value={prodForm.package_size} onChange={e => setProdForm({...prodForm, package_size: e.target.value})} />
                        </div>
                        <div>
                          <label className="block text-xs font-bold text-gray-500 uppercase mb-1 flex items-center gap-1">
                            <ImageIcon className="h-3.5 w-3.5" /> Product Image
                          </label>
                          <input 
                            key={editingId || 'new'} 
                            type="file" accept="image/*" 
                            onChange={(e) => setProdImage(e.target.files[0])} 
                            className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm bg-white focus:outline-none focus:ring-2 focus:ring-[#f68b1e] file:mr-4 file:py-1.5 file:px-4 file:rounded-md file:border-0 file:text-xs file:font-bold file:bg-orange-50 file:text-[#f68b1e] hover:file:bg-orange-100 transition-colors cursor-pointer" 
                          />
                        </div>
                        <button type="submit" className="w-full bg-[#f68b1e] text-white py-2.5 rounded-lg text-sm font-bold hover:bg-orange-600 transition-colors shadow-sm mt-4">
                          {editingId ? 'Apply Database Changes' : 'Commit to Storage'}
                        </button>
                      </form>
                    </>
                  )}
                </div>
              </div>

              {/* Right Table Column */}
              <div className="lg:col-span-2">
                <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
                  {activeTab === 'categories' ? (
                    <div>
                      <h3 className="text-sm font-bold text-gray-400 uppercase tracking-wider mb-4">Database Categories Records</h3>
                      <div className="divide-y divide-gray-100">
                        {categories.map(cat => (
                          <div key={cat.id} className="py-3 flex justify-between items-center group">
                            <div className="flex items-center gap-2">
                              <Tag className="h-4 w-4 text-[#f68b1e]" />
                              <span className="font-medium text-gray-800 text-sm">{cat.name}</span>
                              <span className="text-[10px] text-gray-300 font-mono">({cat.id.substring(0,8)})</span>
                            </div>
                            <div className="flex items-center gap-1 opacity-80 group-hover:opacity-100 transition-opacity">
                              <button onClick={() => { setEditingId(cat.id); setCatName(cat.name); }} className="p-1.5 text-gray-500 hover:text-blue-600 hover:bg-blue-50 rounded-md">
                                <Edit3 className="h-4 w-4" />
                              </button>
                              <button onClick={() => handleDeleteCategory(cat.id)} className="p-1.5 text-gray-500 hover:text-red-600 hover:bg-red-50 rounded-md">
                                <Trash2 className="h-4 w-4" />
                              </button>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  ) : (
                    <div>
                      <h3 className="text-sm font-bold text-gray-400 uppercase tracking-wider mb-4">Warehouse SKU Records</h3>
                      <div className="overflow-x-auto">
                        <table className="w-full text-left border-collapse text-sm">
                          <thead>
                            <tr className="border-b border-gray-100 text-gray-400 font-semibold">
                              <th className="pb-3">Product</th>
                              <th className="pb-3">Category</th>
                              <th className="pb-3">Price</th>
                              <th className="pb-3">Stock</th>
                              <th className="pb-3 text-right">Actions</th>
                            </tr>
                          </thead>
                          <tbody className="divide-y divide-gray-100">
                            {products.map(prod => (
                              <tr key={prod.id} className="hover:bg-gray-50/50 transition-colors group">
                                <td className="py-3.5 font-medium text-gray-900 flex items-center gap-3">
                                  {prod.image_url ? (
                                    <img src={prod.image_url} alt={prod.name} className="w-8 h-8 rounded object-cover border border-gray-200" />
                                  ) : (
                                    <div className="w-8 h-8 rounded bg-gray-100 border border-gray-200 flex items-center justify-center">
                                      <ImageIcon className="h-4 w-4 text-gray-400" />
                                    </div>
                                  )}
                                  <div>
                                    <div>{prod.name}</div>
                                    <div className="text-xs text-gray-400 font-normal">{prod.brand || 'No Brand'}</div>
                                  </div>
                                </td>
                                <td className="py-3.5 text-gray-500">
                                  {categories.find(c => c.id === prod.category_id)?.name || 'Unlinked'}
                                </td>
                                <td className="py-3.5 font-bold text-gray-800">₦{parseFloat(prod.price).toLocaleString()}</td>
                                <td className="py-3.5">
                                  <span className={`px-2 py-0.5 rounded-full text-xs font-bold ${prod.stock > 5 ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'}`}>
                                    {prod.stock} units
                                  </span>
                                </td>
                                <td className="py-3.5 text-right">
                                  <div className="flex justify-end gap-1">
                                    <button onClick={() => handleEditProductClick(prod)} className="p-1.5 text-gray-500 hover:text-blue-600 hover:bg-blue-50 rounded-md">
                                      <Edit3 className="h-4 w-4" />
                                    </button>
                                    <button onClick={() => handleDeleteProduct(prod.id)} className="p-1.5 text-gray-500 hover:text-red-600 hover:bg-red-50 rounded-md">
                                      <Trash2 className="h-4 w-4" />
                                    </button>
                                  </div>
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </>
          )}

        </div>
      </div>

      {/* ✅ ADMIN DISPATCH MODAL OVERLAY */}
      {viewOrder && (
        <div 
          className="fixed inset-0 bg-black/60 z-[100] flex items-center justify-center p-4 backdrop-blur-sm animate-fade-in"
          onClick={() => setViewOrder(null)}
        >
          <div 
            className="bg-white rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto shadow-2xl relative" 
            onClick={e => e.stopPropagation()}
          >
            <div className="bg-gray-950 p-6 flex justify-between items-center sticky top-0 z-10">
              <div>
                <h3 className="text-lg font-black text-white flex items-center gap-2">
                  Dispatch Invoice <span className="text-[#f68b1e]">#{viewOrder.orderNumber}</span>
                </h3>
                <p className="text-xs text-gray-400 font-mono mt-1">UUID: {viewOrder.id}</p>
              </div>
              <button 
                onClick={() => setViewOrder(null)}
                className="bg-white/10 p-2 rounded-full text-gray-400 hover:text-white border border-white/5 hover:bg-white/20 transition-colors shadow-sm"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            <div className="p-6 space-y-6">
              <div className="bg-orange-50/50 border border-orange-100 rounded-xl p-5 space-y-4">
                <h4 className="text-xs font-bold text-[#f68b1e] uppercase tracking-wider border-b border-orange-100 pb-2">Customer & Delivery Info</h4>
                
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div className="flex items-start gap-3">
                    <Phone className="h-4 w-4 text-orange-500 mt-0.5" />
                    <div>
                      <span className="block text-xs font-bold text-gray-400 uppercase">Contact Phone</span>
                      <span className="text-sm font-bold text-gray-900 leading-none">{viewOrder.contact_phone || 'Not Provided'}</span>
                    </div>
                  </div>

                  {viewOrder.gps_link && (
                    <div className="flex items-start gap-3">
                      <Navigation className="h-4 w-4 text-blue-500 mt-0.5" />
                      <div>
                        <span className="block text-xs font-bold text-gray-400 uppercase">Google Maps Dispatch</span>
                        <a href={viewOrder.gps_link} target="_blank" rel="noopener noreferrer" className="text-sm font-black text-blue-600 hover:text-blue-800 hover:underline flex items-center gap-1 bg-blue-50 px-2 py-0.5 rounded border border-blue-100">
                          Open Map <ExternalLink className="h-3 w-3" />
                        </a>
                      </div>
                    </div>
                  )}
                </div>

                <div className="flex items-start gap-3 pt-2">
                  <MapPin className="h-4 w-4 text-orange-500 mt-0.5" />
                  <div className="w-full">
                    <span className="block text-xs font-bold text-gray-400 uppercase">Typed Address</span>
                    <span className="text-sm font-medium text-gray-800 bg-white p-3 border border-gray-100 rounded-lg block mt-1 w-full shadow-sm">
                      {viewOrder.delivery_address || 'No typed address provided'}
                    </span>
                  </div>
                </div>
              </div>

              <div>
                <h4 className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-3 border-b border-gray-100 pb-2 flex items-center gap-1.5">
                  <ShoppingBag className="h-3.5 w-3.5" /> Items to Pack
                </h4>
                <div className="space-y-3">
                  {viewOrder.order_items?.map((item, index) => {
                    const productInfo = products.find(p => p.id === item.product_id);
                    return (
                      <div key={index} className="flex items-center gap-4 bg-gray-50 border border-gray-100 p-3 rounded-xl shadow-sm">
                        <div className="w-12 h-12 bg-white rounded-lg flex items-center justify-center border border-gray-100 flex-shrink-0 p-1">
                          {productInfo?.image_url ? (
                            <img src={productInfo.image_url} alt={productInfo.name} className="w-full h-full object-cover rounded" />
                          ) : (
                            <ShoppingBag className="h-5 w-5 text-gray-300" />
                          )}
                        </div>
                        <div className="flex-grow">
                          <p className="text-sm font-bold text-gray-800 line-clamp-1">{productInfo ? productInfo.name : 'Unknown Product'}</p>
                          <p className="text-[10px] text-gray-400 font-mono mt-0.5">ID: {item.product_id.substring(0,8)}</p>
                        </div>
                        <div className="text-right bg-white px-3 py-1.5 rounded-lg border border-gray-100">
                          <span className="text-[10px] text-gray-400 uppercase font-bold block mb-1">Qty</span>
                          <span className="text-lg font-black text-[#f68b1e] leading-none">x{item.quantity}</span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>

              <div className="flex gap-4 pt-4 border-t border-gray-100">
                <button 
                  onClick={() => setViewOrder(null)}
                  className="flex-1 bg-gray-100 text-gray-700 font-bold py-3 rounded-xl hover:bg-gray-200 transition-colors"
                >
                  Close
                </button>
                <button 
                  className="flex-1 bg-green-500 text-white font-bold py-3 rounded-xl hover:bg-green-600 transition-colors flex justify-center items-center gap-2 shadow-sm"
                  onClick={() => alert("Marked as dispatched! (Database toggle coming soon)")}
                >
                  <CheckCircle2 className="h-5 w-5" /> Mark Dispatched
                </button>
              </div>
              
            </div>
          </div>
        </div>
      )}

    </div>
  );
}