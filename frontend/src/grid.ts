import { AllCommunityModule, ModuleRegistry, themeQuartz } from 'ag-grid-community';

// Register AG grid community modules.
ModuleRegistry.registerModules([ AllCommunityModule ]);

// Theme to adapt radix colors to ag-grid.
// eslint-disable-next-line import/prefer-default-export
export const radixTheme = themeQuartz
  .withParams(
    {
      backgroundColor : 'var(--color-background)',
      chromeBackgroundColor : 'var(--gray-2)',
      foregroundColor : 'var(--gray-12)',
      accentColor : 'var(--accent-9)',
      fontFamily : 'var(--default-font-family)',
      browserColorScheme : 'light dark',
    },
  );
