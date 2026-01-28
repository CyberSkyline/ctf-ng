import type { Sponsor } from "@/types"
import { Tooltip } from "@radix-ui/themes";
import { TbInfoCircle } from "react-icons/tb";
import { useFileUrl } from "@/hooks/fileuploads";

export default function SponsorBadge({sponsor}: {sponsor: Sponsor}){
  const { id, logo, name } = sponsor;

  const { data } = useFileUrl('sponsor-logos', logo);

  return (
    <Tooltip content={name} key={id}>
      {data
        ? <img src={data.download_url} alt="" className="h-9 w-9 object-cover" />
        : <TbInfoCircle key={id} className="h-9 w-9 object-cover" />}
    </Tooltip>
  );
}