// Simple test to verify Next.js setup is working
describe('Next.js Configuration', () => {
  test('package.json exists and has required dependencies', () => {
    const packageJson = require('../package.json');
    
    expect(packageJson.name).toBe('triune-swarm-engine');
    expect(packageJson.dependencies.next).toBeDefined();
    expect(packageJson.dependencies.react).toBeDefined();
    expect(packageJson.dependencies['react-dom']).toBeDefined();
    expect(packageJson.dependencies.recharts).toBeDefined();
    expect(packageJson.dependencies['lucide-react']).toBeDefined();
  });

  test('has required scripts', () => {
    const packageJson = require('../package.json');
    
    expect(packageJson.scripts.dev).toBe('next dev');
    expect(packageJson.scripts.build).toBe('next build');
    expect(packageJson.scripts.start).toBe('next start');
  });
});