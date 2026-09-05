import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowLeft, MapPin, Instagram, Facebook, Music2, ShoppingBag } from 'lucide-react';

const products = [
  'Bags of rice',
  'Bags of beans',
  'Golden Penny pasta',
  'Golden Penny macaroni',
  'White garri',
  'Yellow garri',
  'Cooking oil',
  'Fresh palm oil',
  'Groceries',
  'Provisions',
  'Artworks',
  'Household essentials',
];

const testimonials = [
  {
    quote: 'C Express Minimart makes stocking my kitchen simple. The products are good quality and the team is always helpful.',
    name: 'Amaka Okafor',
    location: 'Gwarinpa, Abuja',
  },
  {
    quote: 'I can rely on them for rice, beans and other provisions whenever I need to shop in larger quantities.',
    name: 'Ibrahim Musa',
    location: 'Kubwa, Abuja',
  },
  {
    quote: 'The service is friendly, responsive and convenient. C Express is now one of my regular places to shop.',
    name: 'Chidinma Eze',
    location: 'Karmo, Abuja',
  },
];

export default function About() {
  return (
    <div className="min-h-screen bg-[#f1f1f2] font-sans text-[#282828]">
      <nav className="sticky top-0 z-40 bg-white px-4 py-4 shadow-sm sm:px-8">
        <div className="mx-auto flex max-w-7xl items-center justify-between gap-4">
          <Link to="/" className="flex items-center gap-2 font-semibold text-gray-600 transition-colors hover:text-[#f68b1e]">
            <ArrowLeft className="h-5 w-5" /> Back to Shopping
          </Link>
          <img src="/logo-vertical.png" alt="CEXPRESS MINIMART" className="h-11 object-contain mix-blend-multiply" />
        </div>
      </nav>

      <main className="mx-auto max-w-5xl px-4 py-10 sm:px-6 lg:px-8">
        <header className="mb-10 rounded-2xl bg-[#282828] px-6 py-10 text-white shadow-md sm:px-10">
          <p className="mb-3 text-sm font-bold uppercase tracking-[0.2em] text-orange-300">About our business</p>
          <h1 className="text-3xl font-black leading-tight sm:text-5xl">C EXPRESS MINIMART</h1>
          <p className="mt-4 max-w-2xl text-lg leading-8 text-gray-200">Your Trusted Source for Quality Foodstuff, Groceries &amp; Household Essentials</p>
        </header>

        <div className="space-y-8">
          <section className="rounded-xl bg-white p-6 shadow-sm sm:p-8">
            <p className="leading-7 text-gray-600">
              C Express Minimart is a customer-focused retail business dedicated to providing quality foodstuff, groceries, provisions, cooking essentials, artworks, and everyday household needs at affordable and competitive prices.
            </p>
            <p className="mt-4 leading-7 text-gray-600">
              We understand how important it is to have access to quality food and essential products in one convenient location. That is why we are committed to making shopping easier, more convenient, and more reliable for individuals, families, businesses, and households across Abuja.
            </p>
            <p className="mt-4 leading-7 text-gray-600">From staple food items to everyday provisions, we offer a wide range of products to meet the needs of our customers.</p>
          </section>

          <section className="grid gap-8 lg:grid-cols-2">
            <article className="rounded-xl bg-white p-6 shadow-sm sm:p-8">
              <h2 className="mb-4 text-2xl font-black text-gray-900">Our Products &amp; Services</h2>
              <p className="mb-4 leading-7 text-gray-600">At C Express Minimart, we deal in a variety of quality products, including:</p>
              <ul className="grid grid-cols-1 gap-2 text-gray-700 sm:grid-cols-2">
                {products.map(product => <li key={product} className="border-l-2 border-[#f68b1e] pl-3">{product}</li>)}
              </ul>
              <p className="mt-5 leading-7 text-gray-600">Our goal is to provide customers with the products they need while maintaining good quality, fair pricing, and excellent customer service.</p>
            </article>

            <div className="space-y-8">
              <article className="rounded-xl bg-white p-6 shadow-sm sm:p-8">
                <h2 className="mb-3 text-2xl font-black text-gray-900">Our Mission</h2>
                <p className="leading-7 text-gray-600">Our mission is to provide quality foodstuff, groceries, provisions, and household essentials at affordable prices while delivering excellent customer service and convenience to every customer we serve.</p>
                <p className="mt-4 leading-7 text-gray-600">We are committed to building a trusted shopping experience where customers can confidently purchase their everyday essentials from a reliable and customer-friendly business.</p>
              </article>
              <article className="rounded-xl bg-white p-6 shadow-sm sm:p-8">
                <h2 className="mb-3 text-2xl font-black text-gray-900">Our Vision</h2>
                <p className="leading-7 text-gray-600">Our vision is to become one of the most trusted and preferred minimarts and foodstuff suppliers in Abuja, known for quality products, affordable prices, convenience, reliability, and exceptional customer service.</p>
                <p className="mt-4 leading-7 text-gray-600">We aspire to grow into a reputable brand that serves more homes, families, businesses, and communities while creating lasting relationships with our customers.</p>
              </article>
            </div>
          </section>

          <section className="rounded-xl bg-white p-6 shadow-sm sm:p-8">
            <h2 className="mb-3 text-2xl font-black text-gray-900">Our Commitment to Our Customers</h2>
            <p className="leading-7 text-gray-600">At C Express Minimart, our customers are at the heart of everything we do. We believe that good business is built on trust, quality, affordability, and excellent service.</p>
            <p className="mt-4 leading-7 text-gray-600">We carefully select the products we offer and strive to ensure that every customer receives value for their money. Whether you need a bag of rice, beans, garri, cooking oil, pasta, provisions, groceries, or other household essentials, we are here to serve you.</p>
          </section>

          <section className="grid gap-8 md:grid-cols-2">
            <article className="rounded-xl bg-orange-50 p-6 ring-1 ring-orange-100 sm:p-8">
              <h2 className="mb-3 flex items-center gap-2 text-2xl font-black text-gray-900"><ShoppingBag className="h-6 w-6 text-[#f68b1e]" /> Home Delivery in Abuja</h2>
              <p className="leading-7 text-gray-700">For your convenience, C Express Minimart offers home delivery within Abuja. You can shop for your essential foodstuff and groceries without having to leave your home or office. Simply place your order with us, and we will discuss delivery arrangements for your address within Abuja.</p>
            </article>
            <article className="rounded-xl bg-white p-6 shadow-sm sm:p-8">
              <h2 className="mb-3 flex items-center gap-2 text-2xl font-black text-gray-900"><MapPin className="h-6 w-6 text-[#f68b1e]" /> Our Location</h2>
              <p className="leading-7 text-gray-600">C Express Minimart<br />Karmo District Market, Shop 59, Farmers Block<br />FCT, Abuja, Nigeria</p>
              <p className="mt-4 font-semibold text-gray-800">Open: Monday - Saturday</p>
            </article>
          </section>

          <section>
            <div className="mb-5">
              <h2 className="text-2xl font-black text-gray-900">What Our Customers Say</h2>
              <p className="mt-1 text-gray-600">A few words from customers who shop with us across Abuja.</p>
            </div>
            <div className="grid gap-5 md:grid-cols-3">
              {testimonials.map(testimonial => (
                <figure key={testimonial.name} className="rounded-xl bg-white p-6 shadow-sm">
                  <blockquote className="leading-7 text-gray-600">&quot;{testimonial.quote}&quot;</blockquote>
                  <figcaption className="mt-5 border-t border-gray-100 pt-4">
                    <p className="font-bold text-gray-900">{testimonial.name}</p>
                    <p className="text-sm text-gray-500">{testimonial.location}</p>
                  </figcaption>
                </figure>
              ))}
            </div>
          </section>
        </div>
      </main>

      <footer className="bg-[#282828] px-4 py-10 text-white">
        <div className="mx-auto flex max-w-5xl flex-col items-center text-center">
          <p className="text-lg font-black">C EXPRESS MINIMART</p>
          <p className="mt-2 text-sm text-gray-400">Quality Products. Affordable Prices. Reliable Service.</p>
          <p className="mt-1 text-sm text-gray-400">Your trusted neighbourhood minimart for foodstuff, groceries, provisions and more.</p>
          <div className="mt-6 flex items-center gap-5">
            <a href="https://www.instagram.com/cexpressminimart?igsi=MW40b2RvM2h1anJrbw==" target="_blank" rel="noreferrer" aria-label="Instagram" className="text-gray-300 transition-colors hover:text-orange-300"><Instagram className="h-5 w-5" /></a>
            <a href="https://www.facebook.com/profile.php?id=61583834015441" target="_blank" rel="noreferrer" aria-label="Facebook" className="text-gray-300 transition-colors hover:text-orange-300"><Facebook className="h-5 w-5" /></a>
            <a href="https://www.tiktok.com/@c_express_minimart?_r=1&_t=ZS-99Fzjg3kLEG" target="_blank" rel="noreferrer" aria-label="TikTok" className="text-gray-300 transition-colors hover:text-orange-300"><Music2 className="h-5 w-5" /></a>
          </div>
        </div>
      </footer>
    </div>
  );
}
