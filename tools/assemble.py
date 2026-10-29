import os, json
PROJ=os.getcwd()+'/proj'; MAP=PROJ+'/maps/nuketown'
ext=open('out/scene_ext.txt').read(); body=open('out/scene_body.txt').read()
spawns=json.load(open('out/spawns.json')) if os.path.exists('out/spawns.json') else dict(A=[[-25,14.0,-8]],B=[[18,14.0,-3]])
n_ext=ext.count('[ext_resource')
if 'structures_collision' not in ext:
    n_ext+=1
    ext+='\n[ext_resource type="PackedScene" path="res://maps/nuketown/collision/nuketown_structures_collision.gltf" id="%d"]'%n_ext
    body+='\n[node name="StructuresCollision" parent="." instance=ExtResource("%d")]\n'%n_ext
sub='''[sub_resource type="ProceduralSkyMaterial" id="sky_mat"]
sky_top_color = Color(0.32, 0.5, 0.78, 1)
sky_horizon_color = Color(0.72, 0.8, 0.9, 1)
ground_horizon_color = Color(0.72, 0.8, 0.9, 1)
ground_bottom_color = Color(0.55, 0.5, 0.42, 1)

[sub_resource type="Sky" id="sky"]
sky_material = SubResource("sky_mat")

[sub_resource type="Environment" id="env"]
background_mode = 2
sky = SubResource("sky")
ambient_light_source = 3
ambient_light_color = Color(0.75, 0.78, 0.85, 1)
ambient_light_energy = 0.8
tonemap_mode = 2
'''
extra='[node name="Environment" type="Node3D" parent="."]\n\n[node name="WorldEnvironment" type="WorldEnvironment" parent="Environment"]\nenvironment = SubResource("env")\n\n[node name="Sun" type="DirectionalLight3D" parent="Environment"]\ntransform = Transform3D(0.866, -0.354, 0.354, 0, 0.707, 0.707, -0.5, -0.612, 0.612, 0, 40, 0)\nlight_energy = 1.1\nshadow_enabled = false\n\n[node name="SpawnPoints" type="Node3D" parent="."]\n\n'
for team in ('A','B'):
    extra+='[node name="Team%s" type="Node3D" parent="SpawnPoints"]\n\n'%team
    for i,(x,y,z) in enumerate(spawns[team]):
        extra+='[node name="Spawn%s%d" type="Marker3D" parent="SpawnPoints/Team%s" groups=["spawn_team_%s"]]\ntransform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, %.3f, %.3f, %.3f)\n\n'%(team,i+1,team,team.lower(),x,y,z)
steps=n_ext+3+1
out='[gd_scene load_steps=%d format=3]\n\n%s\n\n%s\n%s\n%s\n'%(steps,ext,sub,body,extra)
open(MAP+'/Nuketown_original.tscn','w').write(out)
open(PROJ+'/project.godot','w').write('''; Engine configuration file (test project for Nuketown map conversion)
config_version=5

[application]
config/name="NuketownTest"
run/main_scene="res://maps/nuketown/Nuketown.tscn"
config/features=PackedStringArray("4.7", "Mobile")

[rendering]
renderer/rendering_method="mobile"
''')
print('scene written',os.path.getsize(MAP+'/Nuketown_original.tscn')//1024,'KB')
