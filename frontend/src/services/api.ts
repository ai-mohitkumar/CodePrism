import axios from 'axios';
import { 
  UniversalResult, ErrorDiagnosis, ASTResponse, 
  ComplexityResponse, DebugStepResponse, CompileResponse,
  AIResponse, LanguageMeta, FileUploadResponse, ProjectReportResponse,
  ProjectMetadata, ProjectDetails, ProjectFileItem, ProjectVersion,
  ProjectTemplate, ShareProjectResponse
} from '../types';

const API_BASE_URL = (import.meta as any).env?.VITE_API_BASE_URL || 'http://127.0.0.1:8080';

const client = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 45000,
});

export const apiService = {
  async getLanguages(): Promise<{ languages: LanguageMeta[]; templates: Record<string, Record<string, string>> }> {
    const res = await client.get('/api/languages');
    return res.data;
  },

  async compileCode(language: string, code: string, compilerFlags: string[] = []): Promise<CompileResponse> {
    const res = await client.post<CompileResponse>('/api/compile', {
      language,
      code,
      compiler_flags: compilerFlags,
    });
    return res.data;
  },

  async executeCode(language: string, code: string, stdin = ''): Promise<UniversalResult> {
    const res = await client.post<UniversalResult>('/api/execute', {
      language,
      code,
      stdin,
    });
    return res.data;
  },

  async analyzeErrors(language: string, code: string): Promise<ErrorDiagnosis> {
    const res = await client.post<ErrorDiagnosis>('/api/analyze/errors', {
      language,
      code,
    });
    return res.data;
  },

  async analyzeAST(language: string, code: string): Promise<ASTResponse> {
    const res = await client.post<ASTResponse>('/api/analyze/ast', {
      language,
      code,
    });
    return res.data;
  },

  async analyzeComplexity(language: string, code: string): Promise<ComplexityResponse> {
    const res = await client.post<ComplexityResponse>('/api/analyze/complexity', {
      language,
      code,
    });
    return res.data;
  },

  async analyzeFull(language: string, code: string, stdin = ''): Promise<UniversalResult> {
    const res = await client.post<UniversalResult>('/api/analyze/full', {
      language,
      code,
      stdin,
    });
    return res.data;
  },

  async uploadFile(file: File): Promise<FileUploadResponse> {
    const formData = new FormData();
    formData.append('file', file);
    const res = await client.post<FileUploadResponse>('/api/analyze/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return res.data;
  },

  async uploadProjectZip(file: File): Promise<ProjectReportResponse> {
    const formData = new FormData();
    formData.append('file', file);
    const res = await client.post<ProjectReportResponse>('/api/analyze/project', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return res.data;
  },

  async analyzeGitHubRepo(repoUrl: string, branch = 'main'): Promise<ProjectReportResponse> {
    const res = await client.post<ProjectReportResponse>('/api/projects/github', {
      repo_url: repoUrl,
      branch,
    });
    return res.data;
  },

  // Cloud Projects Sync
  async listProjects(): Promise<ProjectMetadata[]> {
    const res = await client.get<ProjectMetadata[]>('/api/projects');
    return res.data;
  },

  async getProject(projectId: string): Promise<ProjectDetails> {
    const res = await client.get<ProjectDetails>(`/api/projects/${projectId}`);
    return res.data;
  },

  async saveProject(data: {
    project_id?: string;
    title: string;
    description?: string;
    language: string;
    files: ProjectFileItem[];
    is_autosave?: boolean;
  }): Promise<ProjectDetails> {
    const res = await client.post<ProjectDetails>('/api/projects/save', data);
    return res.data;
  },

  async getProjectVersions(projectId: string): Promise<ProjectVersion[]> {
    const res = await client.get<ProjectVersion[]>(`/api/projects/${projectId}/versions`);
    return res.data;
  },

  async createProjectSnapshot(projectId: string, versionTag: string, summary = ''): Promise<ProjectVersion> {
    const res = await client.post<ProjectVersion>(`/api/projects/${projectId}/versions/snapshot`, {
      version_tag: versionTag,
      summary
    });
    return res.data;
  },

  async restoreProjectVersion(projectId: string, versionId: string): Promise<ProjectDetails> {
    const res = await client.post<ProjectDetails>(`/api/projects/${projectId}/versions/${versionId}/restore`);
    return res.data;
  },

  async getProjectTemplates(): Promise<ProjectTemplate[]> {
    const res = await client.get<ProjectTemplate[]>('/api/projects/templates');
    return res.data;
  },

  async shareProject(projectId: string): Promise<ShareProjectResponse> {
    const res = await client.post<ShareProjectResponse>(`/api/projects/${projectId}/share`);
    return res.data;
  },

  async getSharedProject(shareToken: string): Promise<ProjectDetails> {
    const res = await client.get<ProjectDetails>(`/api/projects/shared/${shareToken}`);
    return res.data;
  },

  getExportZipUrl(projectId: string): string {
    return `${API_BASE_URL}/api/projects/${projectId}/export`;
  },

  async deleteProject(projectId: string): Promise<{ success: boolean; message: string }> {
    const res = await client.delete(`/api/projects/${projectId}`);
    return res.data;
  },

  async submitJob(language: string, code: string, stdin = ''): Promise<{ job_id: string; status: string }> {
    const res = await client.post('/api/jobs/submit', {
      language,
      code,
      stdin,
    });
    return res.data;
  },

  async pollJob(jobId: string) {
    const res = await client.get(`/api/jobs/${jobId}`);
    return res.data;
  },

  async debugStep(
    language: string, 
    code: string, 
    lineNumber: number, 
    breakpoints: number[] = [], 
    variables: Record<string, any> = {}
  ): Promise<DebugStepResponse> {
    const res = await client.post<DebugStepResponse>('/api/debug/step', {
      language,
      code,
      line_number: lineNumber,
      breakpoints,
      variables,
    });
    return res.data;
  },

  async aiAssistant(
    language: string, 
    code: string, 
    promptType: string, 
    userQuery = ''
  ): Promise<AIResponse> {
    const res = await client.post<AIResponse>('/api/ai/assistant', {
      language,
      code,
      prompt_type: promptType,
      user_query: userQuery,
    });
    return res.data;
  },
};
