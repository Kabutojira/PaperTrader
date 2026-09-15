import Head from "../../quartz/components/Head";
import type {
  QuartzComponent,
  QuartzComponentConstructor,
} from "../../quartz/components/types";
import { joinSegments, pathToRoot } from "../../quartz/util/path";

const QuartzHead = Head();
const BrandHead: QuartzComponent = (props) => {
  const base = pathToRoot(props.fileData.slug!);
  return (
    <QuartzHead
      {...props}
      externalResources={{
        ...props.externalResources,
        additionalHead: [
          ...props.externalResources.additionalHead,
          <link
            rel="icon"
            type="image/svg+xml"
            href={joinSegments(base, "static/icon.svg")}
          />,
          <link
            rel="apple-touch-icon"
            href={joinSegments(base, "static/apple-touch-icon.png")}
          />,
          <meta name="theme-color" content="#123f32" />,
        ],
      }}
    />
  );
};

export default (() => BrandHead) satisfies QuartzComponentConstructor;
