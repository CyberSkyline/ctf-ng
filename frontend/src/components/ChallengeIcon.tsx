import type { IconType } from 'react-icons';
import * as tb from 'react-icons/tb';

export default function ChallengeIcon({ icon }: { icon: string | undefined }) {
  const Icon = icon ? (tb as Record<string, IconType>)[icon] : null;
  return Icon && <Icon />;
}
