import React, { createContext, useContext, useState, useCallback, useRef } from "react";

// ── Action Types ──────────────────────────────────────────────
export type ActionType = "details" | "compare" | "simulator" | "ai-insight";

interface ActionState {
  activeAction: ActionType | null;
  selectedTest: any | null;
  actionInProgress: boolean;
}

interface ActionContextValue extends ActionState {
  openAction: (type: ActionType, test: any) => void;
  closeAction: () => void;
}

const ActionContext = createContext<ActionContextValue | null>(null);

// ── Provider ──────────────────────────────────────────────────
export function ActionProvider({ children }: { children: React.ReactNode }) {
  const [state, setState] = useState<ActionState>({
    activeAction: null,
    selectedTest: null,
    actionInProgress: false,
  });

  // Guard against rapid double-clicks
  const lockRef = useRef(false);

  const openAction = useCallback((type: ActionType, test: any) => {
    if (lockRef.current) return;
    lockRef.current = true;

    setState({
      activeAction: type,
      selectedTest: test,
      actionInProgress: true,
    });

    // Release lock after a short delay so the modal/drawer has time to mount
    setTimeout(() => {
      lockRef.current = false;
      setState((prev) => ({ ...prev, actionInProgress: false }));
    }, 150);
  }, []);

  const closeAction = useCallback(() => {
    setState({
      activeAction: null,
      selectedTest: null,
      actionInProgress: false,
    });
    lockRef.current = false;
  }, []);

  return (
    <ActionContext.Provider value={{ ...state, openAction, closeAction }}>
      {children}
    </ActionContext.Provider>
  );
}

// ── Hook ──────────────────────────────────────────────────────
export function useAction() {
  const ctx = useContext(ActionContext);
  if (!ctx) throw new Error("useAction must be used within <ActionProvider>");
  return ctx;
}
