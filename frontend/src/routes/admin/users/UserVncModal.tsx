import { APIPREFIX, COLOR_HINT } from '@/constants';
import { Button } from '@radix-ui/themes';
import Modal from 'components/Modal';
import { TbTerminal } from 'react-icons/tb';

export default function UserVncModal({ userId }: {userId: number}) {
  return (
    <Modal
      title="Workspace VNC"
      trigger={(
        <Button variant="ghost" color={COLOR_HINT}>
          <TbTerminal />
          VNC
        </Button>
      )}
      className="!max-w-[75vw]"
    >
      <iframe
        title="VNC session"
        className="w-full h-[75vh]"
        src={`${PUBLIC_BASE}/novnc/vnc.html?autoconnect=true&path=${APIPREFIX}/admin/user/${userId}/vnc/access/websockify&reconnect=true&resize=scale`}
      />
    </Modal>
  );
}
