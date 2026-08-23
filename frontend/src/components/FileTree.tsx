import React, { useState } from 'react';
import { 
  Folder, 
  FileCode, 
  Plus, 
  Trash2, 
  X, 
  Check, 
  HardDrive, 
  Download, 
  Cpu 
} from 'lucide-react';

interface ProjectFile {
  name: string;
  language: string;
}

interface LocalSessionFile {
  name: string;
  code: string;
  savedAt: number;
}

interface FileTreeProps {
  files: ProjectFile[];
  activeFile: string;
  onSelectFile: (file: ProjectFile) => void;
  onAddNewFile?: (filename: string) => void;
  onDeleteFile?: (filename: string) => void;
  sessionFiles?: LocalSessionFile[];
  onSelectSessionFile?: (sessionFile: LocalSessionFile) => void;
  onDeleteSessionFile?: (filename: string) => void;
  onDownloadFile?: (filename: string, code: string) => void;
}

export const FileTree: React.FC<FileTreeProps> = ({ 
  files, 
  activeFile, 
  onSelectFile,
  onAddNewFile,
  onDeleteFile,
  sessionFiles = [],
  onSelectSessionFile,
  onDeleteSessionFile,
  onDownloadFile
}) => {
  const [isCreating, setIsCreating] = useState(false);
  const [newFileName, setNewFileName] = useState('');

  const handleCreateSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (newFileName.trim() && onAddNewFile) {
      onAddNewFile(newFileName.trim());
      setNewFileName('');
      setIsCreating(false);
    }
  };

  return (
    <div className="w-56 bg-[#0B0F19] border-r border-gray-800 flex flex-col h-full select-none shrink-0">
      {/* File Tree Header */}
      <div className="h-9 px-3 border-b border-gray-800/80 flex items-center justify-between text-xs text-gray-400 font-semibold tracking-wider uppercase">
        <span className="flex items-center gap-1.5">
          <Folder className="w-3.5 h-3.5 text-blue-400" />
          <span>Explorer</span>
        </span>
        {onAddNewFile && (
          <button
            onClick={() => setIsCreating(true)}
            className="p-1 rounded hover:bg-gray-800 text-gray-400 hover:text-white transition-colors"
            title="New File"
          >
            <Plus className="w-3.5 h-3.5" />
          </button>
        )}
      </div>

      {/* Files List */}
      <div className="p-2 space-y-3 overflow-y-auto flex-1 font-mono text-xs">
        {/* Section 1: Workspace Files */}
        <div className="space-y-1">
          <div className="text-[10px] text-gray-500 font-sans uppercase px-2 py-1 font-bold flex items-center justify-between">
            <span>Workspace Files ({files.length})</span>
          </div>

          {/* New File Inline Creator */}
          {isCreating && (
            <form onSubmit={handleCreateSubmit} className="px-1 py-1 flex items-center gap-1">
              <input
                type="text"
                autoFocus
                placeholder="filename.ext"
                value={newFileName}
                onChange={(e) => setNewFileName(e.target.value)}
                className="flex-1 px-2 py-1 rounded bg-gray-900 border border-blue-500 text-white font-mono text-xs focus:outline-none"
              />
              <button type="submit" className="p-1 rounded bg-blue-600 text-white hover:bg-blue-500">
                <Check className="w-3 h-3" />
              </button>
              <button 
                type="button" 
                onClick={() => { setIsCreating(false); setNewFileName(''); }}
                className="p-1 rounded bg-gray-800 text-gray-400 hover:text-white"
              >
                <X className="w-3 h-3" />
              </button>
            </form>
          )}

          {files.map((file) => {
            const isActive = file.name === activeFile;
            return (
              <div
                key={file.name}
                className={`group flex items-center justify-between px-2.5 py-1.5 rounded-lg text-left transition-colors cursor-pointer ${
                  isActive
                    ? 'bg-blue-600/20 text-blue-300 font-medium border border-blue-500/30'
                    : 'text-gray-400 hover:text-gray-200 hover:bg-gray-800/40'
                }`}
              >
                <button
                  onClick={() => onSelectFile(file)}
                  className="flex-1 flex items-center gap-2 truncate text-left"
                >
                  <FileCode className={`w-4 h-4 shrink-0 ${isActive ? 'text-blue-400' : 'text-gray-500'}`} />
                  <span className="truncate">{file.name}</span>
                </button>

                {onDeleteFile && files.length > 1 && (
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      if (confirm(`Delete file "${file.name}"?`)) {
                        onDeleteFile(file.name);
                      }
                    }}
                    className="opacity-0 group-hover:opacity-100 p-1 hover:text-rose-400 rounded transition-opacity"
                    title="Delete File"
                  >
                    <Trash2 className="w-3 h-3" />
                  </button>
                )}
              </div>
            );
          })}
        </div>

        {/* Section 2: Local Session Files (RAM / LocalStorage) */}
        {sessionFiles && sessionFiles.length > 0 && (
          <div className="space-y-1 pt-2 border-t border-gray-800/60">
            <div className="text-[10px] text-emerald-400 font-sans uppercase px-2 py-1 font-bold flex items-center justify-between">
              <span className="flex items-center gap-1">
                <Cpu className="w-3 h-3 text-emerald-400" />
                <span>Session Saves ({sessionFiles.length})</span>
              </span>
            </div>

            {sessionFiles.map((sf) => (
              <div
                key={sf.name}
                className="group flex items-center justify-between px-2 py-1.5 rounded-lg text-left bg-emerald-950/20 border border-emerald-500/20 hover:border-emerald-500/40 transition-colors"
              >
                <button
                  onClick={() => onSelectSessionFile && onSelectSessionFile(sf)}
                  className="flex-1 flex items-center gap-1.5 truncate text-left"
                  title={`Click to load ${sf.name}`}
                >
                  <FileCode className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                  <div className="truncate">
                    <span className="text-gray-200 text-[11px] block truncate font-bold">{sf.name}</span>
                    <span className="text-[9px] text-gray-400 font-mono block">
                      {new Date(sf.savedAt).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </span>
                  </div>
                </button>

                <div className="flex items-center gap-1 opacity-80 group-hover:opacity-100">
                  {onDownloadFile && (
                    <button
                      onClick={() => onDownloadFile(sf.name, sf.code)}
                      className="p-1 text-gray-400 hover:text-blue-400 rounded"
                      title="Download to Device"
                    >
                      <Download className="w-3 h-3" />
                    </button>
                  )}
                  {onDeleteSessionFile && (
                    <button
                      onClick={() => onDeleteSessionFile(sf.name)}
                      className="p-1 text-gray-400 hover:text-rose-400 rounded"
                      title="Remove from Session"
                    >
                      <Trash2 className="w-3 h-3" />
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
