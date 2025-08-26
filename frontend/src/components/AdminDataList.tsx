import { DataList } from '@radix-ui/themes';
import RoleBadge from './RoleBadge';

/**
 * Presents key-value pairs of the given object in a formatted list.
 * Useful for displaying/debugging admin data or configuration settings.
 */
export default function AdminDataList({ data }: {data: Record<string, unknown>}) {
  return (
    <DataList.Root>
      {Object.entries(data).map(([ key, value ]) => (
        <DataList.Item key={key}>
          <DataList.Label>
            {key.charAt(0).toUpperCase() + key.slice(1).replace(/_/g, ' ')}
          </DataList.Label>
          <DataList.Value className="whitespace-pre-wrap">
            {(() => {
              if (value instanceof Date) {
                return value.toLocaleString();
              }
              if (key === 'role') {
                return <RoleBadge value={value!.toString()} />;
              }
              if (key === 'roles') {
                return (value as string[]).map((role) => (
                  <>
                    <RoleBadge key={role} value={role} />
                    &nbsp;
                  </>
                ));
              }
              return value?.toString();
            })()}
          </DataList.Value>
        </DataList.Item>
      ))}
    </DataList.Root>
  );
}
