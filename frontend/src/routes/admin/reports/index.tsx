import { Card, Inset } from '@radix-ui/themes';
import { useTheme } from 'next-themes';
import { useEffect } from 'react';

export default function AdminReports() {
  useEffect(() => {
    localStorage.setItem('grafana.navigation.docked', 'false');
  }, []);

  const { resolvedTheme } = useTheme();

  return (
    <>
      <title>Admin Reports</title>
      <Card className="h-full w-full !flex flex-col">
        <Inset side="all" className="grow shrink">
          <iframe
            title="Grafana"
            className="w-full h-full"
            src={`/admin/grafana/dashboards?theme=${resolvedTheme}`}
          />
        </Inset>
      </Card>
    </>
  );
}
