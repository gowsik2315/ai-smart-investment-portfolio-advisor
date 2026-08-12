/**
 * Pie Chart Component
 * Visual pie chart for portfolio allocation
 */

import React from 'react';

const PieChart = ({ data, size = 300 }) => {
  // Calculate total
  const total = data.reduce((sum, item) => sum + item.value, 0);
  
  // Calculate percentages and angles
  let currentAngle = -90; // Start from top
  const slices = data.map((item) => {
    const percentage = (item.value / total) * 100;
    const angle = (item.value / total) * 360;
    const slice = {
      ...item,
      percentage,
      startAngle: currentAngle,
      endAngle: currentAngle + angle,
    };
    currentAngle += angle;
    return slice;
  });
  
  // Create SVG paths for pie slices
  const createArcPath = (startAngle, endAngle, radius) => {
    const start = polarToCartesian(size / 2, size / 2, radius, endAngle);
    const end = polarToCartesian(size / 2, size / 2, radius, startAngle);
    const largeArcFlag = endAngle - startAngle <= 180 ? '0' : '1';
    
    return [
      'M', size / 2, size / 2,
      'L', start.x, start.y,
      'A', radius, radius, 0, largeArcFlag, 0, end.x, end.y,
      'Z'
    ].join(' ');
  };
  
  const polarToCartesian = (centerX, centerY, radius, angleInDegrees) => {
    const angleInRadians = (angleInDegrees * Math.PI) / 180.0;
    return {
      x: centerX + radius * Math.cos(angleInRadians),
      y: centerY + radius * Math.sin(angleInRadians),
    };
  };
  
  const radius = (size / 2) - 10;
  
  return (
    <div className="flex flex-col items-center">
      <svg width={size} height={size} className="overflow-visible">
        {/* Pie slices */}
        {slices.map((slice, index) => (
          <g key={index}>
            <path
              d={createArcPath(slice.startAngle, slice.endAngle, radius)}
              fill={slice.color}
              stroke="white"
              strokeWidth="2"
              className="transition-all duration-300 hover:opacity-80 cursor-pointer"
            >
              <title>{`${slice.label}: ${slice.percentage.toFixed(1)}%`}</title>
            </path>
          </g>
        ))}
        
        {/* Center circle (donut style) */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius * 0.5}
          fill="white"
        />
        
        {/* Center text */}
        <text
          x={size / 2}
          y={size / 2}
          textAnchor="middle"
          dominantBaseline="middle"
          className="text-lg font-bold fill-secondary-900"
        >
          Portfolio
        </text>
      </svg>
      
      {/* Legend */}
      <div className="mt-6 grid grid-cols-2 gap-3 w-full max-w-md">
        {slices.map((slice, index) => (
          <div key={index} className="flex items-center gap-2">
            <div
              className="w-4 h-4 rounded"
              style={{ backgroundColor: slice.color }}
            ></div>
            <div className="flex-1">
              <div className="text-sm font-medium text-secondary-900">
                {slice.label}
              </div>
              <div className="text-xs text-secondary-600">
                {slice.percentage.toFixed(1)}%
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default PieChart;
