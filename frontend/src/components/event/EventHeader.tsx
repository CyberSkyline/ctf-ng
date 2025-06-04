import {
  Container, Heading, Text, Button,
  Flex,
  Box,
  AspectRatio,
} from '@radix-ui/themes';

export default function EventHeader({
  name,
  description,
}: {
    name: string;
    description: string;
}) {
  return (
    <Container size="2" px="4" py="8" mb="4" className="bg-[var(--gray-2)]">
      <Flex direction="row" gap="6" align="start">
        <Box className="w-32">
          <AspectRatio ratio={10 / 16}>
            {/* Placeholder for event card image */}
            <Box className="h-full w-full bg-[var(--lime-8)] rounded-xl shadow-xl" />
          </AspectRatio>
        </Box>
        <Box flexGrow="1">
          <Heading size="9" color="lime">{name}</Heading>
          <Text as="p">{description}</Text>
          <Flex direction="row" gap="2">
            <Button variant="solid" color="lime" size="2" mt="4">Button 1</Button>
            <Button variant="soft" color="lime" size="2" mt="4">Button 2</Button>
          </Flex>
        </Box>
      </Flex>
    </Container>
  );
}
