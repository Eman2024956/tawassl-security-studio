import { NextResponse } from 'next/server';
import { serverStore } from '../../../lib/serverStore';

export async function GET(req: Request) {
  const { searchParams } = new URL(req.url);
  const targetId = searchParams.get('target_id');
  if (targetId) {
    return NextResponse.json(serverStore.assessments.filter((a) => a.target_id === targetId));
  }
  return NextResponse.json(serverStore.assessments);
}

export async function POST(req: Request) {
  try {
    const body = await req.json();
    const newAssessment = {
      id: `asm-${Date.now()}-${Math.random().toString(36).substring(2, 6)}`,
      project_id: body.project_id || serverStore.projects[0]?.id || 'proj-default',
      target_id: body.target_id || serverStore.targets[0]?.id || 'target-default',
      name: body.name || 'Assessment Scan',
      profile: body.profile || 'observe',
      status: 'queued' as const,
      ai_provider: body.ai_provider || 'mock',
      model_id: body.model_id || 'mock-sec-v1',
      max_steps: body.max_steps || 25,
      max_requests: body.max_requests || 100,
      max_tool_calls: body.max_tool_calls || 50,
      timeout_seconds: 900,
      max_output_bytes: 5242880,
      steps_taken: 0,
      requests_made: 0,
      tool_calls_made: 0,
      started_at: new Date().toISOString(),
    };
    serverStore.assessments.unshift(newAssessment);
    return NextResponse.json(newAssessment, { status: 201 });
  } catch (err: any) {
    return NextResponse.json({ error: err.message }, { status: 400 });
  }
}
