/**
 * Risk Gauge Component
 * Visual gauge display for risk score
 */

import React from 'react';

const RiskGauge = ({ score, size = 200 }) => {
  // Ensure score is within 0-100 range
  const normalizedScore = Math.max(0, Math.min(100, score));
  
  // Calculate rotation angle (-90 to 90 degrees)
  const rotation = -90 + (normalizedScore / 100 * 180);
  
  // Determine color based on score ranges
  const getColor = () => {
    if (normalizedScore < 40) return '#10b981'; // Green - Conservative
    if (normalizedScore < 70) return '#f59e0b'; // Orange - Moderate
    return '#ef4444'; // Red - Aggressive
  };
  
  // Determine investor type
  const getInvestorType = () => {
    if (normalizedScore < 40) return 'Conservative';
    if (normalizedScore < 70) return 'Moderate';
    return 'Aggressive';
  };
  
  const color = getColor();
  const investorType = getInvestorType();
  const radius = size / 2 - 20;
  const strokeWidth = 20;
  const center = size / 2;
  
  // Calculate arc path for the gauge background
  const startAngle = -90;
  const endAngle = 90;
  
  const polarToCartesian = (centerX, centerY, radius, angleInDegrees) => {
    const angleInRadians = (angleInDegrees - 90) * Math.PI / 180.0;
    return {
      x: centerX + (radius * Math.cos(angleInRadians)),
      y: centerY + (radius * Math.sin(angleInRadians))
    };
  };
  
  const describeArc = (x, y, radius, startAngle, endAngle) => {
    const start = polarToCartesian(x, y, radius, endAngle);
    const end = polarToCartesian(x, y, radius, startAngle);
    const largeArcFlag = endAngle - startAngle <= 180 ? "0" : "1";
    return [
      "M", start.x, start.y,
      "A", radius, radius, 0, largeArcFlag, 0, end.x, end.y
    ].join(" ");
  };
  
  const gaugeArc = describeArc(center, center, radius, startAngle, endAngle);
  const filledArc = describeArc(center, center, radius, startAngle, startAngle + (normalizedScore / 100 * 180));
  
  return (
    <div className="flex flex-col items-center">
      <svg width={size} height={size * 0.7} className="overflow-visible">
        {/* Background arc */}
        <path
          d={gaugeArc}
          fill="none"
          stroke="#e5e7eb"
          strokeWidth={strokeWidth}
          strokeLinecap="round"
        />
        
        {/* Filled arc */}
        <path
          d={filledArc}
          fill="none"
          stroke={color}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
        />
        
        {/* Score segments markers */}
        <line
          x1={center - radius}
          y1={center}
          x2={center - radius + 10}
          y2={center}
          stroke="#9ca3af"
          strokeWidth="2"
        />
        <line
          x1={center}
          y1={center - radius}
          x2={center}
          y2={center - radius + 10}
          stroke="#9ca3af"
          strokeWidth="2"
        />
        <line
          x1={center + radius}
          y1={center}
          x2={center + radius - 10}
          y2={center}
          stroke="#9ca3af"
          strokeWidth="2"
        />
        
        {/* Needle */}
        <g transform={`rotate(${rotation} ${center} ${center})`}>
          <line
            x1={center}
            y1={center}
            x2={center}
            y2={center - radius + strokeWidth / 2}
            stroke="#374151"
            strokeWidth="3"
            strokeLinecap="round"
          />
          <circle
            cx={center}
            cy={center}
            r="6"
            fill="#374151"
          />
        </g>
        
        {/* Center circle */}
        <circle
          cx={center}
          cy={center}
          r="4"
          fill="white"
        />
        
        {/* Labels */}
        <text
          x={center - radius - 5}
          y={center + 20}
          fill="#6b7280"
          fontSize="12"
          textAnchor="end"
        >
          0
        </text>
        <text
          x={center}
          y={center - radius - 10}
          fill="#6b7280"
          fontSize="12"
          textAnchor="middle"
        >
          50
        </text>
        <text
          x={center + radius + 5}
          y={center + 20}
          fill="#6b7280"
          fontSize="12"
          textAnchor="start"
        >
          100
        </text>
      </svg>
      
      {/* Score display */}
      <div className="text-center mt-4">
        <div className="text-4xl font-bold" style={{ color }}>
          {normalizedScore.toFixed(1)}
        </div>
        <div className="text-sm text-secondary-600 mt-1">Risk Score</div>
        <div 
          className="text-lg font-semibold mt-2 px-4 py-2 rounded-full inline-block"
          style={{ 
            backgroundColor: `${color}20`,
            color: color
          }}
        >
          {investorType}
        </div>
      </div>
      
      {/* Legend */}
      <div className="mt-6 flex gap-6 text-xs">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-green-500"></div>
          <span className="text-secondary-600">Conservative (0-39)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-orange-500"></div>
          <span className="text-secondary-600">Moderate (40-69)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-red-500"></div>
          <span className="text-secondary-600">Aggressive (70-100)</span>
        </div>
      </div>
    </div>
  );
};

export default RiskGauge;
