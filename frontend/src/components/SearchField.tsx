import {
  Badge,
  Box,
  Button,
  Flex,
  IconButton,
  Popover,
  Separator,
  Skeleton,
  Spinner,
  Strong,
  Text,
  TextField,
} from '@radix-ui/themes';
import type { IDatasource } from 'ag-grid-community';
import {
  useState,
  useCallback,
  useEffect,
  type ReactNode,
  type Ref,
  Fragment,
  useMemo,
  useRef,
  type KeyboardEvent,
  useImperativeHandle,
  useId,
} from 'react';
import {
  TbChevronDown,
  TbPlus,
  TbSearch,
  TbX,
} from 'react-icons/tb';
import { twMerge } from 'tailwind-merge';
import { Popover as PopoverPrimitive } from 'radix-ui';
import useSWRInfinite from 'swr/infinite';

interface BaseProps<T> extends Omit<TextField.RootProps, 'value' | 'onChange'> {
  /**
   * Where to get search results. either a list of T[], or an IDatasource that can provide pages asynchronously.
   */
  datasource: IDatasource | T[];
  /**
   * Key of T used to get item values (what's used in value/onChange.)
   */
  valueKey: string;
  /**
   * Key of T used to get item labels (what's shown to the user.)
   */
  labelKey: string;
  /**
   * Function to produce sub-labels, which are shown beside or below main labels in the result list for additional context.
   */
  getSublabel?: (item: T) => string | null;
  /**
   * Function to produce icons, which are shown alongside results.
   * May be dynamic, or can return a static element for decorative/type icons.
   */
  getIcon?: (item: T) => ReactNode;
  /**
   * Whether sublabels should be displayed below or to the right of main labels.
   */
  sublabelSide?: 'right' | 'bottom';
  /**
   * SWR hook used to map initial values (i.e. IDs) to full model objects.
   * Needed when using a backend datasource, since not all data will be available to the search field for lookup by ID.
   */
  hook?(value: string | number | null | undefined): { data?: T; isLoading: boolean };
  /**
   * If provided, allows entering values that are not in the datasource.
   * Provided strings are passed to this function to create a new mock item from freeform input, which will be used in the resulting field value.
   * It's up to the consumer to actually create the item on the backend if needed.
   */
  createFreeformItem?(input: string | number): T;
  /**
   * Values to disable in the result listing.
   * Items in the current selection will already be disabled without being specified here.
   */
  disabledValues?: string[] | number[];
  /**
   * Extra ag-grid filter model entries always merged into every search request, in addition to the live text query.
   * Used to scope results (e.g. to a specific parent record) without adding dedicated UI for it.
   */
  staticFilter?: Record<string, unknown>;
  /**
   * Open the results list on focus even with an empty query, instead of waiting for the user to type.
   */
  openOnFocus?: boolean;
}

interface SingleSelectProps<
  T extends Record<string, unknown>
> extends BaseProps<T> {
  /**
   * Whether multiple items may be selected at once. When true, value is string[] instead of string.
   */
  multiple?: false;
  /**
   * The value field of the currently selected item.
   */
  value: string | number | null;
  /**
   * Called with the new value when the currently selected item changes, or null if empty.
   */
  onChange: (v: string | number | null) => void;
}

interface MultiSelectProps<
  T extends Record<string, unknown>
> extends BaseProps<T> {
  /**
   * Whether multiple items may be selected at once. When true, value is string[] instead of string.
   */
  multiple: true;
  /**
   * The value fields of the currently selected items.
   */
  value: string[] | number[];
  /**
   * Called with the new values when the currently selected item changes, or [] if empty.
   */
  onChange: (v: string[] | number[]) => void;
}

export type SearchFieldProps<
  T extends Record<string, unknown>
> = SingleSelectProps<T> | MultiSelectProps<T>;

// How many items to request at once when loading more results.
const BLOCK_SIZE = 20;

