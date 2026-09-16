<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:import href="/root/.ptx/2.37.1/core/xsl/pretext-html.xsl"/>

  <xsl:template match="p[@role='separator']">
    <hr class="writing-rule" role="separator"/>
  </xsl:template>

  <xsl:template match="worksheet//exercise" mode="heading-divisional-exercise-serial">
    <xsl:variable name="hN">
      <xsl:apply-templates select="." mode="hN"/>
    </xsl:variable>
    <xsl:element name="{$hN}">
      <xsl:attribute name="class">heading</xsl:attribute>
      <xsl:if test="title">
        <span class="title">
          <xsl:apply-templates select="." mode="title-full"/>
        </span>
      </xsl:if>
    </xsl:element>
  </xsl:template>

  <xsl:template match="*[
      local-name() = 'h1' or
      local-name() = 'h2' or
      local-name() = 'h3' or
      local-name() = 'h4' or
      local-name() = 'h5' or
      local-name() = 'h6' or
      contains(concat(' ', normalize-space(@class), ' '), ' title ') or
      contains(concat(' ', normalize-space(@class), ' '), ' subtitle ')
    ]">
    <xsl:copy>
      <xsl:apply-templates select="@*"/>
      <xsl:if test="not(@aria-label)">
        <xsl:attribute name="aria-label">
          <xsl:value-of select="normalize-space(.)"/>
        </xsl:attribute>
      </xsl:if>
      <xsl:apply-templates/>
    </xsl:copy>
  </xsl:template>

</xsl:stylesheet>
