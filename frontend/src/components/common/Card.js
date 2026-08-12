/**
 * Card Component
 * Reusable card container
 */

import React from 'react';

const Card = ({ children, className = '', title = null }) => {
  return (
    <div className={`card ${className}`}>
      {title && <h3 className="mb-4">{title}</h3>}
      {children}
    </div>
  );
};

export default Card;
