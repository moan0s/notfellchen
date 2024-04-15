<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="3.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:atom="http://www.w3.org/2005/Atom">
  <xsl:output method="html" version="1.0" encoding="UTF-8" indent="yes"/>
  <xsl:template match="/">
    <html xmlns="http://www.w3.org/1999/xhtml" lang="en">
      <head>
        <title>
          RSS Feed |
          <xsl:value-of select="/atom:feed/atom:title"/>
        </title>
        <meta charset="utf-8"/>
        <meta http-equiv="content-type" content="text/html; charset=utf-8"/>
        <meta name="viewport" content="width=device-width, initial-scale=1"/>
        <link rel="stylesheet" href="/css/rss-styles.css"/>
      </head>
      <body>
        <main>
          <alert-box type="info">
            <strong>This is an RSS feed</strong>. Subscribe by copying
            the URL from the address bar into your newsreader. Visit <a
            href="https://aboutfeeds.com">About Feeds
          </a> to learn more and get started. It’s free.
          </alert-box>
          <div class="rss-summary">
            <h1 class="flex items-start">
              RSS Feed Preview
              <svg
                class="inline-icon"
                version="1.1"
                width="128px"
                height="128px"
                id="RSSicon"
                viewBox="0 0 256 256"
                sodipodi:docname="Feed-icon.svg"
                inkscape:version="1.2.2 (b0a8486541, 2022-12-01)"
                xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"
                xmlns:sodipodi="http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd"
                xmlns="http://www.w3.org/2000/svg"
                xmlns:svg="http://www.w3.org/2000/svg">
                <sodipodi:namedview
                  id="namedview32"
                  pagecolor="#ffffff"
                  bordercolor="#666666"
                  borderopacity="1.0"
                  inkscape:showpageshadow="2"
                  inkscape:pageopacity="0.0"
                  inkscape:pagecheckerboard="0"
                  inkscape:deskcolor="#d1d1d1"
                  showgrid="false"
                  inkscape:zoom="2.9085291"
                  inkscape:cx="161.07798"
                  inkscape:cy="133.22886"
                  inkscape:window-width="2048"
                  inkscape:window-height="1252"
                  inkscape:window-x="0"
                  inkscape:window-y="0"
                  inkscape:window-maximized="1"
                  inkscape:current-layer="RSSicon" />
                <defs
                  id="defs17">
                  <linearGradient
                    x1="0.085"
                    y1="0.085"
                    x2="0.915"
                    y2="0.915"
                    id="RSSg">
                    <stop
                      offset="0.0"
                      stop-color="#E3702D"
                      id="stop2" />
                    <stop
                      offset="0.1071"
                      stop-color="#EA7D31"
                      id="stop4" />
                    <stop
                      offset="0.3503"
                      stop-color="#F69537"
                      id="stop6" />
                    <stop
                      offset="0.5"
                      stop-color="#FB9E3A"
                      id="stop8" />
                    <stop
                      offset="0.7016"
                      stop-color="#EA7C31"
                      id="stop10" />
                    <stop
                      offset="0.8866"
                      stop-color="#DE642B"
                      id="stop12" />
                    <stop
                      offset="1.0"
                      stop-color="#D95B29"
                      id="stop14" />
                  </linearGradient>
                </defs>
                <rect
                  width="256"
                  height="256"
                  rx="55"
                  ry="55"
                  x="0"
                  y="0"
                  fill="#CC5D15"
                  id="rect19"
                  style="fill:#414141;fill-opacity:1" />
                <rect
                  width="246"
                  height="246"
                  rx="50"
                  ry="50"
                  x="5"
                  y="5"
                  fill="#F49C52"
                  id="rect21"
                  style="fill:#414141;fill-opacity:1" />
                <rect
                  width="236"
                  height="236"
                  rx="47"
                  ry="47"
                  x="10"
                  y="10"
                  fill="url(#RSSg)"
                  id="rect23"
                  style="fill:#414141;fill-opacity:1" />
                <circle
                  cx="68"
                  cy="189"
                  r="24"
                  fill="#FFF"
                  id="circle25" />
                <path
                  d="M160 213h-34a82 82 0 0 0 -82 -82v-34a116 116 0 0 1 116 116z"
                  fill="#FFF"
                  id="path27" />
                <path
                  d="M184 213A140 140 0 0 0 44 73 V 38a175 175 0 0 1 175 175z"
                  fill="#FFF"
                  id="path29" />
                <rect
                  width="256"
                  height="256"
                  rx="55"
                  ry="55"
                  x="299.70761"
                  y="188.99872"
                  fill="#CC5D15"
                  id="rect19-3"
                  style="fill:#414141;fill-opacity:1" />
                <rect
                  width="246"
                  height="246"
                  rx="50"
                  ry="50"
                  x="304.70761"
                  y="193.99872"
                  fill="#F49C52"
                  id="rect21-6"
                  style="fill:#414141;fill-opacity:1" />
                <rect
                  width="236"
                  height="236"
                  rx="47"
                  ry="47"
                  x="309.70761"
                  y="198.99872"
                  fill="url(#RSSg)"
                  id="rect23-7"
                  style="fill:#414141;fill-opacity:1" />
                <circle
                  cx="367.70761"
                  cy="377.99872"
                  r="24"
                  fill="#ffffff"
                  id="circle25-5" />
                <path
                  d="m 459.7076,401.99872 h -34 a 82,82 0 0 0 -82,-82 v -34 a 116,116 0 0 1 116,116 z"
                  fill="#ffffff"
                  id="path27-3" />
                <path
                  d="m 483.7076,401.99872 a 140,140 0 0 0 -140,-140 v -35 a 175,175 0 0 1 175,175 z"
                  fill="#ffffff"
                  id="path29-5" />
              </svg>
            </h1>
            <h2><xsl:value-of select="/atom:feed/atom:title"/></h2>
            <p>
              <xsl:value-of select="/atom:feed/atom:subtitle"/>
            </p>
            <a>
              <xsl:attribute name="href">
                <xsl:value-of select="/atom:feed/atom:link/@href"/>
              </xsl:attribute>
              Visit Website &#x2192;
            </a>

            <h2>Recent blog posts</h2>
            <xsl:for-each select="/atom:feed/atom:entry">
              <div class="post-summary">
                <h1>
                  <a>
                    <xsl:attribute name="href">
                      <xsl:value-of select="atom:link/@href"/>
                    </xsl:attribute>
                    <xsl:value-of select="atom:title"/>
                  </a>
                </h1>

                <div class="text-2 text-offset">
                  Published on
                  <xsl:value-of select="substring(atom:updated, 0, 17)" />
                </div>
              </div>
            </xsl:for-each>
          </div>
        </main>
      </body>
    </html>
  </xsl:template>
</xsl:stylesheet>
