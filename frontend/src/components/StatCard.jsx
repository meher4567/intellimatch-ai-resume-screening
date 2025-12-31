import React from 'react';
import { TrendingUp, TrendingDown } from 'lucide-react';

const StatCard = ({ 
  title, 
  value, 
  change, 
  icon: Icon, 
  color = 'blue',
  trend = 'up',
  gradient = true 
}) => {
  const colors = {
    blue: 'from-blue-500 to-blue-600',
    green: 'from-green-500 to-emerald-600',
    purple: 'from-purple-500 to-purple-600',
    pink: 'from-pink-500 to-rose-600',
    orange: 'from-orange-500 to-amber-600',
    indigo: 'from-indigo-500 to-purple-600',
  };

  const TrendIcon = trend === 'up' ? TrendingUp : TrendingDown;
  const trendColor = trend === 'up' ? 'text-green-600' : 'text-red-600';

  return (
    <div className={`
      ${gradient ? `bg-gradient-to-br ${colors[color]}` : 'bg-white'} 
      rounded-2xl p-6 shadow-glass card-hover-lift
      ${gradient ? 'text-white' : 'text-gray-800'}
      animate-fade-in-up relative overflow-hidden
    `}>
      {/* Background decoration */}
      <div className="absolute top-0 right-0 w-32 h-32 bg-white/10 rounded-full blur-2xl transform translate-x-1/2 -translate-y-1/2"></div>
      
      <div className="relative z-10">
        <div className="flex items-start justify-between mb-4">
          <div>
            <p className={`text-sm font-medium ${gradient ? 'text-white/80' : 'text-gray-600'} uppercase tracking-wide`}>
              {title}
            </p>
            <p className="text-4xl font-bold mt-2">{value}</p>
          </div>
          {Icon && (
            <div className={`
              w-14 h-14 rounded-xl flex items-center justify-center
              ${gradient ? 'bg-white/20 backdrop-blur-sm' : 'bg-gray-100'}
            `}>
              <Icon className={`w-7 h-7 ${gradient ? 'text-white' : `text-${color}-600`}`} />
            </div>
          )}
        </div>
        
        {change && (
          <div className={`flex items-center gap-2 ${gradient ? 'text-white/90' : trendColor}`}>
            <TrendIcon className="w-4 h-4" />
            <span className="text-sm font-semibold">{change} from last week</span>
          </div>
        )}
      </div>
    </div>
  );
};

export default StatCard;
