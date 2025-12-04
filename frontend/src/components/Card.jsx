import React from 'react';

const Card = ({ children, className = '', title, action, hover = false }) => {
  return (
    <div className={`bg-white rounded-lg shadow ${hover ? 'hover:shadow-lg transition-shadow' : ''} ${className}`}>
      {title && (
        <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
          <h3 className="text-lg font-semibold text-gray-800">{title}</h3>
          {action && <div>{action}</div>}
        </div>
      )}
      <div className="p-6">{children}</div>
    </div>
  );
};

export default Card;
