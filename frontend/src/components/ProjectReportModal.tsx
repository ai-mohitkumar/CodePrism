import React, { useState } from 'react';
import { 
  FolderArchive, 
  X, 
  FileCode, 
  ShieldAlert, 
  Award, 
  TrendingUp, 
  Zap, 
  GitBranch, 
  CheckCircle2, 
  ExternalLink 
} from 'lucide-react';
import { ProjectReportResponse, ProjectFileSummary } from '../types';

interface ProjectReportModalProps {
  report: ProjectReportResponse | null;
  isOpen: boolean;
  onClose: () => void;
  onOpenFileInEditor: (file: ProjectFileSummary) => void;
}

export const ProjectReportModal: React.FC<ProjectReportModalProps> = ({
  report,
  isOpen,
  onClose,
  onOpenFileInEditor,
}) => {
  const [activeTab, setActiveTab] = useState<'files' | 'optimizations' | 'dependencies'>('files');

  if (!isOpen || !report) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-md p-4 animate-in fade-in select-none">
      <div className="bg-[#0E1322] border border-gray-800 rounded-2xl w-full max-w-4xl max-h-[90vh] shadow-2xl overflow-hidden flex flex-col">
        {/* Header */}
        <div className="px-6 py-4 border-b border-gray-800 bg-[#12182B] flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-purple-600 to-indigo-600 flex items-center justify-center text-white shadow-md">
              <FolderArchive className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="font-bold text-base text-gray-100">{report.project_name}</h2>
                <span className="text-[11px] font-mono px-2 py-0.5 rounded-full bg-purple-500/20 text-purple-300 border border-purple-500/30">
                  {report.files_analyzed_count} files analyzed
                </span>
              </div>
              <div className="flex items-center gap-2 text-xs text-gray-400 mt-0.5">
                <span>Languages:</span>
                {Object.entries(report.languages_distribution).map(([lang, count]) => (
                  <span key={lang} className="font-mono text-gray-300 bg-gray-900 px-1.5 py-0.5 rounded border border-gray-800">
                    {lang} ({count})
                  </span>
                ))}
              </div>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg hover:bg-gray-800 text-gray-400 hover:text-white transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Top Summary Cards */}
        <div className="p-6 border-b border-gray-800/80 bg-[#0B0F19] grid grid-cols-2 md:grid-cols-5 gap-3">
          <div className="p-3 rounded-xl bg-gray-900/80 border border-gray-800">
            <span className="text-[10px] uppercase font-bold text-gray-400 block">Total LOC</span>
            <span className="text-xl font-mono font-bold text-white mt-1 block">{report.total_loc.toLocaleString()}</span>
          </div>

          <div className="p-3 rounded-xl bg-gray-900/80 border border-gray-800">
            <span className="text-[10px] uppercase font-bold text-blue-400 block">Highest Big-O</span>
            <span className="text-xl font-mono font-extrabold text-blue-300 mt-1 block">{report.highest_complexity}</span>
          </div>

          <div className="p-3 rounded-xl bg-gray-900/80 border border-gray-800">
            <span className="text-[10px] uppercase font-bold text-indigo-400 block">Average Big-O</span>
            <span className="text-xl font-mono font-bold text-indigo-300 mt-1 block">{report.average_complexity}</span>
          </div>

          <div className="p-3 rounded-xl bg-gray-900/80 border border-gray-800">
            <span className="text-[10px] uppercase font-bold text-emerald-400 block">Quality Score</span>
            <span className="text-xl font-mono font-bold text-emerald-400 mt-1 block">{report.overall_quality_score}/100</span>
          </div>

          <div className="p-3 rounded-xl bg-gray-900/80 border border-gray-800">
            <span className="text-[10px] uppercase font-bold text-rose-400 block">Security Risks</span>
            <div className="flex items-center gap-1.5 mt-1">
              <span className="text-xs font-mono font-bold text-rose-400">Crit: {report.security_summary.Critical || 0}</span>
              <span className="text-xs font-mono text-amber-400">High: {report.security_summary.High || 0}</span>
            </div>
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="px-6 pt-3 border-b border-gray-800 flex items-center gap-2 text-xs">
          <button
            onClick={() => setActiveTab('files')}
            className={`px-3 py-1.5 rounded-t-lg font-semibold flex items-center gap-1.5 transition-colors ${
              activeTab === 'files'
                ? 'bg-gray-800 text-white border-t-2 border-blue-500'
                : 'text-gray-400 hover:text-gray-200'
            }`}
          >
            <FileCode className="w-3.5 h-3.5" />
            <span>Files Breakdown ({report.files.length})</span>
          </button>

          <button
            onClick={() => setActiveTab('optimizations')}
            className={`px-3 py-1.5 rounded-t-lg font-semibold flex items-center gap-1.5 transition-colors ${
              activeTab === 'optimizations'
                ? 'bg-gray-800 text-white border-t-2 border-purple-500'
                : 'text-gray-400 hover:text-gray-200'
            }`}
          >
            <Zap className="w-3.5 h-3.5 text-yellow-400" />
            <span>Optimizations ({report.optimization_opportunities.length})</span>
          </button>

          <button
            onClick={() => setActiveTab('dependencies')}
            className={`px-3 py-1.5 rounded-t-lg font-semibold flex items-center gap-1.5 transition-colors ${
              activeTab === 'dependencies'
                ? 'bg-gray-800 text-white border-t-2 border-indigo-500'
                : 'text-gray-400 hover:text-gray-200'
            }`}
          >
            <GitBranch className="w-3.5 h-3.5 text-indigo-400" />
            <span>Dependency Graph ({report.dependency_graph.length})</span>
          </button>
        </div>

        {/* Tab Body */}
        <div className="p-6 overflow-y-auto flex-1 font-sans text-xs">
          {/* Files Table */}
          {activeTab === 'files' && (
            <div className="border border-gray-800 rounded-xl overflow-hidden">
              <table className="w-full text-left border-collapse font-sans text-xs">
                <thead>
                  <tr className="bg-gray-900/90 text-gray-400 text-[11px] uppercase tracking-wider font-semibold border-b border-gray-800">
                    <th className="p-3">File Path</th>
                    <th className="p-3">Language</th>
                    <th className="p-3">LOC</th>
                    <th className="p-3">Time Complexity</th>
                    <th className="p-3">Quality</th>
                    <th className="p-3 text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-800/60 font-mono text-xs">
                  {report.files.map((file, idx) => (
                    <tr key={idx} className="hover:bg-gray-900/40 transition-colors">
                      <td className="p-3 font-semibold text-gray-200 flex items-center gap-2">
                        <FileCode className="w-3.5 h-3.5 text-blue-400 shrink-0" />
                        <span className="truncate max-w-[260px]">{file.path}</span>
                      </td>
                      <td className="p-3 text-gray-400 uppercase text-[11px]">{file.language}</td>
                      <td className="p-3 text-gray-300">{file.loc}</td>
                      <td className="p-3">
                        <span className={`px-2 py-0.5 rounded font-bold text-[11px] ${
                          file.time_complexity.includes('²') || file.time_complexity.includes('³')
                            ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
                            : 'bg-blue-500/20 text-blue-300 border border-blue-500/30'
                        }`}>
                          {file.time_complexity}
                        </span>
                      </td>
                      <td className="p-3 text-emerald-400 font-bold">{file.maintainability_score}/10</td>
                      <td className="p-3 text-right font-sans">
                        <button
                          onClick={() => {
                            onOpenFileInEditor(file);
                            onClose();
                          }}
                          className="px-2.5 py-1 rounded bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold flex items-center gap-1 ml-auto shadow-sm"
                        >
                          <span>Open</span>
                          <ExternalLink className="w-3 h-3" />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* Optimization Opportunities */}
          {activeTab === 'optimizations' && (
            <div className="space-y-3">
              {report.optimization_opportunities.map((opt, idx) => (
                <div key={idx} className="p-3.5 rounded-xl bg-purple-950/20 border border-purple-500/30 flex items-start gap-2.5">
                  <Zap className="w-4 h-4 text-yellow-400 shrink-0 mt-0.5" />
                  <div className="text-gray-200 text-xs leading-relaxed">{opt}</div>
                </div>
              ))}
            </div>
          )}

          {/* Dependency Graph */}
          {activeTab === 'dependencies' && (
            <div className="space-y-2">
              <div className="border border-gray-800 rounded-xl p-3 bg-gray-950/60 font-mono text-xs divide-y divide-gray-800/60">
                {report.dependency_graph.map((edge, idx) => (
                  <div key={idx} className="py-2 flex items-center justify-between text-gray-300">
                    <span className="text-blue-300 font-bold">{edge.source}</span>
                    <span className="text-gray-600 font-sans text-[11px]">imports</span>
                    <span className="text-purple-300 font-bold">{edge.target}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
