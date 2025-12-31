import React from 'react';

const Card = ({ children, className = '', title, action, hover = true, gradient = false }) => {
  const baseClass = gradient 
    ? 'glass-card' 
    : 'bg-white/95 backdrop-blur-xl rounded-2xl shadow-glass';
  
  const hoverClass = hover ? 'card-hover-lift glass-card-hover' : '';
  
  return (
    <div className={`${baseClass} ${hoverClass} ${className} animate-fade-in-up`}>
      {title && (
        <div className="px-6 py-5 border-b border-gray-200/50 flex justify-between items-center">
          <h3 className="text-xl font-bold text-gray-800">{title}</h3>
          {action && <div>{action}</div>}
        </div>
      )}
      <div className="p-6">{children}</div>
    </div>
  );
};

export default Card;
