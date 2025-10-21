import { yaml } from '@codemirror/lang-yaml';
import { Button } from '@radix-ui/themes';
import CodeMirror, { type ReactCodeMirrorRef } from '@uiw/react-codemirror';
import { useTheme } from 'next-themes';
import type { Ref } from 'react';
import Dropzone from 'react-dropzone';
import { TbUpload } from 'react-icons/tb';
import { twMerge } from 'tailwind-merge';

export default function YamlEditor({
  value, onChange, ref, ...rest
}: {value: string, onChange: (v: string) => void, ref?: Ref<ReactCodeMirrorRef>}) {
  const theme = useTheme();

  return (
    <Dropzone
      onDrop={(files) => {
        if (files.length > 0) {
          const file = files[0];
          file.text().then((content) => {
            onChange(content);
          });
        }
      }}
      accept={{
        'application/yaml' : [ '.yaml', '.yml' ],
      }}
      multiple={false}
      noClick
    >
      {({
        getRootProps, getInputProps, isDragActive, open,
      }) => (
        <>
          {/* {JSON.stringify(watch())} */}
          <div
            {...getRootProps()}
            tabIndex={-1}
            className={twMerge(
              'relative rounded overflow-clip ',
              isDragActive && '!ring-2 !ring-(--accent-8) relative after:absolute after:inset-0 after:bg-(--accent-a4)',
            )}
          >

            <CodeMirror
              value={value}
              height="546px"
              extensions={[ yaml() ]}
              theme={theme.resolvedTheme === 'dark' ? 'dark' : 'light'}
              basicSetup={{
                dropCursor : false,
              }}
              onChange={onChange}
              placeholder="Drop, paste, or type your YAML here..."
              ref={ref}
              {...rest}
            />
            <Button
              color="gray"
              variant="ghost"
              className="!absolute !bottom-2 !right-2 !m-0"
              onClick={open}
              type="button"
            >
              <TbUpload />
              Upload File
            </Button>
          </div>
          <input
            {...getInputProps()}
            name="file"
            aria-hidden
          />
        </>
      )}
    </Dropzone>

  );
}
