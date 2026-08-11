import { useEffect, useState } from 'react';
import { IconButton, TextField } from '@radix-ui/themes';
import { TbSearch, TbX } from 'react-icons/tb';

type SearchFieldProps = {
  onSearch: (query: string) => void;
  placeholder?: string;
  debounceMs?: number;
  className?: string;
};

export default function SearchField({
  onSearch,
  placeholder = 'Search...',
  debounceMs = 300,
  className,
}: SearchFieldProps) {
  const [ value, setValue ] = useState('');

  useEffect(() => {
    const timeout = window.setTimeout(() => {
      onSearch(value.trim());
    }, debounceMs);

    return () => window.clearTimeout(timeout);
  }, [ value, debounceMs, onSearch ]);

  return (
    <TextField.Root
      className={className}
      value={value}
      onChange={(e) => setValue(e.target.value)}
      placeholder={placeholder}
    >
      <TextField.Slot>
        <TbSearch />
      </TextField.Slot>

      {value && (
        <TextField.Slot side="right">
          <IconButton
            type="button"
            variant="ghost"
            color="gray"
            size="1"
            radius="full"
            onClick={() => {
              setValue('');
              onSearch('');
            }}
            aria-label="Clear search"
          >
            <TbX />
          </IconButton>
        </TextField.Slot>
      )}
    </TextField.Root>
  );
}
