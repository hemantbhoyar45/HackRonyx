import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Sidebar from '../../components/layout/Sidebar';
import Header from '../../components/layout/Header';
import PageContainer from '../../components/layout/PageContainer';
import Dashboard from '../../pages/Dashboard';
import PriorityQueue from '../../pages/PriorityQueue';
import Methodology from '../../pages/Methodology';
import DownloadReport from '../../pages/DownloadReport';

export default function AppRouter() {
  return (
    <Router>
      <div className="flex h-screen bg-slate-50">
        <Sidebar />
        <div className="flex-1 flex flex-col overflow-hidden">
          <Header />
          <PageContainer>
            <Routes>
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/priority-queue" element={<PriorityQueue />} />
              <Route path="/methodology" element={<Methodology />} />
              <Route path="/download-report" element={<DownloadReport />} />
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
            </Routes>
          </PageContainer>
        </div>
      </div>
    </Router>
  );
}
