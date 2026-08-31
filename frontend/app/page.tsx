"use client";

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Mic, Send, Camera, ShoppingBag, Sparkles } from 'lucide-react';

export default function ShopMateAI() {
  // 1. State Management
  const [messages, setMessages] = useState([
    { role: 'mira', text: 'Namaste! I am MIRA. What are you looking for today?' }
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [products, setProducts] = useState<any[]>([]);
  const [selectedProduct, setSelectedProduct] = useState<any | null>(null);

  // 2. Chat Logic
  const handleChat = async (msg: string) => {
    if (!msg.trim()) return;
    setLoading(true);
    const newMessages = [...messages, { role: 'user', text: msg }];
    setMessages(newMessages);
    
    try {
      const res = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: msg, history: [] })
      });
      const data = await res.json();
      setMessages(prev => [...prev, { role: 'mira', text: data.reply }]);
      setProducts(Array.isArray(data.recommended_products) ? data.recommended_products : []);
    } catch (err) {
      setMessages(prev => [...prev, { role: 'mira', text: "MIRA is having trouble connecting to the server. Please check if your backend is running." }]);
    }
    setLoading(false);
    setInput("");
  };

  return (
    <div className="min-h-screen bg-[#050505] text-white font-sans">
      {/* Header */}
      <nav className="p-6 flex justify-between items-center border-b border-white/5 backdrop-blur-md sticky top-0 z-50">
        <div className="flex items-center gap-2">
          <div className="w-10 h-10 bg-gradient-to-br from-cyan-500 to-purple-600 rounded-xl flex items-center justify-center font-bold">S</div>
          <h1 className="text-xl font-bold tracking-tight">ShopMate <span className="text-cyan-400">AI</span></h1>
        </div>
        <div className="flex gap-4 text-sm font-medium text-gray-400">
          <span className="text-green-500 font-bold">● Live Mode</span>
          <span>INR (₹)</span>
        </div>
      </nav>

      <main className="max-w-6xl mx-auto p-4 grid grid-cols-1 lg:grid-cols-12 gap-8 mt-10">
        
        {/* Left: AI Assistant Section */}
        <div className="lg:col-span-7 flex flex-col h-[75vh]">
          <div className="flex-1 overflow-y-auto space-y-6 pr-4">
            <AnimatePresence>
              {messages.map((m, i) => (
                <motion.div 
                  initial={{ opacity: 0, y: 10 }} 
                  animate={{ opacity: 1, y: 0 }} 
                  key={i} 
                  className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div className={`max-w-[85%] p-4 rounded-2xl ${
                    m.role === 'user' 
                    ? 'bg-cyan-600 text-white shadow-lg shadow-cyan-900/20' 
                    : 'bg-white/5 border border-white/10'
                  }`}>
                    {m.text}
                  </div>
                </motion.div>
              ))}
              {loading && <div className="text-cyan-500 animate-pulse text-sm">MIRA is thinking...</div>}
            </AnimatePresence>
          </div>

          {/* Input Bar */}
          <div className="mt-6 relative">
            <div className="bg-white/5 border border-white/10 rounded-2xl p-2 flex items-center gap-2 shadow-2xl">
              <button className="p-3 hover:bg-white/5 rounded-xl transition text-gray-400"><Camera size={22} /></button>
              <input 
                value={input} 
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleChat(input)}
                placeholder="Ask MIRA (e.g. Find me a phone under 30k)" 
                className="flex-1 bg-transparent border-none outline-none px-2 text-white"
              />
              <button onClick={() => handleChat(input)} className="p-3 bg-cyan-500 text-black rounded-xl hover:bg-cyan-400 transition">
                <Send size={20} />
              </button>
            </div>
          </div>
        </div>

        {/* Right: Recommendations Section */}
        <div className="lg:col-span-5 space-y-6">
          <div className="flex items-center gap-2 text-cyan-400 font-semibold mb-4">
            <Sparkles size={18} />
            <h2>AI Recommendations {products.length > 0 && `(${products.length})`}</h2>
          </div>
          
          <div className="grid gap-4">
            {products.length > 0 ? products.map((p: any) => (
              <motion.div whileHover={{ scale: 1.02 }} key={p.id} className="bg-white/5 border border-white/10 rounded-2xl p-4 flex gap-4">
                <button
                  type="button"
                  onClick={() => setSelectedProduct(p)}
                  aria-label={`View details for ${p.name}`}
                  className="w-20 h-20 bg-gray-800 rounded-lg overflow-hidden flex-shrink-0 cursor-pointer focus:outline-none focus:ring-2 focus:ring-cyan-400"
                >
                  <img
                    src={p.img}
                    alt={p.name}
                    className="w-full h-full object-cover"
                    onError={(event) => {
                      event.currentTarget.style.display = 'none';
                    }}
                  />
                </button>
                <div className="flex-1">
                   <h3 className="font-bold text-sm">{p.name}</h3>
                   <p className="text-cyan-400 font-bold">₹{p.price.toLocaleString()}</p>
                   <p className="text-[10px] text-gray-400">{p.ram} RAM · {p.storage} storage</p>
                   <p className="text-[10px] text-gray-400">Match: {p.match}%</p>
                </div>
              </motion.div>
            )) : (
              <div className="h-64 border-2 border-dashed border-white/10 rounded-3xl flex flex-col items-center justify-center text-gray-500">
                <ShoppingBag size={40} className="mb-2 opacity-20" />
                <p className="text-sm italic">Recommendations will appear here</p>
              </div>
            )}
          </div>
        </div>
      </main>

      <AnimatePresence>
        {selectedProduct && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-[60] bg-black/80 backdrop-blur-sm flex items-center justify-center p-4"
            onClick={() => setSelectedProduct(null)}
          >
            <motion.div
              initial={{ opacity: 0, y: 16, scale: 0.98 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: 16, scale: 0.98 }}
              className="w-full max-w-lg bg-[#151515] border border-white/10 rounded-2xl overflow-hidden shadow-2xl"
              onClick={(event) => event.stopPropagation()}
            >
              <div className="h-56 bg-gray-800">
                <img src={selectedProduct.img} alt={selectedProduct.name} className="w-full h-full object-cover" />
              </div>
              <div className="p-6">
                <div className="flex justify-between items-start gap-4">
                  <div>
                    <p className="text-xs uppercase tracking-wider text-cyan-400">{selectedProduct.brand}</p>
                    <h2 className="text-xl font-bold mt-1">{selectedProduct.name}</h2>
                  </div>
                  <button
                    type="button"
                    onClick={() => setSelectedProduct(null)}
                    aria-label="Close product details"
                    className="text-2xl leading-none text-gray-400 hover:text-white"
                  >
                    ×
                  </button>
                </div>
                <p className="text-cyan-400 text-2xl font-bold mt-5">₹{selectedProduct.price.toLocaleString()}</p>
                <div className="grid grid-cols-2 gap-3 mt-5">
                  <div className="bg-white/5 rounded-lg p-3 text-sm">Rating: <strong>{selectedProduct.rating}/5</strong></div>
                  <div className="bg-white/5 rounded-lg p-3 text-sm">Match: <strong>{selectedProduct.match}%</strong></div>
                  <div className="bg-white/5 rounded-lg p-3 text-sm">RAM: <strong>{selectedProduct.ram}</strong></div>
                  <div className="bg-white/5 rounded-lg p-3 text-sm">Storage: <strong>{selectedProduct.storage}</strong></div>
                </div>
                <h3 className="font-semibold mt-6 mb-3">Product features</h3>
                <ul className="space-y-2 text-sm text-gray-300">
                  <li>• {selectedProduct.brand} product</li>
                  <li>• {selectedProduct.ram} RAM and {selectedProduct.storage} storage</li>
                  <li>• Recommended match score: {selectedProduct.match}%</li>
                  <li>• Price: ₹{selectedProduct.price.toLocaleString()} in the demo catalog</li>
                  <li>• Rated {selectedProduct.rating} out of 5 by shoppers</li>
                </ul>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}