'use client';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useState, type ReactNode } from 'react';
import { wireSharedAccessTokenProvider } from '@/lib/access-token';

/**
 * App-wide providers: TanStack Query for server state + API token wiring.
 *
 * Keep this as a client boundary so the root layout can stay a Server Component.
 */
export function Providers({ children }: { children: ReactNode }) {
  const [queryClient] = useState(() => {
    wireSharedAccessTokenProvider();
    return new QueryClient({
      defaultOptions: {
        queries: {
          staleTime: 30_000,
          refetchOnWindowFocus: false,
        },
      },
    });
  });

  return (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
}
