import { useState, useEffect, useRef, useCallback } from "react";

export interface FilterState {
  city: string;
  category: string;
  status: string;
  recommendation: string;
  provider: string;
}

export interface PaginationState {
  page: number;
  pageSize: number;
  sortField: string;
  sortDir: "asc" | "desc";
}

const defaultFilters: FilterState = {
  city: "All",
  category: "All",
  status: "All",
  recommendation: "All",
  provider: "All",
};

const defaultPagination: PaginationState = {
  page: 1,
  pageSize: 15,
  sortField: "difference_pct",
  sortDir: "desc",
};

export function useFilters(
  initialFilters?: Partial<FilterState>,
  initialPagination?: Partial<PaginationState>
) {
  const mergedDefaults = { ...defaultFilters, ...initialFilters };
  const mergedPagDefaults = { ...defaultPagination, ...initialPagination };

  const [filters, setFilters] = useState<FilterState>(mergedDefaults);
  const [search, setSearch] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");
  const [pagination, setPagination] = useState<PaginationState>(mergedPagDefaults);

  const isInitialMount = useRef(true);

  // Debounce search input by 300ms
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(search);
    }, 300);
    return () => clearTimeout(timer);
  }, [search]);

  // When filters or debouncedSearch change, reset pagination to page 1
  useEffect(() => {
    if (isInitialMount.current) {
      isInitialMount.current = false;
      return;
    }
    setPagination(prev => ({ ...prev, page: 1 }));
  }, [filters, debouncedSearch]);

  const updateFilter = useCallback((key: keyof FilterState, value: string) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  }, []);

  const updateSearch = useCallback((query: string) => {
    setSearch(query);
  }, []);

  const resetFilters = useCallback(() => {
    setFilters(mergedDefaults);
    setSearch("");
    setDebouncedSearch("");
    setPagination(mergedPagDefaults);
  }, []);

  const updatePagination = useCallback((key: keyof PaginationState, value: any) => {
    setPagination(prev => ({ ...prev, [key]: value }));
  }, []);

  // FIXED: Atomic sort update — single setPagination call instead of 3 separate calls
  const handleSort = useCallback((field: string) => {
    setPagination(prev => {
      const newDir = prev.sortField === field
        ? (prev.sortDir === "asc" ? "desc" : "asc")
        : "desc";
      return {
        ...prev,
        sortField: field,
        sortDir: newDir,
        page: 1,
      };
    });
  }, []);

  return {
    filters,
    search,
    debouncedSearch,
    pagination,
    updateFilter,
    updateSearch,
    updatePagination,
    handleSort,
    resetFilters,
  };
}
