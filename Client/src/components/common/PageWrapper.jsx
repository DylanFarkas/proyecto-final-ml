import React from 'react';
import ErrorBoundary from './ErrorBoundary';

const PageWrapper = ({ children, pageName }) => {
  return (
    <ErrorBoundary>
      <div className="min-h-screen bg-gray-100 dark:bg-gray-900">
        <div className="container mx-auto py-8 px-4">
          {children}
        </div>
      </div>
    </ErrorBoundary>
  );
};

export default PageWrapper;
