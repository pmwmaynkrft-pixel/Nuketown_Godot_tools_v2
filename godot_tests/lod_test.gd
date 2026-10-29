extends SceneTree
func _init():
	var mesh: Mesh = load("res://maps/nuketown/meshes/cc6e0b764209.res")
	var tris := 0
	for s in range(mesh.get_surface_count()): tris += (mesh.surface_get_arrays(s)[Mesh.ARRAY_INDEX] as PackedInt32Array).size() / 3
	print("mesh tris LOD0 = ", tris, " aabb=", mesh.get_aabb().size)
	var root = Node3D.new(); get_root().add_child(root)
	var cam = Camera3D.new(); cam.fov = 60; root.add_child(cam); await process_frame; cam.current = true
	for mode in ["MeshInstance3D", "MultiMesh"]:
		for d in [4.0, 10.0, 25.0, 60.0, 120.0]:
			for ch in root.get_children(): if ch != cam: ch.queue_free()
			await process_frame
			var n: Node3D
			if mode == "MeshInstance3D":
				var mi = MeshInstance3D.new(); mi.mesh = mesh; n = mi
			else:
				var mm = MultiMesh.new(); mm.transform_format = MultiMesh.TRANSFORM_3D; mm.mesh = mesh; mm.instance_count = 1
				mm.set_instance_transform(0, Transform3D.IDENTITY)
				var mmi = MultiMeshInstance3D.new(); mmi.multimesh = mm; n = mmi
			root.add_child(n); n.position = Vector3(0, -1, -d)
			cam.look_at_from_position(Vector3(0, 0.5, 0), Vector3(0, 0, -d))
			for i in range(5): await process_frame
			print(mode, " dist=", d, " primitives=", int(Performance.get_monitor(Performance.RENDER_TOTAL_PRIMITIVES_IN_FRAME)))
	quit(0)
