export default function ChallengeHeader({
  children = undefined,
}: {
  children?: React.ReactNode;
}) {
  return (
    <div className="bg-dots-1 p-3">
      {children}
    </div>
  );
}
