import React from 'react';
import { Loader2 } from 'lucide-react';

const Button = ({ 
  children, 
  variant = 'primary', 
  size = 'md', 
  loading = false, 
  disabled = false,
  icon: Icon,
  className = '',
  ...props 
}) => {
  const baseStyles = 'inline-flex items-center justify-center font-semibold rounded-xl transition-all duration-200 focus:outline-none focus:ring-4 focus:ring-offset-2 disabled:opacity-60 disabled:cursor-not-allowed';
  
  const variants = {
    primary: 'btn-gradient',
    secondary: 'bg-white/90 backdrop-blur-sm text-gray-800 border-2 border-gray-300 hover:bg-white hover:border-primary-500 hover:-translate-y-1 hover:shadow-lg focus:ring-gray-300',
    success: 'bg-gradient-to-r from-green-500 to-emerald-500 text-white shadow-lg shadow-green-500/40 hover:-translate-y-1 hover:shadow-xl hover:shadow-green-500/50 focus:ring-green-500/50',
    danger: 'bg-gradient-to-r from-red-500 to-rose-500 text-white shadow-lg shadow-red-500/40 hover:-translate-y-1 hover:shadow-xl hover:shadow-red-500/50 focus:ring-red-500/50',
    outline: 'border-2 border-primary-500 text-primary-600 bg-white/50 backdrop-blur-sm hover:bg-primary-500 hover:text-white hover:-translate-y-1 hover:shadow-lg focus:ring-primary-500/50',
    ghost: 'text-gray-700 hover:bg-white/50 hover:backdrop-blur-sm focus:ring-gray-300',
  };
  
  const sizes = {
    sm: 'px-4 py-2 text-sm gap-1.5',
    md: 'px-6 py-3 text-base gap-2',
    lg: 'px-8 py-4 text-lg gap-2.5',
  };
  
  return (
    <button
      className={`${baseStyles} ${variants[variant]} ${sizes[size]} ${className}`}
      disabled={disabled || loading}
      {...props}
    >
      {loading ? (
        <>
          <Loader2 className="w-5 h-5 animate-spin" />
          <span>Loading...</span>
        </>
      ) : (
        <>
          {Icon && <Icon className="w-5 h-5" />}
          {children}
        </>
      )}
    </button>
  );
};

export default Button;
