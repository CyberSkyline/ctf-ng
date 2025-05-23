import { createTheme } from "flowbite-react";

// This file defines theme adjustments for flowbite-react components.
// Try to use default styling as much as possible, but if overriding is necessary, do it here.
// Class lists defined here are merged with base component styling using twMerge.
// See https://flowbite-react.com/docs/customize/theme for more info on how this works.

export const baseTheme = createTheme({
    tabs: {
        tablist: {
            variant: {
                // give tabs equal widths instead of proportional to content, and stack them vertically in small viewports 
                fullWidth: "auto-cols-fr grid-flow-row md:grid-flow-col divide-x-0 divide-y md:divide-x md:divide-y-0",
            }
        }
    }
})