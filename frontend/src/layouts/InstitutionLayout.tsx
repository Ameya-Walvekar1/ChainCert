import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import { InstitutionSidebar } from '../components/institution/InstitutionSidebar';
import { InstitutionHeader } from '../components/institution/InstitutionHeader';

export const InstitutionLayout: React.FC = () => {
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false);

  return (
    <div className="min-h-screen bg-surface flex flex-col">
      <InstitutionSidebar 
        mobileOpen={mobileSidebarOpen} 
        onCloseMobile={() => setMobileSidebarOpen(false)} 
      />
      
      <div className="lg:pl-72 flex-1 flex flex-col min-w-0">
        <InstitutionHeader 
          onToggleMobileSidebar={() => setMobileSidebarOpen(prev => !prev)} 
        />
        
        <main className="flex-1 pt-16 px-4 sm:px-8 py-6 w-full max-w-7xl mx-auto min-w-0">
          <Outlet />
        </main>
      </div>
    </div>
  );
};
