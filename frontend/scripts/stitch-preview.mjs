import { stitch } from '@google/stitch-sdk';

const prompt = process.env.STITCH_PROMPT || `Atelier Operators landing page for a premium French AI operator guide. Make it feel editorial, high-end, asymmetric, and less template-like. Focus on a strong hero, a more distinctive proof section, varied card sizes, and a refined premium dark palette.`;
const title = process.env.STITCH_PROJECT_TITLE || 'Atelier Operators';

async function main() {
  const apiKeyPresent = Boolean(process.env.STITCH_API_KEY);
  if (!apiKeyPresent) {
    console.error('Missing STITCH_API_KEY');
    process.exit(1);
  }

  const tools = await stitch.listTools();
  console.log('Available tools:', tools.tools.map((t) => t.name).join(', '));

  let project;
  try {
    const created = await stitch.callTool('create_project', { title });
    console.log('create_project result:', JSON.stringify(created, null, 2));
    const projectId = created?.projectId || created?.project?.projectId || created?.id || created?.project?.id;
    if (!projectId) throw new Error('Could not infer project id from create_project result');
    project = stitch.project(projectId);
  } catch (err) {
    console.error('create_project failed:', err?.message || err);
    console.error('Falling back to first existing project if any...');
    const projects = await stitch.projects();
    if (!projects.length) throw err;
    project = projects[0];
    console.log('Using project:', project.projectId || project.id);
  }

  const screen = await project.generate(prompt);
  console.log('Generated screen:', screen.id || screen.screenId);
  const html = await screen.getHtml();
  const image = await screen.getImage();
  console.log(JSON.stringify({ html, image }, null, 2));
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
