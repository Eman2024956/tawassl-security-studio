import { NextResponse } from 'next/server';
import { serverStore } from '../../../lib/serverStore';

export async function GET() {
  return NextResponse.json(serverStore.projects);
}

export async function POST(req: Request) {
  try {
    const body = await req.json();
    const newProject = {
      id: `proj-${Date.now()}-${Math.random().toString(36).substring(2, 6)}`,
      name: body.name || 'Untitled Project',
      description: body.description || '',
      created_at: new Date().toISOString(),
    };
    serverStore.projects.unshift(newProject);
    return NextResponse.json(newProject, { status: 201 });
  } catch (err: any) {
    return NextResponse.json({ error: err.message }, { status: 400 });
  }
}
