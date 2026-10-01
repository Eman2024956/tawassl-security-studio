import { NextResponse } from 'next/server';
import { serverStore } from '../../../lib/serverStore';

export async function GET(req: Request) {
  const { searchParams } = new URL(req.url);
  const projectId = searchParams.get('project_id');
  if (projectId) {
    return NextResponse.json(serverStore.targets.filter((t) => t.project_id === projectId));
  }
  return NextResponse.json(serverStore.targets);
}

export async function POST(req: Request) {
  try {
    const body = await req.json();
    const newTarget = {
      id: `target-${Date.now()}-${Math.random().toString(36).substring(2, 6)}`,
      project_id: body.project_id || serverStore.projects[0]?.id || 'proj-default',
      name: body.name || 'New Target',
      target_type: body.target_type || 'website',
      environment_mode: body.environment_mode || 'live',
      authorized_domains: body.authorized_domains || [],
      base_urls: body.base_urls || [],
      allowed_ports: body.allowed_ports || [80, 443],
      allow_subdomains: !!body.allow_subdomains,
      exclusions: body.exclusions || [],
      created_at: new Date().toISOString(),
    };
    serverStore.targets.unshift(newTarget);
    return NextResponse.json(newTarget, { status: 201 });
  } catch (err: any) {
    return NextResponse.json({ error: err.message }, { status: 400 });
  }
}
