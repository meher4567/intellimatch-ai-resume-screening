import React from 'react';
import { Loader2 } from 'lucide-react';

const LoadingSpinner = ({ size = 'md', text = '' }) => {
  const sizes = {
    sm: 'w-5 h-5',
    md: 'w-10 h-10',
    lg: 'w-16 h-16',
    xl: 'w-24 h-24',
  };
  
  return (
    <div className="flex flex-col items-center justify-center py-12 animate-fade-in">
      <div className="relative">
        <Loader2 className={`${sizes[size]} text-primary-500 animate-spin`} />
        <div className="absolute inset-0 blur-xl bg-primary-500/20 rounded-full animate-pulse"></div>
      </div>
      {text && <p className="mt-6 text-gray-700 font-medium text-lg">{text}</p>}
    </div>
  );
};

export default LoadingSpinner;
