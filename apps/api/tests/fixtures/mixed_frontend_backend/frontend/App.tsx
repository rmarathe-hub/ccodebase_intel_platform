import { bump, formatTitle } from "./lib/helpers";

interface Props {
  title: string;
}

export function Badge(props: Props) {
  const label = formatTitle(props.title);
  bump(1);
  return <span>{label}</span>;
}

export default function App() {
  return <Badge title="mixed" />;
}
