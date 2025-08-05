import React from 'react';

export const Tabs = ({ children, value, onValueChange }) => {
  return (
    <div className="tabs" data-value={value}>
      {React.Children.map(children, child => 
        React.cloneElement(child, { activeTab: value, onTabChange: onValueChange })
      )}
    </div>
  );
};

export const TabsList = ({ children, activeTab, onTabChange }) => {
  return (
    <div className="tabs-list">
      {React.Children.map(children, child => 
        React.cloneElement(child, { activeTab, onTabChange })
      )}
    </div>
  );
};

export const TabsTrigger = ({ children, value, activeTab, onTabChange }) => {
  return (
    <button
      className={`tab-trigger ${activeTab === value ? 'active' : ''}`}
      onClick={() => onTabChange(value)}
    >
      {children}
    </button>
  );
};

export const TabsContent = ({ children, value, activeTab }) => {
  if (activeTab !== value) return null;
  
  return (
    <div className="tab-content">
      {children}
    </div>
  );
};
