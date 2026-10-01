import { NextResponse } from 'next/server';
import { serverStore } from '../../../lib/serverStore';

export async function GET(req: Request) {
  const { searchParams } = new URL(req.url);
  const assessmentId = searchParams.get('assessment_id');
  if (assessmentId) {
    return NextResponse.json(serverStore.proposals.filter((p) => p.assessment_id === assessmentId));
  }
  return NextResponse.json(serverStore.proposals);
}

export async function POST(req: Request) {
  try {
    const body = await req.json();
    const { id, action } = body;
    const proposal = serverStore.proposals.find((p) => p.id === id);
    if (proposal) {
      proposal.status = action === 'reject' ? 'rejected' : 'approved';
    }
    return NextResponse.json({ status: 'ok', proposal });
  } catch (err: any) {
    return NextResponse.json({ error: err.message }, { status: 400 });
  }
}
