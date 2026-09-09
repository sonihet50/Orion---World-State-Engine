import React, { useState, useEffect, useRef } from 'react';
import { AppShell } from '../components/AppShell';
import { useWorldStore } from '../store/useWorldStore';

interface Message {
  id: string;
  sender: 'user' | 'assistant';
  text: string | React.ReactNode;
  time: string;
}

export const WorldAssistant: React.FC = () => {
  const { setActiveEntity } = useWorldStore();
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'msg-1',
      sender: 'assistant',
      text: 'Greetings, Chronicler. I am the Orion World Engine Assistant. Ask me to cross-reference entities, discover timeline patterns, or locate consistency gaps in your manuscripts.',
      time: '12:42 AM'
    }
  ]);
  const [inputVal, setInputVal] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  const handleSendMessage = (text: string) => {
    if (!text.trim()) return;

    const userMsg: Message = {
      id: `msg-${Date.now()}`,
      sender: 'user',
      text,
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputVal('');
    setIsTyping(true);

    // Simulate AI response based on keyword matching
    setTimeout(() => {
      setIsTyping(false);
      let responseText: React.ReactNode = '';

      const query = text.toLowerCase();
      if (query.includes('kaelen') || query.includes('mentor')) {
        responseText = (
          <span>
            <button 
              onClick={() => setActiveEntity('kaelen')}
              className="text-primary hover:underline font-semibold font-headline-md"
            >
              Kaelen
            </button>{' '}
            is a legendary archivist who withdrew from the Citadel before the Severance. According to extracted files in Chapter 2, he lives in the Undercity sub-vaults and is Elara\'s former mentor. He lost his left eye during the feedback loop of the Great Severance.
          </span>
        );
      } else if (query.includes('elara') || query.includes('vance')) {
        responseText = (
          <span>
            <button 
              onClick={() => setActiveEntity('elara-vance')}
              className="text-primary hover:underline font-semibold font-headline-md"
            >
              Elara Vance
            </button>{' '}
            is the protagonist of your chronicle. Extracted records show she fled the Ashen Wastes and has a strong affinity for precursor pattern matching. There is a high priority contradiction regarding her age between Chapter 3 (32) and Chapter 12 (34, three years later).
          </span>
        );
      } else if (query.includes('conflict') || query.includes('contradiction')) {
        responseText = (
          <span>
            I found <span className="text-error font-semibold">2 contradictions</span>. One is a temporal mismatch in{' '}
            <button onClick={() => setActiveEntity('elara-vance')} className="text-primary hover:underline font-semibold">Elara Vance's</button>{' '}
            age progression. The second is a geographic clash regarding the cardinal shore location of the Ashen Wastes (East Atlas vs West Prologue).
          </span>
        );
      } else {
        responseText = `I have parsed your manuscripts and indexed 5 major characters and 3 key locations. I'm ready to answer specific inquiries about Ethan, Lyra, Kaelen, or the Obsidian Syndicate.`;
      }

      const assistantMsg: Message = {
        id: `msg-${Date.now() + 1}`,
        sender: 'assistant',
        text: responseText,
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };

      setMessages((prev) => [...prev, assistantMsg]);
    }, 1200);
  };

  const presetQueries = [
    'Who is Kaelen?',
    'What contradictions are in my manuscripts?',
    'Tell me about Elara Vance.'
  ];

  return (
    <AppShell>
      {/* Background ambient lighting */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_bottom_right,rgba(230,162,126,0.02),transparent_60%)] -z-10 pointer-events-none"></div>

      <main className="flex-1 h-screen flex flex-col relative overflow-hidden bg-surface">
        
        {/* Assistant Header */}
        <header className="h-16 border-b border-starlight-white/5 bg-surface-container-lowest/50 backdrop-blur px-8 flex items-center justify-between z-10 select-none">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-full border border-primary/20 bg-primary/10 flex items-center justify-center">
              <span className="material-symbols-outlined text-primary text-lg font-light">chat_bubble_outline</span>
            </div>
            <div>
              <h2 className="font-headline-md text-sm text-starlight-white font-semibold">Orion Assistant</h2>
              <p className="text-[10px] font-label-sm text-on-surface-variant/45 uppercase tracking-wider mt-0.5">Lore Engine AI</p>
            </div>
          </div>
          <span className="text-[10px] font-label-sm text-emerald-400 uppercase tracking-widest bg-emerald-500/5 border border-emerald-500/10 px-2 py-0.5 rounded">Sync Online</span>
        </header>

        {/* Messages Stream */}
        <div className="flex-1 overflow-y-auto px-8 py-10 space-y-6 select-text scrollbar-hide">
          <div className="max-w-3xl mx-auto flex flex-col gap-6">
            
            {messages.map((msg) => {
              const isAssistant = msg.sender === 'assistant';
              return (
                <div 
                  key={msg.id}
                  className={`flex gap-4 max-w-[80%] animate-fade-in-up ${
                    isAssistant ? 'self-start' : 'self-end flex-row-reverse text-right'
                  }`}
                >
                  {/* Avatar Icon */}
                  <div className={`w-8 h-8 rounded-full border shrink-0 flex items-center justify-center text-sm ${
                    isAssistant 
                      ? 'bg-primary/10 border-primary/20 text-primary' 
                      : 'bg-surface-container-highest border-starlight-white/10 text-starlight-white'
                  }`}>
                    <span className="material-symbols-outlined text-[16px] font-light">
                      {isAssistant ? 'bubble_chart' : 'person'}
                    </span>
                  </div>

                  {/* Message Bubble */}
                  <div className={`rounded-xl p-4 border text-xs leading-relaxed ${
                    isAssistant 
                      ? 'bg-surface-container-low/50 border-starlight-white/5 text-on-surface-variant' 
                      : 'bg-primary/5 border-primary/20 text-starlight-white'
                  }`}>
                    <p>{msg.text}</p>
                    <span className="block text-[9px] text-on-surface-variant/30 mt-2 font-label-sm uppercase tracking-wider">
                      {msg.time}
                    </span>
                  </div>
                </div>
              );
            })}

            {/* Typing Loader Indicator */}
            {isTyping && (
              <div className="flex gap-4 self-start max-w-[80%]">
                <div className="w-8 h-8 rounded-full border border-primary/20 bg-primary/10 flex items-center justify-center text-primary text-sm shrink-0">
                  <span className="material-symbols-outlined text-[16px] font-light">bubble_chart</span>
                </div>
                <div className="rounded-xl p-4 bg-surface-container-low/50 border border-starlight-white/5 flex gap-1.5 items-center justify-center">
                  <span className="w-1.5 h-1.5 rounded-full bg-primary/40 animate-bounce" style={{ animationDelay: '0ms' }} />
                  <span className="w-1.5 h-1.5 rounded-full bg-primary/40 animate-bounce" style={{ animationDelay: '150ms' }} />
                  <span className="w-1.5 h-1.5 rounded-full bg-primary/40 animate-bounce" style={{ animationDelay: '300ms' }} />
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Input Bar & Presets */}
        <footer className="p-6 border-t border-starlight-white/5 bg-void-black/85 backdrop-blur z-10 select-none">
          <div className="max-w-3xl mx-auto flex flex-col gap-4">
            
            {/* Preset Query Chips */}
            {messages.length === 1 && (
              <div className="flex flex-wrap gap-2 animate-fade-in-up">
                {presetQueries.map((query, idx) => (
                  <button 
                    key={idx}
                    onClick={() => handleSendMessage(query)}
                    className="px-3.5 py-1.5 rounded-full border border-starlight-white/10 bg-surface-container-low/20 hover:border-primary/50 text-xs text-on-surface-variant hover:text-primary transition-all font-label-sm uppercase tracking-wider text-[10px]"
                  >
                    {query}
                  </button>
                ))}
              </div>
            )}

            {/* Form Input */}
            <form 
              onSubmit={(e) => {
                e.preventDefault();
                handleSendMessage(inputVal);
              }}
              className="relative flex items-center"
            >
              <input 
                type="text"
                value={inputVal}
                onChange={(e) => setInputVal(e.target.value)}
                placeholder="Ask Orion about your manuscripts..."
                className="w-full bg-surface-container-lowest border border-starlight-white/10 rounded-full pl-6 pr-14 py-3 text-xs text-on-surface placeholder:text-on-surface-variant/30 focus:border-primary focus:ring-0 focus:outline-none"
              />
              <button 
                type="submit"
                className="absolute right-2 w-9 h-9 rounded-full bg-primary hover:bg-copper-glow flex items-center justify-center text-void-black transition-colors"
                title="Send query"
              >
                <span className="material-symbols-outlined text-lg font-light">arrow_forward</span>
              </button>
            </form>
          </div>
        </footer>

      </main>
    </AppShell>
  );
};
