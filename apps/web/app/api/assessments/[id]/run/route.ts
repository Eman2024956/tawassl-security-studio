import { NextResponse } from 'next/server';
import { serverStore } from '../../../../../lib/serverStore';

export async function POST(
  _req: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params;
  const assessment = serverStore.assessments.find((a) => a.id === id) || serverStore.assessments[0];
  if (assessment) {
    assessment.status = 'running';
    assessment.requests_made = Math.min(assessment.max_requests, assessment.requests_made + 4);
    assessment.steps_taken += 1;
    assessment.tool_calls_made += 2;
  }
  return NextResponse.json({
    status: 'ok',
    message: 'Assessment audit initialized',
    assessment,
  });
}
