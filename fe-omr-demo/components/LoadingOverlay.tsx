"use client";

import { useLoading } from "@/app/context/LoadingContext";

const LoadingOverlay: React.FC = () => {
  const { isLoading, message } = useLoading();

  if (!isLoading) return null;

  return (
    <div className="loading-overlay flex flex-col">
      <div className="spinner"></div>
      <style jsx>{`
        .loading-overlay {
          position: fixed;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          background: rgba(0, 0, 0, 0.5);
          display: flex;
          justify-content: center;
          align-items: center;
          z-index: 9999;
        }
        .spinner {
          width: 50px;
          height: 50px;
          border: 4px solid rgba(255, 255, 255, 0.6);
          border-top: 4px solid #fff;
          border-radius: 50%;
          animation: spin 1s linear infinite;
        }
        @keyframes spin {
          0% {
            transform: rotate(0deg);
          }
          100% {
            transform: rotate(360deg);
          }
        }
      `}</style>
      {message && <span
        className="text-white animate-pulse mt-5 px-5 font-bold"
        style={{ textShadow: '2px 2px 4px rgba(0,0,0,0.5)' }}
      >
        {message}
      </span>}
    </div>
  );
};

export default LoadingOverlay;