"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function Home() {
  const router = useRouter();
  
  // Auto-redirect to dashboard (guest mode - no authentication required)
  useEffect(() => {
    router.replace("/dashboard");
  }, [router]);

  return (
    <main className="min-h-screen bg-white text-black flex items-center justify-center">
      <div className="max-w-md mx-auto px-4 py-24 text-center">
        <h1 className="text-6xl font-bold tracking-tight text-black mb-8">
          Fortes Education
        </h1>
        <p className="text-xl text-gray-500 mb-8">
          Advanced RAG Q&A System
          <br />
          Intelligent. Grounded. Safe.
        </p>
        <p className="text-gray-600">
          Redirecting to dashboard...
        </p>
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mt-8"></div>
      </div>
    </main>
  );
}
