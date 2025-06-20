import { nord } from '@milkdown/theme-nord';
import { Crepe } from '@milkdown/crepe';
import { listener as listenerPlugin } from '@milkdown/plugin-listener';
import { Milkdown, MilkdownProvider, useEditor } from '@milkdown/react';
import { automd } from '@milkdown/plugin-automd';

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

function CrepeEditor({ initialValue, onChange } : { initialValue? : string, onChange : (value : string) => void }) {
  const features = {
    'image-block' : false,
    latex : false,
  };

  const featureConfigs = {
    placeholder : {
      text : 'Type here...',
    },
  };

  const { } = useEditor((root) => {
    const crepe = new Crepe({ root, features, featureConfigs, defaultValue : initialValue || ''});

    crepe.editor.use(automd);
    crepe.editor.config(nord);
    crepe.editor.use(listenerPlugin);

    crepe.on((listener) => {
      listener.markdownUpdated((_, newMarkdown) => {
        onChange(newMarkdown);
      });
    });

    return crepe;
  }, [ ]);

  return <Milkdown />;
}

export default function MilkdownEditorWrapper({ initialValue, onChange } : { initialValue? : string, onChange : (value : string) => void }) {
  return (
    <MilkdownProvider>
      <div className={styles.milkdownEditor}>
        <CrepeEditor initialValue={initialValue} onChange={onChange} />
      </div>
    </MilkdownProvider>
  );
}
