import { ticketAttachmentUpload } from '@/hooks/fileuploads';
import { Crepe } from '@milkdown/crepe';
import { automd } from '@milkdown/plugin-automd';
import { listener as listenerPlugin } from '@milkdown/plugin-listener';
import { Milkdown, MilkdownProvider, useEditor } from '@milkdown/react';
import { nord } from '@milkdown/theme-nord';

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

const toMb = (bytes : number) => bytes / 1024 / 1024;

const MAX_OUTPUT_IMAGE_MB = 5;

const getCompressionAmount = (size : number) => {
  if (size > toMb(3)) {
    return 0.7;
  } if (size > toMb(1)) {
    return 0.8;
  } if (size > toMb(0.5)) {
    return 0.9;
  }
  return 1;
};

function dataURLToBlob(dataURL : string) {
  // Split the metadata (before the comma) from the Base64 content
  const [ header, base64 ] = dataURL.split(',');

  // Extract the MIME type from the header: data:image/webp;base64
  const mimeMatch = header.match(/:(.*?);/);
  const mime = mimeMatch ? mimeMatch[1] : 'application/octet-stream';

  // Decode Base64 into raw binary
  const binary = atob(base64);
  const { length } = binary;

  // Create an array buffer for the blob
  const u8arr = new Uint8Array(length);
  for (let i = 0; i < length; i += 1) {
    u8arr[i] = binary.charCodeAt(i);
  }

  return new Blob([ u8arr ], { type : mime });
}

const onUpload = (fileUploadPath : string) => async (file : File) => new Promise<string>((resolve, reject) => {
  const img = new Image();

  img.onload = () => {
    URL.revokeObjectURL(img.src);
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    canvas.width = img.width;
    canvas.height = img.height;

    if (!ctx) {
      reject(new Error('Failed to compress image'));
      return;
    }

    ctx.drawImage(img, 0, 0, canvas.width, canvas.height);

    const compressedBase64 = canvas.toDataURL('image/webp', getCompressionAmount(file.size));

    console.log('compressed size', compressedBase64.length / 1024 / 1024);

    if (compressedBase64.length > MAX_OUTPUT_IMAGE_MB * 1024 * 1024) {
      reject(new Error(`Compressed file size exceeds ${MAX_OUTPUT_IMAGE_MB}MB`));
      return;
    }

    const blob = dataURLToBlob(compressedBase64);
    const compressedFile = new File([ blob ], file.name.replace(/\.[^/.]+$/, '.webp'), { type : 'image/webp' });

    console.log(compressedFile);

    ticketAttachmentUpload(fileUploadPath, compressedFile)
      .then((result) => resolve(result.download_url || ''))
      .catch(reject);
  };

  img.src = URL.createObjectURL(file);
});

// const uploader = (fileUploadPath : string) => async (files, schema) => {
//   if (files.length === 0) return [ ];

//   const file = files[0];

//   if (!file.type.includes('image')) return [ ];

//   const src = await onUpload(fileUploadPath)(file);

//   if (!src) return [ ];

//   return schema.nodes.image.createAndFill({
//     src,
//   }) as Node;
// };

function CrepeEditor({
  initialValue = '',
  fileUploadPath,
  onChange,
  version = 0,
}: {
  initialValue?: string,
  fileUploadPath : string,
  onChange: (value: string) => void,
  version: number,
}) {
  const features = {
    'image-block' : !!fileUploadPath,
    latex : false,
  };

  const featureConfigs = {
    'image-block' : {
      inlineOnUpload : onUpload(fileUploadPath),
      blockOnUpload : onUpload(fileUploadPath),
    },
    placeholder : {
      text : `Type here... ${fileUploadPath ? 'Enter /image to upload an attachment' : ''}`,
      mode : 'doc' as const,
    },
  };

  useEditor((root) => {
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

  return <Milkdown />;
}

export default function MilkdownEditorWrapper({
  initialValue = '',
  fileUploadPath = '',
  onChange,
  version = 0,
}: {
  initialValue?: string,
  fileUploadPath? : string,
  onChange: (value: string) => void,
  version?: number
}) {
  return (
    <MilkdownProvider>
      <div className={styles.milkdownEditor}>
        <CrepeEditor initialValue={initialValue} fileUploadPath={fileUploadPath} onChange={onChange} version={version} />
      </div>
    </MilkdownProvider>
  );
}
