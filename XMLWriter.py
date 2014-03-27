'''
Created on 26.03.2014

@author: tobi
'''

url=""
originX=-20037508.342787
originY=20037508.342787
anzZooms=18
latestwkid=900913
blockX=256
blockY=256

def writeFile():
    text = '''<GDAL_WMS>
    <Service name="TMS">
        <ServerUrl>'''
    
    text += str(url)
    
    text+='''</ServerUrl>
    </Service>
    <DataWindow>
        <UpperLeftX>'''
    
    text += str(originX)
    
    text += '''</UpperLeftX>
        <UpperLeftY>'''
    
    text += str(originY)
    
    text += '''</UpperLeftY>
        <LowerRightX>'''
    
    text += str(originY)
    
    text += '''</LowerRightX>
        <LowerRightY>'''
    
    text += str(originX)
    
    text += '''</LowerRightY>
        <TileLevel>'''
    
    text += str(anzZooms)
    
    text += '''</TileLevel>
        <TileCountX>1</TileCountX>
        <TileCountY>1</TileCountY>
        <YOrigin>top</YOrigin>
    </DataWindow>
    <Projection>EPSG:'''
    
    text += str(latestwkid)
    
    text += '''</Projection>
    <BlockSizeX>'''
    
    text += str(blockX)
    
    text += '''</BlockSizeX>
    <BlockSizeY>'''
    
    text += str(blockY)
    
    text += '''</BlockSizeY>
    <Cache />
</GDAL_WMS>'''
    
    return text

def writeV2():
    text = '''<GDAL_WMS>
  <Service name="TMS">
  <ServerUrl>'''
    text += url
    
    text += '''</ServerUrl>
  </Service>
  <DataWindow>
    <UpperLeftX>-20037508.34</UpperLeftX>
    <UpperLeftY>20037508.34</UpperLeftY>
    <LowerRightX>20037508.34</LowerRightX>
    <LowerRightY>-20037508.34</LowerRightY>
    <TileLevel>'''
    
    text += str(anzZooms)
    
    text += '''</TileLevel>
    <TileCountX>1</TileCountX>
    <TileCountY>1</TileCountY>
    <YOrigin>top</YOrigin>
  </DataWindow>
  <Projection>EPSG:900913</Projection>
  <BlockSizeX>256</BlockSizeX>
  <BlockSizeY>256</BlockSizeY>
  <BandsCount>3</BandsCount>
  <Cache />
</GDAL_WMS>'''
    return text
    