import React from 'react';
import { Outlet } from 'react-router-dom';
import { StudentHeader } from '../components/student/StudentHeader';
import { Footer } from '../components/common/Footer';

export const StudentLayout: React.FC = () => {
  return (
    <div className="min-h-screen flex flex-col bg-background text-on-surface">
      <StudentHeader />
      <main className="flex-1 w-full pt-16 px-4 lg:px-12 py-8 max-w-7xl mx-auto">
        <Outlet />
      </main>
      <Footer />
    </div>
  );
};