function useSearchResults<T extends Record<string, unknown>>(
  datasource: IDatasource | T[],
  query: string | null,
  labelKey: string,
  staticFilter?: Record<string, unknown>,
) {
  const id = useId();

  // generate page keys according to this field's unique id, the page index, and the current query.
  const getKey = useCallback((pageIndex: number, previousPageData: T[] | null) => {
    if (query === null) return null;
    if (previousPageData && !previousPageData.length) return null;
    return [ id, pageIndex, query, staticFilter ];
  }, [ id, query, staticFilter ]);

  const fetcher = useCallback(async ([ , pageIndex, searchQuery ]: [string, number, string]) => {
    const startIndex = pageIndex * BLOCK_SIZE;
    const endIndex = startIndex + BLOCK_SIZE;

    if (Array.isArray(datasource)) {
      // datasource is a known array, filter through it on the client side.
      // this filtering logic could be made smarter, but for now it's just a basic substring search.
      const lowercaseQuery = searchQuery.toLowerCase();
      const matches = datasource.filter((item) => (item[labelKey] as string)?.toLowerCase()?.includes(lowercaseQuery));

      // extract the "page" we want.
      return matches.slice(startIndex, endIndex);
    }
    // datasource is a server-side search. retrieve the requested page via its getRows fn.
    return new Promise<T[]>((resolve, reject) => {
      // wrap this in a short timeout to debounce and prevent hitting rate limits
      setTimeout(() => {
        datasource.getRows({
          startRow : startIndex,
          endRow : endIndex,
          successCallback : (rowsThisBlock: T[]) => {
            resolve(rowsThisBlock);
          },
          failCallback : () => {
            reject();
          },
          // use the default sort defined within the datasource
          sortModel : [ ],
          // filter by labelKey (the live text query), plus any caller-provided static scoping filter.
          filterModel : {
            [labelKey] : {
              filterType : 'text',
              type : 'contains',
              filter : searchQuery,
            },
            ...staticFilter,
          },
          context : {},
        });
      }, 50);
    });
  }, [ datasource, labelKey, staticFilter ]);

  const { data, ...rest } = useSWRInfinite<T[]>(
    getKey,
    fetcher,
    {
      keepPreviousData : true,
      revalidateAll : false,
      revalidateFirstPage : false,
      parallel : false,
      dedupingInterval : 30000,
    },
  );

  const flatData = useMemo(() => data?.flat() || [], [ data ]);
  const isReachingEnd = data && data[data.length - 1]?.length < BLOCK_SIZE;

  return {
    data : flatData,
    isReachingEnd,
    ...rest,
  };
}

function SelectionBadge<T extends Record<string, unknown>>({
  value,
  data,
  hook,
  getLabel,
  getIcon,
  onRemove,
}: {
  value: string | number,
  data?: T,
  hook?: SearchFieldProps<T>['hook'],
  getLabel: (item: T) => string,
  getIcon?: (item: T) => ReactNode,
  onRemove: () => void
}) {
  const { data : hookData, isLoading } = hook?.(data ? null : value) ?? { isLoading : false };
  const item = data ?? hookData;

  return (
    <Badge size="2" key={value} className="-order-1">
      {item && getIcon?.(item)}
      <Skeleton loading={isLoading}>
        <Text size="1">
          {(isLoading && 'Unknown') || (item && getLabel(item)) || value}
        </Text>
      </Skeleton>
      <IconButton
        type="button"
        variant="ghost"
        color="gray"
        size="1"
        className="!-my-1 !-ml-1 !-mx-1.5 !p-1 !align-middle"
        onClick={onRemove}
        aria-label="Remove"
      >
        <TbX />
      </IconButton>
    </Badge>
  );
}

