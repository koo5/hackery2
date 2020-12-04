<?xml version="1.0" encoding="iso-8859-1"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns="http://www.w3.org/TR/REC-html40">

<xsl:output method="html" version="1.0" encoding="UTF-8" indent="yes"/>

<!-- copy all nodes and attributes -->
<xsl:template match="node() | @*">
    <xsl:copy>
        <xsl:apply-templates select="node() | @*"/>
    </xsl:copy>
</xsl:template>

<!-- but remove annotations -->
<xsl:template match="xs:annotation"/>

</xsl:stylesheet>
 