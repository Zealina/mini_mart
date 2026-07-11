import React, { useState, useEffect } from 'react';
import { Link, Navigate } from 'react-router-dom';
import { ArrowLeft, Package, Clock, CheckCircle2, X, MapPin, Phone, ShoppingBag } from 'lucide-react';
import apiClient from '../api/client';

export default function Orders({ user, products }) {
  const [orders, setOrders] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedOrder, setSelectedOrder] = useState(null);

  const getItemsCount = (order) => {
    const items = order.order_items || order.items;
    if (!items) return 0;
    if (Array.isArray(items)) return items.length;
    if (typeof items === 'object') return Object.keys(items).length;
    return 0;
  };

  useEffect(() => {
    if (!user) return;
    const fetchOrders = async () => {
      try {
        const userId = user.id || user.user_id || user.uuid || (user.user && user.user.id);
        const response = await apiClient.get('/orders');
        
        const myOrders = Array.isArray(response.data) 
          ? response.data.filter(o => o.user_id === userId) 
          : [];
        
        setOrders(myOrders.reverse());
      } catch (error) {
        console.error("Failed to fetch orders:", error);
      } finally {
        setIsLoading(false);
      }
    };
    fetchOrders();
  }, [user]);

  if (!user) return <Navigate to="/auth" />;

  return (
    <div className="min-h-screen bg-[#f1f1f2] font-sans text-[#282828] flex flex-col relative">
      <nav className="bg-white shadow-sm p-4 sticky top-0 z-40">
        <div className="max-w-5xl mx-auto flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2 text-gray-500 hover:text-[#f68b1e] font-medium transition-colors">
            <ArrowLeft className="h-5 w-5" /> Back to Storefront
          </Link>
          <span className="font-black text-[#f68b1e] text-2xl tracking-tight">FOOD MART</span>
        </div>
      </nav>

      <main className="flex-grow max-w-5xl mx-auto px-4 py-8 w-full">
        <h2 className="text-2xl font-bold text-gray-800 mb-6 flex items-center gap-2">
          <Package className="h-6 w-6 text-[#f68b1e]" /> My Orders
        </h2>

        {isLoading ? (
          <div className="text-center py-20 text-gray-500 font-medium">Fetching your order history...</div>
        ) : orders.length === 0 ? (
          <div className="bg-white rounded-xl border border-gray-100 p-12 text-center shadow-sm">
            <Package className="h-16 w-16 text-gray-200 mx-auto mb-4 stroke-1" />
            <h3 className="text-xl font-bold text-gray-700 mb-1">No orders yet!</h3>
            <p className="text-gray-400 text-sm mb-6">You haven't placed any orders. Start shopping to see them here.</p>
            <Link to="/" className="inline-block bg-[#f68b1e] text-white px-8 py-3 rounded-lg font-bold hover:bg-orange-600 transition-colors shadow-sm">START SHOPPING</Link>
          </div>
        ) : (
          <div className="space-y-4">
            {orders.map((order, idx) => (
              <div key={order.id || idx} className="bg-white rounded-xl border border-gray-100 p-6 shadow-sm hover:shadow-md transition-all">
                <div className="flex justify-between items-start border-b border-gray-50 pb-4 mb-4">
                  <div>
                    <p className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-1">Order ID: {order.id?.substring(0, 8) || 'N/A'}</p>
                    <p className="text-sm font-medium text-gray-800 flex items-center gap-1.5"><Clock className="h-4 w-4 text-gray-400" /> Placed successfully</p>
                  </div>
                  <span className="bg-green-50 text-green-700 border border-green-100 px-3 py-1 rounded-full text-xs font-bold flex items-center gap-1.5 shadow-sm">
                    <CheckCircle2 className="h-3.5 w-3.5" /> Confirmed
                  </span>
                </div>
                <div className="flex justify-between items-end">
                  <div className="text-sm text-gray-500">Total Items: <span className="font-bold text-gray-800">{getItemsCount(order)} Products</span></div>
                  <button onClick={() => setSelectedOrder(order)} className="text-sm font-bold text-[#f68b1e] hover:text-orange-600 transition-colors">View Details</button>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>

      {/* ORDER DETAILS MODAL */}
      {selectedOrder && (
        <div className="fixed inset-0 bg-black/60 z-[100] flex items-center justify-center p-4 backdrop-blur-sm animate-fade-in" onClick={() => setSelectedOrder(null)}>
          <div className="bg-white rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto shadow-2xl relative" onClick={e => e.stopPropagation()}>
            <div className="bg-gray-50 p-6 border-b border-gray-100 flex justify-between items-center sticky top-0 z-10">
              <div>
                <h3 className="text-lg font-black text-gray-900">Order Invoice</h3>
                <p className="text-xs text-gray-500 font-mono mt-1">ID: {selectedOrder.id}</p>
              </div>
              <button onClick={() => setSelectedOrder(null)} className="bg-white p-2 rounded-full text-gray-500 hover:text-red-500 border border-gray-200 hover:bg-red-50 shadow-sm"><X className="h-5 w-5" /></button>
            </div>

            <div className="p-6 space-y-6">
              <div className="bg-orange-50/50 border border-orange-100 rounded-xl p-4 space-y-3">
                <h4 className="text-xs font-bold text-[#f68b1e] uppercase tracking-wider mb-2">Delivery Details</h4>
                <div className="flex items-start gap-3">
                  <MapPin className="h-4 w-4 text-orange-400 mt-0.5" />
                  <div>
                    <span className="block text-xs font-bold text-gray-400 uppercase">Address</span>
                    <span className="text-sm font-medium text-gray-800">{selectedOrder.delivery_address || 'No address provided'}</span>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <Phone className="h-4 w-4 text-orange-400 mt-0.5" />
                  <div>
                    <span className="block text-xs font-bold text-gray-400 uppercase">Contact Phone</span>
                    <span className="text-sm font-medium text-gray-800">{selectedOrder.contact_phone || 'No phone provided'}</span>
                  </div>
                </div>
              </div>

              <div>
                <h4 className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-3 border-b border-gray-100 pb-2">Purchased Items</h4>
                <div className="space-y-3">
                  {selectedOrder.order_items?.map((item, index) => {
                    const productInfo = products.find(p => p.id === item.product_id);
                    return (
                      <div key={index} className="flex items-center gap-4 bg-gray-50 border border-gray-100 p-3 rounded-xl">
                        <div className="w-12 h-12 bg-white rounded-lg flex items-center justify-center border border-gray-100 flex-shrink-0">
                          {productInfo?.image_url ? <img src={productInfo.image_url} alt={productInfo.name} className="w-full h-full object-cover rounded-lg" /> : <ShoppingBag className="h-5 w-5 text-gray-300" />}
                        </div>
                        <div className="flex-grow">
                          <p className="text-sm font-bold text-gray-800 line-clamp-1">{productInfo ? productInfo.name : 'Unknown Product'}</p>
                          <p className="text-xs text-gray-500 font-mono mt-0.5">ID: {item.product_id.substring(0,8)}</p>
                        </div>
                        <div className="text-right">
                          <span className="text-xs text-gray-400 uppercase font-bold block">Qty</span>
                          <span className="text-sm font-black text-gray-900">x{item.quantity}</span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>

              <div className="bg-gray-50 p-4 rounded-xl text-center">
                <p className="text-xs text-gray-500 font-medium">Payment Method: <span className="font-bold text-green-600">CASH ON DELIVERY</span></p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}