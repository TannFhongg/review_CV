const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public details?: Record<string, unknown>
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new ApiError(
      errorData.error?.message || `API error: ${response.status}`,
      response.status,
      errorData.error?.details
    );
  }
  return response.json();
}

export async function analyzeCV(
  jdFile: File | null,
  cvFile: File | null,
  jdText: string | null,
  cvText: string | null
): Promise<import('./types').AnalysisResult> {
  const formData = new FormData();

  if (jdFile) formData.append('jd_file', jdFile);
  if (cvFile) formData.append('cv_file', cvFile);
  if (jdText) formData.append('jd_text', jdText);
  if (cvText) formData.append('cv_text', cvText);

  const response = await fetch(`${API_BASE_URL}/analyze`, {
    method: 'POST',
    body: formData,
  });

  return handleResponse(response);
}

export async function healthCheck(): Promise<{ status: string; version: string }> {
  const response = await fetch(`${API_BASE_URL}/health`);
  return handleResponse(response);
}
