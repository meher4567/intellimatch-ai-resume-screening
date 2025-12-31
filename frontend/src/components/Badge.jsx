import React from 'react';

const Badge = ({ children, variant = 'default', size = 'md', className = '', glow = false }) => {
  const variants = {
    default: 'bg-gray-100 text-gray-800 border border-gray-200',
    primary: 'bg-gradient-to-r from-primary-100 to-primary-50 text-primary-800 border border-primary-200',
    success: 'bg-gradient-to-r from-green-100 to-emerald-50 text-green-800 border border-green-200',
    warning: 'bg-gradient-to-r from-yellow-100 to-amber-50 text-yellow-800 border border-yellow-200',
    danger: 'bg-gradient-to-r from-red-100 to-rose-50 text-red-800 border border-red-200',
    purple: 'bg-gradient-to-r from-purple-100 to-violet-50 text-purple-800 border border-purple-200',
    'tier-S': 'bg-gradient-to-r from-yellow-400 to-yellow-300 text-gray-900 shadow-lg shadow-yellow-500/40 font-bold',
    'tier-A': 'bg-gradient-to-r from-gray-300 to-gray-200 text-gray-900 shadow-lg shadow-gray-400/40 font-bold',
    'tier-B': 'bg-gradient-to-r from-orange-400 to-orange-300 text-white shadow-lg shadow-orange-500/40 font-bold',
    'tier-C': 'bg-gradient-to-r from-blue-500 to-blue-400 text-white shadow-md shadow-blue-500/30',
    'tier-D': 'bg-gradient-to-r from-green-500 to-green-400 text-white shadow-md shadow-green-500/30',
    'tier-F': 'bg-gradient-to-r from-red-500 to-red-400 text-white shadow-md shadow-red-500/30',
  };
  
  const sizes = {
    sm: 'px-2.5 py-1 text-xs',
    md: 'px-3 py-1.5 text-sm',
    lg: 'px-4 py-2 text-base',
  };
  
  const glowClass = glow ? 'badge-glow' : '';
  
  return (
    <span className={`inline-flex items-center font-semibold rounded-full ${variants[variant]} ${sizes[size]} ${glowClass} ${className} transition-all duration-200`}>
      {children}
    </span>
  );
};

export default Badge;
