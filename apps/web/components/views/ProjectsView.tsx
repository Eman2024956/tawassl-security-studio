'use client';

import React from 'react';
import { useStudio } from '../../lib/context';
import { FolderGit2, Plus, Calendar, Layers, ArrowRight } from 'lucide-react';

export default function ProjectsView() {
  const { projects, targets, setIsWizardOpen, setActiveTab, t } = useStudio();

  return (
    <div className="space-y-5">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-zinc-800 pb-4">
        <div>
          <h2 className="text-base font-bold text-zinc-100 flex items-center gap-2">
            <FolderGit2 className="w-5 h-5 text-cyan-400" />
            <span>Workspace Projects</span>
          </h2>
          <p className="text-xs text-zinc-400 mt-1">
            Projects organize targets, authorized scopes, and continuous security audits.
          </p>
        </div>
        <button
          onClick={() => setIsWizardOpen(true)}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-semibold shadow-md transition cursor-pointer"
        >
          <Plus className="w-4 h-4" />
          <span>New Project</span>
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {projects.map((proj) => {
          const projectTargets = targets.filter((tgt) => tgt.project_id === proj.id);
          return (
            <div
              key={proj.id}
              className="p-5 rounded-xl border border-zinc-800 bg-zinc-900/40 hover:border-zinc-700 transition flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="font-bold text-sm text-zinc-100">{proj.name}</span>
                  <span className="text-[10px] font-mono text-zinc-400">ID: {proj.id}</span>
                </div>
                <p className="text-xs text-zinc-400 leading-relaxed">{proj.description}</p>
              </div>

              <div className="mt-5 pt-3 border-t border-zinc-800 flex items-center justify-between text-xs">
                <div className="flex items-center gap-1 text-zinc-400">
                  <Layers className="w-3.5 h-3.5 text-cyan-400" />
                  <span>{projectTargets.length} Registered Targets</span>
                </div>
                <button
                  onClick={() => setActiveTab('targets')}
                  className="text-cyan-400 hover:text-cyan-300 flex items-center gap-1 font-medium cursor-pointer"
                >
                  <span>Explore Scope</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