function SearchField<T extends Record<string, unknown>>(
  props: SearchFieldProps<T> & { ref?: Ref<HTMLInputElement> },
) {
  const {
    ref,
    datasource,
    valueKey,
    labelKey,
    getSublabel,
    getIcon,
    sublabelSide = 'right',
    value,
    onChange,
    multiple,
    createFreeformItem,
    hook,
    disabledValues = [ ],
    staticFilter,
    openOnFocus = false,
    ...textFieldProps
  } = props;

  const inputRef = useRef<HTMLInputElement | null>(null);
  useImperativeHandle(ref, () => inputRef.current!);

  /*
   * The current search query.
   */
  const [ query, setQuery ] = useState<string>('');

  /**
    * Debounced version of query to prevent rapid key changes from
    * triggering excessive SWRInfinite revalidations.
    *
    * This is used internally to trigger the majority of state updates.
    */
  const [ debouncedQuery, setDebouncedQuery ] = useState<string>('');
  useEffect(() => {
    const timer = setTimeout(() => setDebouncedQuery(query), 150);
    return () => clearTimeout(timer);
  }, [ query ]);

  /** Whether results should be shown. Controlled automatically by query/fetch state, and manually via user-facing chevron button. */
  const [ resultsOpen, setResultsOpen ] = useState(false);

  /**
   * since the text field must maintain true focus so the user can continue typing,
   * this tracks their "fake focus" within the results list
   */
  const [ selectedIndex, setSelectedIndex ] = useState(-1);

  // hook to get search results for the given query.
  const {
    data, isValidating, size, setSize, isReachingEnd,
  } = useSearchResults(
    datasource,
    resultsOpen ? debouncedQuery : null, // only query for results if they are visible.
    labelKey,
    staticFilter,
  );

  // reset state when datasource changes
  useEffect(() => {
    setQuery('');
    setResultsOpen(false);
    setSelectedIndex(-1);
  }, [ datasource ]);

  /** cache to map values to full items for badge display */
  const itemCacheRef = useRef<Map<string | number, T>>(new Map());

  // refs used for results scrolling logic
  const selectedButtonRef = useRef<HTMLButtonElement | null>(null);
  const popoverContentRef = useRef<HTMLDivElement | null>(null);

  // helpers to retrieve values and labels from items
  const getValue = useCallback((item: T) => item[valueKey] as string | number, [ valueKey ]);
  const getLabel = useCallback((item: T) => String(item[labelKey]), [ labelKey ]);

  // selected values expressed as T[] for both single and multiple cases to simplify badge rendering logic
  const displayValues = useMemo(() => {
    if (multiple) {
      return value;
    }
    if (value) {
      return [ value ] as string[] | number[];
    }
    return [];
  }, [ value, multiple ]);

  // helper to check whether a value in the results should be disabled.
  const isValueDisabled = useCallback(
    (val: string | number) => (disabledValues as (string | number)[]).includes(val)
    || (displayValues as (string | number)[]).includes(val),
    [ disabledValues, displayValues ],
  );

  /**
   * Called when an item is selected from the results list.
   */
  const handleSelect = (item: T) => {
    const itemValue = getValue(item);

    if (isValueDisabled(itemValue)) {
      // prevent selection of disabled items.
      return;
    }

    // write selection to cache so its badge can be displayed.
    itemCacheRef.current.set(itemValue, item);

    if (multiple) {
      // add item to selection
      onChange([ ...(value || []), itemValue ] as string[] | number[]);
    } else {
      // replace current selection
      onChange(itemValue);
      setResultsOpen(false);
    }

    if (query !== '') {
      // reset the query - assume the user is either done or will start typing another query.
      setQuery('');
    }
  };

  /**
   * Remove an item from the selection by value.
   */
  const handleRemove = (rmValue: string | number) => {
    if (multiple) {
      onChange(value.filter((v) => v !== rmValue) as string[] | number[]);
    } else {
      onChange(null);
    }
    inputRef.current?.focus();
  };

  /**
   * Handler for keystrokes within the search field.
   */
  const handleKeystroke = (e: KeyboardEvent) => {
    if (e.key === 'ArrowDown') {
      // Go to next result
      e.preventDefault();
      setResultsOpen(true); // make sure results are open
      setSelectedIndex((prev) => Math.min(prev + 1, data.length - 1));
    } else if (e.key === 'ArrowUp') {
      // Go to previous result
      e.preventDefault();
      setSelectedIndex((prev) => Math.max(prev - 1, -1));
    } else if (e.key === 'PageDown') {
      // Jump down by 5 results
      e.preventDefault();
      setSelectedIndex((prev) => Math.min(prev + 5, data.length - 1));
    } else if (e.key === 'PageUp') {
      // Jump up by 5 results
      e.preventDefault();
      setSelectedIndex((prev) => Math.max(prev - 5, -1));
    } else if (e.key === 'Home') {
      // Go to first result
      e.preventDefault();
      setSelectedIndex(-1);
    } else if (e.key === 'End') {
      // Go to last *known* result. This will trigger loading more results if available.
      e.preventDefault();
      setSelectedIndex(data.length - 1);
    } else if (e.key === 'Enter') {
      e.preventDefault();
      if (selectedIndex >= 0 && selectedIndex < data.length) {
        // Select the current result.
        const selectedResult = data[selectedIndex];
        handleSelect(selectedResult);
      } else if (createFreeformItem && query.trim() !== '') {
        // If freeform creation is allowed, create an item from the query and select it.
        const newItem = createFreeformItem(query.trim());
        handleSelect(newItem);
      }
    } else if (e.key === 'Backspace' && query === '' && displayValues.length > 0) {
      // Backspace on empty query removes the last selected item
      e.preventDefault();
      handleRemove(displayValues[displayValues.length - 1]);
    } else if (e.key === 'Escape') {
      // Close the results list
      e.preventDefault();
      setResultsOpen(false);
    }
  };

  /**
   * Ensure the selected item is always scrolled into view when navigating with the keyboard and the field is focused.
   */
  useEffect(() => {
    if (resultsOpen && selectedButtonRef.current) {
      // if we're selecting an item, scroll it into view
      selectedButtonRef.current.scrollIntoView({ block : 'nearest' });
    }
    if (selectedIndex === -1 && popoverContentRef.current) {
      // if selection is cleared, scroll back to the top of the list
      popoverContentRef.current.scrollTop = 0;
    }
  }, [ selectedIndex, resultsOpen ]);

  /**
    * Maps values onto full items if datasource is a known array.
    * used for O(1) retrieval of labels and icons from a given value string.
    */
  const datasourceMap = useMemo(() => {
    if (Array.isArray(datasource)) {
      return new Map(datasource.map((item) => [ getValue(item), item ]));
    }
    return null;
  }, [ datasource, getValue ]);

  /**
    * Get a full item from a value string to be able to display its label and icon.
    */
  const lookupItem = useCallback((val: string | number): T | null => {
    // check cache first. if the user just selected this item, it will be here.
    if (itemCacheRef.current.has(val)) {
      return itemCacheRef.current.get(val)!;
    }

    // if we have the full datasource list, look the item up directly there.
    if (datasourceMap?.has(val)) {
      const item = datasourceMap.get(val)!;
      itemCacheRef.current.set(val, item);
      return item;
    }

    if (createFreeformItem) {
      const item = createFreeformItem(val);
      itemCacheRef.current.set(val, item);
      return item;
    }

    return null;
  }, [ datasourceMap, createFreeformItem ]);

  /**
   * The set of badges showing the current selection that will be displayed within or below the search field.
   */
  const badges = displayValues.map((v) => (
    <SelectionBadge
      // remount if hook is added or removed to ensure hook call is never conditional within a single component instance
      // this realisitically shouldn't happen, but guard against it anyway just in case.
      key={`${v}-${Boolean(hook)}`}
      value={v}
      data={lookupItem(v) ?? undefined}
      hook={hook}
      getLabel={getLabel}
      getIcon={getIcon}
      onRemove={() => handleRemove(v)}
    />
  ));

  // respond to debounced query changes - the results list is about to update when this runs
  useEffect(() => {
    if (size !== 1) {
      // reset swrInfinite size if needed as the debounced query changes.
      // swr is supposed to handle this by itself, but it doesn't appear to be.
      setSize(1);
    }

    if (debouncedQuery.trim() !== '') {
      // open the results if the user has started typing a query
      setResultsOpen(true);
    }

    // reset item selection since the list is about to change.
    setSelectedIndex(-1);

    // reset results list scroll.
    if (popoverContentRef.current) {
      popoverContentRef.current.scrollTop = 0;
    }
    // size/setSize omitted, would reset pagination on load-more
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [ debouncedQuery ]);

  // when results close, reset selection and discard old result pages
  useEffect(() => {
    if (!resultsOpen) {
      setSelectedIndex(-1);
      setSize(1);
    }
  }, [ resultsOpen, setSize ]);

  return (
    <Popover.Root open={resultsOpen && (data.length > 0 || !isValidating)}>
      <PopoverPrimitive.Anchor>
        <TextField.Root
          {...textFieldProps}
          value={query || ''}
          onChange={(e) => {
            setQuery(e.currentTarget.value);
          }}
          onFocus={(e) => {
            // try to load results on initial selection
            if (!isValidating) {
              setQuery(e.currentTarget.value);
            }
            if (openOnFocus) {
              setResultsOpen(true);
            }
          }}
          onBlur={() => { setResultsOpen(false); }}
          ref={inputRef}
          onKeyDown={handleKeystroke}
          autoComplete="off"
          className={twMerge(
            'gap-1 flex-wrap! items-center! p-1! h-auto! bg-clip-border! cursor-text! '
            + '[&>input]:min-w-16! [&>input]:w-0! [&>input]:grow! [&>input]:h-6! pr-7! relative',
            textFieldProps?.className,
          )}
        >
          <TextField.Slot className="ml-0! px-1!">
            {/* Loading spinner and search icon. */}
            <Box className="w-4">
              {(isValidating || query !== debouncedQuery) ? <Spinner /> : <TbSearch className="mx-auto" />}
            </Box>
          </TextField.Slot>
          {badges}
          <TextField.Slot side="right" className="mr-0! px-0! absolute right-1.5!">
            <IconButton
              type="button"
              variant="ghost"
              color="gray"
              onPointerDown={(e) => {
                e.preventDefault();
                inputRef.current?.focus();
                setResultsOpen((open) => !open);
              }}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  e.preventDefault();
                  inputRef.current?.focus();
                  setResultsOpen((open) => !open);
                }
              }}
              aria-label={resultsOpen ? 'Close results' : 'Open results'}
            >
              <TbChevronDown className={twMerge('transition-transform', resultsOpen && 'rotate-180')} />
            </IconButton>
          </TextField.Slot>
        </TextField.Root>
      </PopoverPrimitive.Anchor>
      <Popover.Content
        align="start"
        // text field needs to maintain focus when results open.
        onOpenAutoFocus={(e) => e.preventDefault()}
        className="min-h-0! p-0! max-h-68! overscroll-contain"
        ref={popoverContentRef}
        // load next page when scrolling approaches the end of the list.
        onScroll={(e) => {
          const target = e.currentTarget;
          const scrolledToBottom = target.scrollHeight - target.scrollTop <= target.clientHeight + 500;

          if (scrolledToBottom && resultsOpen && !isValidating && !isReachingEnd) {
            setSize((s) => s + 1);
          }
        }}
      >
        <Flex direction="column">
          {/* Show the create new button if createFreeformItem is defined */}
          {createFreeformItem && query.trim() !== '' && (
            <>
              <Button
                variant="ghost"
                color="gray"
                className={twMerge(
                  'm-0! justify-start! text-left!',
                  selectedIndex === -1 && 'bg-(--accent-a3)!', // fake focus highlight based on selectedIndex
                )}
                onPointerDown={(e) => {
                  e.preventDefault();
                  // create and select new item when the button is clicked.
                  const newItem = createFreeformItem(query.trim());
                  handleSelect(newItem);
                }}
                ref={selectedIndex === -1 ? selectedButtonRef : null}
              >
                <TbPlus className="shrink-0" />
                <Strong>
                  Create
                  {` "${query.trim()}"`}
                </Strong>
              </Button>
              <Separator size="4" className="last:hidden!" />
            </>
          )}
          {/* Show the results list. Keyed by both value and index, since values can be duplicated in some cases (i.e. cluster search) */}
          {data.map((result, index) => (
            <Fragment key={getValue(result) + String(index)}>
              <Button
                disabled={isValueDisabled(getValue(result))}
                variant="ghost"
                color="gray"
                className={twMerge(
                  'm-0! justify-between! items-start!',
                  index === selectedIndex && 'bg-(--accent-a3)!', // fake focus highlight based on selectedIndex
                  sublabelSide === 'bottom' && 'flex-col!',
                )}
                onPointerDown={(e) => {
                  e.preventDefault();
                  handleSelect(result);
                }}
                ref={index === selectedIndex ? selectedButtonRef : null}
              >
                <Flex direction="row" align="center" gap="1">
                  {getIcon && <span className="shrink-0">{getIcon(result)}</span>}
                  <Strong className="grow text-left">
                    {getLabel(result)}
                  </Strong>
                </Flex>
                {getSublabel && (
                  <Text align="right">
                    {getSublabel(result)}
                  </Text>
                )}
              </Button>
              <Separator size="4" className="last:hidden!" />
            </Fragment>
          ))}
          {data.length === 0 && !isValidating && !(createFreeformItem && query.trim() !== '') && (
            <Flex justify="center" align="center" p="2" className="h-10">
              <Text color="gray">
                {createFreeformItem ? 'No results, start typing to create one' : 'No results'}
              </Text>
            </Flex>
          )}
        </Flex>
      </Popover.Content>
    </Popover.Root>
  );
}

export default SearchField;
