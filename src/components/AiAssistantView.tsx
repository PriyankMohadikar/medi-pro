/**
 * AI Pricing Assistant — Premium ChatGPT-style Interface
 * Redesigned for usability, alignment, and modern aesthetics.
 */

import React, { useState, useRef, useEffect } from "react";
import { ChatMessage } from "../types";
import {
  Sparkles,
  Send,
  Paperclip,
  AlertTriangle,
  RefreshCw,
  Activity,
  Bot,
  User,
} from "lucide-react";
import ReactMarkdown from "react-markdown";

interface AiAssistantViewProps {
  currency: "INR";
}

const SUGGESTED_CHIPS = [
  "Compare CBC in Ahmedabad",
  "Compare Vitamin D prices",
  "Suggest Women's Wellness Package",
  "Create package under \u20B93000",
  "Calculate 20% margin",
  "Compare Diabetes Packages",
  "Which competitor is cheapest?",
  "Create Premium Health Package",
];

export default function AiAssistantView({ currency }: AiAssistantViewProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputText, setInputText] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Provider Selection State
  const [selectedProvider, setSelectedProvider] = useState<string>("ollama");
  const [providerStatus, setProviderStatus] = useState<"connected" | "error" | "checking">("connected");
  
  const messagesEndRef = useRef<HTMLDivElement | null>(null);
  const textareaRef = useRef<HTMLTextAreaElement | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = Math.min(textareaRef.current.scrollHeight, 160) + "px";
    }
  }, [inputText]);

  const handleRetry = () => {
    setError(null);
    if (messages.length >= 1) {
      const lastUserMsg = [...messages].reverse().find((m) => m.sender === "user");
      if (lastUserMsg) {
        handleSendMessage(lastUserMsg.text);
      }
    }
  };

  const handleProviderChange = async (newProvider: string) => {
    const previous = selectedProvider;
    setSelectedProvider(newProvider);
    setProviderStatus("checking");
    setError(null);
    try {
      const { checkAiHealth } = await import("../api");
      await checkAiHealth(newProvider);
      setProviderStatus("connected");
    } catch (err) {
      setProviderStatus("error");
      setError(`Failed to connect to ${newProvider}. Reverting back.`);
      setTimeout(() => {
        setSelectedProvider(previous);
        setProviderStatus("connected");
        setError(null);
      }, 3000);
    }
  };

  const handleSendMessage = async (textToSend: string) => {
    if (!textToSend.trim() || loading || providerStatus === "checking") return;

    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    abortControllerRef.current = new AbortController();
    setError(null);

    const userMsg: ChatMessage = {
      id: `user-${Date.now()}`,
      sender: "user",
      text: textToSend,
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputText("");
    setLoading(true);

    const historyPayload = messages.map((msg) => ({
      role: msg.sender === "assistant" ? "assistant" : "user",
      content: msg.text,
    }));

    const assistantMsgId = `ai-${Date.now()}`;
    const initialAssistantMsg: ChatMessage = {
      id: assistantMsgId,
      sender: "assistant",
      text: "",
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    };

    setMessages((prev) => [...prev, initialAssistantMsg]);

    try {
      const { sendChatMessage } = await import("../api");
      const res = await sendChatMessage(textToSend, historyPayload, abortControllerRef.current.signal, selectedProvider);

      if (!res.body) throw new Error("No response body");

      const reader = res.body.getReader();
      const decoder = new TextDecoder("utf-8");

      let done = false;
      while (!done) {
        const { value, done: readerDone } = await reader.read();
        done = readerDone;
        if (value) {
          const chunk = decoder.decode(value, { stream: true });
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === assistantMsgId ? { ...msg, text: msg.text + chunk } : msg
            )
          );
        }
      }
    } catch (err: any) {
      if (err.name !== "AbortError") {
        const errorText = err.message || `Unable to connect to AI service. Please verify that the backend is running.`;
        setError(errorText);
        setMessages((prev) => prev.filter((m) => m.id !== assistantMsgId));
      }
    } finally {
      setLoading(false);
      abortControllerRef.current = null;
    }
  };

  useEffect(() => {
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, []);

  const hasMessages = messages.length > 0 || loading;

  return (
    <div style={styles.container}>
      {/* ── STATUS BAR (slim) ──────────────────────────── */}
      <div style={styles.header}>
        <div style={styles.headerInner}>
          <span style={{
            ...styles.statusBadge,
            color: providerStatus === "connected" ? "#16a34a" : providerStatus === "checking" ? "#eab308" : "#dc2626"
          }}>
            <span style={{
              ...styles.statusDot,
              background: providerStatus === "connected" ? "#22c55e" : providerStatus === "checking" ? "#eab308" : "#dc2626",
              boxShadow: providerStatus === "connected" ? "0 0 6px rgba(34,197,94,0.5)" : "none"
            }} />
            {providerStatus === "checking" ? "Checking Connection..." : `Connected to ${selectedProvider.charAt(0).toUpperCase() + selectedProvider.slice(1)}`}
          </span>
          <span style={styles.dot} />
          <span style={styles.headerSubtitle}>Healthcare Pricing Intelligence</span>
        </div>
      </div>

      {/* ── CONVERSATION AREA ───────────────────────────── */}
      <div style={styles.conversationArea}>
        {!hasMessages ? (
          /* ── WELCOME STATE ─────────────────────────────── */
          <div style={styles.welcomeContainer}>
            <div style={styles.welcomeIcon}>
              <Bot style={{ width: 32, height: 32, color: "#6366f1" }} />
            </div>
            <h2 style={styles.welcomeTitle}>AI Pricing Assistant</h2>
            <p style={styles.welcomeSubtitle}>
              Ask me anything about Pricing, Competitors, Packages, Margin Optimization, or Healthcare Pricing. I use your real PostgreSQL data to provide accurate insights.
            </p>

            <div style={styles.welcomeGrid}>
              {SUGGESTED_CHIPS.slice(0, 4).map((chip, i) => (
                <WelcomeCard key={i} text={chip} onClick={() => handleSendMessage(chip)} />
              ))}
            </div>
          </div>
        ) : (
          /* ── MESSAGES ──────────────────────────────────── */
          <div style={styles.messagesContainer}>
            {messages.map((msg) => (
              <MessageBubble key={msg.id} msg={msg} />
            ))}

            {/* Loading dots when AI is typing */}
            {loading && messages[messages.length - 1]?.text === "" && (
              <div style={styles.messageRow("#ffffff", true)}>
                <div style={styles.messageInner}>
                  <div style={styles.avatar("ai")}>
                    <Sparkles style={{ width: 16, height: 16, color: "#fff", animation: "assistantSpin 2s linear infinite" }} />
                  </div>
                  <div style={{ display: "flex", alignItems: "center", gap: 5, paddingTop: 8 }}>
                    <span style={dotAnimStyle(0)} />
                    <span style={dotAnimStyle(1)} />
                    <span style={dotAnimStyle(2)} />
                  </div>
                </div>
              </div>
            )}

            {/* Error Card */}
            {error && (
              <div style={{ padding: "12px 0" }}>
                <div style={styles.messageInner}>
                  <div style={styles.errorCard}>
                    <AlertTriangle style={{ width: 20, height: 20, color: "#ef4444", flexShrink: 0, marginTop: 1 }} />
                    <div style={{ flex: 1 }}>
                      <p style={styles.errorTitle}>Unable to connect to AI service</p>
                      <p style={styles.errorBody}>{error}</p>
                      <div style={{ display: "flex", gap: 8, marginTop: 12 }}>
                        <button onClick={handleRetry} style={styles.retryBtn}>
                          <RefreshCw style={{ width: 13, height: 13 }} /> Retry
                        </button>
                        <button onClick={() => window.open("/api/health", "_blank")} style={styles.statusBtn}>
                          <Activity style={{ width: 13, height: 13 }} /> Check Status
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* ── BOTTOM INPUT SECTION ────────────────────────── */}
      <div style={styles.bottomBar}>
        {/* Suggested Chips (horizontal scroll) */}
        {hasMessages && (
          <div style={styles.chipTrack}>
            {SUGGESTED_CHIPS.map((chip, i) => (
              <ChipButton key={i} text={chip} disabled={loading} onClick={() => handleSendMessage(chip)} />
            ))}
          </div>
        )}

        {/* Input Box */}
        <div style={styles.inputOuter}>
          <InputBox
            ref={textareaRef}
            value={inputText}
            loading={loading || providerStatus === "checking"}
            onChange={setInputText}
            onSend={() => handleSendMessage(inputText)}
            selectedProvider={selectedProvider}
            onProviderChange={handleProviderChange}
          />
          <p style={styles.disclaimer}>
            AI responses are generated from your configured AI provider. Verify data before making pricing decisions.
          </p>
        </div>
      </div>

      {/* ── KEYFRAME ANIMATIONS ──────────────────────────── */}
      <style>{`
        @keyframes assistantDotPulse {
          0%, 80%, 100% { opacity: 0.3; transform: scale(0.8); }
          40% { opacity: 1; transform: scale(1); }
        }
        @keyframes assistantSpin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
        .ai-md-content a { color: #4f46e5; text-decoration: underline; }
        .ai-md-content blockquote {
          border-left: 3px solid #6366f1;
          margin: 12px 0;
          padding: 8px 16px;
          background: #f5f3ff;
          border-radius: 0 8px 8px 0;
          color: #4338ca;
        }
      `}</style>
    </div>
  );
}

/* ════════════════════════════════════════════════════════
   SUB-COMPONENTS
   ════════════════════════════════════════════════════════ */

function WelcomeCard({ text, onClick }: { text: string; onClick: () => void }) {
  const [hovered, setHovered] = useState(false);
  return (
    <button
      onClick={onClick}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      style={{
        padding: "14px 16px",
        background: hovered ? "#f5f3ff" : "#ffffff",
        border: `1px solid ${hovered ? "#a5b4fc" : "#e2e8f0"}`,
        borderRadius: 12,
        fontSize: 13,
        fontWeight: 500,
        color: hovered ? "#4f46e5" : "#334155",
        cursor: "pointer",
        textAlign: "left",
        transition: "all 0.15s ease",
        lineHeight: 1.4,
        fontFamily: "'Inter', system-ui, sans-serif",
      }}
    >
      {text}
    </button>
  );
}

function ChipButton({ text, disabled, onClick }: { text: string; disabled: boolean; onClick: () => void }) {
  const [hovered, setHovered] = useState(false);
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      style={{
        padding: "6px 14px",
        background: hovered && !disabled ? "#f5f3ff" : "#f8fafc",
        border: `1px solid ${hovered && !disabled ? "#a5b4fc" : "#e2e8f0"}`,
        borderRadius: 20,
        fontSize: 12,
        fontWeight: 500,
        color: hovered && !disabled ? "#4f46e5" : "#64748b",
        cursor: disabled ? "not-allowed" : "pointer",
        whiteSpace: "nowrap" as const,
        flexShrink: 0,
        transition: "all 0.15s ease",
        fontFamily: "'Inter', system-ui, sans-serif",
        opacity: disabled ? 0.5 : 1,
      }}
    >
      {text}
    </button>
  );
}

function MessageBubble({ msg }: { msg: ChatMessage }) {
  const isUser = msg.sender === "user";
  return (
    <div style={styles.messageRow(isUser ? "transparent" : "#ffffff", !isUser)}>
      <div style={styles.messageInner}>
        {/* Avatar */}
        <div style={styles.avatar(isUser ? "user" : "ai")}>
          {isUser ? (
            <User style={{ width: 16, height: 16, color: "#fff" }} />
          ) : (
            <Sparkles style={{ width: 16, height: 16, color: "#fff" }} />
          )}
        </div>

        {/* Content */}
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 6 }}>
            <span style={styles.senderName}>{isUser ? "You" : "AI Assistant"}</span>
            <span style={styles.timestamp}>{msg.timestamp}</span>
          </div>

          {isUser ? (
            <p style={styles.userText}>{msg.text}</p>
          ) : (
            <div className="ai-md-content" style={styles.aiText}>
              <ReactMarkdown
                components={{
                  table: ({ children }) => (
                    <div style={{ overflowX: "auto", margin: "12px 0", borderRadius: 8, border: "1px solid #e2e8f0" }}>
                      <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>{children}</table>
                    </div>
                  ),
                  thead: ({ children }) => <thead style={{ background: "#f8fafc" }}>{children}</thead>,
                  th: ({ children }) => (
                    <th style={{ padding: "10px 14px", textAlign: "left", fontWeight: 600, color: "#475569", borderBottom: "2px solid #e2e8f0", fontSize: 12, textTransform: "uppercase", letterSpacing: "0.04em" }}>{children}</th>
                  ),
                  td: ({ children }) => (
                    <td style={{ padding: "10px 14px", borderBottom: "1px solid #f1f5f9", color: "#334155" }}>{children}</td>
                  ),
                  strong: ({ children }) => <strong style={{ color: "#0f172a", fontWeight: 600 }}>{children}</strong>,
                  h1: ({ children }) => <h1 style={{ fontSize: 18, fontWeight: 700, color: "#0f172a", margin: "16px 0 8px 0" }}>{children}</h1>,
                  h2: ({ children }) => <h2 style={{ fontSize: 16, fontWeight: 600, color: "#0f172a", margin: "14px 0 6px 0" }}>{children}</h2>,
                  h3: ({ children }) => <h3 style={{ fontSize: 14, fontWeight: 600, color: "#1e293b", margin: "12px 0 4px 0" }}>{children}</h3>,
                  ul: ({ children }) => <ul style={{ margin: "8px 0", paddingLeft: 20 }}>{children}</ul>,
                  ol: ({ children }) => <ol style={{ margin: "8px 0", paddingLeft: 20 }}>{children}</ol>,
                  li: ({ children }) => <li style={{ marginBottom: 4 }}>{children}</li>,
                  code: ({ children, className }) => {
                    const isBlock = className?.includes("language-");
                    return isBlock ? (
                      <pre style={{ background: "#1e293b", color: "#e2e8f0", padding: 16, borderRadius: 8, fontSize: 13, overflowX: "auto", margin: "12px 0" }}>
                        <code>{children}</code>
                      </pre>
                    ) : (
                      <code style={{ background: "#f1f5f9", color: "#7c3aed", padding: "2px 6px", borderRadius: 4, fontSize: 13 }}>{children}</code>
                    );
                  },
                  p: ({ children }) => <p style={{ margin: "6px 0", lineHeight: 1.7 }}>{children}</p>,
                }}
              >
                {msg.text}
              </ReactMarkdown>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

const InputBox = React.forwardRef<
  HTMLTextAreaElement,
  { value: string; loading: boolean; onChange: (v: string) => void; onSend: () => void; selectedProvider: string; onProviderChange: (p: string) => void }
>(({ value, loading, onChange, onSend, selectedProvider, onProviderChange }, ref) => {
  const canSend = value.trim() && !loading;
  const isProduction = import.meta.env.VITE_APP_ENV === "production";
  
  return (
    <div
      style={{
        display: "flex",
        alignItems: "flex-end",
        gap: 8,
        background: "#f8fafc",
        border: "1px solid #e2e8f0",
        borderRadius: 16,
        padding: "8px 12px",
        transition: "all 0.15s ease",
      }}
    >
      <div style={{ display: "flex", flexDirection: "column", gap: 4, paddingBottom: 4 }}>
        <button style={styles.attachBtn} title="Attach file (coming soon)">
          <Paperclip style={{ width: 18, height: 18 }} />
        </button>
        <select 
          value={selectedProvider}
          onChange={(e) => onProviderChange(e.target.value)}
          disabled={loading}
          style={{
            fontSize: 11,
            padding: "2px 4px",
            borderRadius: 4,
            border: "1px solid #cbd5e1",
            background: "#fff",
            color: "#475569",
            outline: "none",
            cursor: loading ? "not-allowed" : "pointer"
          }}
        >
          {!isProduction && <option value="ollama">Ollama</option>}
          <option value="groq">Groq</option>
          <option value="openrouter">OpenRouter</option>
        </select>
      </div>

      <textarea
        ref={ref}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            onSend();
          }
        }}
        style={styles.textarea}
        placeholder="Ask about pricing, competitors, packages or margins..."
        rows={1}
      />

      <button
        onClick={onSend}
        disabled={!canSend}
        style={{
          width: 36,
          height: 36,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          background: canSend ? "linear-gradient(135deg, #4f46e5 0%, #6366f1 100%)" : "#e2e8f0",
          border: "none",
          borderRadius: 10,
          cursor: canSend ? "pointer" : "not-allowed",
          transition: "all 0.15s ease",
          flexShrink: 0,
        }}
      >
        <Send style={{ width: 16, height: 16, color: canSend ? "#fff" : "#94a3b8" }} />
      </button>
    </div>
  );
});

/* ════════════════════════════════════════════════════════
   STYLE CONSTANTS
   ════════════════════════════════════════════════════════ */

const font = "'Inter', system-ui, sans-serif";

function dotAnimStyle(index: number): React.CSSProperties {
  return {
    width: 8,
    height: 8,
    borderRadius: "50%",
    background: "#94a3b8",
    animation: "assistantDotPulse 1.4s ease-in-out infinite",
    animationDelay: `${index * 0.2}s`,
  };
}

const styles = {
  container: {
    display: "flex",
    flexDirection: "column" as const,
    height: "100%",
    background: "#fafbfc",
    overflow: "hidden",
  },

  /* Header */
  header: {
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    padding: "8px 24px",
    borderBottom: "1px solid #f1f5f9",
    background: "#ffffff",
    maxHeight: 40,
    flexShrink: 0,
  },
  headerInner: { display: "flex", alignItems: "center", gap: 12 } as React.CSSProperties,
  headerIcon: {
    width: 36, height: 36, borderRadius: 10,
    background: "linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%)",
    display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0,
  } as React.CSSProperties,
  headerTitle: {
    fontSize: 15, fontWeight: 700, color: "#0f172a", margin: 0,
    lineHeight: 1.3, letterSpacing: "-0.01em", fontFamily: font,
  } as React.CSSProperties,
  headerMeta: { display: "flex", alignItems: "center", gap: 6, marginTop: 2 } as React.CSSProperties,
  headerSubtitle: { fontSize: 11, color: "#64748b", fontWeight: 500, fontFamily: font } as React.CSSProperties,
  dot: {
    width: 3, height: 3, borderRadius: "50%", background: "#cbd5e1", display: "inline-block",
  } as React.CSSProperties,
  statusBadge: {
    display: "inline-flex", alignItems: "center", gap: 4, fontSize: 11, color: "#16a34a", fontWeight: 600,
  } as React.CSSProperties,
  statusDot: {
    width: 6, height: 6, borderRadius: "50%", background: "#22c55e",
    display: "inline-block", boxShadow: "0 0 6px rgba(34,197,94,0.5)",
  } as React.CSSProperties,

  /* Conversation */
  conversationArea: {
    flex: 1, overflowY: "auto" as const, overflowX: "hidden" as const,
    display: "flex", flexDirection: "column" as const,
  },

  /* Welcome */
  welcomeContainer: {
    flex: 1, display: "flex", flexDirection: "column" as const,
    alignItems: "center", justifyContent: "center", padding: "40px 24px", textAlign: "center" as const,
  },
  welcomeIcon: {
    width: 64, height: 64, borderRadius: 20,
    background: "linear-gradient(135deg, #ede9fe 0%, #e0e7ff 100%)",
    display: "flex", alignItems: "center", justifyContent: "center", marginBottom: 24,
  } as React.CSSProperties,
  welcomeTitle: {
    fontSize: 24, fontWeight: 700, color: "#0f172a", margin: "0 0 8px 0",
    fontFamily: font, letterSpacing: "-0.02em",
  } as React.CSSProperties,
  welcomeSubtitle: {
    fontSize: 14, color: "#64748b", margin: "0 0 32px 0",
    maxWidth: 420, lineHeight: 1.6, fontFamily: font,
  } as React.CSSProperties,
  welcomeGrid: {
    display: "grid", gridTemplateColumns: "repeat(2, 1fr)",
    gap: 10, maxWidth: 500, width: "100%",
  } as React.CSSProperties,

  /* Messages */
  messagesContainer: {
    flex: 1, padding: "16px 0", display: "flex",
    flexDirection: "column" as const, gap: 0,
  },
  messageRow: (bg: string, border: boolean) =>
    ({
      padding: "14px 0",
      background: bg,
      borderBottom: border ? "1px solid #f1f5f9" : "none",
    }) as React.CSSProperties,
  messageInner: {
    maxWidth: 768, margin: "0 auto", padding: "0 24px",
    display: "flex", gap: 14, alignItems: "flex-start",
  } as React.CSSProperties,
  avatar: (type: "user" | "ai") =>
    ({
      width: 32, height: 32, borderRadius: type === "user" ? 8 : 10,
      background: type === "user"
        ? "linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)"
        : "linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%)",
      display: "flex", alignItems: "center", justifyContent: "center",
      flexShrink: 0, marginTop: 2,
    }) as React.CSSProperties,
  senderName: { fontSize: 13, fontWeight: 600, color: "#0f172a", fontFamily: font } as React.CSSProperties,
  timestamp: { fontSize: 11, color: "#94a3b8", fontWeight: 400 } as React.CSSProperties,
  userText: {
    fontSize: 14, lineHeight: 1.7, color: "#1e293b", margin: 0,
    whiteSpace: "pre-wrap" as const, fontFamily: font,
  },
  aiText: { fontSize: 14, lineHeight: 1.7, color: "#1e293b", fontFamily: font } as React.CSSProperties,

  /* Error */
  errorCard: {
    background: "#fef2f2", border: "1px solid #fecaca", borderRadius: 12,
    padding: "16px 20px", display: "flex", alignItems: "flex-start", gap: 12,
  } as React.CSSProperties,
  errorTitle: {
    fontSize: 14, fontWeight: 600, color: "#991b1b", margin: "0 0 4px 0", fontFamily: font,
  } as React.CSSProperties,
  errorBody: {
    fontSize: 13, color: "#b91c1c", margin: 0, lineHeight: 1.5,
  } as React.CSSProperties,
  retryBtn: {
    display: "inline-flex", alignItems: "center", gap: 6,
    padding: "7px 14px", fontSize: 12, fontWeight: 600,
    color: "#fff", background: "#ef4444", border: "none", borderRadius: 8, cursor: "pointer",
  } as React.CSSProperties,
  statusBtn: {
    display: "inline-flex", alignItems: "center", gap: 6,
    padding: "7px 14px", fontSize: 12, fontWeight: 600,
    color: "#991b1b", background: "#fecaca", border: "none", borderRadius: 8, cursor: "pointer",
  } as React.CSSProperties,

  /* Bottom bar */
  bottomBar: {
    borderTop: "1px solid #e8ecf0", background: "#ffffff",
    padding: "12px 24px 16px", flexShrink: 0,
  } as React.CSSProperties,
  chipTrack: {
    display: "flex", gap: 8, overflowX: "auto" as const,
    paddingBottom: 10, marginBottom: 4,
    scrollbarWidth: "none" as const,
  },
  inputOuter: { maxWidth: 768, margin: "0 auto" } as React.CSSProperties,
  attachBtn: {
    width: 36, height: 36, display: "flex", alignItems: "center", justifyContent: "center",
    background: "transparent", border: "none", cursor: "pointer",
    borderRadius: 8, color: "#94a3b8", flexShrink: 0,
  } as React.CSSProperties,
  textarea: {
    flex: 1, border: "none", outline: "none", resize: "none" as const,
    padding: "8px 4px", fontSize: 14, lineHeight: 1.5, background: "transparent",
    color: "#0f172a", minHeight: 24, maxHeight: 160, fontFamily: font,
  },
  disclaimer: {
    fontSize: 11, color: "#94a3b8", textAlign: "center" as const,
    margin: "8px 0 0 0", fontFamily: font,
  },
};
