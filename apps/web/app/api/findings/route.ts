import { NextResponse } from 'next/server';
import { serverStore } from '../../../lib/serverStore';

export async function GET(req: Request) {
  const { searchParams } = new URL(req.url);
  const assessmentId = searchParams.get('assessment_id');
  if (assessmentId) {
    return NextResponse.json(serverStore.findings.filter((f) => f.assessment_id === assessmentId));
  }
  return NextResponse.json(serverStore.findings);
}
