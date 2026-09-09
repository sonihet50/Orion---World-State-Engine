import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

export const SignIn: React.FC = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // In our client-side prototype, unlock logs us directly in
    navigate('/worlds');
  };

  return (
    <div className="min-h-screen w-full flex items-center justify-center text-on-surface antialiased bg-void-black relative selection:bg-primary/30 select-none">
      
      {/* Background Radial Glow */}
      <div className="fixed inset-0 ambient-glow pointer-events-none z-0"></div>

      {/* Atmospheric Background Layers */}
      <div className="fixed inset-0 pointer-events-none z-0">
        <div className="absolute top-0 right-0 w-1/2 h-1/2 bg-[radial-gradient(ellipse_at_top_right,rgba(230,162,126,0.03),transparent_70%)]"></div>
        <div className="absolute bottom-0 left-0 w-1/2 h-1/2 bg-[radial-gradient(ellipse_at_bottom_left,rgba(254,182,141,0.02),transparent_70%)]"></div>
      </div>

      <div className="w-full max-w-md px-gutter relative z-10 animate-fade-in-up">
        
        {/* Floating Glass Panel */}
        <div className="bg-surface-container-low/95 backdrop-blur-xl border border-starlight-white/10 rounded-xl p-8 shadow-2xl relative overflow-hidden group">
          
          {/* Subtle Hover Glow Effect */}
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_-20%,rgba(230,162,126,0.08),transparent_70%)] opacity-0 group-hover:opacity-100 transition-opacity duration-700 pointer-events-none"></div>

          {/* Logo Section */}
          <div className="flex flex-col items-center justify-center mb-stack-lg relative z-10">
            <div className="w-16 h-16 rounded-full border border-starlight-white/5 flex items-center justify-center mb-stack-sm bg-surface-container/50 shadow-inner">
              <span className="material-symbols-outlined text-[32px] text-copper-glow font-extralight animate-pulse">bubble_chart</span>
            </div>
            <h2 className="font-headline-md text-headline-md text-primary tracking-tighter">Orion</h2>
          </div>

          {/* Header */}
          <div className="text-center mb-stack-lg relative z-10">
            <h1 className="font-display-lg text-display-lg text-starlight-white mb-2 hidden md:block">Enter the Archive</h1>
            <h1 className="font-headline-lg-mobile text-headline-lg-mobile text-starlight-white mb-2 md:hidden">Enter the Archive</h1>
            <p className="font-body-md text-body-md text-on-surface-variant/80">Your sanctuary for world-building awaits.</p>
          </div>

          {/* Login Form */}
          <form onSubmit={handleSubmit} className="space-y-stack-md relative z-10">
            <div className="flex flex-col">
              <label className="sr-only" htmlFor="email">Email Address</label>
              <input 
                id="email"
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="Email Address"
                className="bg-transparent border-0 border-b border-starlight-white/10 rounded-none py-3 px-0 font-body-md text-starlight-white placeholder:text-on-surface-variant/30 w-full focus:outline-none focus:ring-0 focus:border-copper-glow transition-all"
              />
            </div>
            <div className="flex flex-col">
              <label className="sr-only" htmlFor="password">Password</label>
              <input 
                id="password"
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Password"
                className="bg-transparent border-0 border-b border-starlight-white/10 rounded-none py-3 px-0 font-body-md text-starlight-white placeholder:text-on-surface-variant/30 w-full focus:outline-none focus:ring-0 focus:border-copper-glow transition-all"
              />
            </div>

            <div className="pt-stack-sm flex items-center justify-between">
              <button type="button" className="text-on-surface-variant/60 hover:text-starlight-white font-label-sm text-xs uppercase tracking-widest transition-colors">
                Forgot Password?
              </button>
            </div>

            <div className="pt-stack-md">
              <button 
                type="submit" 
                className="w-full py-3.5 rounded border border-copper-glow text-copper-glow hover:bg-copper-glow hover:text-void-black uppercase font-label-sm text-xs tracking-widest flex items-center justify-center gap-2 transition-all duration-300 shadow-[0_0_15px_rgba(230,162,126,0.1)] hover:shadow-[0_0_25px_rgba(230,162,126,0.25)] font-semibold"
              >
                <span>Unlock</span>
                <span className="material-symbols-outlined text-[18px] font-light">key</span>
              </button>
            </div>
          </form>

          {/* Social Login Divider */}
          <div className="mt-stack-lg relative z-10">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-starlight-white/5"></div>
            </div>
            <div className="relative flex justify-center text-xs">
              <span className="px-3 bg-surface-container-low text-on-surface-variant/40 font-label-sm text-[10px] uppercase tracking-wider">Or access via</span>
            </div>
          </div>

          {/* Social Logins */}
          <div className="mt-stack-md flex justify-center gap-4 relative z-10">
            <button 
              onClick={() => navigate('/worlds')}
              className="w-12 h-12 rounded-full border border-starlight-white/10 flex items-center justify-center text-on-surface-variant/60 hover:text-starlight-white hover:border-starlight-white/30 transition-all bg-surface-container-lowest/50 hover:bg-surface-container-low" 
              type="button"
              title="Fingerprint Login"
            >
              <span className="material-symbols-outlined font-light text-xl">fingerprint</span>
            </button>
            <button 
              onClick={() => navigate('/worlds')}
              className="w-12 h-12 rounded-full border border-starlight-white/10 flex items-center justify-center text-on-surface-variant/60 hover:text-starlight-white hover:border-starlight-white/30 transition-all bg-surface-container-lowest/50 hover:bg-surface-container-low" 
              type="button"
              title="Public Key Auth"
            >
              <span className="material-symbols-outlined font-light text-xl">public</span>
            </button>
          </div>

          {/* Bottom Prompt */}
          <div className="mt-stack-lg text-center relative z-10">
            <p className="font-body-md text-sm text-on-surface-variant/70">
              New to the Archive? 
              <button 
                onClick={() => navigate('/worlds/new')}
                className="text-copper-glow hover:text-primary-fixed-dim transition-colors ml-1.5 underline underline-offset-4"
              >
                Forge an entry
              </button>
            </p>
          </div>

        </div>
      </div>
    </div>
  );
};
