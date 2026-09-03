import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  Database, Store, PlusCircle, Tag, Package, Trash2, 
  Edit3, CheckCircle2, AlertCircle, X, Layers, Image as ImageIcon, 
  Truck, Navigation, ExternalLink, ShoppingBag, FileText, Phone, MapPin, Clock, Search, Shield, UserPlus, Users, User
} from 'lucide-react';
import apiClient, { getApiErrorMessage } from '../api/client';

export default function AdminDashboard({ user, categories, products, triggerReload, handleLogout }) {
  const [status, setStatus] = useState({ type: '', message: '' });
  const [activeTab, setActiveTab] = useState('orders');
  const [searchQuery, setSearchQuery] = useState('');

  const [catName, setCatName] = useState('');
  const [editingId, setEditingId] = useState(null);
  const [prodForm, setProdForm] = useState({
    name: '', price: '', brand: '', category_id: '', stock: 20, package_size: '', description: '', image_url: ''
  });
  const [prodImage, setProdImage] = useState(null);

  const [orders, setOrders] = useState([]);
  const [viewOrder, setViewOrder] = useState(null);

  const [carouselImages, setCarouselImages] = useState([]);
  const [carouselFiles, setCarouselFiles] = useState([]);
  const [carouselUploading, setCarouselUploading] = useState(false);

  const [staffList, setStaffList] = useState([]);
  const [staffTrigger, setStaffTrigger] = useState(0);
  const [staffForm, setStaffForm] = useState({
    email: '', role: 'sub_admin'
  });

  const actualUser = user?.user || user;
  const adminId = actualUser?.id || actualUser?.user_id || actualUser?.uuid;
  const isSuperAdmin = actualUser && (actualUser.is_super_admin === true || actualUser.is_super_admin === 1 || actualUser.is_super_admin === 'true' || actualUser.is_super_admin === 'True');
  const canClearTestOrders = actualUser?.email?.trim().toLowerCase() === 'masterbright02@gmail.com';

  useEffect(() => {
    const fetchAdminOrders = async () => {
      try {
        const response = await apiClient.get('orders');
        let fetchedOrders = Array.isArray(response.data) ? response.data : [];
        fetchedOrders.sort((a, b) => {
          const dateA = a.created_at ? new Date(a.created_at).getTime() : 0;
          const dateB = b.created_at ? new Date(b.created_at).getTime() : 0;
          return dateB - dateA;
        });
        setOrders(fetchedOrders);
      } catch (error) {
        console.error("Failed to fetch admin orders:", error);
      }
    };
    if (activeTab === 'orders') {
      fetchAdminOrders();
    }
  }, [activeTab]);

  useEffect(() => {
    const fetchCarouselImages = async () => {
      try {
        const response = await apiClient.get('/carousel-images');
        setCarouselImages(Array.isArray(response.data) ? response.data : []);
      } catch (error) {
        console.error("Failed to fetch carousel images:", error);
      }
    };
    if (activeTab === 'carousel') {
      fetchCarouselImages();
    }
  }, [activeTab]);

  useEffect(() => {
    if (activeTab === 'staff' && isSuperAdmin) {
      const fetchStaff = async () => {
        try {
          const res = await apiClient.get('/users');
          const admins = res.data.filter(u => u.is_admin === true || u.is_admin === 1 || u.is_admin === 'true');
          setStaffList(admins);
        } catch (e) {
          console.error("Failed to fetch staff:", e);
        }
      };
      fetchStaff();
    }
  }, [activeTab, isSuperAdmin, staffTrigger]);

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

  const handleCancelOrder = async (orderId) => {
    if (!window.confirm("Are you sure? This will delete the order and return the items to warehouse stock.")) return;
    try {
      await apiClient.delete(`/orders/${orderId}`);
      displayAlert('success', 'Order cancelled and inventory restocked!');
      setViewOrder(null);
      setOrders(prev => prev.filter(o => o.id !== orderId));
      triggerReload();
    } catch (err) {
      displayAlert('error', getApiErrorMessage(err, 'Failed to cancel order.'));
    }
  };

  const handleUpdateStatus = async (orderId, newStatus) => {
    try {
      await apiClient.put(`/orders/${orderId}/status`, { status: newStatus });
      setOrders(prev => prev.map(o => o.id === orderId ? { ...o, status: newStatus } : o));
      setViewOrder(prev => ({ ...prev, status: newStatus }));
      displayAlert('success', `Order marked as ${newStatus.toUpperCase()}!`);
    } catch (err) {
      displayAlert('error', getApiErrorMessage(err, 'Failed to update delivery status.'));
    }
  };

  const handleConfirmPayment = async (orderId) => {
    const confirmedBy = actualUser?.first_name || actualUser?.email || 'Admin';
    try {
      await apiClient.put(`/orders/${orderId}/confirm-payment`, { confirmed_by: confirmedBy });
      setOrders(prev => prev.map(o => o.id === orderId ? { ...o, payment_confirmed: true, payment_confirmed_by: confirmedBy } : o));
      setViewOrder(prev => (prev && prev.id === orderId) ? { ...prev, payment_confirmed: true, payment_confirmed_by: confirmedBy } : prev);
      displayAlert('success', 'Payment confirmed!');
    } catch (err) {
      displayAlert('error', getApiErrorMessage(err, 'Failed to confirm payment.'));
    }
  };

  const handleClearTestOrders = async () => {
    if (!window.confirm('Clear all tested orders? Their reserved inventory will be returned to stock.')) return;
    try {
      const response = await apiClient.delete('/orders/test-data');
      displayAlert('success', `${response.data.deleted} tested order${response.data.deleted === 1 ? '' : 's'} cleared.`);
      setViewOrder(null);
      setOrders([]);
      triggerReload();
    } catch (err) {
      displayAlert('error', getApiErrorMessage(err, 'Failed to clear tested orders.'));
    }
  };

  const getCustomerName = (order) => {
    const first = order.user?.first_name || order.customer_first_name || order.customer_name;
    const last = order.user?.last_name || order.customer_last_name || '';
    const name = [first, last].filter(Boolean).join(' ').trim();
    return name || 'Guest Customer';
  };

  const getCustomerEmail = (order) =>
    order.user?.email || order.customer_email || order.email || 'No email on file';

  const renderStatusBadge = (orderStatus) => {
    switch(orderStatus) {
      case 'Delivered': return <span className="bg-green-100 text-green-700 px-2 py-0.5 rounded text-[10px] font-black uppercase">Delivered</span>;
      case 'Dispatched': return <span className="bg-orange-100 text-orange-700 px-2 py-0.5 rounded text-[10px] font-black uppercase">Dispatched</span>;
      case 'Processing': return <span className="bg-blue-100 text-blue-700 px-2 py-0.5 rounded text-[10px] font-black uppercase">Processing</span>;
      default: return <span className="bg-gray-100 text-gray-600 px-2 py-0.5 rounded text-[10px] font-black uppercase">Pending</span>;
    }
  };

  const handleCategorySubmit = async (e) => {
    e.preventDefault();
    if (!catName.trim()) return;
    try {
      if (editingId) {
        await apiClient.put(`/categories/${editingId}`, { name: catName, user_id: adminId });
        displayAlert('success', `Category updated successfully!`);
      } else {
        await apiClient.post('/categories', { name: catName, user_id: adminId });
        displayAlert('success', `Category "${catName}" added successfully!`);
      }
      setCatName('');
      setEditingId(null);
      triggerReload();
    } catch (err) {
      displayAlert('error', getApiErrorMessage(err, 'Category operation failed.'));
    }
  };

  const handleDeleteCategory = async (id) => {
    if (!window.confirm("Are you sure? Deleting this category might impact linked products!")) return;
    try {
      await apiClient.delete(`/categories/${id}?user_id=${adminId}`);
      displayAlert('success', 'Category deleted from database.');
      triggerReload();
    } catch (err) {
      displayAlert('error', getApiErrorMessage(err, 'Failed to delete category.'));
    }
  };

  const handleProductSubmit = async (e) => {
    e.preventDefault();
    const formData = new FormData();
    formData.append('user_id', adminId);

    formData.append('name', prodForm.name);
    formData.append('price', prodForm.price);
    formData.append('category_id', prodForm.category_id);
    formData.append('stock', prodForm.stock);
    if (prodForm.brand) formData.append('brand', prodForm.brand);
    if (prodForm.package_size) formData.append('package_size', prodForm.package_size);
    if (prodForm.description) formData.append('description', prodForm.description);
    if (prodImage) formData.append('image', prodImage);

    try {
      if (editingId) {
        await apiClient.put(`/products/${editingId}`, formData, { headers: { 'Content-Type': 'multipart/form-data' } });
        displayAlert('success', 'Product updated successfully!');
      } else {
        await apiClient.post('/products', formData, { headers: { 'Content-Type': 'multipart/form-data' } });
        displayAlert('success', `Product "${prodForm.name}" created!`);
      }
      setEditingId(null);
      setProdForm({ name: '', price: '', brand: '', category_id: '', stock: 20, package_size: '', description: '', image_url: '' });
      setProdImage(null);
      triggerReload();
    } catch (err) {
      displayAlert('error', getApiErrorMessage(err, 'Product operation failed.'));
    }
  };

  const handleEditProductClick = (product) => {
    setEditingId(product.id);
    setProdForm({
      name: product.name, price: product.price, brand: product.brand || '',
      category_id: product.category_id || '', stock: product.stock,
      package_size: product.package_size || '', description: product.description || '',
      image_url: product.image_url || ''
    });
    setProdImage(null);
    setActiveTab('products');
  };

  const handleDeleteProduct = async (id) => {
    if (!window.confirm("Delete this product permanently?")) return;
    try {
      await apiClient.delete(`/products/${id}?user_id=${adminId}`);
      displayAlert('success', 'Product dropped from inventory.');
      triggerReload();
    } catch (err) {
      displayAlert('error', getApiErrorMessage(err, 'Failed to delete product.'));
    }
  };

  const handleCarouselUpload = async (e) => {
    e.preventDefault();
    if (!carouselFiles || carouselFiles.length === 0) {
      displayAlert('error', 'Choose at least one image file first.');
      return;
    }

    setCarouselUploading(true);
    let successCount = 0;
    let failCount = 0;

    for (const file of carouselFiles) {
      const formData = new FormData();
      formData.append('user_id', adminId);
      formData.append('image', file);
      try {
        const response = await apiClient.post('/carousel-images', formData, { headers: { 'Content-Type': 'multipart/form-data' } });
        setCarouselImages(prev => [...prev, response.data]);
        successCount++;
      } catch (err) {
        failCount++;
      }
    }

    setCarouselFiles([]);
    setCarouselUploading(false);
    if (failCount === 0) {
      displayAlert('success', `${successCount} image${successCount !== 1 ? 's' : ''} uploaded successfully!`);
    } else {
      displayAlert('error', `${successCount} uploaded, ${failCount} failed. Try again for the failed ones.`);
    }
  };

  const handleDeleteCarouselImage = async (id) => {
    try {
      await apiClient.delete(`/carousel-images/${id}?user_id=${adminId}`);
      setCarouselImages(prev => prev.filter(img => img.id !== id));
      displayAlert('success', 'Carousel image removed.');
    } catch (err) {
      displayAlert('error', getApiErrorMessage(err, 'Failed to delete carousel image.'));
    }
  };

  const handleStaffSubmit = async (e) => {
    e.preventDefault();
    try {
      await apiClient.post('/users/access', {
        email: staffForm.email,
        role: staffForm.role
      });
      displayAlert('success', `${staffForm.role === 'super_admin' ? 'Super Admin' : 'Sub-Admin'} access granted to ${staffForm.email}.`);
      setStaffForm({ email: '', role: 'sub_admin' });
      setStaffTrigger(prev => prev + 1);
    } catch (err) {
      displayAlert('error', getApiErrorMessage(err, 'Failed to create staff account.'));
    }
  };

  const handleDeleteStaff = async (id, email) => {
    if (email === 'masterbright02@gmail.com') {
      displayAlert('error', 'Action Denied: You cannot delete the Master Super Admin.');
      return;
    }
    if (!window.confirm(`Are you sure you want to revoke access and delete ${email}?`)) return;

    try {
      await apiClient.delete(`/users/${id}`);
      displayAlert('success', 'Staff access revoked and account deleted.');
      setStaffTrigger(prev => prev + 1);
    } catch (err) {
      displayAlert('error', getApiErrorMessage(err, 'Failed to delete staff.'));
    }
  };

  const processedOrders = orders.map((o, idx) => ({ ...o, orderNumber: orders.length - idx }));

  const filteredOrders = processedOrders.filter(o =>
    (o.id || '').toString().toLowerCase().includes(searchQuery.toLowerCase()) ||
    (o.contact_phone && o.contact_phone.includes(searchQuery)) ||
    getCustomerName(o).toLowerCase().includes(searchQuery.toLowerCase()) ||
    getCustomerEmail(o).toLowerCase().includes(searchQuery.toLowerCase()) ||
    o.orderNumber.toString().includes(searchQuery)
  );

  const filteredProducts = products.filter(p =>
    p.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    (p.brand && p.brand.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  const filteredCategories = categories.filter(c =>
    c.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const filteredStaff = staffList.filter(s =>
    s.email.toLowerCase().includes(searchQuery.toLowerCase()) ||
    s.first_name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-gray-50 font-sans text-gray-900 pb-12">
      <nav className="bg-gray-950 text-white shadow-md p-3 flex flex-col md:flex-row justify-between items-center gap-3 px-4 sm:px-8 sticky top-0 z-40">
        <div className="flex items-center gap-3 w-full md:w-auto justify-center md:justify-start">
          <img src="/logo-circular.png" alt="C_Express" className="h-10 w-10 rounded-full object-contain bg-white" />
          <div>
            <span className="block font-black tracking-widest uppercase text-sm leading-none flex items-center gap-1.5">
              C_EXPRESS CONSOLE {isSuperAdmin && <Shield className="h-3.5 w-3.5 text-green-400" />}
            </span>
            <span className="block text-[10px] text-gray-400 font-mono mt-1 text-center md:text-left">
              v1.0.0 ({isSuperAdmin ? 'Super Admin' : 'Sub Admin'})
            </span>
          </div>
        </div>

        <div className="flex items-center gap-4 w-full md:w-auto justify-between md:justify-end">
          <button
            onClick={async () => {
              await handleLogout();
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

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 md:py-8">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center border-b border-gray-200 pb-5 mb-6 gap-4">
          <div>
            <h1 className="text-xl md:text-2xl font-black text-gray-950 tracking-tight">System Administration</h1>
            <p className="text-sm text-gray-500 mt-1">Manage products, categories, and fulfill incoming orders.</p>
          </div>

          {/* ✅ MOBILE FIX: Scrollable Tab Navigation */}
          <div className="flex flex-nowrap bg-gray-100 p-1.5 rounded-xl w-full md:w-auto overflow-x-auto snap-x hide-scrollbar">
            <button onClick={() => { setActiveTab('carousel'); setEditingId(null); setSearchQuery(''); }} className={`px-4 md:px-5 py-2 whitespace-nowrap rounded-lg text-sm font-bold transition-all flex items-center justify-center gap-2 snap-center ${activeTab === 'carousel' ? 'bg-white text-[#f68b1e] shadow-sm' : 'text-gray-600 hover:text-gray-900'}`}>
              <ImageIcon className="h-4 w-4" /> Carousel
            </button>
            <button onClick={() => { setActiveTab('orders'); setEditingId(null); setSearchQuery(''); }} className={`px-4 md:px-5 py-2 whitespace-nowrap rounded-lg text-sm font-bold transition-all flex items-center justify-center gap-2 snap-center ${activeTab === 'orders' ? 'bg-white text-[#f68b1e] shadow-sm' : 'text-gray-600 hover:text-gray-900'}`}>
              <Truck className="h-4 w-4" /> Orders
            </button>
            <button onClick={() => { setActiveTab('products'); setEditingId(null); setSearchQuery(''); }} className={`px-4 md:px-5 py-2 whitespace-nowrap rounded-lg text-sm font-bold transition-all flex items-center justify-center gap-2 snap-center ${activeTab === 'products' ? 'bg-white text-[#f68b1e] shadow-sm' : 'text-gray-600 hover:text-gray-900'}`}>
              <Package className="h-4 w-4" /> Products
            </button>
            <button onClick={() => { setActiveTab('categories'); setEditingId(null); setSearchQuery(''); }} className={`px-4 md:px-5 py-2 whitespace-nowrap rounded-lg text-sm font-bold transition-all flex items-center justify-center gap-2 snap-center ${activeTab === 'categories' ? 'bg-white text-[#f68b1e] shadow-sm' : 'text-gray-600 hover:text-gray-900'}`}>
              <Layers className="h-4 w-4" /> Categories
            </button>
            {isSuperAdmin && (
              <button onClick={() => { setActiveTab('staff'); setEditingId(null); setSearchQuery(''); }} className={`px-4 md:px-5 py-2 whitespace-nowrap rounded-lg text-sm font-bold transition-all flex items-center justify-center gap-2 snap-center ${activeTab === 'staff' ? 'bg-white text-[#f68b1e] shadow-sm' : 'text-gray-600 hover:text-gray-900'}`}>
                <Shield className="h-4 w-4" /> Staff Mgmt
              </button>
            )}
          </div>
        </div>

        <div className="mb-6 relative max-w-2xl">
          <input
            type="text"
            placeholder={`Search ${activeTab} data...`}
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-11 pr-4 py-3 bg-white border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#f68b1e] shadow-sm transition-all"
          />
          <Search className="absolute left-4 top-3.5 h-5 w-5 text-gray-400" />
          {searchQuery && (
            <button
              onClick={() => setSearchQuery('')}
              className="absolute right-3 top-3.5 text-gray-400 hover:text-gray-600 bg-gray-100 rounded-full p-0.5"
            >
              <X className="h-4 w-4" />
            </button>
          )}
        </div>

        {status.message && (
          <div className={`p-4 rounded-xl flex items-start gap-3 text-sm mb-6 max-w-2xl animate-fade-in shadow-sm ${status.type === 'success' ? 'bg-green-50 text-green-700 border border-green-100' : 'bg-red-50 text-red-700 border border-red-100'}`}>
            {status.type === 'success' ? <CheckCircle2 className="h-5 w-5 mt-0.5 flex-shrink-0" /> : <AlertCircle className="h-5 w-5 mt-0.5 flex-shrink-0" />}
            <span>{status.message}</span>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 md:gap-8">
          
          {activeTab === 'carousel' && (
            <div className="col-span-1 lg:col-span-3">
              <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-4 md:p-6 overflow-hidden">
                <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-4 gap-2">
                  <h3 className="text-sm font-bold text-gray-400 uppercase tracking-wider flex items-center gap-2">
                    <ImageIcon className="h-4 w-4" /> Storefront Carousel Images
                  </h3>
                  <span className="text-xs font-bold text-gray-500 bg-gray-100 px-2 py-1 rounded">{carouselImages.length} image{carouselImages.length !== 1 ? 's' : ''}</span>
                </div>

                <form onSubmit={handleCarouselUpload} className="mb-3">
                  <div className="flex flex-col sm:flex-row items-center gap-2 bg-gray-50 border border-gray-100 rounded-lg p-2">
                    <input
                      type="file"
                      accept="image/*"
                      multiple
                      onChange={(e) => setCarouselFiles(Array.from(e.target.files || []))}
                      className="w-full flex-grow text-xs file:mr-3 file:py-1.5 file:px-3 file:rounded-md file:border-0 file:text-[11px] file:font-bold file:bg-gray-900 file:text-white hover:file:bg-[#f68b1e] file:cursor-pointer"
                    />
                    <button
                      type="submit"
                      disabled={carouselUploading || carouselFiles.length === 0}
                      className="w-full sm:w-auto bg-[#f68b1e] text-white text-xs font-bold px-4 py-2 rounded-lg hover:bg-orange-600 transition-colors disabled:opacity-40 flex items-center justify-center gap-1.5 whitespace-nowrap"
                    >
                      <PlusCircle className="h-3.5 w-3.5" />
                      {carouselUploading ? 'Uploading...' : carouselFiles.length > 0 ? `Upload ${carouselFiles.length}` : 'Upload'}
                    </button>
                  </div>
                </form>
                <p className="text-[11px] text-gray-400 mb-6 leading-relaxed">
                  For best results on the storefront, use <span className="font-bold text-gray-500">landscape images</span> around <span className="font-bold text-gray-500">1600×900px</span> (16:9), under <span className="font-bold text-gray-500">5MB</span> each. You can select and upload several images at once.
                </p>

                {carouselImages.length === 0 ? (
                  <div className="text-center py-12 text-gray-400">
                    <ImageIcon className="h-12 w-12 mx-auto mb-3 opacity-20" />
                    <p>No carousel images yet. Upload some above.</p>
                  </div>
                ) : (
                  <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                    {carouselImages.map((img) => (
                      <div key={img.id} className="relative rounded-xl overflow-hidden border border-gray-100 shadow-sm aspect-video bg-gray-50">
                        <img src={"http://127.0.0.1" + img.image_url} alt="Carousel" className="w-full h-full object-cover" />
                        <button
                          onClick={() => handleDeleteCarouselImage(img.id)}
                          className="absolute top-1.5 right-1.5 bg-black/70 text-white h-6 w-6 rounded-full flex items-center justify-center hover:bg-red-600 transition-colors shadow-sm"
                        >
                          <X className="h-3.5 w-3.5" />
                        </button>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}

          {activeTab === 'orders' && (
            <div className="col-span-1 lg:col-span-3">
              <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-4 md:p-6 overflow-hidden">
                <div className="flex flex-col gap-3 mb-6 sm:flex-row sm:items-center sm:justify-between">
                  <h3 className="text-sm font-bold text-gray-400 uppercase tracking-wider flex items-center gap-2">
                    <FileText className="h-4 w-4" /> Customer Purchase Orders
                  </h3>
                  <div className="flex flex-wrap items-center gap-2">
                    {searchQuery && <span className="text-xs font-bold text-[#f68b1e] bg-orange-50 px-2 py-1 rounded">{filteredOrders.length} Results Found</span>}
                    {canClearTestOrders && (
                      <button onClick={handleClearTestOrders} className="rounded-lg border border-red-200 bg-red-50 px-2.5 py-1.5 text-[10px] font-black uppercase text-red-600 transition-colors hover:bg-red-600 hover:text-white">
                        Clear Tested Orders
                      </button>
                    )}
                  </div>
                </div>

                {filteredOrders.length === 0 ? (
                  <div className="text-center py-12 text-gray-400">
                    <Truck className="h-12 w-12 mx-auto mb-3 opacity-20" />
                    <p>{searchQuery ? "No matching orders found." : "No incoming orders found in the database."}</p>
                  </div>
                ) : (
                  // ✅ MOBILE FIX: Scrollable Tables
                  <div className="overflow-x-auto w-full -mx-4 px-4 md:mx-0 md:px-0">
                    <table className="w-full text-left border-collapse text-sm min-w-[700px]">
                      <thead>
                        <tr className="border-b border-gray-200 text-gray-500 font-bold bg-gray-50/50 uppercase text-xs tracking-wider">
                          <th className="p-4 rounded-tl-lg whitespace-nowrap">Order Number</th>
                          <th className="p-4 whitespace-nowrap">Customer</th>
                          <th className="p-4 whitespace-nowrap">Items</th>
                          <th className="p-4 whitespace-nowrap">Contact Number</th>
                          <th className="p-4 whitespace-nowrap">Status</th>
                          <th className="p-4 whitespace-nowrap">Payment</th>
                          <th className="p-4 text-right rounded-tr-lg whitespace-nowrap">Action</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-gray-100">
                        {filteredOrders.map((order) => (
                          <tr key={order.id} className="hover:bg-orange-50/30 transition-colors group">
                            <td className="p-4">
                              <div className="font-black text-gray-900 text-sm whitespace-nowrap">Order #{order.orderNumber}</div>
                              <div className="font-mono text-[10px] text-gray-400 mt-0.5 whitespace-nowrap">UUID: {(order.id || '').toString().substring(0, 8)}</div>
                            </td>
                            <td className="p-4">
                              <div className="font-bold text-gray-900 text-sm leading-tight whitespace-nowrap">{getCustomerName(order)}</div>
                              <div className="text-xs text-gray-400 mt-0.5 truncate max-w-[150px]">{getCustomerEmail(order)}</div>
                            </td>
                            <td className="p-4 font-bold text-gray-800">
                              <span className="bg-gray-100 text-gray-700 px-2.5 py-1 rounded text-xs whitespace-nowrap">
                                {getItemsCount(order)} units
                              </span>
                            </td>
                            <td className="p-4 text-gray-600 font-medium whitespace-nowrap">
                              {order.contact_phone || 'No phone'}
                            </td>
                            <td className="p-4 whitespace-nowrap">
                              {renderStatusBadge(order.status)}
                            </td>
                            <td className="p-4 whitespace-nowrap">
                              {order.payment_confirmed ? (
                                <div>
                                  <span className="bg-green-100 text-green-700 px-2 py-0.5 rounded text-[10px] font-black uppercase flex items-center gap-1 w-max">
                                    <CheckCircle2 className="h-3 w-3" /> Confirmed
                                  </span>
                                  {order.payment_confirmed_by && (
                                    <span className="block text-[10px] text-gray-400 mt-1">by {order.payment_confirmed_by}</span>
                                  )}
                                </div>
                              ) : (
                                <button
                                  onClick={() => handleConfirmPayment(order.id)}
                                  className="text-[10px] font-black uppercase bg-green-50 text-green-700 border border-green-200 px-2.5 py-1.5 rounded-lg hover:bg-green-600 hover:text-white transition-colors"
                                >
                                  Confirm Payment
                                </button>
                              )}
                            </td>
                            <td className="p-4 text-right">
                              <button
                                onClick={() => setViewOrder(order)}
                                className="text-xs font-bold bg-gray-900 text-white px-4 py-2 rounded-lg hover:bg-[#f68b1e] shadow-sm transition-all flex items-center gap-1.5 ml-auto whitespace-nowrap"
                              >
                                View Dispatch <ExternalLink className="h-3.5 w-3.5" />
                              </button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            </div>
          )}

          {activeTab === 'staff' && isSuperAdmin && (
            <>
              <div className="col-span-1">
                <div className="bg-white p-4 md:p-6 rounded-2xl border border-gray-100 shadow-sm lg:sticky lg:top-24">
                  <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
                    <UserPlus className="h-5 w-5 text-[#f68b1e]" /> Provision Sub-Admin
                  </h3>
                  <p className="text-xs text-gray-500 mb-5 leading-relaxed">
                    Sub-Admins can manage products and fulfill orders, but cannot access bank settings or add staff.
                  </p>

                  <form onSubmit={handleStaffSubmit} className="space-y-4">
                    <div>
                      <label className="block text-xs font-bold text-gray-500 uppercase mb-1">Email Address *</label>
                      <input required type="email" placeholder="existing-user@example.com" className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#f68b1e]" value={staffForm.email} onChange={e => setStaffForm({ ...staffForm, email: e.target.value })} />
                    </div>

                    <div>
                      <label className="block text-xs font-bold text-gray-500 uppercase mb-1">System Role *</label>
                      <select className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#f68b1e] bg-white" value={staffForm.role} onChange={e => setStaffForm({ ...staffForm, role: e.target.value })}>
                        <option value="sub_admin">Sub-Admin (Manage Products/Orders)</option>
                        <option value="super_admin">Super Admin (Full Access + Bank Details)</option>
                      </select>
                    </div>

                    <button type="submit" className="w-full bg-[#f68b1e] text-white py-2.5 rounded-lg text-sm font-bold hover:bg-orange-600 transition-colors shadow-sm mt-4 flex items-center justify-center gap-2">
                      <Shield className="h-4 w-4" /> Grant Access
                    </button>
                  </form>
                </div>
              </div>

              <div className="col-span-1 lg:col-span-2">
                <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-4 md:p-6 overflow-hidden">
                  <div className="flex justify-between items-center mb-6">
                    <h3 className="text-sm font-bold text-gray-400 uppercase tracking-wider flex items-center gap-2">
                      <Users className="h-4 w-4" /> Authorized System Users
                    </h3>
                    {searchQuery && <span className="text-xs font-bold text-[#f68b1e] bg-orange-50 px-2 py-1 rounded">{filteredStaff.length} Results</span>}
                  </div>

                  {filteredStaff.length === 0 ? (
                    <div className="text-center py-8 text-gray-400">No staff found matching "{searchQuery}".</div>
                  ) : (
                    // ✅ MOBILE FIX: Scrollable Tables
                    <div className="overflow-x-auto w-full -mx-4 px-4 md:mx-0 md:px-0">
                      <table className="w-full text-left border-collapse text-sm min-w-[500px]">
                        <thead>
                          <tr className="border-b border-gray-100 text-gray-400 font-semibold">
                            <th className="pb-3 whitespace-nowrap">Staff Member</th>
                            <th className="pb-3 whitespace-nowrap">Access Level</th>
                            <th className="pb-3 whitespace-nowrap">Contact</th>
                            <th className="pb-3 text-right whitespace-nowrap">Actions</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-100">
                          {filteredStaff.map(staff => {
                            const isStaffSuper = staff.is_super_admin === true || staff.is_super_admin === 1 || staff.is_super_admin === 'true';
                            return (
                              <tr key={staff.id} className="hover:bg-gray-50/50 transition-colors group">
                                <td className="py-3.5 font-medium text-gray-900">
                                  <div className="flex items-center gap-3">
                                    <div className={`h-8 w-8 rounded-full flex items-center justify-center text-white font-bold text-xs ${isStaffSuper ? 'bg-green-500' : 'bg-orange-400'} flex-shrink-0`}>
                                      {staff.first_name?.charAt(0).toUpperCase()}
                                    </div>
                                    <div>
                                      <div className="text-sm whitespace-nowrap">{staff.first_name} {staff.last_name}</div>
                                      <div className="text-xs text-gray-400 font-normal truncate max-w-[120px] md:max-w-[200px]">{staff.email}</div>
                                    </div>
                                  </div>
                                </td>
                                <td className="py-3.5">
                                  {isStaffSuper ? (
                                    <span className="bg-green-50 text-green-700 px-2 py-1 rounded text-[10px] font-bold uppercase flex items-center gap-1 w-max">
                                      <Shield className="h-3 w-3" /> Super Admin
                                    </span>
                                  ) : (
                                    <span className="bg-orange-50 text-orange-700 px-2 py-1 rounded text-[10px] font-bold uppercase flex items-center gap-1 w-max">
                                      <User className="h-3 w-3" /> Sub Admin
                                    </span>
                                  )}
                                </td>
                                <td className="py-3.5 text-gray-500 text-xs whitespace-nowrap">
                                  {staff.whatsapp_number || 'N/A'}
                                </td>
                                <td className="py-3.5 text-right">
                                  <button
                                    onClick={() => handleDeleteStaff(staff.id, staff.email)}
                                    className="text-xs font-bold text-red-500 hover:text-white bg-red-50 hover:bg-red-500 px-3 py-1.5 rounded transition-colors whitespace-nowrap"
                                  >
                                    Revoke
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
            </>
          )}

          {activeTab !== 'orders' && activeTab !== 'staff' && activeTab !== 'carousel' && (
            <>
              <div className="col-span-1">
                <div className="bg-white p-4 md:p-6 rounded-2xl border border-gray-100 shadow-sm lg:sticky lg:top-24">
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
                        <div className="flex flex-col sm:flex-row gap-2">
                          <button type="submit" className="flex-1 bg-[#f68b1e] text-white py-2 rounded-lg text-sm font-bold hover:bg-orange-600 transition-colors">
                            {editingId ? 'Update Category' : 'Save Category'}
                          </button>
                          {editingId && (
                            <button type="button" onClick={() => { setEditingId(null); setCatName(''); }} className="w-full sm:w-auto p-2 bg-gray-100 rounded-lg text-gray-500 hover:bg-gray-200 flex justify-center items-center">
                              <X className="h-4 w-4" /> <span className="sm:hidden ml-2 text-sm font-bold">Cancel</span>
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
                          <button onClick={() => { setEditingId(null); setProdForm({ name: '', price: '', brand: '', category_id: '', stock: 20, package_size: '', description: '', image_url: '' }); setProdImage(null); }} className="text-xs font-bold text-gray-400 hover:text-gray-600 flex items-center gap-1">
                            <X className="h-3.5 w-3.5" /> Clear Edit
                          </button>
                        )}
                      </div>
                      <form onSubmit={handleProductSubmit} className="space-y-3.5">
                        <div>
                          <label className="block text-xs font-bold text-gray-500 uppercase mb-1">Product Title *</label>
                          <input required type="text" className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#f68b1e]" value={prodForm.name} onChange={e => setProdForm({ ...prodForm, name: e.target.value })} />
                        </div>
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                          <div>
                            <label className="block text-xs font-bold text-gray-500 uppercase mb-1">Price (₦) *</label>
                            <input required type="number" step="0.01" className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#f68b1e]" value={prodForm.price} onChange={e => setProdForm({ ...prodForm, price: e.target.value })} />
                          </div>
                          <div>
                            <label className="block text-xs font-bold text-gray-500 uppercase mb-1">Stock Vol *</label>
                            <input required type="number" className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#f68b1e]" value={prodForm.stock} onChange={e => setProdForm({ ...prodForm, stock: e.target.value })} />
                          </div>
                        </div>
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                          <div>
                            <label className="block text-xs font-bold text-gray-500 uppercase mb-1">Category Link *</label>
                            <select required className="w-full px-2 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#f68b1e]" value={prodForm.category_id} onChange={e => setProdForm({ ...prodForm, category_id: e.target.value })}>
                              <option value="">Select...</option>
                              {categories.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
                            </select>
                          </div>
                          <div>
                            <label className="block text-xs font-bold text-gray-500 uppercase mb-1">Brand</label>
                            <input type="text" className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#f68b1e]" value={prodForm.brand} onChange={e => setProdForm({ ...prodForm, brand: e.target.value })} />
                          </div>
                        </div>
                        <div>
                          <label className="block text-xs font-bold text-gray-500 uppercase mb-1">Package Sizing</label>
                          <input type="text" placeholder="e.g. 50cl, 1kg" className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#f68b1e]" value={prodForm.package_size} onChange={e => setProdForm({ ...prodForm, package_size: e.target.value })} />
                        </div>
                        <div>
                          <label className="block text-xs font-bold text-gray-500 uppercase mb-1 flex items-center gap-1">
                            <ImageIcon className="h-3.5 w-3.5" /> Product Image
                          </label>
                          <div className="flex items-center gap-3">
                            {(prodImage || prodForm.image_url) && (
                              <img
                                src={prodImage ? URL.createObjectURL(prodImage) : prodForm.image_url}
                                alt="Preview"
                                className="w-12 h-12 rounded-lg object-cover border border-gray-200 flex-shrink-0"
                              />
                            )}
                            <input
                              type="file"
                              accept="image/*"
                              onChange={(e) => setProdImage(e.target.files?.[0] || null)}
                              className="flex-grow w-full overflow-hidden text-xs file:mr-3 file:py-1.5 file:px-3 file:rounded-md file:border-0 file:text-[11px] file:font-bold file:bg-gray-900 file:text-white hover:file:bg-[#f68b1e] file:cursor-pointer"
                            />
                          </div>
                          {editingId && !prodImage && prodForm.image_url && (
                            <p className="text-[11px] text-gray-400 mt-1.5">Current image shown above. Choose a file only if you want to replace it.</p>
                          )}
                        </div>

                        <button type="submit" className="w-full bg-[#f68b1e] text-white py-2.5 rounded-lg text-sm font-bold hover:bg-orange-600 transition-colors shadow-sm mt-4">
                          {editingId ? 'Apply Database Changes' : 'Commit to Storage'}
                        </button>
                      </form>
                    </>
                  )}
                </div>
              </div>

              <div className="col-span-1 lg:col-span-2">
                <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-4 md:p-6 overflow-hidden">
                  {activeTab === 'categories' ? (
                    <div>
                      <div className="flex justify-between items-center mb-4">
                        <h3 className="text-sm font-bold text-gray-400 uppercase tracking-wider">Database Categories</h3>
                        {searchQuery && <span className="text-xs font-bold text-[#f68b1e] bg-orange-50 px-2 py-1 rounded">{filteredCategories.length} Results</span>}
                      </div>
                      {filteredCategories.length === 0 ? (
                        <div className="text-center py-8 text-gray-400">No categories found matching "{searchQuery}".</div>
                      ) : (
                        <div className="divide-y divide-gray-100">
                          {filteredCategories.map(cat => (
                            <div key={cat.id} className="py-3 flex justify-between items-center group">
                              <div className="flex items-center gap-2">
                                <Tag className="h-4 w-4 text-[#f68b1e] flex-shrink-0" />
                                <span className="font-medium text-gray-800 text-sm truncate">{cat.name}</span>
                                <span className="text-[10px] text-gray-300 font-mono hidden sm:inline">({cat.id.substring(0, 8)})</span>
                              </div>
                              <div className="flex items-center gap-1 opacity-100 md:opacity-80 group-hover:opacity-100 transition-opacity">
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
                      )}
                    </div>
                  ) : (
                    <div>
                      <div className="flex justify-between items-center mb-4">
                        <h3 className="text-sm font-bold text-gray-400 uppercase tracking-wider">Warehouse SKU Records</h3>
                        {searchQuery && <span className="text-xs font-bold text-[#f68b1e] bg-orange-50 px-2 py-1 rounded">{filteredProducts.length} Results</span>}
                      </div>

                      {filteredProducts.length === 0 ? (
                        <div className="text-center py-8 text-gray-400">No products found matching "{searchQuery}".</div>
                      ) : (
                        // ✅ MOBILE FIX: Scrollable Tables
                        <div className="overflow-x-auto w-full -mx-4 px-4 md:mx-0 md:px-0">
                          <table className="w-full text-left border-collapse text-sm min-w-[500px]">
                            <thead>
                              <tr className="border-b border-gray-100 text-gray-400 font-semibold">
                                <th className="pb-3 whitespace-nowrap">Product</th>
                                <th className="pb-3 whitespace-nowrap">Category</th>
                                <th className="pb-3 whitespace-nowrap">Price</th>
                                <th className="pb-3 whitespace-nowrap">Stock</th>
                                <th className="pb-3 text-right whitespace-nowrap">Actions</th>
                              </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-100">
                              {filteredProducts.map(prod => (
                                <tr key={prod.id} className="hover:bg-gray-50/50 transition-colors group">
                                  <td className="py-3.5 font-medium text-gray-900 flex items-center gap-3">
                                    {prod.image_url ? (
                                      <img src={prod.image_url} alt={prod.name} className="w-8 h-8 rounded object-cover border border-gray-200 flex-shrink-0" />
                                    ) : (
                                      <div className="w-8 h-8 rounded bg-gray-100 border border-gray-200 flex items-center justify-center flex-shrink-0">
                                        <ImageIcon className="h-4 w-4 text-gray-400" />
                                      </div>
                                    )}
                                    <div>
                                      <div className="truncate max-w-[150px] sm:max-w-xs">{prod.name}</div>
                                      <div className="text-xs text-gray-400 font-normal truncate max-w-[150px] sm:max-w-xs">{prod.brand || 'No Brand'}</div>
                                    </div>
                                  </td>
                                  <td className="py-3.5 text-gray-500 whitespace-nowrap">
                                    {categories.find(c => c.id === prod.category_id)?.name || 'Unlinked'}
                                  </td>
                                  <td className="py-3.5 font-bold text-gray-800 whitespace-nowrap">₦{parseFloat(prod.price).toLocaleString()}</td>
                                  <td className="py-3.5 whitespace-nowrap">
                                    <span className={`px-2 py-0.5 rounded-full text-xs font-bold ${prod.stock > 5 ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'}`}>
                                      {prod.stock} units
                                    </span>
                                  </td>
                                  <td className="py-3.5 text-right whitespace-nowrap">
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
                      )}
                    </div>
                  )}
                </div>
              </div>
            </>
          )}
        </div>
      </div>

      {viewOrder && (
        <div
          className="fixed inset-0 bg-black/60 z-[100] flex items-center justify-center p-4 backdrop-blur-sm animate-fade-in"
          onClick={() => setViewOrder(null)}
        >
          {/* ✅ MOBILE FIX: Safe Modals */}
          <div
            className="bg-white rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto shadow-2xl relative flex flex-col"
            onClick={e => e.stopPropagation()}
          >
            <div className="bg-gray-950 p-4 sm:p-6 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 sticky top-0 z-10 flex-shrink-0">
              <div>
                <h3 className="text-base sm:text-lg font-black text-white flex items-center gap-2">
                  Dispatch Invoice <span className="text-[#f68b1e]">#{viewOrder.orderNumber}</span>
                </h3>
                <div className="flex items-center gap-2 mt-1">
                  {renderStatusBadge(viewOrder.status)}
                  <p className="text-xs text-gray-400 font-mono">UUID: {(viewOrder.id || '').toString().substring(0, 8)}</p>
                </div>
              </div>
              <button
                onClick={() => setViewOrder(null)}
                className="absolute top-4 right-4 sm:static bg-white/10 p-2 rounded-full text-gray-400 hover:text-white border border-white/5 hover:bg-white/20 transition-colors shadow-sm"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            <div className="p-4 sm:p-6 space-y-6 flex-grow">
              <div className="bg-orange-50/50 border border-orange-100 rounded-xl p-4 sm:p-5 space-y-4">
                <h4 className="text-xs font-bold text-[#f68b1e] uppercase tracking-wider border-b border-orange-100 pb-2">Customer & Delivery Info</h4>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div className="flex items-start gap-3">
                    <User className="h-4 w-4 text-orange-500 mt-0.5" />
                    <div>
                      <span className="block text-xs font-bold text-gray-400 uppercase">Customer Name</span>
                      <span className="text-sm font-bold text-gray-900 leading-none">{getCustomerName(viewOrder)}</span>
                    </div>
                  </div>

                  <div className="flex items-start gap-3">
                    <FileText className="h-4 w-4 text-orange-500 mt-0.5" />
                    <div className="w-full pr-2">
                      <span className="block text-xs font-bold text-gray-400 uppercase">Customer Email</span>
                      <span className="text-sm font-bold text-gray-900 leading-none break-words block">{getCustomerEmail(viewOrder)}</span>
                    </div>
                  </div>

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
                        <a href={viewOrder.gps_link} target="_blank" rel="noopener noreferrer" className="text-sm font-black text-blue-600 hover:text-blue-800 hover:underline flex items-center gap-1 bg-blue-50 px-2 py-0.5 rounded border border-blue-100 w-max mt-1">
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
                    <span className="text-sm font-medium text-gray-800 bg-white p-3 border border-gray-100 rounded-lg block mt-1 w-full shadow-sm break-words">
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
                      <div key={index} className="flex items-center gap-3 sm:gap-4 bg-gray-50 border border-gray-100 p-2.5 sm:p-3 rounded-xl shadow-sm">
                        <div className="w-10 h-10 sm:w-12 sm:h-12 bg-white rounded-lg flex items-center justify-center border border-gray-100 flex-shrink-0 p-1">
                          {productInfo?.image_url ? (
                            <img src={productInfo.image_url} alt={productInfo.name} className="w-full h-full object-cover rounded" />
                          ) : (
                            <ShoppingBag className="h-4 w-4 sm:h-5 sm:w-5 text-gray-300" />
                          )}
                        </div>
                        <div className="flex-grow min-w-0">
                          <p className="text-xs sm:text-sm font-bold text-gray-800 line-clamp-1">{productInfo ? productInfo.name : 'Unknown Product'}</p>
                          <p className="text-[9px] sm:text-[10px] text-gray-400 font-mono mt-0.5 truncate">ID: {item.product_id.substring(0, 8)}</p>
                        </div>
                        <div className="text-right bg-white px-2 sm:px-3 py-1 sm:py-1.5 rounded-lg border border-gray-100 flex-shrink-0">
                          <span className="text-[9px] sm:text-[10px] text-gray-400 uppercase font-bold block mb-1">Qty</span>
                          <span className="text-sm sm:text-lg font-black text-[#f68b1e] leading-none">x{item.quantity}</span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>

              <div className="bg-gray-50 p-4 border-t border-gray-100 rounded-xl">
                <h4 className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-3">Payment Verification</h4>
                {viewOrder.payment_confirmed ? (
                  <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between bg-green-50 border border-green-200 rounded-lg px-4 py-3 gap-2">
                    <span className="flex items-center gap-2 text-green-700 font-black text-xs uppercase">
                      <CheckCircle2 className="h-4 w-4" /> Payment Confirmed
                    </span>
                    {viewOrder.payment_confirmed_by && (
                      <span className="text-[10px] sm:text-[11px] text-green-700/70 font-medium break-all text-left sm:text-right">by {viewOrder.payment_confirmed_by}</span>
                    )}
                  </div>
                ) : (
                  <button
                    onClick={() => handleConfirmPayment(viewOrder.id)}
                    className="w-full bg-green-600 text-white text-xs font-black uppercase py-2.5 sm:py-3 rounded-lg hover:bg-green-700 transition-colors flex items-center justify-center gap-2"
                  >
                    <CheckCircle2 className="h-4 w-4" /> Confirm Payment
                  </button>
                )}
              </div>

              <div className="bg-gray-50 p-4 border-t border-gray-100 rounded-xl">
                <h4 className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-3">Update Order Pipeline</h4>
                <div className="grid grid-cols-2 sm:flex sm:flex-wrap gap-2">
                  <button onClick={() => handleUpdateStatus(viewOrder.id, 'Pending')} className="w-full sm:flex-1 bg-white border border-gray-200 text-gray-600 text-xs font-bold py-2 rounded-lg hover:bg-gray-100 transition-colors">Pending</button>
                  <button onClick={() => handleUpdateStatus(viewOrder.id, 'Processing')} className="w-full sm:flex-1 bg-blue-50 border border-blue-200 text-blue-700 text-xs font-bold py-2 rounded-lg hover:bg-blue-100 transition-colors">Processing</button>
                  <button onClick={() => handleUpdateStatus(viewOrder.id, 'Dispatched')} className="w-full sm:flex-1 bg-orange-50 border border-orange-200 text-orange-700 text-xs font-bold py-2 rounded-lg hover:bg-orange-100 transition-colors">Dispatched</button>
                  <button onClick={() => handleUpdateStatus(viewOrder.id, 'Delivered')} className="w-full sm:flex-1 bg-green-50 border border-green-200 text-green-700 text-xs font-bold py-2 rounded-lg hover:bg-green-100 transition-colors">Delivered</button>
                </div>
              </div>

            </div>
            
            {/* Modal Sticky Footer */}
            <div className="bg-white p-4 sm:p-6 border-t border-gray-100 flex flex-col sm:flex-row gap-3 mt-auto sticky bottom-0 z-10">
                <button
                  onClick={() => handleCancelOrder(viewOrder.id)}
                  className="w-full sm:flex-1 bg-red-50 text-red-600 text-sm font-bold py-3 rounded-xl hover:bg-red-100 transition-colors flex justify-center items-center gap-2 shadow-sm order-2 sm:order-1"
                >
                  <Trash2 className="h-4 w-4" /> Cancel & Return Stock
                </button>
                <button
                  onClick={() => setViewOrder(null)}
                  className="w-full sm:flex-1 bg-gray-900 text-white text-sm font-bold py-3 rounded-xl hover:bg-gray-800 transition-colors order-1 sm:order-2"
                >
                  Done
                </button>
              </div>
          </div>
        </div>
      )}
    </div>
  );
}