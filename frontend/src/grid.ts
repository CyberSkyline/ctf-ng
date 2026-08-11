import {
  AllCommunityModule,
  ModuleRegistry,
  provideGlobalGridOptions,
  themeQuartz,
} from 'ag-grid-community';
import { formatDate } from '@/util';

// Register AG grid community modules.
ModuleRegistry.registerModules([ AllCommunityModule ]);

// Set global date handling behavior.
provideGlobalGridOptions({
  dataTypeDefinitions : {
    dateString : {
      baseDataType : 'dateString',
      extendsDataType : 'dateString',
      // flatten to date only when parsing dates for filters
      dateParser : (value) => {
        const parsed = value ? new Date(value) : undefined;
        return parsed && !Number.isNaN(parsed.getTime())
          ? new Date(parsed.getFullYear(), parsed.getMonth(), parsed.getDate())
          : undefined;
      },
      dateFormatter : (date) => date?.toISOString(),
      // use our date formatter for display
      valueFormatter : ({ value }) => formatDate(value),
    },
  },
});

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
