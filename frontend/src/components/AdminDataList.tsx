import { DataList } from '@radix-ui/themes';

/**
 * Presents key-value pairs of the given object in a formatted list.
 * Useful for displaying/debugging admin data or configuration settings.
 */
export default function AdminDataList({ data }: {data: Record<string, unknown>}) {
  return (
    <DataList.Root>
      {Object.entries(data).map(([key, value]) => (
        <DataList.Item key={key}>
          <DataList.Label>{key}</DataList.Label>
          <DataList.Value className="whitespace-pre-wrap">
            {value?.toString()}
          </DataList.Value>
        </DataList.Item>
      ))}
    </DataList.Root>
  );
}
