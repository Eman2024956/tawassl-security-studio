'use client';

import React from 'react';
import { StudioProvider, useStudio } from '../lib/context';
import Header from '../components/Header';
import Sidebar from '../components/Sidebar';
import WizardModal from '../components/WizardModal';
import DashboardView from '../components/views/DashboardView';
import ProjectsView from '../components/views/ProjectsView';
import TargetsView from '../components/views/TargetsView';
import PlansView from '../components/views/PlansView';
import AgentView from '../components/views/AgentView';
import CommandQueueView from '../components/views/CommandQueueView';
import LiveOutputView from '../components/views/LiveOutputView';
import FindingsView from '../components/views/FindingsView';
import ReportsView from '../components/views/ReportsView';
import SettingsView from '../components/views/SettingsView';

function StudioContent() {
  const { activeTab } = useStudio();

  const renderActiveView = () => {
    switch (activeTab) {
      case 'dashboard':
        return <DashboardView />;
      case 'projects':
        return <ProjectsView />;
      case 'targets':
        return <TargetsView />;
      case 'plans':
        return <PlansView />;
      case 'agent':
        return <AgentView />;
      case 'queue':
        return <CommandQueueView />;
      case 'live':
        return <LiveOutputView />;
      case 'findings':
        return <FindingsView />;
      case 'reports':
        return <ReportsView />;
      case 'settings':
        return <SettingsView />;
      default:
        return <DashboardView />;
    }
  };

  return (
    <div className="flex flex-col min-h-screen">
      <Header />
      <div className="flex flex-1 overflow-hidden">
        <Sidebar />
        <main className="flex-1 p-6 overflow-y-auto bg-zinc-950">
          <div className="max-w-7xl mx-auto">
            {renderActiveView()}
          </div>
        </main>
      </div>
      <WizardModal />
    </div>
  );
}

export default function Page() {
  return (
    <StudioProvider>
      <StudioContent />
    </StudioProvider>
  );
}
