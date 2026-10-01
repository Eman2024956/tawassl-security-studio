import { NextResponse } from 'next/server';

export async function GET() {
  return NextResponse.json({
    status: 'ok',
    mode: 'sovereign-local-first',
    version: '0.1.0',
    developer: 'Falah.G.Salieh (Baghdad, Iraq 2026)',
    timestamp: new Date().toISOString(),
  });
}
