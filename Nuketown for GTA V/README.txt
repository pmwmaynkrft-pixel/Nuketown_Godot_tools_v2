==============================================================================
   NUKETOWN  (Call of Duty: Black Ops)  -  Add-on map for GTA V story mode
==============================================================================

Nuketown, the 1960s nuclear test town from Call of Duty: Black Ops (2010),
ported 1:1 into GTA V as an add-on DLC map. It sits on its own desert island
in the sea off the north-east coast of San Andreas, so it does not replace or
touch anything in the normal map.

  Location:  X 6000, Y 10000  (see images\location_map.png)
  Size:      about 2.2 x 2.2 km (the town, the desert valley and its mountains)
  Pack:      dlcpacks\nuketown\dlc.rpf  (94 MB)


------------------------------------------------------------------------------
 WHAT'S INCLUDED
------------------------------------------------------------------------------
 - Both houses (the green house and the yellow house), fully enterable:
   ground floor, upstairs, garages, kitchens, living rooms, bedrooms, balconies.
   All doors and the closed garage door have been removed, so nothing blocks
   your way in or out.
 - Breakable windows: the house windows shatter when you shoot or hit them,
   like shop windows in GTA.
 - The cul-de-sac with the school bus and the moving truck, the mannequins,
   the backyards, fences, the fallout shelter, the neighbouring houses along
   the street, street lights and power lines.
 - The doomsday clock tower, the desert valley with bushes, rocks and power
   pylons, the army trucks down the road and the mountains around the valley.
 - The barricade at the street entrance to the cul-de-sac has been removed,
   so you can drive straight in.
 - The parked cars from Black Ops have been replaced by spawn points for clean
   Declasse Tornados (7 of them, in the driveways and along the street).
 - Full collision on everything you can see, with proper surfaces (wood,
   carpet, tiles, grass, sand, asphalt, metal...). No invisible walls.
 - Rooms are darker inside than outside, like in the original, and the house
   lamps are lit.

 Not included: Black Ops game-mode objects (bomb sites, HQ crates, flags),
 the end-of-match nuke, particle effects and sounds.


------------------------------------------------------------------------------
 REQUIREMENTS
------------------------------------------------------------------------------
 - GTA V (story mode). Made for GTA V Legacy.
 - OpenIV with the "mods" folder set up (ASI Loader + OpenIV.ASI installed
   from OpenIV: Tools > ASI Manager).
 - Optional: Menyoo or any trainer to teleport there.


------------------------------------------------------------------------------
 INSTALLATION
------------------------------------------------------------------------------
 1. Copy the folder  dlcpacks\nuketown  into

        Grand Theft Auto V\mods\update\x64\dlcpacks\

    so that you end up with
        Grand Theft Auto V\mods\update\x64\dlcpacks\nuketown\dlc.rpf

 2. In OpenIV (Edit mode on), open

        mods\update\update.rpf\common\data\dlclist.xml

    (if update.rpf is not in your mods folder yet: right-click
    update\update.rpf in OpenIV > "Copy to mods folder" first)

    and add this line just above </Paths>:

        <Item>dlcpacks:/nuketown/</Item>

    Save the file.

 3. Start story mode.


------------------------------------------------------------------------------
 GETTING THERE
------------------------------------------------------------------------------
 Fly or take a boat north-east from Paleto Bay / Mount Chiliad, or teleport.
 Good spots:

   Place                                    X         Y         Z      Heading
   Cul-de-sac (street entrance)          6001.0    9991.6     13.3       9
   Yellow house (inside, living room)    6018.3   10006.6     13.6     122

 Menyoo users: open Menyoo\Nuketown_teleports.xml, copy the two <Loc> blocks
 into  Grand Theft Auto V\menyooStuff\SavedMapLocations.xml  (just above the
 last line), then in game use Menyoo > Teleport > Saved Locations.

 The Tornados are normal parked-car spawns: they appear as you come near.
 If one is missing, drive away a bit and come back.


------------------------------------------------------------------------------
 COMPATIBILITY
------------------------------------------------------------------------------
 The island uses the area X 4870..7050, Y 8900..11130 (open sea north-east of
 the map). Other add-on maps that use the same spot will overlap with it.
 Nuketown does not replace any game file.


------------------------------------------------------------------------------
 UNINSTALL
------------------------------------------------------------------------------
 Remove the <Item>dlcpacks:/nuketown/</Item> line from dlclist.xml and delete
 the mods\update\x64\dlcpacks\nuketown folder.


------------------------------------------------------------------------------
 CREDITS
------------------------------------------------------------------------------
 Original map, models and textures: Treyarch / Activision
 (Call of Duty: Black Ops, mp_nuked).
 This is a non-commercial fan port. All rights to the original content
 belong to their owners.
 Tools: OpenAssetTools, CodeWalker, OpenIV, Blender.
==============================================================================
