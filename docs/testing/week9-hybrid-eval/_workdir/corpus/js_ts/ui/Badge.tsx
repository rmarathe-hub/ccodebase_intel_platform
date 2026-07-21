import React from "react";
import { util } from "../pkg/helpers";

interface Props {
  label: string;
}

export function Badge(props: Props) {
  util(1);
  return <span>{props.label}</span>;
}

export default function HomePage() {
  return <Badge label="ok" />;
}
