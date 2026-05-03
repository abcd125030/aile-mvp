const envDemoMode = import.meta.env.VITE_DEMO_MODE

export const appConfig = {
  demoMode: envDemoMode === 'true',
}
