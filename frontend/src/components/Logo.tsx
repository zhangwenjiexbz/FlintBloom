import React from 'react';

export const Logo: React.FC<{ size?: number }> = ({ size = 40 }) => {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 100 100"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      {/* Gradient Definitions */}
      <defs>
        <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" style={{ stopColor: '#667eea', stopOpacity: 1 }} />
          <stop offset="100%" style={{ stopColor: '#764ba2', stopOpacity: 1 }} />
        </linearGradient>
        <linearGradient id="grad2" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" style={{ stopColor: '#ff8c42', stopOpacity: 1 }} />
          <stop offset="100%" style={{ stopColor: '#fb8500', stopOpacity: 1 }} />
        </linearGradient>
        <filter id="glow">
          <feGaussianBlur stdDeviation="2" result="coloredBlur" />
          <feMerge>
            <feMergeNode in="coloredBlur" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
      </defs>

      {/* Outer Circle - Monitoring Ring */}
      <circle
        cx="50"
        cy="50"
        r="45"
        stroke="url(#grad1)"
        strokeWidth="3"
        fill="none"
        opacity="0.3"
      />

      {/* Middle Circle - Data Flow */}
      <circle
        cx="50"
        cy="50"
        r="35"
        stroke="url(#grad1)"
        strokeWidth="2"
        fill="none"
        strokeDasharray="5,5"
        opacity="0.5"
      >
        <animateTransform
          attributeName="transform"
          type="rotate"
          from="0 50 50"
          to="360 50 50"
          dur="20s"
          repeatCount="indefinite"
        />
      </circle>

      {/* Center Bloom - Stylized Flower/Node with Sharp Petals */}
      <g filter="url(#glow)">
        {/* Center Core */}
        <circle cx="50" cy="50" r="12" fill="url(#grad1)" />

        {/* Sharp Petals - Using Polygons for Sharp Edges */}
        {/* Top Petal */}
        <polygon
          points="50,18 44,30 56,30"
          fill="url(#grad2)"
          opacity="0.9"
        />

        {/* Right Petal */}
        <polygon
          points="82,50 70,44 70,56"
          fill="url(#grad2)"
          opacity="0.9"
        />

        {/* Bottom Petal */}
        <polygon
          points="50,82 44,70 56,70"
          fill="url(#grad2)"
          opacity="0.9"
        />

        {/* Left Petal */}
        <polygon
          points="18,50 30,44 30,56"
          fill="url(#grad2)"
          opacity="0.9"
        />

        {/* Diagonal Sharp Petals */}
        {/* Top-Left */}
        <polygon
          points="32,32 38,38 32,44 26,38"
          fill="url(#grad2)"
          opacity="0.8"
        />

        {/* Top-Right */}
        <polygon
          points="68,32 74,38 68,44 62,38"
          fill="url(#grad2)"
          opacity="0.8"
        />

        {/* Bottom-Right */}
        <polygon
          points="68,68 74,62 68,56 62,62"
          fill="url(#grad2)"
          opacity="0.8"
        />

        {/* Bottom-Left */}
        <polygon
          points="32,68 38,62 32,56 26,62"
          fill="url(#grad2)"
          opacity="0.8"
        />

        {/* Inner Glow */}
        <circle cx="50" cy="50" r="8" fill="white" opacity="0.9" />
        <circle cx="50" cy="50" r="4" fill="url(#grad1)" />
      </g>

      {/* Pulse Animation Circles */}
      <circle cx="50" cy="50" r="20" stroke="url(#grad1)" strokeWidth="1" fill="none" opacity="0">
        <animate
          attributeName="r"
          from="20"
          to="40"
          dur="2s"
          repeatCount="indefinite"
        />
        <animate
          attributeName="opacity"
          from="0.6"
          to="0"
          dur="2s"
          repeatCount="indefinite"
        />
      </circle>
    </svg>
  );
};

export default Logo;
