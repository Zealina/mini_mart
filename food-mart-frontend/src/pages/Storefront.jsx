import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Database, User, LogOut, ShoppingCart, Search, Grid, ShieldCheck, ShoppingBag, ChevronDown, Package, Settings, X, Tag, ChevronLeft, ChevronRight } from 'lucide-react';

export default function Storefront({ user, handleLogout, products, categories, addToCart, cartCount }) {
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);
  const [viewProduct, setViewProduct] = useState(null);

  // ✅ STATE & LOGIC FOR THE HERO SLIDER
  const [currentSlide, setCurrentSlide] = useState(0);
  
  const slides = [
    { id: 1, image: '/slider1.jpeg', alt: 'Everyday Needs Delivered Fast' },
    { id: 2, image: '/slider2.jpeg', alt: '1 Year Anniversary C_Express' },
    { id: 3, image: '/slider3.jpeg', alt: 'Hello July Good Vibes' }
  ];

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentSlide((prev) => (prev === slides.length - 1 ? 0 : prev + 1));
    }, 8000);
    return () => clearInterval(timer);
  }, [slides.length]);

  const actualUser = user?.user || user;
  const isAdmin = actualUser && (actualUser.is_admin == 1 || actualUser.is_admin === true);

  const filteredProducts = products.filter(product => {
    const matchesCategory = selectedCategory ? product.category_id === selectedCategory : true;
    const matchesSearch = searchQuery
      ? product.name.toLowerCase().includes(searchQuery.toLowerCase()) || 
        (product.brand && product.brand.toLowerCase().includes(searchQuery.toLowerCase()))
      : true;
    return matchesCategory && matchesSearch;
  });

  return (
    <div className="min-h-screen bg-[#f1f1f2] font-sans text-[#282828] flex flex-col relative">
      
      {isAdmin && (
        <div className="bg-green-200 text-green-900 text-xs font-bold py-1.5 px-4 flex justify-center items-center gap-2 tracking-wide">
          <ShieldCheck className="h-4 w-4" />
          SECURE ADMIN SESSION ACTIVE
        </div>
      )}

      <nav className="bg-white shadow-sm p-3 flex justify-between items-center px-4 sm:px-8 sticky top-0 z-40">
        <Link to="/" className="flex items-center">
          {/* ✅ FIXED TYPO IN THE IMAGE SRC */}
          <img src="/logo-horizontal.jpg" alt="C_Express Mini-Mart" className="h-12 object-contain mix-blend-multiply" />
        </Link>
        
        <div className="hidden md:flex flex-1 max-w-xl mx-8 relative">
          <input 
            type="text" 
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search products, brands and categories..." 
            className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#f68b1e] transition-all"
          />
          <Search className="absolute left-3 top-2.5 h-5 w-5 text-gray-400" />
        </div>

        <div className="flex items-center space-x-6">
          {isAdmin && (
            <Link to="/admin" className="text-xs font-bold text-gray-600 hover:text-[#f68b1e] border border-gray-200 px-3 py-1.5 rounded-lg hidden md:flex items-center gap-1.5 transition-colors shadow-sm">
              <Database className="h-3.5 w-3.5 text-[#f68b1e]" /> Enter Console
            </Link>
          )}

          {actualUser ? (
            <div className="relative">
              <button 
                onClick={() => setIsUserMenuOpen(!isUserMenuOpen)}
                className="flex items-center space-x-2 text-gray-700 hover:text-[#f68b1e] font-medium transition-colors cursor-pointer p-1"
              >
                <User className="h-5 w-5 text-[#f68b1e]" />
                <span className="text-sm">Hi, {actualUser.first_name || 'User'}</span>
                <ChevronDown className={`h-4 w-4 transition-transform duration-200 ${isUserMenuOpen ? 'rotate-180' : ''}`} />
              </button>

              {isUserMenuOpen && (
                <div className="absolute right-0 mt-3 w-56 bg-white rounded-xl shadow-xl border border-gray-100 overflow-hidden z-50 animate-fade-in">
                  <div className="p-4 border-b border-gray-50 bg-gray-50/50">
                    <p className="text-sm font-bold text-gray-900">{actualUser.first_name} {actualUser.last_name || ''}</p>
                    <p className="text-xs text-gray-500 truncate">{actualUser.email}</p>
                  </div>
                  <div className="p-2 flex flex-col">
                    <Link to="/orders" className="flex items-center gap-3 px-3 py-2.5 text-sm font-medium text-gray-700 hover:bg-orange-50 hover:text-[#f68b1e] rounded-lg transition-colors">
                      <Package className="h-4 w-4" /> My Orders
                    </Link>
                    <Link to="/settings" className="flex items-center gap-3 px-3 py-2.5 text-sm font-medium text-gray-700 hover:bg-orange-50 hover:text-[#f68b1e] rounded-lg transition-colors">
                      <Settings className="h-4 w-4" /> Account Settings
                    </Link>
                  </div>
                  <div className="p-2 border-t border-gray-50">
                    <button 
                      onClick={() => {
                        setIsUserMenuOpen(false);
                        handleLogout();
                      }} 
                      className="w-full flex items-center gap-3 px-3 py-2.5 text-sm font-bold text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                    >
                      <LogOut className="h-4 w-4" /> Logout
                    </button>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <Link to="/auth" className="flex items-center space-x-2 text-gray-700 hover:text-[#f68b1e] font-medium transition-colors">
              <User className="h-6 w-6" />
              <span className="hidden md:inline text-sm">Login / Register</span>
            </Link>
          )}
          
          <Link to="/cart" className="flex items-center space-x-1 text-gray-700 hover:text-[#f68b1e] transition-colors relative">
            <ShoppingCart className="h-6 w-6" />
            <span className="hidden md:inline font-medium text-sm">Cart</span>
            {cartCount > 0 && (
              <span className="absolute -top-2 -right-2 bg-[#f68b1e] text-white text-xs font-bold rounded-full h-5 w-5 flex items-center justify-center shadow-sm">
                {cartCount}
              </span>
            )}
          </Link>
        </div>
      </nav>

      <main className="flex-grow max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 w-full">
        
        {/* ✅ DYNAMIC HERO SLIDER */}
        <div className="relative w-full h-[250px] md:h-[400px] rounded-2xl overflow-hidden shadow-md mb-8 group bg-white">
          {slides.map((slide, index) => (
            <div
              key={slide.id}
              className={`absolute inset-0 transition-opacity duration-1000 ease-in-out ${index === currentSlide ? 'opacity-100 z-10' : 'opacity-0 z-0'}`}
            >
              <img 
                src={slide.image} 
                alt={slide.alt} 
                className="w-full h-full object-cover md:object-contain bg-gray-50" 
              />
            </div>
          ))}
          
          <div className="absolute bottom-4 left-0 right-0 z-20 flex justify-center gap-2">
            {slides.map((_, index) => (
              <button
                key={index}
                onClick={() => setCurrentSlide(index)}
                className={`h-2.5 rounded-full transition-all duration-300 shadow-sm ${index === currentSlide ? 'bg-[#f68b1e] w-8' : 'bg-white/80 hover:bg-white w-2.5'}`}
                aria-label={`Go to slide ${index + 1}`}
              />
            ))}
          </div>
          
          <button 
            onClick={() => setCurrentSlide(prev => prev === 0 ? slides.length - 1 : prev - 1)} 
            className="absolute left-4 top-1/2 -translate-y-1/2 z-20 bg-black/20 hover:bg-black/40 text-white p-2 rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-300 backdrop-blur-sm"
          >
            <ChevronLeft className="h-6 w-6" />
          </button>
          <button 
            onClick={() => setCurrentSlide(prev => prev === slides.length - 1 ? 0 : prev + 1)} 
            className="absolute right-4 top-1/2 -translate-y-1/2 z-20 bg-black/20 hover:bg-black/40 text-white p-2 rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-300 backdrop-blur-sm"
          >
            <ChevronRight className="h-6 w-6" />
          </button>
        </div>

        <div className="flex flex-col lg:flex-row gap-8">
          <div className="w-full lg:w-64 flex-shrink-0">
            <div className="bg-white rounded-xl p-5 border border-gray-100 shadow-sm sticky top-24">
              <h3 className="text-sm font-bold text-gray-900 uppercase tracking-wider mb-4 flex items-center gap-2">
                <Grid className="h-4 w-4 text-[#f68b1e]" /> Categories
              </h3>
              <div className="relative">
                <select
                  value={selectedCategory || ''}
                  onChange={(e) => setSelectedCategory(e.target.value || null)}
                  className="w-full appearance-none bg-gray-50 border border-gray-200 text-gray-700 py-3 px-4 pr-8 rounded-lg text-sm font-medium focus:outline-none focus:ring-2 focus:ring-[#f68b1e] focus:border-transparent transition-all cursor-pointer shadow-sm"
                >
                  <option value="">All Categories</option>
                  {categories.map(cat => (
                    <option key={cat.id} value={cat.id}>{cat.name}</option>
                  ))}
                </select>
              </div>
            </div>
          </div>

          <div className="flex-grow">
            <div className="mb-6 flex items-center justify-between border-b border-gray-100 pb-4">
              <h2 className="text-xl font-bold text-gray-800">
                {selectedCategory ? categories.find(c => c.id === selectedCategory)?.name : 'All Products'}
              </h2>
              <span className="text-sm text-gray-500 font-medium">{filteredProducts.length} Items found</span>
            </div>
            
            {filteredProducts.length === 0 ? (
              <div className="bg-white rounded-xl border border-gray-100 p-16 text-center shadow-sm">
                <ShoppingBag className="h-16 w-16 text-gray-300 mx-auto stroke-1 mb-4" />
                <h3 className="text-lg font-bold text-gray-700">No Products Found</h3>
              </div>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-6">
                {filteredProducts.map(product => (
                  <div 
                    key={product.id} 
                    onClick={() => setViewProduct(product)}
                    className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden hover:shadow-xl hover:-translate-y-1 transition-all duration-300 group flex flex-col cursor-pointer"
                  >
                    <div className="relative h-48 overflow-hidden bg-gray-50 flex items-center justify-center">
                      {product.image_url ? (
                        <img src={product.image_url} alt={product.name} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300" />
                      ) : (
                        <ShoppingBag className="h-12 w-12 text-gray-300 stroke-1" />
                      )}
                    </div>
                    <div className="p-4 flex flex-col flex-grow">
                      <h3 className="text-sm font-semibold text-gray-800 line-clamp-2 h-10 leading-tight group-hover:text-[#f68b1e] transition-colors">{product.name}</h3>
                      <p className="text-xs text-gray-400 mt-1">{product.brand || 'Generic'}</p>
                      <div className="mt-auto pt-4 border-t border-gray-50 flex flex-col">
                        <span className="text-lg font-bold text-gray-900">₦{parseFloat(product.price).toLocaleString()}</span>
                        {product.stock <= 0 ? (
                          <span className="text-xs font-semibold text-red-500 mt-2 text-center bg-red-50 py-1.5 rounded-lg">Out Of Stock</span>
                        ) : (
                          <button 
                            onClick={(e) => { e.stopPropagation(); addToCart(product); }}
                            className="w-full mt-3 bg-white border border-[#f68b1e] text-[#f68b1e] py-2 rounded-lg text-sm font-bold hover:bg-[#f68b1e] hover:text-white transition-colors shadow-sm flex justify-center items-center gap-2"
                          >
                            <ShoppingCart className="h-4 w-4" /> ADD TO CART
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </main>

      <footer className="bg-[#282828] text-white py-12 mt-auto">
        <div className="max-w-7xl mx-auto px-4 flex flex-col items-center text-center">
          <img src="/logo-circular.jpg" alt="C_Express Mini-Mart" className="h-20 w-20 rounded-full mb-4 shadow-lg object-contain bg-white" />
          <p className="text-gray-400 text-sm">© 2026 C_Express Mini-Mart. All Rights Reserved.</p>
        </div>
      </footer>

      {viewProduct && (
        <div 
          className="fixed inset-0 bg-black/60 z-[100] flex items-center justify-center p-4 backdrop-blur-sm animate-fade-in"
          onClick={() => setViewProduct(null)}
        >
          <div 
            className="bg-white rounded-2xl max-w-3xl w-full max-h-[90vh] overflow-y-auto shadow-2xl flex flex-col md:flex-row relative" 
            onClick={e => e.stopPropagation()}
          >
            <button 
              onClick={() => setViewProduct(null)}
              className="absolute top-4 right-4 bg-white/80 p-2 rounded-full text-gray-500 hover:text-red-500 hover:bg-red-50 z-10 transition-colors shadow-sm backdrop-blur-md"
            >
              <X className="h-5 w-5" />
            </button>
            
            <div className="w-full md:w-1/2 bg-gray-50 min-h-[300px] md:min-h-full flex items-center justify-center p-6 border-r border-gray-100">
              {viewProduct.image_url ? (
                <img src={viewProduct.image_url} alt={viewProduct.name} className="w-full h-auto object-contain drop-shadow-md rounded-xl" />
              ) : (
                <ShoppingBag className="h-24 w-24 text-gray-300 stroke-1" />
              )}
            </div>

            <div className="w-full md:w-1/2 p-6 md:p-8 flex flex-col">
              <span className="text-xs font-bold text-[#f68b1e] uppercase tracking-wider mb-2">
                {categories.find(c => c.id === viewProduct.category_id)?.name || 'Product Detail'}
              </span>
              <h2 className="text-2xl font-black text-gray-900 leading-tight mb-2">{viewProduct.name}</h2>
              <div className="flex flex-wrap items-center gap-3 mb-6 border-b border-gray-100 pb-4">
                <span className="flex items-center gap-1 text-sm font-semibold text-gray-600 bg-gray-100 px-2.5 py-1 rounded-md">
                  <Tag className="h-3.5 w-3.5" /> {viewProduct.brand || 'No Brand'}
                </span>
                {viewProduct.package_size && (
                  <span className="text-sm font-semibold text-gray-600 bg-gray-100 px-2.5 py-1 rounded-md">
                    {viewProduct.package_size}
                  </span>
                )}
              </div>

              <div className="flex-grow">
                <h4 className="text-sm font-bold text-gray-900 mb-2">Description</h4>
                <p className="text-gray-500 text-sm leading-relaxed mb-6 whitespace-pre-wrap">
                  {viewProduct.description || 'No detailed description available for this item.'}
                </p>
              </div>

              <div className="mt-auto pt-6 border-t border-gray-100">
                <div className="flex justify-between items-end mb-4">
                  <div>
                    <span className="block text-xs text-gray-400 font-bold uppercase mb-1">Price</span>
                    <span className="text-3xl font-black text-gray-900">₦{parseFloat(viewProduct.price).toLocaleString()}</span>
                  </div>
                  <span className={`px-3 py-1 rounded-full text-xs font-bold ${viewProduct.stock > 0 ? 'bg-green-50 text-green-600' : 'bg-red-50 text-red-600'}`}>
                    {viewProduct.stock > 0 ? `${viewProduct.stock} In Stock` : 'Out of Stock'}
                  </span>
                </div>

                <button 
                  onClick={() => { addToCart(viewProduct); setViewProduct(null); }}
                  disabled={viewProduct.stock <= 0}
                  className={`w-full py-3.5 rounded-xl font-bold flex justify-center items-center gap-2 transition-all shadow-md ${viewProduct.stock > 0 ? 'bg-[#f68b1e] hover:bg-orange-600 text-white' : 'bg-gray-200 text-gray-400 cursor-not-allowed'}`}
                >
                  <ShoppingCart className="h-5 w-5" /> 
                  {viewProduct.stock > 0 ? 'ADD TO CART' : 'CURRENTLY UNAVAILABLE'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}
