import { Crepe } from '@milkdown/crepe';
import { automd } from '@milkdown/plugin-automd';
import { listener as listenerPlugin } from '@milkdown/plugin-listener';
import { Milkdown, MilkdownProvider, useEditor } from '@milkdown/react';
import { nord } from '@milkdown/theme-nord';
import { useEffect, useRef, type RefObject } from 'react';

import '@milkdown/crepe/theme/common/style.css';
import '@milkdown/crepe/theme/nord.css';
import styles from './milkdown.module.css';

/*
 Crepe already comes with these plugins:
  - @milkdown/plugin-commonmark
  - @milkdown/plugin-listener
  - @milkdown/plugin-history
  - @milkdown/plugin-indent
  - @milkdown/plugin-trailing
  - @milkdown/plugin-clipboard
  - @milkdown/plugin-gfm
*/

/** Accessibility attributes applied to the editable element (WCAG 1.3.1, 4.1.2). */
type EditorA11yProps = {
  id?: string;
  'aria-label'?: string;
  'aria-labelledby'?: string;
  'aria-describedby'?: string;
  'aria-invalid'?: 'true' | 'false';
};

function CrepeEditor({
  initialValue = '',
  onChange,
  version = 0,
  containerRef,
  a11y,
}: {
  initialValue?: string,
  onChange: (value: string) => void,
  version: number,
  containerRef: RefObject<HTMLDivElement | null>,
  a11y: EditorA11yProps,
}) {
  const features = {
    'image-block' : false,
    latex : false,
  };

  const featureConfigs = {
    placeholder : {
      text : `Type here... `,
      mode : 'doc' as const,
    },
  };

  const { loading } = useEditor((root) => {
    const crepe = new Crepe({
      root,
      features,
      featureConfigs,
      defaultValue : initialValue,
    });

    crepe.editor.use(automd);
    crepe.editor.config(nord);
    crepe.editor.use(listenerPlugin);

    crepe.on((listener) => {
      listener.markdownUpdated((_, newMarkdown) => {
        onChange(newMarkdown);
      });
    });

    return crepe;
  }, [ version ]);

  // Crepe doesn't expose ProseMirror's attribute options, so name the editable element directly once the editor
  // exists (and again when it's recreated). ProseMirror applies its own attributes as decorations and leaves
  // these alone.
  const {
    id, 'aria-label' : ariaLabel, 'aria-labelledby' : labelledBy, 'aria-describedby' : describedBy, 'aria-invalid' : invalid,
  } = a11y;

  useEffect(() => {
    if (loading) return;

    const editable = containerRef.current?.querySelector<HTMLElement>('.ProseMirror[contenteditable]');
    if (!editable) return;

    const attributes: Record<string, string | undefined> = {
      id,
      role : 'textbox',
      'aria-multiline' : 'true',
      'aria-label' : ariaLabel,
      'aria-labelledby' : labelledBy,
      'aria-describedby' : describedBy,
      'aria-invalid' : invalid,
    };

    Object.entries(attributes).forEach(([ name, value ]) => {
      if (value === undefined) {
        editable.removeAttribute(name);
      } else {
        editable.setAttribute(name, value);
      }
    });
  }, [ loading, version, containerRef, id, ariaLabel, labelledBy, describedBy, invalid ]);

  return <Milkdown />;
}

export default function MilkdownEditorWrapper({
  initialValue = '',
  onChange,
  version = 0,
  ...a11y
}: {
  initialValue?: string,
  onChange: (value: string) => void,
  version?: number
} & EditorA11yProps) {
  const containerRef = useRef<HTMLDivElement>(null);

  return (
    <MilkdownProvider>
      <div className={styles.milkdownEditor} ref={containerRef}>
        <CrepeEditor initialValue={initialValue} onChange={onChange} version={version} containerRef={containerRef} a11y={a11y} />
      </div>
    </MilkdownProvider>
  );
}
