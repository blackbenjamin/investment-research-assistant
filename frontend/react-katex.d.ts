/**
 * Type declarations for react-katex
 * react-katex doesn't have TypeScript definitions, so we provide them here
 */

declare module "react-katex" {
  import * as React from "react";

  export interface BlockMathProps {
    math: string;
    errorColor?: string;
    renderError?: (error: Error) => React.ReactNode;
  }

  export interface InlineMathProps {
    math: string;
    errorColor?: string;
    renderError?: (error: Error) => React.ReactNode;
  }

  export class BlockMath extends React.Component<BlockMathProps> {}
  export class InlineMath extends React.Component<InlineMathProps> {}
}



