import React from 'react';

interface AuthCardProps {
  children: React.ReactNode;
  title: string;
  subtitle?: string;
  className?: string;
}

const AuthCard: React.FC<AuthCardProps> = ({
  children,
  title,
  subtitle,
  className = ''
}) => {
  return (
    <div className={`
      min-h-screen flex items-center justify-center
      p-2 sm:p-4 mobile-safe-area
      ${className}
    `}>
      {/* Glassmorphism Card - Mobile responsive sizing */}
      <div className="
        w-full
        max-w-[320px] sm:max-w-[400px]
        min-h-[420px] sm:min-h-[580px] sm:h-[580px]
        bg-glass-card
        backdrop-blur-glass
        rounded-glass
        border-2 border-glass-border
        shadow-glass
        px-[16px] sm:px-[35px]
        py-[20px] sm:py-[50px]
        animate-mobile-fade-in
      ">
        {/* Header */}
        <div className="text-center mb-4 sm:mb-8">
          <h3 className="
            text-[20px] sm:text-[32px]
            font-medium
            leading-[26px] sm:leading-[42px]
            text-center
            text-glass font-poppins
            tracking-[0.5px]
          ">
            {title}
          </h3>
          {subtitle && (
            <p className="text-glass/80 text-xs sm:text-sm mt-1 sm:mt-2 font-poppins">
              {subtitle}
            </p>
          )}
        </div>

        {/* Content */}
        <div className="space-y-0">
          {children}
        </div>
      </div>
    </div>
  );
};

export default AuthCard;
