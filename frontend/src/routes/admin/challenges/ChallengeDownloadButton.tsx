import { COLOR_POSITIVE } from '@/constants';
import { useAdminChallengeYaml } from '@/hooks/challenge';
import type { Challenge } from '@/types';
import { Button } from '@radix-ui/themes';
import { TbDownload } from 'react-icons/tb';

export default function ChallengeDownloadButton({ challenge }: { challenge: Challenge }) {
  const { data, error, isLoading } = useAdminChallengeYaml(challenge.id);

  /**
   * Download the YAML via Blob object URL.
   */
  const handleDownload = () => {
    // if the yaml hasn't loaded yet, do nothing - the button should be disabled at that point
    if (data?.yaml) {
      const element = document.createElement('a');
      const file = new Blob([ data.yaml ], { type : 'application/yaml' });
      element.href = URL.createObjectURL(file);
      element.download = `${challenge.name}.yaml`;
      document.body.appendChild(element);
      element.click();
      document.body.removeChild(element);
    }
  };

  return (
    <Button
      type="button"
      variant="soft"
      color={COLOR_POSITIVE}
      disabled={isLoading || !!error}
      onClick={handleDownload}
    >
      <TbDownload />
      Download
    </Button>
  );
}
