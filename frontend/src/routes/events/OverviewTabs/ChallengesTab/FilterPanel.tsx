import { OTHER_TAXONOMY } from '@/constants';
import type { Challenge } from '@/types';
import { getTaxonomy, prettyPrintTag } from '@/util';
import {
  Button,
  Card,
  DataList,
  Flex,
  Inset,
  Text,
} from '@radix-ui/themes';
import { groupBy } from 'lodash';
import { useMemo } from 'react';

export default function FilterPanel({
  challenges,
  selectedTags,
  onTagToggle,
  id,
}: {
  challenges: Challenge[];
  selectedTags: Set<string>;
  onTagToggle: (tag: string) => void;
  id: string;
}) {
  // group all tags by taxonomy, sort tags within each taxonomy by frequency for display
  const taxonomizedTags = useMemo(() => {
    // compute tag frequencies across all challenges
    const tagFrequencies = new Map<string, number>();
    challenges.forEach((challenge) => {
      challenge.tags.forEach((tag) => {
        tagFrequencies.set(tag, (tagFrequencies.get(tag) ?? 0) + 1);
      });
    });

    // group tags by taxonomy (the part before the last colon, or OTHER_TAXONOMY if no colon)
    const grouped = groupBy(Array.from(tagFrequencies.keys()), getTaxonomy);

    // sort tags within each taxonomy by frequency
    Object.keys(grouped).forEach((taxonomy) => {
      grouped[taxonomy].sort((a, b) => (tagFrequencies.get(b) || 0) - (tagFrequencies.get(a) || 0));
    });

    return grouped;
  }, [ challenges ]);

  return (
    <Card mt="1" id={id} role="region" aria-label="Filters">
      <Inset side="all" className="max-h-64 overflow-y-auto! p-3">
        <DataList.Root>
          {Object.entries(taxonomizedTags)
            .sort(([ a ], [ b ]) => {
              // sort alphabetically, but with OTHER_TAXONOMY last
              if (a === OTHER_TAXONOMY) return 1;
              if (b === OTHER_TAXONOMY) return -1;
              return a.localeCompare(b);
            })
            .map(([ taxonomy, tags ]) => (
              <DataList.Item key={taxonomy}>
                <DataList.Label className="translate-y-0.5" id={`${id}-${taxonomy}`}>{taxonomy}</DataList.Label>
                <DataList.Value>
                  <Flex
                    direction="row"
                    gap="1"
                    wrap="wrap"
                    role="group"
                    aria-labelledby={`${id}-${taxonomy}`}
                  >
                    {tags.map((tag) => {
                      const selected = selectedTags.has(tag);
                      return (
                        <Button
                          key={tag}
                          radius="full"
                          size="1"
                          variant={selected ? 'solid' : 'outline'}
                          color={selected ? undefined : 'gray'}
                          aria-pressed={selected}
                          onClick={() => onTagToggle(tag)}
                        >
                          {prettyPrintTag(tag)}
                        </Button>
                      );
                    })}
                  </Flex>
                </DataList.Value>
              </DataList.Item>
            ))}
        </DataList.Root>
        {Object.entries(taxonomizedTags).length === 0 && (
          <Text color="gray">No filters available.</Text>
        )}
      </Inset>
    </Card>
  );
}
